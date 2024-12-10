import math
import pprint

from backtesting import Backtest, Strategy
from pyxirr import xirr

from data_reader import ACWD

AMOUNT_TO_INVEST = 5000


class DcaStrategy(Strategy):
    day_of_month_to_invest = 20

    def __init__(self, broker, data, params):
        super().__init__(broker, data, params)
        self.amount_to_invest = AMOUNT_TO_INVEST
        self.cashflows = []
        self.date_cashflows = []
        self.last_index = None
        self._commission = 0.002

    def init(self):
        self.last_index = len(self.data.Close) - 1

    def next(self):
        price = self.data.Close[-1]
        if len(self.data.Close) == self.last_index:
            self.cashflows.append(math.floor(self.equity))
            now = self.data.index[-1]
            # print(f"last day {now}")
            self.date_cashflows.append(now)
            # self.date_cashflows.append(datetime.datetime(now.year, now.month, now.day))
            return

        now = self.data.index[-1]
        if now.day >= self.day_of_month_to_invest and not self.is_bought_this_month():
            self.cashflows.append(-self.amount_to_invest)

            self.date_cashflows.append(now)
            # print(f"buy day {now}")
            adjusted_price = price * (1 + self._commission)
            math.floor(self.amount_to_invest / adjusted_price)
            self.buy(size=math.floor(self.amount_to_invest / price))

    def is_bought_this_month(self):
        if len(self.date_cashflows) == 0:
            return False
        return self.data.index[-1].month == self.date_cashflows[-1].month


ohlcv_data = ACWD
ohlcv_data["Volume"] *= 10**4
ohlcv_data *= 10**-4
ohlcv_data["Volume"] *= 10**4
bt = Backtest(ohlcv_data, DcaStrategy, cash=AMOUNT_TO_INVEST * 118, commission=0.002)

result = {}

for i in range(1, 29):
    stats = bt.run(day_of_month_to_invest=i)
    # stats = bt.optimize(day_of_month_to_invest=range(1, 29), maximize="Equity Final [$]")

    xirr_result = xirr(stats._strategy.date_cashflows, stats._strategy.cashflows) * 100
    stats["XIRR [%]"] = xirr_result

    pprint.pp(stats)
    result[i] = stats["Return [%]"]
# bt.plot()
sorted_result = sorted(result.items(), key=lambda item: item[1], reverse=True)
pprint.pp(sorted_result)
