#!/usr/bin/env python3
import click

import argparse
from ast import arg
import sys
from typing import List


@click.group()
def main():
    pass


@main.command()
@click.argument('src_plan_hdf')
@click.argument('dst_plan_tmp_hdf')
def create_plan_tmp_hdf(src_plan_hdf: str, dst_plan_tmp_hdf: str):
    print(src_plan_hdf)
    print(dst_plan_tmp_hdf)


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