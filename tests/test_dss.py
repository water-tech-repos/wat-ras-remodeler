"""Tests for reading hydrograph data"""
import numpy as np
from dss_util import read_dss_timeseries, read_csv_timeseries


def test_read_dss():
    """Test reading dss file on local filesystem"""
    timeseries = read_dss_timeseries(
        "tests/data/hydrograph.dss:/REGULAR/TIMESERIES/FLOW//1HOUR/Ex1/")
    num_rows = len(timeseries.index)
    assert num_rows == 7
    assert timeseries.columns[0] == 'time'
    assert timeseries.columns[1] == 'value'
    assert timeseries.dtypes['time'] == np.dtype('datetime64[ns]')
    assert timeseries.dtypes['value'] == np.dtype('float32')


def test_read_csv():
    """Test reading csv file on local filesystem"""
    timeseries = read_csv_timeseries("tests/data/hydrograph.csv")
    num_rows = len(timeseries.index)
    assert num_rows == 728
    assert timeseries.columns[0] == 'time'
    assert timeseries.columns[1] == 'value'
    assert timeseries.dtypes['time'] == np.dtype('datetime64[ns]')
    assert timeseries.dtypes['value'] == np.dtype('float32')
