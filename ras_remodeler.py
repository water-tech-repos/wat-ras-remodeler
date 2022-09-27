#!/usr/local/bin/python
"""CLI tools for reshaping HEC-RAS model data."""
from typing import List, Union
import os
import click
import h5py
from fs_helper import get_file, put_file


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
    # copy data to local temp files and remove group(s)
    src_filepath = get_file(src_hdf_uri)
    temp_filepath = get_file()
    with h5py.File(src_filepath, 'r') as src, h5py.File(temp_filepath, 'w') as temp:
        for attr in src.attrs.keys():
            temp.attrs[attr] = src.attrs.get(attr)
        for group in src.keys():
            if remove_groups and not group in remove_groups:
                src.copy(group, temp)
    # copy result file to URI
    put_file(temp_filepath, dst_hdf_uri)
    # delete temp files
    os.remove(src_filepath)
    os.remove(temp_filepath)


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
@click.option('--type', type=click.Choice(['DSS', 'CSV']), default='DSS')
@click.option('--auto-set-dates', is_flag=True, help="Set 'StartDate' and 'EndDate' in HDF hydrograph attributes based on hydrograph start/end datetimes")
def set_plan_hdf_hydrograph(plan_hdf: str, plan_hdf_hydrograph_name: str, src_hydrograph: str,
                            type: str = 'DSS', auto_set_dates: bool = False) -> None:
    print(plan_hdf)
    print(plan_hdf_hydrograph_name)
    print(src_hydrograph)
    print(format)
    print(auto_set_dates)


if __name__ == '__main__':
    main()
