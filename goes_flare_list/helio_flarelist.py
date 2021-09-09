import pandas as pd 
import matplotlib.pyplot as plt 
import numpy as np 
from astropy.io.votable import parse
from astropy.coordinates import SkyCoord
from astropy import units as u 
from sunpy.coordinates import frames
from sunpy.time import parse_time
import datetime

def get_goes_class(x):
    if x[0]=="C":
        return float(x[1:])*1e-6
    elif x[0] == "M":
        return float(x[1:])*(1e-5)
    elif x[0] == "X":
        return float(x[1:])*(1e-4)
    elif x[0] == "B":
        return float(x[1:])*(1e-7)
    elif x[0] == "A":
        return float(x[1:])*(1e-8)
    else:
        return


# http://hec.helio-vo.eu/hec/hec_gui.php
def get_helio_flarelist():
    aa = parse("http://hec.helio-vo.eu/hec/hec_gui_fetch.php?interfacetype=vmstilts&sql=select+%2A+from+gevloc_sxr_flare+where+time_start%3E%3D%272010-01-01+00%3A00%3A00%27+AND+time_start%3C%3D%272018-12-31+23%3A59%3A59%27&type=votable")
    full_table = aa.get_first_table().to_table().to_pandas()
    # full_table.head()
    full_table["goes_class_ind"] = [x[0] for x in full_table["xray_class"]]
    full_table["goes_class_val"] = full_table["xray_class"].map(get_goes_class)
    full_table.to_csv("helio_flarelist_full.csv", index_label=False)



get_make_final():
	full_table = pd.read_csv("helio_flarelist_full.csv")
	helio_c = full_table[full_table["goes_class_ind"].isin(["X", "M", "C"])]
	helio_c.reset_index(drop=True, inplace=True)
	helio_c.to_csv("helio_flarelist_c.csv", index_label=False)

get_helio_flarelist()
get_make_final()