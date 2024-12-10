import pandas as pd


def read_file(filename):
    from os.path import dirname, join

    return pd.read_csv(
        join(dirname(__file__), filename),
        index_col=0,
        parse_dates=["Date"],
        dayfirst=True,
        infer_datetime_format=True,
        delimiter="\t",
    )


VWRA = read_file("data/VWRA_ohlcv.csv")
ACWD = read_file("data/ACWD_ohlcv.csv")
