import numpy as np 
from sunpy.util import scraper
from sunpy.time import parse_time, TimeRange
import urllib
import pandas as pd


savedir = "/Users/laurahayes/ml_project_flares/flare_analysis/goes_flare_list/goes_files/"

def get_swpc_reports(trange, savedir=None):
    """
    Function to search for an download the SWPC event reports.
    The reports are available from 2015-06-29 to present.

    Parameters
    ----------
    timerange : `sunpy.time.timerange.TimeRange`

    savedir : `str`, optional
        directory to download the files to, default is cwd.

    Returns
    -------
    `list` of the files downloaded

    Notes
    -----
    The data is available here as txt files in format `yyyymmddevents.txt`:
    ftp://ftp.swpc.noaa.gov/pub/indices/events/
    """
    if savedir is None:
        savedir = os.getcwd() + "/"

    file_pattern_swpc = ("ftp://ftp.swpc.noaa.gov/pub/indices/events/%Y%m%devents.txt")
    file_scraper_swpc = scraper.Scraper(file_pattern_swpc)

    urls = file_scraper_swpc.filelist(trange)
    return download_urls(urls, savedir)

    
def get_ngdc_reports(timerange, savedir=None):
    """
    Function to search and download the NOAA NDGC reports.
    The reports are available from 1975 - 2017-06-28.

    Parameters
    ----------
    timerange : `sunpy.time.timerange.TimeRange`

    savedir : `str`, optional
        directory to download the files to, default is cwd.

    Returns
    -------
    `list` of the files downloaded

    Notes
    -----
    The data is available here:
    https://www.ngdc.noaa.gov/stp/space-weather/solar-data/solar-features/solar-flares/x-rays/goes/xrs/
    """

    if savedir is None:
        savedir = os.getcwd() + "/"

    file_pattern_ngdc = ("https://www.ngdc.noaa.gov/stp/space-weather/solar-data/solar-features/solar-flares/x-rays/goes/xrs/goes-xrs-report_%Y.txt")

    file_scraper_ngdc = scraper.Scraper(file_pattern_ngdc)
    urls = file_scraper_ngdc.filelist(timerange)
    return download_urls(urls, savedir)
    

def download_urls(urls, savedir):
    """
    Download a list of urls using urllib.request.urlretrieve

    Parameters
    ----------
    urls : `list`
        list of urls to download
    savedir : `str`
        where to save files

    Returns
    -------
    list of files downloaded
    """
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

def read_swpc_reports(file):
    """
    Function to read the daily SWPC files and return X-ray GOES flares that are present.
    
    Parameters
    ----------
    file : `str`
        report txt file (format goes-xrs-report_yyyy.txt)

    Returns
    -------
    flare_list : pandas DataFrame of the event list with associated parameters 
    available from report. It will obviously only be from one day.

    Notes
    -----
    The description of the data format within txt file is here:
    ftp://ftp.swpc.noaa.gov/pub/indices/events/README

    There is more events listed within the SWPC report, this function only parses out the GOES XRS flares
    noted as "XRA"
    """

    with open(file, "r") as f:
        flare_list = []
        for line in f.readlines():
            if "Date:" in line:
                date = line[7:17].replace(" ", "")
            if "XRA" in line:
                event_list = {}
                event_list["date"] = date
                event_list["event_no"] = line[0:4]
                event_list["start_time"] = line[11:15]
                event_list["max_time"] = line[18:22]
                event_list["end_time"] = line[28:32]
                event_list["goes_sat"] = line[34:37]
                event_list["goes_channel"] = line[48:52]
                event_list["goes_class"] = line[58:62]
                event_list["integrated_flux"] = line[66:73]
                event_list["swpc_ar"] = line[76:80]
                flare_list.append(event_list)

    return pd.DataFrame(flare_list)




