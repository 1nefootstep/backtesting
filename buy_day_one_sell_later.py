import pprint

import pandas as pd
from backtesting import Backtest, Strategy

from data_reader import ACWD

AMOUNT_TO_INVEST = 5000


class BuyStartMonthAndSellEndMonth(Strategy):
    day_to_buy = 1
    day_to_sell = 24

    def __init__(self, broker, data, params):
        super().__init__(broker, data, params)
        self.amount_to_invest = AMOUNT_TO_INVEST
        self.date_cashflows_buy = []
        self.date_cashflows_sell = []
        self.last_index = None
        self._commission = 0.002
        self.price_last_buy = None

    def init(self):
        self.last_index = len(self.data.Close) - 1

    def next(self):
        price = self.data.Close[-1]
        now = self.data.index[-1]

        if (
            self.day_to_buy <= now.day <= 10
            and not self.is_bought_this_month()
            and self.price_last_buy is None
        ):
            self.date_cashflows_buy.append(now)
            self.price_last_buy = price
            self.buy()
            return

        if (
            self.day_to_sell <= now.day <= 31
            and not self.is_sold_this_month()
            and self.price_last_buy is not None
            and price > self.price_last_buy
        ):
            self.position.close()
            self.price_last_buy = None
            self.date_cashflows_sell.append(now)
            return

    def is_bought_this_month(self):
        if len(self.date_cashflows_buy) == 0:
            return False
        return self.data.index[-1].month == self.date_cashflows_buy[-1].month

    def is_sold_this_month(self):
        if len(self.date_cashflows_sell) == 0:
            return False
        return self.data.index[-1].month == self.date_cashflows_sell[-1].month


ohlcv_data = ACWD
ohlcv_data["Volume"] *= 10**4
ohlcv_data *= 10**-4
ohlcv_data["Volume"] *= 10**4
bt = Backtest(ohlcv_data, BuyStartMonthAndSellEndMonth, cash=10000, commission=0.002)

# stats = bt.run(day_to_buy=3, day_to_sell=21)
# pprint.pp(stats)
# pprint.pp(f"trades: {stats._trades}")
# pprint.pp(f"buy: {stats._strategy.date_cashflows_buy}")
# pprint.pp(f"sell: {stats._strategy.date_cashflows_sell}")
# bt.plot(superimpose=False)

stats, heatmap = bt.optimize(
    day_to_buy=range(1, 10),
    day_to_sell=range(20, 28),
    maximize="Equity Final [$]",
    return_heatmap=True,
)

pd.set_option("display.max_rows", 500)
pprint.pp(heatmap.sort_values(ascending=False))
