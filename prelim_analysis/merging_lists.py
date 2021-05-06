import pandas as pd 
import matplotlib.pyplot as plt 
from sunpy.coordinates import frames
from astropy.coordinates import SkyCoord
from astropy import units as u 

flare_list = pd.read_csv("/Users/laurahayes/ml_project_flares/flare_analysis/goes_flare_list/helio_flarelist_c.csv")
cme_list = pd.read_csv("/Users/laurahayes/ml_project_flares/flare_analysis/cme_lists/cdaw_2010_2018_w_quality.csv")

def check_benchmark_numbers():
	"""
	In table 2 of https://arxiv.org/pdf/1907.02905.pdf the number of flare days 
	are listed, lets just make sure ours are the same.

	Which is correct (C+ :188, M+: 26, X+: 3)
	"""
	flare_list = flare_list.set_index(pd.to_datetime(flare_list["time_start"]))
	flare_list_test = flare_list.truncate("2016-01-01", "2017-12-31")
	flare_list_test["date"] = pd.to_datetime(flare_list_test["time_start"]).dt.strftime("%Y-%m-%d")

	print("C+", len(flare_list_test["date"].unique()))
	print("M+", len(flare_list_test[flare_list_test["goes_class_ind"].isin(["M", "X"])]["date"].unique()))
	print("X+", len(flare_list_test[flare_list_test["goes_class_ind"].isin(["X"])]["date"].unique()))




