import pprint

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

    def init(self):
        self.last_index = len(self.data.Close) - 1

    def next(self):
        price = self.data.Close[-1]
        now = self.data.index[-1]

        if self.day_to_buy <= now.day <= 10 and not self.is_bought_this_month():
            self.date_cashflows_buy.append(now)
            self.buy()
            return

        if self.day_to_sell <= now.day <= 31 and not self.is_sold_this_month():
            self.position.close()
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

stats = bt.run(day_to_buy=3, day_to_sell=26)
pprint.pp(stats)
# pprint.pp(f"trades: {stats._trades}")
# pprint.pp(f"buy: {stats._strategy.date_cashflows_buy}")
# pprint.pp(f"sell: {stats._strategy.date_cashflows_sell}")
bt.plot(superimpose=False)

# result = []
# for buy in range(1, 10):
#     for sell in range(20, 28):
#         stats = bt.run(day_to_buy=buy, day_to_sell=sell)
#         # stats = bt.optimize(day_of_month_to_invest=range(1, 29), maximize="Equity Final [$]")
#
#         # xirr_result = xirr(stats._strategy.date_cashflows, stats._strategy.cashflows) * 100
#         # stats["XIRR [%]"] = xirr_result
#         #
#         # pprint.pp(stats)
#         result.append((buy, sell, stats["Return [%]"]))
# sorted_result = sorted(result, key=lambda item: item[2], reverse=True)
# pprint.pp(sorted_result)
