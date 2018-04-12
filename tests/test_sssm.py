#!/usr/bin/env python3
'''
Created on 10 Apr 2018

@author: conor
'''

import unittest

from sssm import utils
from sssm.market import Market
from sssm.stock import Stock
from sssm.trade import Trade
from sssm.utils import geometric_mean, Error, reset_auto_increment, \
    auto_increment, assert_true


class TestBase(unittest.TestCase):

    def setUp(self):
        reset_auto_increment()
        self._micros_since_epoch = utils._micros_since_epoch
        self.tea = Stock("TEA", 0, 100)
        self.pop = Stock("POP", 8, 100)
        self.ale = Stock("ALE", 23, 60)
        self.gin = Stock("GIN", 8, 100, fixed_dividend=0.02)
        self.joe = Stock("JOE", 13, 250)

    def tearDown(self):
        self.clear_mocks()

    def mock_time(self, t):
        """ mock utils.micros_since_epoch to return given value """
        utils._micros_since_epoch = lambda : t

    def clear_mocks(self):
        """ reset any mocked functions in utils """
        utils._micros_since_epoch = self._micros_since_epoch

    def assert_trade(self, trade, **kwargs):
        """ assert data in given Trade object
        
        @param trade - the Trade object to assert
        @param kwargs - expected values for Trade object fields
        """
        self.assertEqual(trade.get_id(), kwargs["id"])
        self.assertEqual(trade.get_timestamp(), kwargs["timestamp"])
        self.assertEqual(trade.get_stock(), kwargs["stock"])
        self.assertEqual(trade.get_trade_type(), kwargs["trade_type"])
        self.assertEqual(trade.get_quantity(), kwargs["quantity"])
        self.assertEqual(trade.get_price(), kwargs["price"])
        total_amount = kwargs["price"] * kwargs["quantity"]
        self.assertEqual(trade.get_total_amount(), total_amount)


class UtilsTests(TestBase):

    def test_geometric_mean(self):
        self.assertEqual(geometric_mean([]), None)
        self.assertEqual(geometric_mean([1]), 1)
        self.assertEqual(geometric_mean([1, 1]), 1)
        self.assertEqual(geometric_mean([2]), 2)
        self.assertEqual(geometric_mean([2, 2]), 2)
        self.assertEqual(geometric_mean([4.5, 2]), 3)
        self.assertEqual(geometric_mean([4, 2, 1]), 2)

    def test_auto_increment(self):
        self.assertEqual(auto_increment(), 0)
        self.assertEqual(auto_increment(), 1)
        self.assertEqual(auto_increment(), 2)
        reset_auto_increment()
        self.assertEqual(auto_increment(), 0)

    def test_assert_true(self):
        assert_true(1, "foo")
        self.assertRaisesRegex(Error, "foo", assert_true, 0, "foo")


class StockTests(TestBase):

    def test_stock(self):
        """ test Stock object constructor """
        self.assertEqual(self.tea.get_name(), "TEA")
        self.assertEqual(self.tea.get_last_dividend(), 0)
        self.assertEqual(self.tea.get_fixed_dividend(), None)
        self.assertEqual(self.tea.get_par_value(), 100)
        self.assertEqual(self.gin.get_name(), "GIN")
        self.assertEqual(self.gin.get_last_dividend(), 8)
        self.assertEqual(self.gin.get_fixed_dividend(), 0.02)
        self.assertEqual(self.gin.get_par_value(), 100)

        self.assertEqual(
            str(self.tea),
            "stock(name=TEA, last_dividend=0, par=100, fixed_dividend=None)"
            )

        self.assertEqual(
            str(self.gin),
            "stock(name=GIN, last_dividend=8, par=100, fixed_dividend=0.02)"
            )

    def test_calculate_dividend_yield(self):
        """ test dividend yield calculation for all stocks """

        def case(stock, price, exp_yield):
            self.assertEqual(stock.calculate_dividend_yield(price), exp_yield)

        price = 100.0

        case(self.tea, price, 0)
        case(self.pop, price, 0.08)
        case(self.ale, price, 0.23)
        case(self.gin, price, 0.02)
        case(self.joe, price, 0.13)

    def test_calculate_dividend_yield_invalid_price(self):
        """ test handling of invalid price given to calculate_dividend_yield """
        func = self.tea.calculate_dividend_yield
        self.assertRaisesRegex(Error, "invalid price: 0", func, 0)

    def test_calculate_pe_ratio(self):
        """ test P/E ratio calculation for all stocks """

        # note for reviewer: see comment in stock.Stock.calculate_pe_ratio

        def case(stock, price, exp_pe_ratio):
            self.assertEqual(stock.calculate_pe_ratio(price), exp_pe_ratio)

        price = 100.0

        case(self.tea, price, None)
        case(self.pop, price, price / 8)
        case(self.ale, price, price / 23)
        case(self.gin, price, price / 2)
        case(self.joe, price, price / 13)

    def test_calculate_pe_ratio_invalid_price(self):
        """ test handling of invalid price given to calculate_pe_ratio """
        func = self.tea.calculate_pe_ratio
        self.assertRaisesRegex(Error, "invalid price: 0", func, 0)


