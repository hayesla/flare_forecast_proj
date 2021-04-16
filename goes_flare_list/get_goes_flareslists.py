import numpy as np 
from sunpy.util import scraper
from sunpy.time import parse_time, TimeRange
import urllib
import pandas as pd

# this ftp access is only available since 2015-06-29
file_pattern_swpc = ("ftp://ftp.swpc.noaa.gov/pub/indices/events/%Y%m%devents.txt")
file_scraper_swpc = scraper.Scraper(file_pattern_swpc)

trange = TimeRange("2021-01-01", "2021-04-16")
urls = file_scraper_swpc.filelist(trange)


file_pattern_ngdc = ("https://www.ngdc.noaa.gov/stp/space-weather/solar-data/solar-features/solar-flares/x-rays/goes/xrs/goes-xrs-report_%Y.txt")
file_scraper_ngdc = scraper.Scraper(file_pattern_ngdc)

trange = TimeRange("2013-01-01", "2013-10-30")

savedir = "/Users/laurahayes/ml_project_flares/flare_analysis/goes_flare_list/goes_files/"

def get_swpc_reports(trange, savedir=None):


    
def get_ngdc_reports(timerange, savedir=None):
    """
    Function to search and download the NOAA NDGC reports.

    Parameters
    ----------
    timerange : `sunpy.time.timerange.TimeRange`

    savedir : `str`, optional
        directory to download the files to, default is cwd.

    Returns
    -------
    `list` of the files downloaded
    """

    if savedir is None:
        savedir = os.getcwd() + "/"

    file_pattern_ngdc = ("https://www.ngdc.noaa.gov/stp/space-weather/solar-data/ \
                          solar-features/solar-flares/x-rays/goes/xrs/goes-xrs-report_%Y.txt")

    urls = file_scraper_ngdc.filelist(trange)
    
    results = []
    if len(urls) != 0:
        for u in urls:
            try:
                res = urllib.request.urlretrieve(u, savedir+u.split("/")[-1])
                results.append(res[0])
                print("download success {:s}".format(res[0]))
            except:
                print("couldn't download {:s}".format(u))

    return results


def read_ngdc_goes_reports(file):
    """
    Function to read the yearly X-ray solar flare reports provided by NGDC.
    The files available span from 1975 - mid-2017.

    Parameters
    ----------
    file : `str`
        report txt file (format goes-xrs-report_yyyy.txt)

    Returns
    -------
    pandas DataFrame of the event list with associated parameters available from report.

    Notes
    -----
    The data is available here:
    https://www.ngdc.noaa.gov/stp/space-weather/solar-data/solar-features/solar-flares/x-rays/goes/xrs/

    The description of the data and how the txt file was parsed is based here:
    https://www.ngdc.noaa.gov/stp/space-weather/solar-data/solar-features/solar-flares/x-rays/documentation/miscellaneous/xray.fmt.rev
    """
    with open(file, "r") as f:
        flare_list = []
        for line in f.readlines():
            event_list = {}
            event_list["data_code"] = line[0:5]
            event_list["date"] = line[5:11]
            event_list["start_time"] = line[13:17]
            event_list["end_time"] = line[18:22]
            event_list["max_time"] = line[23:27]
            event_list["position"] = line[28:34]
            event_list["goes_class"] = line[59:62]+"."+line[62]
            event_list["goes_sat"] = line[67:70]
            event_list["integrated_flux"] = line[72:79]
            event_list["noaa_ar"] = line[80:85]
            flare_list.append(event_list)

    return pd.DataFrame(flare_list)

