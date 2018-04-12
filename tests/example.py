#!/usr/bin/env python3
'''
Created on 12 Apr 2018

@author: conor
'''
from sssm.market import Market
from sssm.stock import Stock
from sssm.trade import Trade


def main():

    # create market and add stocks

    market = Market()
    market.add_stock((Stock("TEA", 0, 100)))
    market.add_stock((Stock("POP", 8, 100)))
    market.add_stock((Stock("GIN", 8, 100, 0.02)))

    print("market stocks:")
    for stock in market.get_all_stocks():
        print(stock)

    tea = market.get_stock("TEA")
    pop = market.get_stock("POP")
    gin = market.get_stock("GIN")

    # calculate dividend yields

    print("dividend yield for TEA at 10 pence: %s" % tea.calculate_dividend_yield(10))
    print("dividend yield for POP at 10 pence: %s" % pop.calculate_dividend_yield(10))
    print("dividend yield for GIN at 10 pence: %s" % gin.calculate_dividend_yield(10))

    # calculate P/E ratios

    print("P/E ratio for TEA at 10 pence: %s" % tea.calculate_pe_ratio(10))
    print("P/E ratio for POP at 10 pence: %s" % pop.calculate_pe_ratio(10))
    print("P/E ratio for GIN at 10 pence: %s" % gin.calculate_pe_ratio(10))

    # record some trades

    market.record_trade("TEA", Trade.BUY, 100, 99)
    market.record_trade("TEA", Trade.SELL, 100, 102)
    market.record_trade("POP", Trade.BUY, 200, 100)

    print("TEA trades:")
    for trade in market.get_trades("TEA"):
        print(trade)

    print("POP trades:")
    for trade in market.get_trades("POP"):
        print(trade)

    print("GIN trades:")
    for trade in market.get_trades("GIN"):
        print(trade)

    # calculate volume weighted stock prices
    print("VWSP for TEA: %s" % market.calculate_vwsp("TEA"))
    print("VWSP for POP: %s" % market.calculate_vwsp("POP"))
    print("VWSP for GIN: %s" % market.calculate_vwsp("GIN"))

    # calculate GBCE all share index over all stocks
    print("GBCE ASI: %s" % market.calculate_gbce_asi())


"""
##################
# console output #
##################

market stocks:
stock(name=GIN, last_dividend=8, par=100, fixed_dividend=0.02)
stock(name=POP, last_dividend=8, par=100, fixed_dividend=None)
stock(name=TEA, last_dividend=0, par=100, fixed_dividend=None)
dividend yield for TEA at 10 pence: 0.0
dividend yield for POP at 10 pence: 0.8
dividend yield for GIN at 10 pence: 0.2
P/E ratio for TEA at 10 pence: None
P/E ratio for POP at 10 pence: 1.25
P/E ratio for GIN at 10 pence: 5.0
TEA trades:
trade(id=0, stock=TEA, type=0, quantity=100, price=99, timestamp=1523567551269963)
trade(id=1, stock=TEA, type=1, quantity=100, price=102, timestamp=1523567551269976)
POP trades:
trade(id=2, stock=POP, type=0, quantity=200, price=100, timestamp=1523567551269982)
GIN trades:
VWSP for TEA: 100.5
VWSP for POP: 100.0
VWSP for GIN: None
GBCE ASI: 100.2496882788171
"""

if __name__ == '__main__':
    main()
