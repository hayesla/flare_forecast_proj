import pandas as pd
import numpy as np 
from sunpy.util import scraper
from sunpy.time import TimeRange 
# from sunpy.io.special import srs
import  read_srs as srs
from dateutil.relativedelta import relativedelta
from astropy.table import Column, vstack

def get_srs_files():
	trange = TimeRange("2010-01-01", "2018-12-31")
	file_pattern_swpc = ("ftp://ftp.swpc.noaa.gov/pub/warehouse/%Y/%Y_SRS.tar.gz")
	file_scraper_swpc = scraper.Scraper(file_pattern_swpc)

	urls = file_scraper_swpc.filelist(trange)
	for u in urls:
		urllib.request.urlretrieve(u, '/Users/laurahayes/ml_project_flares/flare_analysis/AR_analysis/srs_data/'+u.split("/")[-1])



filedir = "/Users/laurahayes/ml_project_flares/flare_analysis/AR_analysis/srs_data/%Y_SRS/%Y%m%dSRS.txt"
timerange = TimeRange("2010-01-01", "2018-12-31")
t0 = timerange.start.datetime
files = [t0.strftime(filedir)]
while timerange.end.datetime>t0:
	t0 = t0 + relativedelta(days=1)
	files.append(t0.strftime(filedir))

files.sort()


def make_srs_df(file):

	file_table = srs.read_srs(file)
	date_obs = file_table.meta["issued"]
	date_column = Column(name="date", data=[date_obs.strftime("%Y-%m-%d %H:%M")]*len(file_table))
	file_table.add_column(date_column)

	return file_table

# errors = []
# for i in range(len(files)):
# 	try:
# 		_ = make_srs_df(files[i])
# 	except:
# 		errors.append(files[i])

errors= []
data0 = make_srs_df(files[0])
for i in range(1, len(files)):

	try:
		data1 = make_srs_df(files[i])
		if len(data1)>0:
			data0 = vstack([data0, data1])
	except:
		print(i)
		errors.append(i)

