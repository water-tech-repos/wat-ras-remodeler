#!/usr/bin/env python3
"""CLI tools for reshaping HEC-RAS model data."""
from typing import Union
import os
import click
from fs_util import get_temp_file, put_file
from dss_util import read_csv_timeseries, read_dss_timeseries
from hdf_util import copy_hdf, update_hydrograph


@click.group()
def main():
    """ras_remodeler -- tools for reshaping HEC-RAS modeler data.

    Supported filesystems are local, S3, and Azure.

    For S3 access, the following environment vairables can be set and picked up for authentication:

     - AWS_ACCESS_KEY_ID

     - AWS_SECRET_ACCESS_KEY

     - AWS_SESSION_TOKEN

    For Azure blob storage the following enviornment variables can be set and picked up for authentication:

     - AZURE_STORAGE_CONNECTION_STRING

     - AZURE_STORAGE_ACCOUNT_NAME

     - AZURE_STORAGE_ACCOUNT_KEY

     - AZURE_STORAGE_SAS_TOKEN

     - AZURE_STORAGE_CLIENT_SECRET

     - AZURE_STORAGE_CLIENT_ID

     - AZURE_STORAGE_TENANT_ID

    Unless otherwise specified, paths to data can be specified on the command line though any of the following:

     - For local file use: `<filepath>`

     - For S3 use: `s3://<bucket_name>/<key_name>`

     - For Azure use: `abfs://<container_name>/<key_name>`

    """


@main.command(short_help="Create a *.p**.tmp.hdf file.", help="""
Create a plan *.tmp.hdf file from a source plan HDF file with the "Results" group removed.

SRC_PLAN_HDF  Exisiting plan HDF file.

DST_DIR       Destination directory to save the new plan *.tmp.hdf file
              (saved as ".p**.tmp.hdf"). If none, file will be created in
              the same directory as the source HDF file.
""")
@click.argument('src_plan_hdf')
@click.argument('dst_dir', default=None, required=False)
def create_plan_tmp_hdf(src_plan_hdf: str, dst_dir: Union[str, None]) -> None:
    """Create a .tmp.hdf plan file from a source plan hdf file with the Results group removed.

    Args:
        src_plan_hdf (str): Source plan HDF URI (should have name *.p**.hdf).
        dst_dir (Union[str, None]): Directory to save resulting plan temp HDF file with Results group removed.
        (saved as *.p**.tmp.hdf). If None, file will be created in the same directory as source HDF file.
    """
    if dst_dir:
        dst_plan_hdf = os.path.join(dst_dir, os.path.splitext(
            os.path.basename(src_plan_hdf))[0])
    else:
        dst_plan_hdf = os.path.splitext(src_plan_hdf)[0] + ".tmp.hdf"
    copy_hdf(src_plan_hdf, dst_plan_hdf, ["Results"])


@main.command(short_help="Overwrite a hydrograph in an HDF file.", help="""
Overwrite a hydrograph in a HEC-RAS plan HDF file.

PLAN_HDF                    Existing plan HDF file.

PLAN_HDF_HYDROGRAPH_NAME    Name of the hydrograph in the HDF file that will be overwritten.

SRC_HYDROGRAPH              Hydrograph file used to overwrite the data.
""")
@click.argument('plan_hdf')
@click.argument('plan_hdf_hydrograph_name')
@click.argument('src_hydrograph')
@click.option('--input_type', type=click.Choice(['DSS', 'CSV']), default='DSS', help="Hydrograph file type. Defaults to 'DSS'. DSS file should be in <URI>:<pathname> format.")
@click.option('--keep_dates', is_flag=True, help="Do not modify 'Start Date' and 'End Date' in HDF hydrograph attributes based on hydrograph start/end datetimes")
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
    temp_hdf_filepath = get_temp_file(plan_hdf)
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
