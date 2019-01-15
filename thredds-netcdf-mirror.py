#!/usr/bin/env python3
import argparse
import datetime
import io
import lxml
import os
import pandas as pd
import re
import requests
import time


def read_catalog(thredds, catalog):
  nc_pattern = re.compile("^.*\.nc$")
  result = {}
  catalog_url = '{0}/catalog/{1}/catalog.html'.format(thredds,catalog)
  http_nc_folder = '{0}/fileServer/{1}'.format(thredds,catalog)
  dfs = pd.read_html(catalog_url)
  for i, row in dfs[0].iterrows():
    fname = row[0]
    if not nc_pattern.match(fname):
        continue
    modtime = datetime.datetime.strptime(row[2], '%Y-%m-%dT%H:%M:%SZ')
    nc_url = '{0}/{1}'.format(http_nc_folder,fname)
    result[fname] = {
            'fname': fname,
            'url': nc_url,
            'modtime': modtime
            }
  return result


def rm(filename):
    try:
        os.remove(filename)
    except FileNotFoundError: 
        pass
       
def download(item, folder):
    filename = '{0}/{1}'.format(folder,item['fname'])
    tmp_filename = '{0}.{1}'.format(filename,item['modtime'].timestamp())
    timeout = 10
    url = item['url']
    try:
        # NOTE the stream=True parameter
        print('GET: {0}'.format(url))
        r = requests.get(url, timeout=timeout, stream=True)
        with open(tmp_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024 * 1024):
                if chunk: # filter out keep-alive new chunks
                    f.write(chunk)
        timestamp = item['modtime'].timestamp()
        os.utime(tmp_filename, (timestamp, timestamp))
        os.rename(tmp_filename,filename)
        return filename
    finally:
        rm(tmp_filename)

#
# Mirror the dataset nc files to the folder.
# Return a list of nc files no longer in the catalog
#
def mirror(thredds, catalog_path, folder, delay):
    old = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder,f)) and f.endswith('.nc')]
    mark = {}
    for f in old:
        mark[f] = datetime.datetime.utcfromtimestamp(os.path.getmtime(os.path.join(folder,f)))

    catalog = read_catalog(thredds, catalog_path)
    fetched = False
    for nc, o in sorted(catalog.items()):
        if nc in old: old.remove(nc)
        if not (nc in mark and mark[nc] == o['modtime']):
            time.sleep(delay)
            download(o, folder)
            fetched = True

        print('OK: {0}'.format(nc))

    if not fetched:
        print ('Nothing fetched. Will not remove any old files.');
        return []

    old.sort()
    return old

start_time = time.time()

parser = argparse.ArgumentParser(description='Mirror the dataset netcdf files from a thredds catalog')
parser.add_argument('--thredds', required=True, help='url of the thredds web application, eg http://thredds.marine.ie/thredds')
parser.add_argument('--catalog', required=True, help='the dataset catalog, eg IMI_ROMS_HYDRO/CONNEMARA_250M_20L_1H/FORECAST ')
parser.add_argument('--output', required=True, help='the target folder into which files are mirrored')
parser.add_argument('--delay', help='delay in seconds between http requests', default=5, type=int)
args = parser.parse_args()

old = mirror(args.thredds, args.catalog, args.output, args.delay)
for f in old:
    print('DELETE: {0}'.format(f))
    rm(os.path.join(args.output,f))

print('DONE: %.2f seconds' % (time.time() - start_time))
