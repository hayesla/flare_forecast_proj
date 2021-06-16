import urllib
import pandas as pd 
from sunpy.time import TimeRange
from sunpy.util import scraper
import glob
import tarfile
from flarelist_utils import read_swpc_reports, read_ngdc_goes_reports
from dateutil.relativedelta import relativedelta
import pandas as pd 
import datetime

"""
This is the script that allows you to get the GOES flare list from the SWPC daily
event reports. The `get_yearly_tar_files` searches and downloads the files between
a given timerange, and then `get_swpc_flarelist` then reads in the files and then can
create a pandas dataframe of the flarelist between given dates and saves the results as a 
csv file.

This is used to create swpc_event_list.csv.
"""

def get_yearly_tar_files(tstart, tend, savedir='./goes_files'):
	"""
	Function to download yearly tar files that contain all the daily swpc reports and
	save them to the `./goes_files` dir (by default).

	Parameters
	----------
	tstart : ~str
		start date of search to download
	tend : ~str
		end date of search to download
	savedir : ~str, optional
		path to where to save the files. Default is ./goes_files.

	"""
	file_url = "ftp://ftp.swpc.noaa.gov/pub//warehouse/%Y/%Y_events.tar.gz"
	goes_scraper = scraper.Scraper(file_url)

	urls = goes_scraper.filelist(TimeRange(tstart, tend))

	for u in urls:
		urllib.request.urlretrieve(u, u.split("/")[-1])

	tar_files = glob.glob("*event*.tar.gz")
	for f in tar_files:
		my_tar = tarfile.open(f)
		my_tar.extractall(savedir) # specify which folder to extract to
		my_tar.close()


def get_swpc_flarelist(tstart, tend, csv_filename='swpc_event_list.csv'):
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

	df_flares = read_swpc_reports(files[0])
	for f in files[1:]:
		df = read_swpc_reports(f)
		df_flares = df_flares.append(df)
	df_flares.reset_index(inplace=True, drop=True)
	df_flares["ts"] = df_flares.date + df_flares.start_time
	df_flares = df_flares.drop_duplicates(subset="ts")

	df_flares_c = df_flares[df_flares["goes_class_ind"].isin(["C", "X", "M"])]
	df_flares_c.reset_index(inplace=True, drop=True)
	df_flares_c.to_csv(csv_filename, index_label=False)

"""
--------------------------------------------------------
This is where you would add in your own timerange dates, 
your own local directory to save the daily report txt files
and define the name you want for your output csv to save 
flarelist.
--------------------------------------------------------
"""

tstart, tend = "2010-01-01", "2018-01-01"
get_yearly_tar_files(tstart, tend)
get_swpc_flarelist(tstart, tend)
