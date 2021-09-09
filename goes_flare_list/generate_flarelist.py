import urllib
import pandas as pd 
from sunpy.time import TimeRange
from sunpy.util import scraper
import glob
import tarfile
from flarelist_utils import read_swpc_reports, read_ngdc_goes_reports, get_yearly_swpc_event_reports
from dateutil.relativedelta import relativedelta
import pandas as pd 
import datetime
import os

tstart = "1996-07-31"
tend = "2018-12-31"
# get_yearly_swpc_event_reports(tstart, tend)


def get_swpc_flarelist(tstart, tend, csv_filename=None):
	"""
	Function to read in all SWPC daily reports and save flarelist
	as a csv for flares >=C1.0.

	The flarelist is saved to "swpc_event_list.csv"

	"""
	filedir = "./goes_files/%Y_events/%Y%m%devents.txt"
	timerange = TimeRange(tstart, tend)
	t0 = timerange.start.datetime
	files = [t0.strftime(filedir)]
	while timerange.end.datetime>t0:
		t0 = t0 + relativedelta(days=1)
		files.append(t0.strftime(filedir))

	files.sort()
	for f in files:
		if not os.path.exists(f):
			print("No data found {:s}".format(f))
			files.remove(f)


	df_flares = read_swpc_reports(files[0])
	for f in files[1:]:
		print(f)
		df = read_swpc_reports(f)
		df_flares = df_flares.append(df)
	df_flares.reset_index(inplace=True, drop=True)
	df_flares["ts"] = df_flares.date + df_flares.start_time
	df_flares = df_flares.drop_duplicates(subset="ts")

	df_flares_c = df_flares[df_flares["goes_class_ind"].isin(["C", "X", "M"])]
	df_flares_c.reset_index(inplace=True, drop=True)
	if csv_filename is None:
		csv_filename = "swpc_flarelist_{:s}_{:s}.csv".format(timerange.start.strftime("%Y%m%d"), timerange.end.strftime("%Y%m%d"))


	df_flares_c["start_time"] = pd.to_datetime(df_flares_c["date"] + df_flares_c["start_time"], format="%Y%m%d%H%M")
	df_flares_c["end_time"] = pd.to_datetime(df_flares_c["date"] + df_flares_c["end_time"], format="%Y%m%d%H%M")


	df_flares_c.to_csv(csv_filename, index_label=False)

get_swpc_flarelist(tstart, tend)