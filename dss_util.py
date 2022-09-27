"""Utility functions for DSS files"""
import os
from pydsstools.heclib.dss import HecDss
import pandas as pd
from fs_util import get_file


def read_dss_timeseries(dss_path: str, irregular: bool = False) -> pd.DataFrame:
    """Read a path from a dss file pointing to timeseries data into a pandas dataframe. Time column is 'time' and value
    column is 'value'.

    Args:
        dss_path (str): DSS file and pathname formated as shown below:
            For local file use:
             - <filepath>:<pathname>
            For S3 use:
             - s3://<bucket_name>/<key_name>:<path/name>
            For Azure use:
             - abfs://<container_name>/<key_name>:<path/name>
        irregular (bool, optional): is timeseries data irregular? Defaults to False.

    Returns:
        pd.DataFrame: Dataframe with time column 'time' with datetime entries and value column 'value' with float
        entries.
    """
    uri, pathname = dss_path.rsplit(':', 1)
    dss_filepath = get_file(uri)
    timeseries = pd.DataFrame(columns=['time', 'value'])
    with HecDss.Open(dss_filepath) as fid:
        dss_ts = fid.read_ts(pathname, regular=not irregular)
        timeseries['time'] = dss_ts.pytimes
        timeseries['value'] = dss_ts.values
    # delete temp file
    os.remove(dss_filepath)
    return timeseries


def read_csv_timeseries(csv_uri: str, sep: str = ',') -> pd.DataFrame:
    """Read a csv file pointing to timeseries data into a pandas dataframe. Time column is 'time' and value
    column is 'value'. CSV file should have headers and the first column should be datetime format parsable by pandas
    read_csv function. (e.g. 2018-01-01 01:01:01.000000001 -0500) and the second column should be numeric values.

    Args:
        csv_uri (str): uri to csv.
            For local file use:
             - <filepath>
            For S3 use:
             - s3://<bucket_name>/<key_name>
            For Azure use:
             - abfs://<container_name>/<key_name>
        sep (str): csv separator. Default is ','.

    Returns:
        pd.DataFrame: _description_
    """
    return pd.read_csv(csv_uri, sep=sep, parse_dates=['time'], header=0, names=['time', 'value'])
