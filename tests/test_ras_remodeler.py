"""Integration tests for ras remodeler"""
import os
from click.testing import CliRunner
import h5py
from ras_remodeler import create_plan_tmp_hdf, set_plan_hdf_hydrograph
from fs_util import get_temp_file
from hdf_util import copy_hdf


def teardown_module():
    """Cleanup created test files."""
    if os.path.exists("tests/data/Muncie.p04.tmp.hdf"):
        os.remove("tests/data/Muncie.p04.tmp.hdf")


def test_create_plan_tmp_hdf():
    """Test create tmp HDF file with Results group removed"""
    src_file = "tests/data/Muncie.p04.hdf"
    runner = CliRunner()
    runner.invoke(create_plan_tmp_hdf, [src_file])
    assert os.path.exists("tests/data/Muncie.p04.tmp.hdf")
    with h5py.File("tests/data/Muncie.p04.tmp.hdf", 'r') as file:
        assert "Results" not in file.keys()


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
