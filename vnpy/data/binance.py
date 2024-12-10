import argparse
import pandas as pd

from binance.fut import CoinM
from binance.fut import USDTM


N_MS_PER_DAY = 24 * 3600E3



class Dumper(object):

    def __init__(self, kind='cm'):
        kind = kind.upper()
        if kind == 'CM':
            self.cli = CoinM()
        else:
            self.cli = USDTM()


class BarDumper(Dumper):

    def __init__(self, kind='cm'):
        super().__init__(kind)
    
    def dump(self, date, symbol):
        start_t = pd.to_datetime(date).timestamp() * 1000
        end_t = start_t + N_MS_PER_DAY
        dat = self.cli.klines(symbol, '1m', endTime=end_t, limit=1440)
        assert dat[-1][0] + 6E4 == end_t, 'expected the last bar.end_t == end_t'
        dat = pd.DataFrame(dat, columns=[
            'start_t', 'open', 'high', 'low', 'close',
            'volume', 'end_t', 'amount', 'trade_cnt',
            'taker_vol', 'taker_amt', 'reserved'
        ])
        return dat


class TickDumper(Dumper):

    def __init__(self, kind='cm'):
        super().__init__(kind)
    
    def dump(self, date, symbol):


        

if __name__ == "__main__":
