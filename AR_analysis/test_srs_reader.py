import pandas as pd 
import read_srs as srs

# Read in flare data
swpc_flares = pd.read_csv("/Users/laurahayes/ml_project_flares/flare_analysis/goes_flare_list/swpc_flarelist_19960731_20181231.csv")
swpc_flares["start_time"] = pd.to_datetime(swpc_flares["start_time"], format="%Y-%m-%d %H:%M:%S")
swpc_flares["matchtime"] = swpc_flares.start_time.dt.strftime("%Y-%m-%d 00:30")
swpc_flares["match_noaa_ar"] = swpc_flares["noaa_ar"].astype(str)
swpc_flares2 = swpc_flares[swpc_flares["noaa_ar"]!=0]


# Read in AR_analysis data
# ar_data = pd.read_csv("/Users/laurahayes/ml_project_flares/flare_analysis/AR_analysis/SRS_data_19960101_20181231.csv")
# ar_data = pd.read_csv("/Users/laurahayes/ml_project_flares/flare_analysis/AR_analysis/SRS_data_new_19960101_20181231.csv")
# ar_data = ar_data[ar_data["ID"].isin(["I", "IA"])]
# ar_data["Number"][ar_data["Number"]>19000]  =  ar_data["Number"][ar_data["Number"]>19000] - 10000
# ar_data["matchtime"] = pd.to_datetime(ar_data["date"]).dt.strftime("%Y-%m-%d 00:30")
# ar_data["match_noaa_ar"] = ar_data["Number"].astype(int).astype(str)
# ar_data.drop(columns=["col1", "col2", "col3", "col4", "col5"], inplace=True)

ar_data = pd.read_csv("/Users/laurahayes/ml_project_flares/flare_analysis/AR_analysis/SRS_data_new_19960101_20181231.csv")

ar_data["matchtime"] = pd.to_datetime(ar_data["date"]).dt.strftime("%Y-%m-%d 00:30")
ar_data["match_noaa_ar"] = ar_data["NMBR"].map(lambda x: x + 10000 if x<4000 else x).astype(int).astype(str)
ar_data.drop(columns=["NM", "NONE", "BETA"], inplace=True)


# Merge the dataframes
flare_ar_df = pd.merge(swpc_flares2, ar_data, how="left", on=["matchtime", "match_noaa_ar"])

flare_w_ar = flare_ar_df[~flare_ar_df["date_y"].isnull()]
flare_no_ar = flare_ar_df[flare_ar_df["date_y"].isnull()]

flare_no_ar.reset_index(inplace=True, drop=True)

dates_of_issue = flare_no_ar["matchtime"].unique()


savedir ='/Users/laurahayes/ml_project_flares/flare_analysis/AR_analysis/srs_data/'
filedir = "{:s}%Y_SRS/%Y%m%dSRS.txt".format(savedir)

files_to_test = pd.to_datetime(dates_of_issue).strftime(filedir)

# files_to_test.sort()
# for f in files_to_test:
# 	if not os.path.exists(f):
# 		print("No data found {:s}".format(f))
# 		files_to_test.remove(f)
