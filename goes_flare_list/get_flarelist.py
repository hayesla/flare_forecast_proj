from sunpy.time import parse_time, TimeRange
from flarelist_utils import *
import pandas as pd 

# directory where .txt files are saved to
savedir = "/Users/laurahayes/ml_project_flares/flare_analysis/goes_flare_list/goes_files/"

# final columns of interest to merge lists on
final_columns = ["date", "start_time", "max_time", "end_time",
		         "goes_class", "goes_class_ind", "integrated_flux", "noaa_ar", "goes_sat"]

# start and end time of requested GOES flare list
tstart = "2010-01-01"
tend = "2018-12-31"

def download_files(savedir):
	"""
	Use the yearly files from 2010-2016 and then the swpc daily
	reports for the remainder 2017-2018.
	"""
	get_ngdc_reports(TimeRange("2010-01-01", "2017-01-01"), savedir=savedir)

	# get some overlapping times to test.
	get_swpc_reports(TimeRange("2015-01-01", "2018-12-31"), savedir=savedir)


def merge_ngdc(tstart, tend):
	"""
	Read and merge the NGDC yearly files into a single pandas DataFrame

	Parameters
	----------
	tstart : `str` 
		start time (yearly date)
	tend : `str`
		end time (yearly date)
	
	Returns
	-------
	df_flares : pd.DataFrame merged between tstart and tend with `final_columns` columns.

	"""
	files = get_ngdc_reports(TimeRange(tstart, tend), savedir=savedir)
	files.sort()

	df_flares = read_ngdc_goes_reports(files[0])
	for f in files[1:]:
		df = read_ngdc_goes_reports(f)
		df_flares = df_flares.append(df)

	df_flares.reset_index(inplace=True)
	df_flares["noaa_ar"] = df_flares["noaa_ar"].replace(["\n",""],  "     ")
	return df_flares[final_columns]


def merge_swpc(tstart, tend):
	"""
	Read and merge the daily SWPC report files into a single pandas DataFrame

	Parameters
	----------
	tstart : `str` 
		start time 
	tend : `str`
		end time 
	
	Returns
	-------
	df_flares : pd.DataFrame merged between `tstart` and `tend` with `final_columns` columns.
	"""
	files = get_swpc_reports(TimeRange(tstart, tend), savedir=savedir)
	files.sort()

	df_flares = read_swpc_reports(files[0])
	for f in files[1:]:
		df = read_swpc_reports(f)
		df_flares = df_flares.append(df)
	df_flares.reset_index(inplace=True)
	return df_flares[final_columns]


df_ngdc = merge_ngdc("2010-01-01", "2016-12-31")
df_swpc = merge_swpc("2017-01-01", "2018-12-31")

flare_list = df_ngdc.append(df_swpc)
flare_list.reset_index(inplace=True)

flare_list_c = flare_list[flare_list["goes_class_ind"].isin(["X", "M", "C"])]
flare_list_c.reset_index(inplace=True)


flare_list_c["tstart_datetime"] = pd.to_datetime(flare_list_c.date+flare_list_c.start_time, format="%Y%m%d%H%M")
flare_list_c["max_time"] = flare_list_c["max_time"].replace("////", "0000")
flare_list_c["tpeak_datetime"] = pd.to_datetime(flare_list_c.date+flare_list_c.max_time, format="%Y%m%d%H%M")
flare_list_c["tend_datetime"] = pd.to_datetime(flare_list_c.date+flare_list_c.end_time, format="%Y%m%d%H%M")



