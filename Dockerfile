FROM python:3.7

RUN mkdir /app
WORKDIR /app

COPY requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

COPY thredds-netcdf-mirror.py /app

ENTRYPOINT ["/app/thredds-netcdf-mirror.py"]
CMD ["-h"]

