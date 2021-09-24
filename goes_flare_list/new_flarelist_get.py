from sunpy.util import scraper
from sunpy.time import TimeRange
import urllib
import pandas as pd
import os 

def get_swpc_reports(tstart, tend, savedir='./goes_files/'):
    """
    Function to search for an download the SWPC event reports.
    The reports are available from 2015-06-29 to present.

    Parameters
    ----------
    tstart : ~str
        start date of search to download
    tend : ~str
        end date of search to download

    savedir : ~str, optional
        directory to download the files to, default is ./goes_files.

    Returns
    -------
    `list` of the files downloaded

    Notes
    -----
    The data is available here as txt files in format `yyyymmddevents.txt`:
    ftp://ftp.swpc.noaa.gov/pub/indices/events/ or ftp://ftp.swpc.noaa.gov/pub//warehouse/%Y/%Y_events.tar.gz

    """


    file_pattern_swpc = ("ftp://ftp.swpc.noaa.gov/pub/indices/events/%Y%m%devents.txt")
    file_scraper_swpc = scraper.Scraper(file_pattern_swpc)

    urls = file_scraper_swpc.filelist(TimeRange(tstart, tend))
    urls.sort()
    for u in urls:
        filepath = savedir + u.split("/")[-1][0:4] + "_events/" + u.split("/")[-1]
        if not os.path.exists(filepath):
            print("toi")
            urllib.request.urlretrieve(u, filepath)
        else:
            print("already exists")


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


get_swpc_reports("2020-01-01", "2021-08-10")
get_swpc_flarelist("2010-01-01", "2021-08-10", csv_filename="swpc_flarelist_20200101-20210810.csv")
