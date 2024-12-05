#!/usr/bin/env python
#-*- coding:utf-8 -*-


from vnpy.event import EventEngine
from vnpy.trader.engine import MainEngine
from vnpy.trader.ui import MainWindow, create_qapp
from vnpy.gateway.binance import Spot, CoinM, USDTM

from vnpy.cta.strategy import CtaStrategyApp


def main():
    """主入口函数"""
    qapp = create_qapp()

    event_engine = EventEngine()
    main_engine = MainEngine(event_engine)
    # add gateways
    main_engine.add_gateway(Spot)
    main_engine.add_gateway(CoinM)
    main_engine.add_gateway(USDTM)
    # add applications
    main_engine.add_app(CtaStrategyApp)
    # main window setting
    main_window = MainWindow(main_engine, event_engine)
    main_window.showMaximized()
    # start
    qapp.exec()


if __name__ == "__main__":
    main()
