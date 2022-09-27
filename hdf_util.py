"""Utility functions for HDF5 files"""
from typing import List, Union, Any
import os
from datetime import timedelta, datetime
import h5py
import pandas as pd
import numpy as np
from fs_util import get_file, put_file


def copy_hdf(src_hdf_uri: str, dst_hdf_uri: str, remove_groups: Union[List[str], None] = None) -> None:
    """Copy an HDF file and optionally remove some groups.

    Args:
        src_hdf_uri (str): URI of the source HDF file.
        dst_hdf_uri (str): URI to save the resulting HDF file.
        remove_groups (List[str] | None, optional): list of group names to
        remove. Defaults to None.
    """
    # copy data to local temp files and remove group(s)
    src_filepath = get_file(src_hdf_uri)
    temp_filepath = get_file(ext=".hdf")
    with h5py.File(src_filepath, 'r') as src, h5py.File(temp_filepath, 'w') as temp:
        for attr in src.attrs.keys():
            temp.attrs[attr] = src.attrs.get(attr)
        for group in src.keys():
            if remove_groups and not group in remove_groups:
                src.copy(group, temp)
            elif remove_groups is None:
                src.copy(group, temp)
    # copy result file to URI
    put_file(temp_filepath, dst_hdf_uri)
    # delete temp files
    os.remove(src_filepath)
    os.remove(temp_filepath)


def create_hydrograph_times(datetime_column: pd.DataFrame, units: str) -> 'np.ndarray[np.float32]':
    """create an array of times starting at zero in the given units from a datetime column of a pandas dataframe

    Args:
        datetime_column (pd.DataFrame): datetime column of pandas dataframe
        units (str): Interval of time series. Must be one of ['Days']

    Returns:
        np.ndarray[np.float32]: array of times in specified units offset to start at 0.
    """
    if units == 'Days':
        result = np.ndarray(dtype=np.float32, shape=(
            len(datetime_column.index)))
        time = 0.0
        result[0] = time
        # get time as fractions of a day using 32 bit floats
        for i in range(1, len(datetime_column.index)):
            time += (datetime_column[i] -
                     datetime_column[i-1]) / timedelta(days=1)
            result[i] = time
    else:
        raise ValueError(
            f"Timeseries has unknown interval units. Must be 'Days' but found {units}")
    return result


def format_date_string_hydrograph_attrib(raw_datetime: datetime) -> str:
    """Format date string to be consistent with HEC-RAS HDF hydrograph attribute format

    Args:
        raw_datetime (datetime): the datetime to format

    Returns:
        str: DDMMMYYYY HHMM format
    """
    return raw_datetime.strftime("%d%b%Y %H%M")


def copy_attrib(src_dataset: h5py.Dataset, dst_dataset: h5py.Dataset, attrib: str, value: Any = None):
    """Copy an attribute from one HDF5 dataset to another and optionally update the value

    Args:
        src_dataset (h5py.Dataset): src_dataset
        dst_dataset (h5py.Dataset): dst_dataset
        attrib (str): attribute name
        value (Any, optional): new value. Defaults to None. If None, the existing value is used
    """
    data = value if value is not None else src_dataset.attrs[attrib]
    dst_dataset.attrs.create(
        attrib,
        data,
        src_dataset.attrs[attrib].shape,
        src_dataset.attrs[attrib].dtype)


def update_hydrograph(hdf_filepath: str,
                      hydrograph_name: str,
                      timeseries: pd.DataFrame,
                      keep_dates: bool = False) -> None:
    """Update the hydrograph data from a pandas dataframe containing timeseries data

    Args:
        hdf_filepath (str): local filepath to HDF file to update
        hydrograph_name (str): name of the hydrograph to update. This dataset should be in the
        '/Event Conditions/Unsteady/Boundary Conditions/Flow Hydrographs/' group of the HDF file.
        keep_dates (bool): If true, do not modify 'StartDate' and 'EndDate' in HDF hydrograph attributes based on
        hydrograph start/end datetimes
    """
    hydrograph_dataset_path = "/Event Conditions/Unsteady/Boundary Conditions/Flow Hydrographs/" + hydrograph_name
    temp_hydrograph_dataset_path = "/Event Conditions/Unsteady/Boundary Conditions/Flow Hydrographs/temp"
    with h5py.File(hdf_filepath, 'r+') as file:
        # maxsize of dataset is set on creation so we can't just update the data in place.
        # create a new dataset since the existing may have been created with a max size that is too small.
        num_rows = len(timeseries.index)
        ex_dataset = file[hydrograph_dataset_path]
        units = ex_dataset.attrs['Interval'].decode()
        data = np.column_stack((
            create_hydrograph_times(timeseries['time'], units),
            timeseries['value'].to_numpy(dtype=np.float32)
        ))
        new_dataset = file.create_dataset(name=temp_hydrograph_dataset_path, shape=(
            num_rows, 2), dtype='f', data=data, maxshape=(num_rows, 2), compression='gzip', compression_opts=1)
        # copy attributes
        copy_attrib(ex_dataset, new_dataset, "Coordinates")
        copy_attrib(ex_dataset, new_dataset, "Data Type")
        copy_attrib(ex_dataset, new_dataset, "Interval")
        copy_attrib(ex_dataset, new_dataset, "Node Index")
        copy_attrib(ex_dataset, new_dataset, "RS")
        copy_attrib(ex_dataset, new_dataset, "Reach")
        copy_attrib(ex_dataset, new_dataset, "River")
        if not keep_dates:
            copy_attrib(ex_dataset, new_dataset, 'Start Date', format_date_string_hydrograph_attrib(
                min(timeseries['time'])))
            copy_attrib(ex_dataset, new_dataset, 'End Date', format_date_string_hydrograph_attrib(
                max(timeseries['time'])))
        else:
            copy_attrib(ex_dataset, new_dataset, "Start Date")
            copy_attrib(ex_dataset, new_dataset, "End Date")
        # delete existing dataset and move new dataset
        del file[hydrograph_dataset_path]
        file.move(temp_hydrograph_dataset_path, hydrograph_dataset_path)
