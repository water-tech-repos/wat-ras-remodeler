"""Integration tests for ras remodeler"""
import os
from click.testing import CliRunner
import h5py
from ras_remodeler import create_plan_tmp_hdf, set_plan_hdf_hydrograph


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
    """Test update hydrograph of HDF file. MUST RUN AFTER test_create_plan_tmp_hdf!"""
    hydrograph_name = "River: White  Reach: Muncie  RS: 15696.24"
    # dss hydrograph that doesn't have realistic flows
    #hydrograph = "tests/data/hydrograph.dss:/REGULAR/TIMESERIES/FLOW//1HOUR/Ex1/"
    # csv with realistic flows
    hydrograph = "tests/data/hydrograph2.csv"
    hdf_filepath = "tests/data/Muncie.p04.tmp.hdf"
    runner = CliRunner()
    runner.invoke(set_plan_hdf_hydrograph, [
                  hdf_filepath, hydrograph_name, hydrograph, "--keep_dates", "--input_type", "CSV"])
    with h5py.File(hdf_filepath) as file:
        dataset = file["/Event Conditions/Unsteady/Boundary Conditions/Flow Hydrographs/River: White  Reach: Muncie  RS: 15696.24"]
        assert dataset[16][1] == 22000
        #assert dataset.shape == (7, 2) # for DSS test
    # check that HEC-RAS runs
    assert os.system(
        "export LD_LIBRARY_PATH=./bin/libs:./bin/libs/mkl && ./bin/RAS610/RasUnsteady ./tests/data/Muncie.c04 b04") == 0
    # check that results were created
    with h5py.File(hdf_filepath, 'r') as file:
        assert "Results" in file.keys()