class TradeTests(TestBase):

    def test_trade(self):
        """ test Trade object constructor """
        t = 10 ** 6  # epoch + 1s
        trade = Trade(0, "TEA", Trade.BUY, 1000, 100, t)

        self.assert_trade(
            trade,
            id=0,
            timestamp=t,
            stock="TEA",
            trade_type=Trade.BUY,
            quantity=1000,
            price=100
            )

        exp_str = "trade(id=0, stock=TEA, type=0, quantity=1000, price=100, timestamp=1000000)"
        self.assertEqual(str(trade), exp_str)


class MarketTests(TestBase):

    def setUp(self):
        TestBase.setUp(self)
        self.market = Market()
        self.market.add_stock(self.tea)
        self.market.add_stock(self.pop)
        self.market.add_stock(self.ale)
        self.market.add_stock(self.gin)
        self.market.add_stock(self.joe)

        self.t1 = 10 ** 6  # epoch + 1s
        self.t2 = 600 * (10 ** 6)  # epoch + 10 minutes

    def record_trades(self, all_trades=False):
        """ record some trades at mocked time points, then some extra ones if
        all_trades=True. """
        record = self.market.record_trade

        self.mock_time(self.t1)
        self.tea_trade_1 = record("TEA", Trade.BUY, 1000, 100)
        self.mock_time(2 * self.t1)
        self.tea_trade_2 = record("TEA", Trade.SELL, 1000, 100)
        self.pop_trade_1 = record("POP", Trade.BUY, 2000, 100)

        if all_trades:
            self.mock_time(self.t2 - 5)
            self.tea_trade_3 = record("TEA", Trade.BUY, 1000, 100)
            self.mock_time(self.t2 - 4)
            self.tea_trade_4 = record("TEA", Trade.BUY, 1000, 100)
            self.mock_time(self.t2 - 3)
            self.tea_trade_5 = record("TEA", Trade.SELL, 2000, 150)
            self.mock_time(self.t2 - 2)
            self.pop_trade_2 = record("POP", Trade.BUY, 1000, 100)

    def test_get_stock(self):
        """ test getting stock by name """
        self.assertEqual(self.market.get_stock("TEA"), self.tea)
        self.assertEqual(self.market.get_stock("POP"), self.pop)
        self.assertEqual(self.market.get_stock("ALE"), self.ale)
        self.assertEqual(self.market.get_stock("GIN"), self.gin)
        self.assertEqual(self.market.get_stock("JOE"), self.joe)
        self.assertEqual(self.market.get_stock("FOO"), None)

    def test_get_all_stocks(self):
        """ test getting all stocks """
        stock_order = ["ALE", "GIN", "JOE", "POP", "TEA"]
        results = [self.market.get_stock(stock) for stock in stock_order]
        self.assertEqual(self.market.get_all_stocks(), results)

    def test_add_duplicate_stock_error(self):
        """ test error when try to add duplicate named stock """
        error_regex = "duplicate stock: 'TEA'"

        self.assertRaisesRegex(
            Error, error_regex, self.market.add_stock, self.tea
            )

    def test_record_trade(self):
        """ test recording a single trade """
        self.mock_time(self.t1)
        trade = self.market.record_trade("TEA", Trade.BUY, 1000, 100)

        self.assert_trade(
            trade,
            id=0,
            timestamp=self.t1,
            stock="TEA",
            trade_type=Trade.BUY,
            quantity=1000,
            price=100
            )

        self.assertEqual(self.market.get_trades("TEA")[0], trade)

    def test_record_trade_errors(self):
        """ test error raised for invalid values given to record_trade """

        cases = [
            (("FOO", Trade.BUY, 1000, 100), "unknown stock: 'FOO'"),
            (("TEA", 2, 1000, 100), "invalid type: 2"),
            (("TEA", Trade.BUY, 0, 100), "invalid quantity: 0"),
            (("TEA", Trade.BUY, -1, 100), "invalid quantity: -1"),
            (("TEA", Trade.BUY, 1000, -1), "invalid price: -1"),
            ]

        for args, err in cases:
            self.assertRaisesRegex(Error, err, self.market.record_trade, *args)

    def test_get_trades(self):
        """ test fetching recorded trades by stock """
        self.record_trades()
        tea_trades = [self.tea_trade_1, self.tea_trade_2]
        self.assertEqual(self.market.get_trades("TEA"), tea_trades)
        self.assertEqual(self.market.get_trades("POP"), [self.pop_trade_1])

    def test_get_trades_period(self):
        """ test getting all trades for a stock during given period """
        self.record_trades()
        now = 2.5 * self.t1
        self.mock_time(now)  # time is epoch + 2.5 seconds

        # results from last second
        dt = self.t1
        self.assertEqual(
            self.market.get_trades("TEA", period=(now - dt, now)),
            [self.tea_trade_2]
            )

        # results from last two seconds
        dt = 2 * self.t1
        self.assertEqual(
            self.market.get_trades("TEA", period=(now - dt, now)),
            [self.tea_trade_1, self.tea_trade_2]
            )

    def test_volume_weighted_stock_price(self):
        """ test volume weighted stock price calculation """

        self.record_trades(True)
        now = self.t2  # epoch + 10 minutes
        five_minutes = now / 2
        self.mock_time(now)
        last_five_minutes = (now - five_minutes, now)

        # TEA
        # vwsp = sum_i(price_i * quantity_i) / sum_i(quantity_i)
        #      = 500000                      / 4000
        #      = 125

        self.assertEqual(
            self.market.calculate_vwsp("TEA", last_five_minutes), 125
            )

        # POP
        # vwsp = sum_i(price_i * quantity_i) / sum_i(quantity_i)
        #      = 100000                      / 1000
        #      = 100

        self.assertEqual(
            self.market.calculate_vwsp("POP", last_five_minutes), 100
            )

        # ALE
        # vwsp = None (no trades)
        self.assertEqual(
            self.market.calculate_vwsp("ALE", last_five_minutes), None
            )

    def test_volume_weighted_stock_price_default_period(self):
        """ test default value used (five minutes) when no period given """

        self.record_trades(True)
        now = self.t2
        self.mock_time(now)

        self.assertEqual(self.market.calculate_vwsp("TEA"), 125)

    def test_gbce_all_share_index(self):
        """ test gbce all share index calculation """

        now = self.t2
        self.mock_time(now)
        five_minutes = now / 2
        period = (now - five_minutes, now)

        # cannot calculate valid value with no trades so return None
        self.assertEqual(self.market.calculate_gbce_asi(period), None)

        # now with trades

        self.record_trades(True)
        self.mock_time(now)

        # gbce_asi = geometric_mean([volume weighted stock prices])
        #
        # (ignore stocks with no trades as they don't have valid vwsp)
        #
        #          = geometric_mean([125, 100])
        #          = sqrt(12500)

        exp = 12500 ** 0.5

        self.assertEqual(self.market.calculate_gbce_asi(period), exp)

    def test_gbce_all_share_index_default_value(self):
        """ test default value used when no period given """

        self.record_trades(True)
        now = self.t2
        self.mock_time(now)
        exp = 12500 ** 0.5

        self.assertEqual(self.market.calculate_gbce_asi(), exp)


if __name__ == "__main__":
    unittest.main()

