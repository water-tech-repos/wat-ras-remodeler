#!/usr/bin/env python3
"""CLI tools for reshaping HEC-RAS model data."""
from typing import Union
import os
import click
from fs_util import get_file, put_file
from dss_util import read_csv_timeseries, read_dss_timeseries
from hdf_util import copy_hdf, update_hydrograph


@click.group()
def main():
    """ras_remodeler -- tools for reshaping HEC-RAS modeler data."""


@main.command()
@click.argument('src_plan_hdf')
@click.argument('dst_dir', default=None, required=False)
def create_plan_tmp_hdf(src_plan_hdf: str, dst_dir: Union[str, None]) -> None:
    """Create a .tmp.hdf plan file from a source plan hdf file with the Results group removed.

    Args:
        src_plan_hdf (str): Source plan HDF URI (should have name *.p**.hdf).
        dst_dir (Union[str, None]): Directory to save resulting plan temp HDF file with Results group removed.
        (saved as *.p**.tmp.hdf). If None, file will be created in the same directory as source HDF file.
    """
    dst_plan_hdf = os.path.join(dst_dir, os.path.splitext(os.path.basename(src_plan_hdf))[
                                0] + ".tmp.hdf") if dst_dir else os.path.splitext(src_plan_hdf)[0] + ".tmp.hdf"
    copy_hdf(src_plan_hdf, dst_plan_hdf, ["Results"])


@main.command()
@click.argument('plan_hdf')
@click.argument('plan_hdf_hydrograph_name')
@click.argument('src_hydrograph')
@click.option('--input_type', type=click.Choice(['DSS', 'CSV']), default='DSS')
@click.option('--keep_dates', is_flag=True, help="Do not modify 'StartDate' and 'EndDate' in HDF hydrograph attributes based on hydrograph start/end datetimes")
def set_plan_hdf_hydrograph(plan_hdf: str, plan_hdf_hydrograph_name: str, src_hydrograph: str,
                            input_type: str = 'DSS', keep_dates: bool = False) -> None:
    """Overwrite a hydrograph in a HEC-RAS plan HDF file.

    Args:
        plan_hdf (str): URI of existing HEC-RAS HDF plan file
        plan_hdf_hydrograph_name (str): name of the hydrograph in the HDF file to overwrite
        (e.g. 'River: White  Reach: Muncie  RS: 15696.24').
        src_hydrograph (str): URI of hydrograph to overwrite the data
        input_type (str, optional): one of ['DSS', 'CSV']. Defaults to 'DSS'. DSS file should be in <URI>:<pathname>
        format.
        keep_dates (bool, optional): Defaults to False.

    Raises:
        ValueError
    """
    temp_hdf_filepath = get_file(plan_hdf)
    if input_type == 'DSS':
        timeseries = read_dss_timeseries(src_hydrograph)
    elif input_type == 'CSV':
        timeseries = read_csv_timeseries(src_hydrograph)
    else:
        raise ValueError(
            "Invalid input_type option. Must be one of ['DSS', 'CSV']")
    update_hydrograph(temp_hdf_filepath, plan_hdf_hydrograph_name,
                      timeseries, keep_dates=keep_dates)
    # overwrite existing file with new data
    os.remove(plan_hdf)
    put_file(temp_hdf_filepath, plan_hdf)


if __name__ == '__main__':
    main()
