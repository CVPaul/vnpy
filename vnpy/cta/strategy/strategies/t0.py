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


class T0Strategy(CtaTemplate):
    """"""

    author = "T0"

    volume = 1
    maxpos = 5

    parameters = [
        # "freq",
        # "atr_window",
        # "his_window",
        "volume",
        "maxpos"
    ]

    variables = [
        # "atr",
        # "upp",
        # "dnn"
        "threshold"
    ]

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        """"""
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)

        self.bg = BarGenerator(self.on_bar)
        # self.am = ArrayManager(self.atr_window)
        # self.hm = ArrayManager(self.his_window)
        self.stopped = False
        self.threshold = 0.5
        self.last_trade = None
        self.last_trade_time = 0
    
    # def on_init_am(self, bar: BarData):
    #     self.am.update_bar(bar)
    
    # def on_init_hm(self, bar: BarData):
    #     self.hm.update_bar(bar)

    def on_init(self):
        """
        Callback when strategy is inited.
        """
        self.stopped = False
        self.write_log("策略初始化")
        # self.load_bar(self.atr_window // 3 + 1, "8h", self.on_init_am)
        # self.load_bar(self.his_window // 24 + 1,  "1m", self.on_init_hm)

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
        # if self.hm.inited and self.am.inited:
        #     return
        if tick.localtime.timestamp() - self.last_trade_time < 100: # 10s
            self.last_trade_time = tick.localtime.timestamp()
            return
        if self.last_trade and abs(tick.last_price / self.last_trade.price - 1.0) < 0.01:
            return
        self.cancel_all()
        if abs(self.pos) > self.maxpos:
            return
        if np.random.uniform() > self.threshold:
            if self.pos >= 0:
                self.buy(tick.bid_price_1, self.volume, False)
            else:
                self.cover(tick.bid_price_1, self.volume, False)
        else:
            if self.pos <= 0:
                self.short(tick.ask_price_1, self.volume, False)
            else:
                self.sell(tick.ask_price_1, self.volume, False)
        self.put_event()


    def on_bar(self, bar: BarData):
        """
        Callback of new bar data update.
        """

    def on_order(self, order: OrderData):
        """
        Callback of new order data update.
        """
        pass

    def on_trade(self, trade: TradeData):
        """
        Callback of new trade data update.
        """
        if self.last_trade:
            if trade.direction == Direction.LONG:
                if self.last_trade.direction == Direction.LONG:
                    self.threshold += 0.05
                else:
                    if self.last_trade.price * 0.999 > trade.price:
                        self.threshold += 0.1
                    elif self.last_trade.price < trade.price:
                        self.threshold -= 0.1
            else:
                if self.last_trade.direction == Direction.SHORT:
                    self.threshold -= 0.05
                else:
                    if self.last_trade.price * 1.001 < trade.price:
                        self.threshold -= 0.1
                    elif self.last_trade.price < trade.price:
                        self.threshold -= 0.1
            self.threshold = min(1.0, max(0, self.threshold))
        self.last_trade = trade
        self.put_event()

    def on_stop_order(self, stop_order: StopOrder):
        """
        Callback of stop order update.
        """
        pass
