from sunpy.time import parse_time, TimeRange
from flarelist_utils import *
import pandas as pd 

savedir = "/Users/laurahayes/ml_project_flares/flare_analysis/goes_flare_list/goes_files/"

final_columns = ["date", "start_time", "max_time", "end_time",
		         "goes_class", "goes_class_ind", "integrated_flux", "noaa_ar", "goes_sat"]

test_2012 = read_ngdc_goes_reports("goes-xrs-report_2012.txt")

def download_files():
	"""
	Use the yearly files from 2010-2016 and then the swpc daily
	reports for the remainder 2017-2018.
	"""
	get_ngdc_reports(TimeRange("2010-01-01", "2017-01-01"), savedir=savedir)

	# get some overlapping times to test.
	get_swpc_reports(TimeRange("2015-01-01", "2018-12-31"), savedir=savedir)


tstart = "2010-01-01"
tend = "2018-12-31"

def merge_ngdc():
	files = get_ngdc_reports(TimeRange("2010-01-01", "2018-02-02"), savedir=savedir)
	files.sort()

	df_flares = read_ngdc_goes_reports(files[0])
	for f in files[1:]:
		df = read_ngdc_goes_reports(f)
		df_flares = df_flares.append(df)

	df_flares.reset_index(inplace=True)
	return df_flares[final_columns]


def merge_swpc(tstart, tend):
	files = get_swpc_reports(TimeRange(tstart, tend), savedir=savedir)
	files.sort()
