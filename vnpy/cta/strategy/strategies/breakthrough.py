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


class BreakStrategy(CtaTemplate):
    """"""

    author = "Leurez"

    mp = 0
    k1 = 0.1
    s1 = 0.1
    s2 = 0.1
    volume = 1
    atr_window = 20
    his_window = 30


    parameters = [
        # "freq",
        "atr_window",
        "his_window",
        "volume",
        "period",
        "k1",
        "s1",
        "s2",
        "mp"
    ]

    variables = [
        "upp",
        "dnn",
        "atr",
        "ma",
        "range"
    ]

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        """"""
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)

        self.stopped = False
        self.last_order_time = 0
        self.upp = 0.0
        self.dnn = 0.0
        self.ma = 0.0
        self.range = 0.0
        self.hpp = 0.0
        self.lpp = 0.0
        self.enpp = 0.0
        self.mp = 0

        self.bg = BarGenerator(self.on_bar, 8, self.on_8h_bar, Interval.HOUR)
        self.am_8h = ArrayManager(self.atr_window + 1)
        self.am_1m = ArrayManager(self.his_window + 1)
    
    def on_init(self):
        """
        Callback when strategy is inited.
        """
        self.stopped = False
        self.load_bar(10)
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
        self.bg.update_tick(tick)
        self.hpp = max(self.hpp, tick.ask_price_1)
        self.lpp = max(self.lpp, tick.bid_price_1)
        if self.atr <= 0:
            return
        if not(self.am_1m.inited and self.am_8h.inited):
            return
        if self.stopped:
            return 
        # self.cancel_all()
        if self.mp == 0:
            if tick.ask_price_1 >= self.ma + self.atr * self.k1:
                self.buy(tick.ask_price_1, self.volume)
                self.mp = 1
            elif tick.bid_price_1 <= self.ma - self.atr * self.k1:
                self.short(tick.bid_price_1, self.volume)
                self.mp = -1
        elif self.mp > 0:
            # if tick.bid_price_1 <= self.enpp - self.atr * self.s2: # loss
            #     self.sell(tick.bid_price_1, self.mp)
            if tick.bid_price_1 <= self.hpp - self.atr * self.s1: # may loss
                self.sell(tick.bid_price_1, self.mp)
                self.mp = 0
        else:
            # if tick.ask_price_1 >= self.enpp + self.atr * self.s2: # loss
            #     self.cover(tick.bid_price_1, self.mp)
            if tick.ask_price_1 >= self.lpp + self.atr * self.s1: # may loss
                self.cover(tick.bid_price_1, self.mp)
                self.mp = 0
        self.put_event()

    def on_bar(self, bar: BarData):
        """
        Callback of new bar data update.
        """
        self.bg.on_bar(bar)
        self.am_1m.update_bar(bar)
        if not self.am_1m.inited:
            return
        self.hpp = self.am_1m.high[-1]
        self.dnn = self.am_1m.low[-1]
        self.put_event()
    
    def on_8h_bar(self, bar: BarData):
        self.am_8h.update_bar(bar)
        if not self.am_8h.inited:
            return
        self.atr = self.am_8h.atr(self.atr_window)
        self.ma = self.am_8h.sma(self.atr_window)

    def on_order(self, order: OrderData):
        """
        Callback of new order data update.
        """
        pass

    def on_trade(self, trade: TradeData):
        """
        Callback of new trade data update.
        """
        self.enpp = self.hpp = self.lpp = trade.price
        self.put_event()

    def on_stop_order(self, stop_order: StopOrder):
        """
        Callback of stop order update.
        """
        pass