from sunpy.util import scraper
from sunpy.time import TimeRange
import urllib
import pandas as pd
import os 
import glob
import tarfile

"""
This is a script that holds a number of utility functions to search for and 
download GOES event list files. It also holds functions to read the different 
GOES event files. 
"""

def get_daily_swpc_reports(timerange, savedir=None):
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

    urls = file_scraper_swpc.filelist(timerange)
    urls.sort()
    return download_urls(urls, savedir)


def get_yearly_swpc_event_reports(tstart, tend, savedir='./goes_files/'):
    """
    Function to download yearly tar files that contain all the daily swpc reports and
    save them to the `./goes_files` dir (by default). Data available from 1996-present.

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
        # check is data directory already exists locally
        # and if not download
        dir_name = u.split("/")[-1]
        if not os.path.exists(savedir + dir_name.split(".")[0]):
            urllib.request.urlretrieve(u, dir_name)
            # extract tar to savedir directory
            my_tar = tarfile.open(dir_name)
            my_tar.extractall(savedir) # specify which folder to extract to
            my_tar.close()

    
def get_yearly_ngdc_reports(timerange, savedir=None):
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
    urls.sort()
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
            if os.path.exists(savedir+u.split("/")[-1]):
                results.append(savedir+u.split("/")[-1])
                continue
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
            if len(line)>79:
                event_list = {}
                event_list["data_code"] = line[0:5]
                event_list["date"] = "20"+line[5:11]
                event_list["start_time"] = line[13:17]
                event_list["end_time"] = line[18:22]
                event_list["max_time"] = line[23:27]
                event_list["position"] = line[28:34]
                event_list["goes_class_ind"] = line[59]
                event_list["goes_class"] = line[59]+line[61]+"."+line[62]
                event_list["goes_sat"] = line[67:70]
                event_list["integrated_flux"] = line[72:79]
                if len(line)>=80:
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
            elif "EDITED EVENTS for" in line:
                date = pd.to_datetime(line[18:29]).strftime("%Y%m%d")

            if "XRA" in line:
                event_list = {}
                event_list["date"] = date
                event_list["event_no"] = line[0:4]
                event_list["start_time"] = line[11:15]
                event_list["max_time"] = line[18:22]
                event_list["end_time"] = line[28:32]
                event_list["goes_sat"] = line[34:37]
                event_list["goes_channel"] = line[48:52]
                event_list["goes_class_ind"] = line[58]
                event_list["goes_class"] = line[58:62]
                event_list["integrated_flux"] = line[66:73]
                # to adjust for cases when no active region number
                # and when the NOAA ar numbering passed 9000.
                if len(line)>75:
                    ar = int(line[76:80]) if (line[76:80]!= "    " and '\n' not in line[76:80]) else 0
                    if (ar < 4000 and ar!=0):
                        ar = ar + 10000
                else:
                    ar = 0
                event_list["noaa_ar"] = ar
                flare_list.append(event_list)

    return pd.DataFrame(flare_list)




