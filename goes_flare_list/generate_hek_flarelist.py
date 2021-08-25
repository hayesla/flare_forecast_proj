from sunpy.net import Fido, attrs as a 
import pandas as pd 
import time
import pickle


def generate_hek():
	"""
	Query the HEK for solar flare data from SWPC. 
	This takes ~27 minutes to run which is long - something
	up with the sunpy HEK api.
	"""
	t1 = time.time()
	res = Fido.search(a.Time("1996-01-01", "2018-12-31"), 
	                  a.hek.EventType("FL"), a.hek.FRM.Name == "SWPC",
	                  a.hek.FL.GOESCls >= "C1.0")# a.hek.OBS.Observatory=="GOES")

	t2 = time.time()

	diff = t2 - t1
	print(diff)


	with open("hek_query_1996-2018.pickle", "wb") as f:
		pickle.dump(res["hek"], f)

	new_table = res["hek"]["event_starttime", "event_peaktime",
	                        "event_endtime", "fl_goescls", "ar_noaanum", 'hpc_x', 'hpc_y']

	new_table.write("hek_flares_table_1996-2018.csv", format="csv")