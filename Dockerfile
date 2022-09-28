FROM python:3.8-slim

# install pydsstools non-python dependencies
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends gfortran

RUN mkdir /opt/ras_remodeler
WORKDIR /opt/ras_remodeler

COPY ras_remodeler.py dss_util.py fs_util.py hdf_util.py requirements.txt ./
# linux version of pydsstools, may require Ubuntu 20.04 LTS and Python 3.8
COPY bin/pydsstools-2.1-cp38-cp38-linux_x86_64.whl ./bin/
RUN pip install -r requirements.txt

ENTRYPOINT ["./ras_remodeler.py"]