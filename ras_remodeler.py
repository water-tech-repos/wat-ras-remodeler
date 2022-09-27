#!/usr/local/bin/python
"""CLI tools for reshaping HEC-RAS model data."""
from typing import List, Union
import os
import tempfile
import click
import h5py
from fs_helper import get_file, get_bytes, put_bytes


@click.group()
def main():
    """CLI Entrypoint"""


def copy_hdf(src_hdf_uri: str, dst_hdf_uri: str, remove_groups: Union[List[str], None] = None) -> None:
    """Copy an HDF file and optionally remove some groups.

    Args:
        src_hdf_uri (str): URI of the source HDF file.
        dst_hdf_uri (str): URI to save the resulting HDF file.
        remove_groups (List[str] | None, optional): list of group names to
        remove. Defaults to None.
    """
    src_file = get_file(src_hdf_uri)
    # tried this with an in memory temp file but HDF library does not seem to work when copying the temp file back onto
    # disk. A file is created, but is corrupted. Possibly a bug.
    dst_file = os.path.join(tempfile.gettempdir(), "temp.hdf")
    src = h5py.File(src_file, 'r')
    dst = h5py.File(dst_file, 'w')
    for attr in src.attrs.keys():
        dst.attrs[attr] = src.attrs.get(attr)
    for group in src.keys():
        if remove_groups and not group in remove_groups:
            src.copy(group, dst)
    # close hdf file handles
    src.close()
    dst.close()
    # close source file
    src_file.close()
    # copy temp file to URI
    put_bytes(get_bytes(dst_file), dst_hdf_uri)


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
@click.option('--format', type=click.Choice(['DSS', 'CSV']), default='DSS')
@click.option('--auto-set-dates', is_flag=True, help="Set 'StartDate' and 'EndDate' in HDF hydrograph attributes based on hydrograph start/end datetimes")
def set_plan_hdf_hydrograph(plan_hdf: str, plan_hdf_hydrograph_name: str, src_hydrograph: str,
                            format: str = 'DSS', auto_set_dates: bool = False):
    print(plan_hdf)
    print(plan_hdf_hydrograph_name)
    print(src_hydrograph)
    print(format)
    print(auto_set_dates)


if __name__ == '__main__':
    main()
