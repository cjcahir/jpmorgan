'''
Created on 10 Apr 2018

@author: conor
'''
from sssm.utils import assert_true

_fmt = "stock(name=%s, last_dividend=%s, par=%s, fixed_dividend=%s)"


class Stock(object):

    def __init__(self, name, last_dividend, par_value, fixed_dividend=None):
        """ constructor
        
        @param name - name of the stock
        @param last_dividend - last dividend for this stock in pennies
        @param par_value - par value for this stock in pennies
        @param fixed_dividend - optional fixed dividend percentage as a floating
            point number between 0 and 1.
        """
        self.name = name
        self.last_dividend = last_dividend
        self.par_value = par_value
        self.fixed_dividend = fixed_dividend

    def __str__(self):

        args = (
            self.name,
            self.last_dividend,
            self.par_value,
            self.fixed_dividend,
            )

        return _fmt % args

    def __repr__(self):
        return self.__str__()

    def get_name(self):
        return self.name

    def get_last_dividend(self):
        return self.last_dividend

    def get_fixed_dividend(self):
        return self.fixed_dividend

    def get_par_value(self):
        return self.par_value

    def dividend(self):
        """ return dividend using last_dividend or fixed_dividend if it is
        defined. """
        preferred = self.fixed_dividend != None

        return (self.fixed_dividend * self.par_value) if preferred else \
            self.last_dividend

    def validate_price(self, price):
        """ validate the given price value
        
        @param price - the price in pennies
        """
        assert_true(price > 0, "invalid price: %s" % price)

    def calculate_dividend_yield(self, price):
        """ calculate dividend yield for this stock at the given price.
        
        @param price - price in pennies
        """
        self.validate_price(price)
        return self.dividend() / float(price)

    def calculate_pe_ratio(self, price):
        """ calculate P/E ratio for this stock at the given price.
        
        @param price - price in pennies
        """

        # Note for reviewer:
        #
        # I interpreted the term "Dividend" in the bottom line of the formula
        # for P/E ratio as meaning the last dividend or fixed dividend, if
        # available, multiplied by the par value (i.e as in the top row of the
        # dividend yield formula, thus making the P/E ratio the inverse of the
        # dividend yield).
        #
        # I'm not sure if this is correct, however, as the formula sheet was
        # ambiguous and I don't have any experience of stock markets to call on.

        self.validate_price(price)
        dividend = self.dividend()
        return (float(price) / dividend) if dividend > 0 else None
