from datetime import datetime

from vnpy.trader.utility import ArrayManager
from vnpy.trader.object import TickData, BarData
from vnpy.trader.constant import Direction

from vnpy.portfolio import StrategyTemplate, StrategyEngine
from vnpy.portfolio.utility import PortfolioBarGenerator


class DataDumper(StrategyTemplate):
    """DataDumper"""

    author = "用Python的交易员"

    parameters = [
    ]
    variables = [
    ]

    def __init__(
        self,
        strategy_engine: StrategyEngine,
        strategy_name: str,
        vt_symbols: list[str],
        setting: dict
    ) -> None:
        """构造函数"""
        super().__init__(strategy_engine, strategy_name, vt_symbols, setting)
        self.pbg = PortfolioBarGenerator(self.on_bars)

    def on_init(self) -> None:
        """策略初始化回调"""
        self.write_log("策略初始化")

    def on_start(self) -> None:
        """策略启动回调"""
        self.write_log("策略启动")

    def on_stop(self) -> None:
        """策略停止回调"""
        self.write_log("策略停止")

    def on_tick(self, tick: TickData) -> None:
        """行情推送回调"""
        self.pbg.update_tick(tick)

    def on_bars(self, bars: dict[str, BarData]) -> None:
        """K线切片回调"""
        # 更新K线计算RSI数值
        self.put_event()