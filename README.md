# thredds-netcdf-mirror
Mirror the netcdf files from a tds/thredds catalog to local disk. Runs locally or in docker.

# Running locally

This is a python3 application

## Installation

The dependencies are listed in requirements.txt file and can normally be installed using pip


```pip install -r requirements.txt```

## Running

Files will be downloaded from the thredds server into the output folder, which must exist already. NB: any netcdf .nc files which are in the folder but not listed in the catalog will be deleted.

In this example, the files are saved into the /my/output/folder directory with a http politeness delay of 1 second between http requests.

```python3 thredds-netcdf-mirror.py --thredds http://thredds.marine.ie/thredds --catalog IMI_ROMS_HYDRO/CONNEMARA_250M_20L_1H/FORECAST --output /my/output/folder --delay 1```

# Using docker

When running in docker the typical usage is to map a volume for the output data.


## Build

```docker build -t thredds-netcdf-mirror . ```

## Run

Here we run the application in docker, saving the files into a volume mapped to /my/output/folder directory with politeness of only 1 second delay between http requests.

```docker run --rm -i -t -v /my/output/folder:/output thredds-netcdf-mirror --thredds http://thredds.marine.ie/thredds --catalog IMI_ROMS_HYDRO/CONNEMARA_250M_20L_1H/FORECAST --output /output --delay 1```

# Using with docker swarm

```docker build -t 127.0.0.1:5000/thredds-netcdf-mirror . ```

## Push

```docker push 127.0.0.1:5000/thredds-netcdf-mirror```

## Run

```docker run --rm -i -t -v /opt/thredds/connemara_his:/output 127.0.0.1:5000/thredds-netcdf-mirror --thredds http://thredds.marine.ie/thredds --catalog IMI_ROMS_HYDRO/CONNEMARA_250M_20L_1H/FORECAST --output /output --delay 1```

# TODO:

 * build a smaller docker image by starting from  python:3.7-apline (tried and failed)
 * schedule in swarm using https://github.com/mcuadros/ofelia

