import urllib
import pandas as pd 
from sunpy.time import TimeRange
from sunpy.util import scraper
import glob
import tarfile
from flarelist_utils import read_swpc_reports, read_ngdc_goes_reports
from dateutil.relativedelta import relativedelta
import pandas as pd 


def get_yearly_tar_files():
	"""
	Download yearly tar files that contain all the daily swpc reports and
	save them to the `goes_files` dir.
	"""
	file_url = "ftp://ftp.swpc.noaa.gov/pub//warehouse/%Y/%Y_events.tar.gz"
	scraper = scraper.Scraper(file_url)

	urls = scraper.filelist(TimeRange("2010-01-01", "2018-01-01"))

	for u in urls:
		urllib.request.urlretrieve(u, u.split("/")[-1])


	tar_files = glob.glob("*event*.tar.gz")
	for f in tar_files:
		my_tar = tarfile.open(f)
		my_tar.extractall('./goes_files') # specify which folder to extract to
		my_tar.close()


filedir = "./goes_files/%Y_events/%Y*events*"#%Y%m%devents.txt"
timerange = TimeRange("2010-01-01", "2018-12-31")
years = [timerange.start.datetime + relativedelta(years=i) for i in range(9)]
all_files = []
for y in years:
	all_files += glob.glob(y.strftime(filedir))

all_files.sort()

df_flares = read_swpc_reports(all_files[0])
for f in all_files[1:]:
	df = read_swpc_reports(f)
	df_flares = df_flares.append(df)
df_flares.reset_index(inplace=True, drop=True)
df_flares["ts"] = df_flares.date + df_flares.start_time
df_flares.drop_duplicates(subset="ts")

df_flares_c = df_flares[df_flares["goes_class_ind"].isin(["C", "X", "M"])]


def get_yearly_swpc(year):
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
	file = "goes-xrs-report_%Y.txt"
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