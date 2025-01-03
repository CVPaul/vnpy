#!/usr/bin/env python
#-*- coding:utf-8 -*-


from vnpy.cta.backtest.engine import BacktesterEngine
from vnpy.event import EventEngine
from vnpy.trader.engine import MainEngine
from vnpy.trader.ui import MainWindow, create_qapp
from vnpy.gateway.binance import Spot, CoinM, USDTM, UnifyCM

from vnpy.cta.strategy.base import EVENT_CTA_LOG
from vnpy.cta.strategy import CtaStrategyApp
from vnpy.cta.backtest import CtaBacktesterApp
from vnpy.data.recorder import DataRecorderApp
from vnpy.portfolio import PortfolioStrategyApp


def main():
    """主入口函数"""
    qapp = create_qapp()

    event_engine = EventEngine()
    main_engine = MainEngine(event_engine)
    # add gateways
    main_engine.add_gateway(UnifyCM)
    main_engine.add_gateway(Spot)
    main_engine.add_gateway(CoinM)
    main_engine.add_gateway(USDTM)
    # add applications
    main_engine.add_app(CtaStrategyApp)
    main_engine.add_app(DataRecorderApp)
    main_engine.add_app(CtaBacktesterApp)
    main_engine.add_app(PortfolioStrategyApp)
    # add log event
    log_engine = main_engine.get_engine("log")
    event_engine.register(
            EVENT_CTA_LOG, log_engine.process_log_event)
    # main window setting
    main_window = MainWindow(main_engine, event_engine)
    main_window.showMaximized()
    # start
    qapp.exec()


if __name__ == "__main__":
    main()
