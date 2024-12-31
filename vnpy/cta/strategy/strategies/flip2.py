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


class Flip2Strategy(CtaTemplate):
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
        "k1",
        "s1",
        "s2",
        "mp"
    ]

    variables = [
        "ma",
        "upp",
        "dnn",
        "atr",
        "hpp",
        "lpp",
        "enpp"
    ]

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        """"""
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)

        self.stopped = True
        self.last_order_time = 0
        self.atr = 0.0
        self.upp = 0.0
        self.dnn = 0.0
        self.ma = 0.0
        self.hpp = 0.0
        self.lpp = 0.0
        self.enpp = 0.0
        self.count = 0

        self.next_open = -1.0
        self.bg = BarGenerator(self.on_bar, 8, self.on_8h_bar, Interval.HOUR)
        self.am_8h = ArrayManager(self.atr_window + 1)
        self.am_1m = ArrayManager(self.his_window)
        self.order_pair = {}
    
    def on_init(self):
        """
        Callback when strategy is inited.
        """
        self.load_bar(10)
        self.write_log("策略初始化")

    def on_start(self):
        """
        Callback when strategy is started.
        """
        self.stopped = False
        self.write_log("策略启动")

    def on_stop(self):
        """
        Callback when strategy is stopped.
        """
        self.stopped = True
        self.write_log("策略停止")

    @property
    def long_loss_price(self):
        return self.enpp - self.atr * self.s1

    @property
    def long_profit_price(self):
        return self.enpp + self.atr * self.s2

    @property
    def short_loss_price(self):
        return self.enpp + self.atr * self.s1

    @property
    def short_profit_price(self):
        return self.enpp - self.atr * self.s2

    def on_tick(self, tick: TickData):
        """
        Callback of new tick data update.
        """
        self.bg.update_tick(tick)
        # trade logical
        if self.stopped:
            return
        if not (self.am_8h.inited and self.am_1m.inited):
            return
        # self.cancel_all()
        # open
        cond_s = self.upp - tick.bid_price_1 > self.k1 * self.atr
        cond_l = tick.ask_price_1 - self.dnn > self.k1 * self.atr
        if self.mp == 0 and cond_l:
            self.write_log(f'long-open,{self.atr},{self.upp},{self.dnn},{tick.bid_price_1}')
            self.buy(tick.bid_price_1, self.volume)
            self.enpp = tick.bid_price_1
            self.mp = 1
        if self.mp == 0 and cond_s:
            self.write_log(f'short-open,{self.atr},{self.upp},{self.dnn},{tick.ask_price_1}')
            self.short(tick.ask_price_1, self.volume)
            self.enpp = tick.ask_price_1
            self.mp = -1
        # close
        if self.mp > 0 and not cond_l:
            if tick.bid_price_1 < self.long_loss_price:
                self.write_log(f'long-win,{self.atr},{self.upp},{self.dnn},{tick.bid_price_1}')
                self.sell(tick.bid_price_1, self.volume)
                self.mp = 0
            elif tick.ask_price_1 > self.long_profit_price:
                self.write_log(f'long-win,{self.atr},{self.upp},{self.dnn},{tick.ask_price_1}')
                self.sell(tick.ask_price_1, self.volume)
                self.mp = 0
        if self.mp < 0 and not cond_s:
            if tick.ask_price_1 > self.short_loss_price:
                self.write_log(f'short-loss,{self.atr},{self.upp},{self.dnn},{tick.ask_price_1}')
                self.cover(tick.ask_price_1, self.volume)
                self.mp = 0
            elif tick.bid_price_1 < self.short_profit_price:
                self.write_log(f'short-win,{self.atr},{self.upp},{self.dnn},{tick.bid_price_1}')
                self.cover(tick.bid_price_1, self.volume)
                self.mp = 0
        self.put_event()

    def on_bar(self, bar: BarData):
        """
        Callback of new bar data update.
        """
        self.bg.update_bar(bar)
        self.am_1m.update_bar(bar)
        if not self.am_1m.inited:
            return
        # 但是这是符合预取的Key Point（by @xqli）
        self.upp = np.mean(self.am_1m.high)
        self.dnn = np.mean(self.am_1m.low)
        self.put_event()
    
    def on_8h_bar(self, bar: BarData):
        self.am_8h.update_bar(bar)
        if not self.am_8h.inited:
            return
        self.atr = self.am_8h.atr(self.atr_window)

    def on_order(self, order: OrderData):
        """
        Callback of new order data update.
        """
        pass

    def on_trade(self, trade: TradeData):
        """
        Callback of new trade data update.
        """
        self.put_event()

    def on_stop_order(self, stop_order: StopOrder):
        """
        Callback of stop order update.
        """
        self.put_event()
