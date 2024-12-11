import numpy as np

from vnpy.trader.constant import Interval, Direction, Offset
from vnpy.cta.strategy import (
    CtaTemplate,
    StopOrder,
    TickData,
    BarData,
    TradeData,
    OrderData,
    BarGenerator,
    ArrayManager,
)


class TakeFlashPinStrategy(CtaTemplate):
    """"""

    author = "T0"

    volume = 1
    period = 30
    ratio = 0.1
    hpp = 0.0

    parameters = [
        # "freq",
        # "atr_window",
        # "his_window",
        "volume",
        "period",
        "ratio",
        "hpp",
    ]

    variables = [
        # "atr",
        # "upp",
        # "dnn"
    ]

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        """"""
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)

        self.stopped = False
        self.last_order_time = 0

        self.bg = BarGenerator(self.on_bar)
        self.am = ArrayManager(self.period)
    
    def on_init(self):
        """
        Callback when strategy is inited.
        """
        self.stopped = False
        self.write_log("策略初始化")

    def on_start(self):
        """
        Callback when strategy is started.
        """
        self.write_log("策略启动")

    def on_stop(self):
        """
        Callback when strategy is stopped.
        """
        self.stopped = True
        self.write_log("策略停止")

    def on_tick(self, tick: TickData):
        """
        Callback of new tick data update.
        """
        # self.bg.update_tick(tick)
        # if self.hm.inited and self.am.inited:
        #     return
        self.hpp = max(self.hpp, tick.last_price)
        if self.stopped:
            return
        if tick.datetime.timestamp() - self.last_order_time < 10: # 10s
            return
        self.cancel_all()
        if self.hpp * (1.0 - self.ratio) > tick.bid_price_1:
            self.last_order_time = tick.datetime.timestamp()
            self.buy(tick.bid_price_1, self.volume, market=True)
        self.put_event()


    def on_bar(self, bar: BarData):
        """
        Callback of new bar data update.
        """
        am = self.am
        am.update_bar(bar)
        if not am.inited:
            return
        self.hpp = am.high[-1]
        self.put_event()

    def on_order(self, order: OrderData):
        """
        Callback of new order data update.
        """
        pass

    def on_trade(self, trade: TradeData):
        """
        Callback of new trade data update.
        """
        self.hpp = trade.price
        self.put_event()

    def on_stop_order(self, stop_order: StopOrder):
        """
        Callback of stop order update.
        """
        pass
