import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt 
from sunpy.net import Fido, attrs as a 
import urllib
import requests 
import time 

flares = pd.read_csv("swpc_event_list.csv")
flares["datetime"] = pd.to_datetime(flares["ts"], format="%Y%m%d%H%M")



latestevents = pd.read_csv("query_sswlatestevents.csv")
latestevents["datetime"] = pd.to_datetime(latestevents["datetime"])
def fixnoaa_num(x):
    if x == 0:
        return '     '
    else: 
        return "1"+str(x)

latestevents["ar_noaanum"] = latestevents["ar_noaanum"].map(fixnoaa_num)

common = pd.merge(flares, latestevents, on="datetime")
ssw_excess = latestevents[~latestevents["datetime"].isin(common["datetime"])]
flare_excess = flares[~flares["datetime"].isin(common["datetime"])]


def get_hek_sswlatestevents():
    res = Fido.search(a.Time("2010-01-01", "2018-12-31"), 
                      a.hek.EventType("FL"), a.hek.FRM.Name=="SSW Latest Events")

    res2 = res[0].to_pandas()

    new_table = res2[["event_starttime", "event_peaktime",
                             "event_endtime", "fl_goescls", "ar_noaanum", "frm_name",
                              "obs_observatory", "frm_institute", "search_frm_name", 
                              "hpc_x", "hpc_y", "hgc_x", "hgc_y", "hgs_x", "hgs_y",
                              ]]

    new_table["goes_class_ind"] = [x[0] for x in new_table["fl_goescls"]]
    new_table_c = new_table[new_table["goes_class_ind"].isin(["X", "M", "C"])]
    new_table_c["datetime"] = pd.to_datetime(new_table_c.event_starttime)
    new_table_c["tt"] = new_table_c.datetime.dt.strftime("%Y%m%d%H%M")
    new_table_c = new_table_c.drop_duplicates(subset="tt")
    new_table_c.reset_index(drop=True, inplace=True)
    new_table_c.to_csv("query_sswlatestevents.csv", index_label=False)


urlbase = "https://www.lmsal.com/solarsoft/latest_events_archive/events_summary/%Y/%m/%d/gev_%Y%m%d_%H%M/"
urls = flares["datetime"].dt.strftime(urlbase)

def get_df(url, retry_count=1):
    """
    urls
    """
    try: 
        test = requests.get(url)
        listy = pd.read_html(url)
        for l in listy:
            if "EName" in l:
                return l
    
    except urllib.error.HTTPError as e:
        print("error HTTP")
        return url

    except ConnectionResetError as e:
        print("error with connection")
        if retry_count == 10:
            raise e
        time.sleep(5)
        print("trying again")
        get_df(url, retry_count + 1)
    except:
        print("random error!")
        return url


def get_pos_df():
    events_df = get_df(urls[0])
    events_df.to_csv("event_loc_info.csv", index_label=True)
    errors = []
    for i in range(1091, len(urls)):
        print(i)
        res = get_df(urls[i])
        if isinstance(res, pd.DataFrame):
            with open("event_loc_info.csv", "a") as f:
                res.to_csv(f, header=False)
            events_df = events_df.append(res)

        elif res is None:
            print("None there")
            errors.append("None")
        else:
            print("theres been some type of error")
            errors.append(res)


def check_url_exists(url):
    try:
        urllib.request.urlopen(url).getcode()
    except urllib.error.HTTPError as e:
        print('HTTPError: {}'.format(e.code))
        return "error!"