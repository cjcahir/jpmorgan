'''
Created on 10 Apr 2018

@author: conor
'''
from sssm.trade import Trade
from sssm.utils import micros_since_epoch, auto_increment, geometric_mean, \
    assert_true

_five_minutes = (300 * (10 ** 6))  # five minutes in microseconds


def _default_period():
    now = micros_since_epoch()
    return (now - _five_minutes, now)


class Market(object):

    def __init__(self):
        self.stocks = {}
        self.trades = []

    def add_stock(self, stock):
        """ add a given stock to the market.
        
        @param stock - Stock object
        """
        name = stock.get_name()
        assert_true(name not in self.stocks, "duplicate stock: %r" % name)
        self.stocks[name] = stock

    def get_stock(self, name):
        """ return named stock
        
        @param name - name of stock to return
        """
        return self.stocks.get(name)

    def get_all_stocks(self):
        """ return all stocks orderd by name """
        return sorted(self.stocks.values(), key=lambda stock: stock.get_name())

    def record_trade(self, stock, trade_type, quantity, price):
        """ create new trade for given values with auto increment id and
        timestamp and store it. Also return newly created trade object.
        
        @param stock - name of the stock
        @param trade_type - buy or sell indicator (Trade.BUY / Trade.SELL)
        @param quantity - quantity traded
        @param pice - price traded at
        """

        assert_true(stock in self.stocks, "unknown stock: %r" % stock)
        valid_type = trade_type in [Trade.BUY, Trade.SELL]
        assert_true(valid_type, "invalid type: %s" % trade_type)
        assert_true(quantity > 0, "invalid quantity: %s" % quantity)
        assert_true(price >= 0, "invalid price: %s" % price)

        trade_id = auto_increment()
        ts = micros_since_epoch()
        new_trade = Trade(trade_id, stock, trade_type, quantity, price, ts)
        self.trades.append(new_trade)
        return new_trade

    def get_trades(self, stock, period=None):
        """ get all trades for the given stock chronologically, optionally
        within the given period.
        
        @param stock - name of the stock
        @param period - optional tuple of (t1, t2) in microseconds (default is
          all trades)
        """

        def include_trade(trade):
            """ return True to include trade if correct stock and, optionally,
            within period
            
            @param trade - the Trade object
            """

            if trade.get_stock() == stock:

                if period:
                    timestamp = trade.get_timestamp()
                    t1, t2 = period
                    return timestamp >= t1 and timestamp < t2

                else:
                    return True

            else:
                return False

        return list(filter(include_trade, self.trades))

    def calculate_vwsp(self, stock, period=None):
        """ calculate volume weighted stock price for all trades over given
        period.
        
        @param stock - name of the stock
        @param period - optional tuple of (t1, t2) in microseconds (default is
          last five minutes)
        """

        trades = self.get_trades(stock, period or _default_period())

        if trades:
            top = sum([trade.get_total_amount() for trade in trades])
            bottom = sum([trade.get_quantity() for trade in trades])
            return float(top) / bottom

        else:
            return None

    def calculate_gbce_asi(self, period=None):
        """ calculate GBCE all share index for all stocks over given period.
        
        @param period - optional tuple of (t1, t2) in microseconds (default is
          last five minutes)
        """

        stocks = self.stocks.keys()
        period = period or _default_period()
        vwsps = [self.calculate_vwsp(stock, period) for stock in stocks]

        # remove None values for stocks with no trades
        actual_vwsps = list(filter(lambda val: val != None, vwsps))

        return geometric_mean(actual_vwsps)

