"""Tests for reading and writing hdf5 files"""
import os
from datetime import datetime
import h5py
import numpy as np
from hdf_util import copy_hdf, create_hydrograph_times, format_date_string_hydrograph_attrib, copy_attrib, update_hydrograph
from dss_util import read_dss_timeseries
from fs_util import get_temp_file


def test_copy_hdf():
    """Test copying HDF file and removing groups"""
    src_file = "tests/data/Muncie.p04.hdf"
    temp_file1 = get_temp_file(ext=".hdf")
    temp_file2 = get_temp_file(ext=".hdf")
    copy_hdf(src_file, temp_file1, ["Results"])
    copy_hdf(src_file, temp_file2)
    with h5py.File(temp_file1, 'r') as file:
        n_rows = 0
        for group1, group2 in zip(file.keys(), ["Event Conditions", "Geometry", "Plan Data"]):
            assert group1 == group2
            n_rows += 1
        assert n_rows == 3
    with h5py.File(temp_file2, 'r') as file:
        n_rows = 0
        for group1, group2 in zip(file.keys(), ["Event Conditions", "Geometry", "Plan Data", "Results"]):
            assert group1 == group2
            n_rows += 1
        assert n_rows == 4
    os.remove(temp_file1)
    os.remove(temp_file2)


def test_create_hydrograph_times():
    """Test creating hydrograph times for HDF file"""
    times = create_hydrograph_times(read_dss_timeseries(
        "tests/data/hydrograph.dss:/REGULAR/TIMESERIES/FLOW//1HOUR/Ex1/")['time'], 'Days')
    assert times.shape == (7,)
    assert times.dtype == np.float32


def test_format_date_string():
    """Test date formating for HEC-RAS HDF"""
    date_str = format_date_string_hydrograph_attrib(datetime(2019, 4, 13))
    assert date_str == "13Apr2019 0000"


def test_copy_attrib():
    """Test copy attributes in hdf files"""
    src_file = "tests/data/Muncie.p04.hdf"
    temp_file = get_temp_file(ext=".hdf")
    copy_hdf(src_file, temp_file, ["Results"])
    with h5py.File(src_file, 'r') as src, h5py.File(temp_file, 'r+') as temp:
        dataset1 = src["/Event Conditions/Unsteady/Boundary Conditions/Flow Hydrographs/River: White  Reach: Muncie  RS: 15696.24"]
        dataset2 = temp["/Event Conditions/Unsteady/Boundary Conditions/Flow Hydrographs/River: White  Reach: Muncie  RS: 15696.24"]
        copy_attrib(dataset1, dataset2, "Interval", "Mins")
        assert dataset2.attrs["Interval"].decode() == "Mins"
    os.remove(temp_file)


def test_update_hydrograph():
    """Test hydrograph update hdf file"""
    src_file = "tests/data/Muncie.p04.hdf"
    temp_file = get_temp_file(ext=".hdf")
    copy_hdf(src_file, temp_file, ["Results"])
    timeseries = read_dss_timeseries(
        "tests/data/hydrograph.dss:/REGULAR/TIMESERIES/FLOW//1HOUR/Ex1/")
    update_hydrograph(
        temp_file, "River: White  Reach: Muncie  RS: 15696.24", timeseries)
    with h5py.File(temp_file, 'r') as temp:
        dataset = temp["/Event Conditions/Unsteady/Boundary Conditions/Flow Hydrographs/River: White  Reach: Muncie  RS: 15696.24"]
        assert dataset.shape == (7, 2)
    os.remove(temp_file)
