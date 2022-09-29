"""Integration tests for ras remodeler"""
from os.path import exists
from click.testing import CliRunner
from ras_remodeler import create_plan_tmp_hdf, set_plan_hdf_hydrograph
import h5py
import os
from fs_util import get_temp_file
from hdf_util import copy_hdf


def test_create_plan_tmp_hdf():
    """Test create tmp HDF file with Results group removed"""
    src_file = "tests/data/Muncie.p04.hdf"
    runner = CliRunner()
    runner.invoke(create_plan_tmp_hdf, [src_file])
    assert exists("tests/data/Muncie.p04.tmp.hdf")


def test_set_plan_hdf_hydrograph():
    """Test update hydrograph of HDF file"""
    src_file = "tests/data/Muncie.p04.hdf"
    temp_file = get_temp_file(ext=".hdf")
    copy_hdf(src_file, temp_file, ["Results"])
    hydrograph_name = "River: White  Reach: Muncie  RS: 15696.24"
    hydrograph = "tests/data/hydrograph.dss:/REGULAR/TIMESERIES/FLOW//1HOUR/Ex1/"
    runner = CliRunner()
    runner.invoke(set_plan_hdf_hydrograph, [
                  temp_file, hydrograph_name, hydrograph])
    with h5py.File(temp_file) as file:
        dataset = file["/Event Conditions/Unsteady/Boundary Conditions/Flow Hydrographs/River: White  Reach: Muncie  RS: 15696.24"]
        assert dataset.shape == (7, 2)
    os.remove(temp_file)
