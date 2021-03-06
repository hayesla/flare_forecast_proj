import pandas as pd 
from sunpy.time import TimeRange
import glob
from dateutil.relativedelta import relativedelta
import pandas as pd 
import datetime
from flarelist_utils import read_swpc_reports, read_ngdc_goes_reports
import numpy as np 

filedir = "./goes_files/%Y_events/%Y%m%devents.txt"
timerange = TimeRange("2010-01-01", "2018-12-31")

def test_files_missing():
	"""
	Print missing files - if any missing check solarmoniter.
	"""
	filedir = "./goes_files/%Y_events/%Y%m%devents.txt"
	t0 = timerange.start.datetime
	days = [t0]
	while timerange.end.datetime > t0:
		t0 = t0 + relativedelta(days=1)
		days.append(t0)

	missing_files = []
	for d in days:
		if not os.path.exists(d.strftime(filedir)):
			missing_files.append(d.strftime(filedir))
	print(missing_files)


## Testing differences
def get_yearly_swpc(year):
	filedir = "./goes_files/%Y_events/*.txt"
	all_files = []
	all_files += glob.glob(year.strftime(filedir))
	all_files.sort()
	df_flares = read_swpc_reports(all_files[0])
	for f in all_files[1:]:
		df = read_swpc_reports(f)
		df_flares = df_flares.append(df)
	df_flares.reset_index(inplace=True, drop=True)
	df_flares["ts"] = df_flares.date + df_flares.start_time
	df_flares.drop_duplicates(subset="ts")
	return df_flares[df_flares["goes_class_ind"].isin(["C", "X", "M"])]


def get_yearly_ngdc(year):
	file = "./goes_files/goes-xrs-report_%Y.txt"
	df = read_ngdc_goes_reports(year.strftime(file))
	df["ts"] = df.date + df.start_time
	df.drop_duplicates(subset="ts")
	return df[df["goes_class_ind"].isin(["X", "M", "C"])]


def print_flares(df):
	x = np.sum(df["goes_class_ind"].isin(["X"]))
	m = np.sum(df["goes_class_ind"].isin(["M"]))
	c = np.sum(df["goes_class_ind"].isin(["C"]))	
	print("X: {:d}, M: {:d}, C: {:d}".format(x, m, c))


df_swpc_2012 = get_yearly_swpc(datetime.datetime(2012,1,1))
df_ngdc_2012 = get_yearly_ngdc(datetime.datetime(2012,1,1))

extra_flare_times = list((set(df_ngdc_2012["ts"]) - set(df_swpc_2012["ts"])))
extra_flare_times = list((set(df_swpc_2012["ts"]) - set(df_ngdc_2012["ts"])))

def print_dif(year):
	print("SWPC:")
	print_flares(get_yearly_swpc(datetime.datetime(year,1,1)))
	print("NGDC:")
	print_flares(get_yearly_ngdc(datetime.datetime(year,1,1)))