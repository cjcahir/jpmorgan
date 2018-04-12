'''
Created on 10 Apr 2018

@author: conor
'''

_fmt = "trade(id=%s, stock=%s, type=%s, quantity=%s, price=%s, timestamp=%s)"


class Trade(object):

    BUY = 0
    SELL = 1

    def __init__(self, trade_id, stock, trade_type, quantity, price, timestamp):
        """ constructor
        
        @param trade_id - unique id for this trade
        @param stock - name of the stock
        @param trade_type - buy or sell indicator (Trade.BUY / Trade.SELL)
        @param quantity - quantity traded
        @param pice - price traded at
        @param timestamp - integer timestamp (microseconds since epoch)
        """
        self.id = trade_id
        self.stock = stock
        self.trade_type = trade_type
        self.quantity = quantity
        self.price = price
        self.timestamp = timestamp

    def get_id(self):
        return self.id

    def get_stock(self):
        return self.stock

    def get_trade_type(self):
        return self.trade_type

    def get_quantity(self):
        return self.quantity

    def get_price(self):
        return self.price

    def get_timestamp(self):
        return self.timestamp

    def get_total_amount(self):
        return self.price * self.quantity

    def __str__(self):

        args = (
            self.id,
            self.stock,
            self.trade_type,
            self.quantity,
            self.price,
            self.timestamp
            )

        return _fmt % args

    def __repr__(self):
        return self.__str__()
