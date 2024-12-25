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

        self.next_open = -1.0
        self.bg = BarGenerator(self.on_bar, 8, self.on_8h_bar, Interval.HOUR)
        self.am_8h = ArrayManager(self.atr_window + 1)
        self.am_1m = ArrayManager(self.his_window + 1)
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
        self.next_open = tick.last_price
        self.hpp = max(self.hpp, tick.ask_price_1)
        self.lpp = min(self.lpp, tick.bid_price_1)
        # self.cancel_all()
        if self.mp > 0:
            if tick.last_price >= self.long_profit_price or tick.last_price <= self.long_loss_price:
                self.mp = 0
        if self.mp < 0:
            if tick.last_price <= self.long_profit_price or tick.last_price >= self.long_loss_price:
                self.mp = 0
        self.put_event()

    def on_bar(self, bar: BarData):
        """
        Callback of new bar data update.
        """
        self.bg.update_bar(bar)
        self.am_1m.update_bar(bar)
        if not (self.am_1m.inited and self.am_8h.inited):
            return
        # next_open实盘是可以获取的，但是离线订单匹配的时候是cross机制，所以一定会match，实盘不一定抢得到
        # 但是这是符合预取的Key Point（by @xqli）
        self.upp = max(self.am_1m.high)
        self.dnn = min(self.am_1m.low)
        # trade logical
        if self.stopped or self.atr <= 0:
            return
        next_open = self.next_open if self.next_open > 0 else bar.next_open
        if self.mp == 0:
            if next_open - self.dnn > self.atr * self.k1: # short
                self.buy(next_open, self.volume)
                self.mp = 1
                self.enpp = self.hpp = self.lpp = next_open
                loss_id = self.sell(self.long_loss_price, self.volume, stop=True)[0] # loss
                prof_id = self.sell(self.long_profit_price, self.volume)[0] # profit
                self.order_pair[loss_id] = prof_id
                self.order_pair[prof_id] = loss_id
                self.write_log(f"buy:({self.enpp=},{self.long_loss_price=},{self.long_profit_price=},{self.volume=})")
            elif self.upp - next_open > self.atr * self.k1: # long
                self.short(next_open, self.volume)
                self.mp = -1
                self.enpp = self.hpp = self.lpp = next_open
                loss_id = self.cover(self.short_loss_price, self.volume, stop=True)[0] # loss
                prof_id = self.cover(self.short_profit_price, self.volume)[0] # profit
                self.order_pair[loss_id] = prof_id
                self.order_pair[prof_id] = loss_id
                self.write_log(f"sell:({self.enpp=},{self.long_loss_price=},{self.long_profit_price=},{self.volume=})")
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
        if self.next_open <= 0 and trade.offset == Offset.CLOSE: # close
            if trade.vt_orderid in self.order_pair:
                cid = self.order_pair[trade.vt_orderid]
                self.cancel_order(cid)
                del self.order_pair[cid]
                del self.order_pair[trade.vt_orderid]
                # self.write_log(f"cancel: order pair=(trade={trade.vt_orderid}, cancel={cid})")
            self.mp = 0
        self.write_log(f"trade:{self.__class__.__name__},{trade.price=},{trade.volume=},{trade.direction=},{trade.offset},{trade.orderid}")
        self.put_event()

    def on_stop_order(self, stop_order: StopOrder):
        """
        Callback of stop order update.
        """
        if self.next_open <= 0 and stop_order.offset == Offset.CLOSE: # close
            if stop_order.vt_orderids:
                vt_orderid = stop_order.stop_orderid
                if vt_orderid in self.order_pair:
                    cid = self.order_pair[vt_orderid]
                    self.cancel_order(cid)
                    del self.order_pair[cid]
                    del self.order_pair[vt_orderid]
                    # self.write_log(f"cancel: order pair=(trade={vt_orderid}, cancel={cid})")
            self.mp = 0
        self.put_event()
