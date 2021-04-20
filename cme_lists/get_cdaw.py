import pandas as pd 
import urllib

def get_cdaw_file():
	"""
	Download SOHO LASCO CME catalogue, see https://cdaw.gsfc.nasa.gov/CME_list/.
	"""
	url = "https://cdaw.gsfc.nasa.gov/CME_list/UNIVERSAL/text_ver/univ_all.txt"
	urllib.request.urlretrieve(url, "univ_all.txt")

def cdaw_to_df(file):
	"""
	Read the txt file of the SOHO LASCO CME Catalogue and return a 
	pandas dataframe.

	Parameters
	----------
	file : `str` - .txt file of the yearly or full CDAW catalogue

	Returns
	-------
	`pd.DataFrame` of the catalogue

	Notes
	-----
	- Parameters and txt file format is described: https://cdaw.gsfc.nasa.gov/CME_list/catalog_description.htm
	- Data available : https://cdaw.gsfc.nasa.gov/CME_list/UNIVERSAL/text_ver/
	- The columns are all in `str` types - this is just to help with post-processing, dealing with *'s and "Halo" values etc.
	"""
	f = open(file, "r")
	lines = f.readlines()
	data_as_dict = []
	for l in lines[4:-1]:
		events = {}
		data = l.split()
		events["date"] = data[0]
		events["time"] = data[1]
		events["central_pa"] = data[2]
		events["width"] = data[3]
		events["linear_speed"] = data[4]
		events["2nd_order_speed_inital"] = data[5]
		events["2nd_order_speed_final"] = data[6]
		events["2nd_order_speed_20R"] = data[7]
		events["accel"] = data[8]
		events["mass"] = data[9]
		events["kinetic_energy"] = data[10]
		events["MPA"] = data[11]
		if len(data)>12:
			events["remarks"] = " ".join(data[12:])
		else:
			events["remarks"] = ""
		data_as_dict.append(events)

	f.close()
	return pd.DataFrame(data_as_dict)

cdaw_data = cdaw_to_df("univ_all.txt")
cdaw_data["time_c2"] = pd.to_datetime(cdaw_data.date + cdaw_data.time, format="%Y/%m/%d%H:%M:%S")


