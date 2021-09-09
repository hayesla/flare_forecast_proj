import pandas as pd
import numpy as np 
from sunpy.util import scraper
from sunpy.time import TimeRange 
# from sunpy.io.special import srs
import  read_srs as srs
from dateutil.relativedelta import relativedelta
from astropy.table import Column, vstack
import urllib
import tarfile
import os



def get_srs_files(tstart, tend, savedir='./'):
	"""
	Function to download the NOAA solar region summary files SRS files
	given a timerange. The text files will be downloaded to a local directory
	specified in the savedir keyword.
	
	Parameters
	----------
	tstart : ~str
		start date of search to download
	tend : ~str
		end date of search to download
	savedir : ~str, optional
		path to where to save the files. Default is cwd.

	"""

	trange = TimeRange(tstart, tend)
	file_pattern_swpc = ("ftp://ftp.swpc.noaa.gov/pub/warehouse/%Y/%Y_SRS.tar.gz")
	file_scraper_swpc = scraper.Scraper(file_pattern_swpc)

	urls = file_scraper_swpc.filelist(trange)
	for u in urls:
		filename = savedir+u.split("/")[-1]
		if os.path.exists(filename):
			return
		urllib.request.urlretrieve(u, filename)
		if os.path.exists(filename):
			with tarfile.open(filename, 'r') as t:
				t.extractall(path=savedir)


def make_srs_table(file):
	"""
	Function to read a SRS text file and return an astropy Table with the read in data.

	Parameters
	----------
	file : ~str
		SRS txt file to be read in

	Returns
	-------
	astropy.table.Table

	"""

	file_table = srs.read_srs(file)
	date_obs = file_table.meta["issued"]
	date_column = Column(name="date", data=[date_obs.strftime("%Y-%m-%d %H:%M")]*len(file_table))
	file_table.add_column(date_column)

	return file_table

def get_srs_df(files, save=False, csv_filename="SRS_all.csv"):
	"""
	Function to read a list of SRS files and then return a pandas DataFrame 
	of the concatenated information from the files.

	Parameters
	----------
	files : ~list
		list of SRS files
	save : Boolean, optional
		if True, it will save the pd.DataFrame as a csv file
	"""
	errors= []
	data0 = make_srs_table(files[0])
	for i in range(1, len(files)):

		try:
			data1 = make_srs_table(files[i])
			if len(data1)>0:
				data0 = vstack([data0, data1])
		except:
			print(i)
			errors.append(files[i])

	srs_df = data0.to_pandas()
	if save:
		srs_df.to_csv(csv_filename, index_label=False)
		return errors
	else:
		return srs_df, errors

def get_all_ar_info(tstart, tend, savedir, csv_filename=None):
	"""
	Function that takes a start and end time, download the SRS files
	between those times, and then saves all in the information in one csv
	file, which can then be read into a pandas dataframe.

	Parameters
	----------
	tstart : ~str
		start date of search to download
	tend : ~str
		end date of search to download
	savedir : ~str, optional
		path to where to save the files. Default is cwd.
	csv_filename : ~str
		name of csv file to which to save final pd.DataFrame

	"""
	# download SRS files
	#get_srs_files(tstart, tend, savedir=savedir)

	# get list of all the files
	filedir = "{:s}%Y_SRS/%Y%m%dSRS.txt".format(savedir)
	timerange = TimeRange(tstart, tend)
	t0 = timerange.start.datetime
	files = [t0.strftime(filedir)]
	while timerange.end.datetime>t0:
		t0 = t0 + relativedelta(days=1)
		files.append(t0.strftime(filedir))
	files.sort()
	
	
	files.sort()
	for f in files:
		if not os.path.exists(f):
			print("No data found {:s}".format(f))
			files.remove(f)

	if csv_filename is None:
		csv_filename = "SRS_data_{:s}_{:s}.csv".format(timerange.start.strftime("%Y%m%d"), timerange.end.strftime("%Y%m%d"))

	# read in all individal files and save to csv file.
	errors = get_srs_df(files, save=True, csv_filename=csv_filename)
	return errors

"""
--------------------------------------------------------
This is where you would add in your own timerange dates, 
your own local directory to save the SRS txt files
and define the name you want for your output csv
--------------------------------------------------------
"""

savedir ='/Users/laurahayes/ml_project_flares/flare_analysis/AR_analysis/srs_data/'

# tstart, tend = "2010-01-01", "2018-12-31"

# csv_filename = 'SRS_all_2010-2018.csv'
# get_srs_files(tstart, tend, savedir)
# get_all_ar_info(tstart, tend, savedir, csv_filename=csv_filename)



tstart = "1996-01-01"
tend = "2018-12-31"


errors = get_all_ar_info(tstart, tend, savedir)