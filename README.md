# wat-ras-remodeler
Tools for reshaping HEC-RAS model data.

## Developer Setup
1. Install VS Code and Docker Desktop
1. Install the Remote Development extension pack in VSCode
1. In VS Code, Press ctrl + shift + P and select *Remote-Containers: Rebuild and Reopen Container*

As the container is built, project dependencies will be installed. Once it completes you will be able to develop from inside of the container.

### Tests
Build the dev container using VS Code, then navigate to the testing page in VS Code and click run tests. You may need to run discover tests first.

## Usage
### `create-plan-tmp-hdf`
Create a new HDF file from an existing HDF file with the "Results" group removed

```
./ras_remodeler.py create-plan-tmp-hdf "<src_plan_hdf>" "<dst_dir: optional>"
```

The `dst_dir` argument is optional. If not supplied, the `dst_dir` is set to the same folder containing the `src_plan_hdf`. The name of the resulting file is identical to the `src_hdf_file` but the extension is replaced with `.tmp.hdf`.

### `set-plan-hdf-hydrograph`
Overwrite a hydrograph in a HEC-RAS generated plan HDF file.

```
./ras_remodeler.py set-plan-hdf-hydrograph "<plan_hdf>" "<plan_hdf_hydrograph_name>" "<src_hydrograph>" --input_type DSS --keep_dates
```

`plan_hdf` is the path to the existing HDF file to update.

`plan_hdf_hydrograph_name` is the name of the existing hydrograph to update (e.g. "River: White  Reach: Muncie  RS: 15696.24")

`src_hydrograph` should be one of the following:

1. If input_type is `DSS` (the default):
 - For local file use: `<filepath>:<pathname>`
 - For S3 use: `s3://<bucket_name>/<key_name>:<pathname>`
 - For Azure use: `abfs://<container_name>/<key_name>:<pathname>`

2. If input_type is `CSV`:
 - For local file use: `<filepath>`
 - For S3 use: `s3://<bucket_name>/<key_name>`
 - For Azure use: `abfs://<container_name>/<key_name>`

`--input_type` should be either `DSS` or `CSV` and defaults to `DSS`

`--keep_dates` flag should be supplied if you do not want to modify the Start Date and End Date attributed in the HDF file for the hydrograph. The default is to update these attributes to match to new hydrograph.

### Supported Filesystems
Local, S3, and Azure filesystems are supported through `fsspec`.

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

