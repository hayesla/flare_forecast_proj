import pandas as pd 
import urllib
import random

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

# lets trim this list to the last solar cycle as that's what I'm interested in.
cdaw_data_final = cdaw_data[(cdaw_data["time_c2"]>=("2010-01-01")) & (cdaw_data["time_c2"]<="2018-12-31")]
cdaw_data_final.reset_index(inplace=True, drop=True)


def get_event_txtfile(cme_event):
	"""
	Construct txt file urls based on particular pattern.
	Bit messy but works.

	The files follow the format:
	 yyyymmdd.hhmmss.w(width){n,p,h}.v{velocity}.p(position_angle)g.yht

	Parameters
	----------
	cme_event : pd.Series
		row of the cdaw pandas dataframe

	Returns
	-------
	final_url : `str` - the corresponding url to cme_event input.

	"""	
	# cme_event = cdaw_data_final.iloc[i]

	urlbase = "https://cdaw.gsfc.nasa.gov/CME_list/UNIVERSAL/"
	
	if cme_event["central_pa"]=="Halo":
		type_cme = "halo"
	elif "Partial Halo" in cme_event["remarks"]:
		type_cme = "partial_halo"
	else:
		type_cme = "normal"

	dict_type = {"halo":"h", "partial_halo": "p", "normal":"n"}
	final_url = urlbase + cme_event["time_c2"].strftime("%Y_%m/yht/%Y%m%d.%H%M%S") \
	             + ".w{:03d}{:s}".format(int(cme_event["width"]), dict_type[type_cme]) \
	             + ".v{:04d}".format(int(cme_event["linear_speed"])) \
	             + ".p{:03d}g.yht".format(int(cme_event["MPA"]))
	return final_url

def read_event_txtfile_quality(url):
	opn = urllib.request.urlopen(url)
	lines = [x.decode() for x in opn.readlines()]
	for l in lines:
		if "QUALITY_INDEX" in l:
			return  " ".join(l.split())


def read_event_txtfile_times(url):
	opn = urllib.request.urlopen(url)
	lines = [x.decode() for x in opn.readlines()]
	onset1 = ""
	onset2 = ""
	onset2_rsun = ""
	for l in lines:
		if "ONSET1" in l:
			onset1 = " ".join(l.split())
		if "ONSET2:" in l:
			onset2 = " ".join(l.split())
		if "ONSET2_RSUN" in l:
			onset2_rsun = " ".join(l.split())
	return onset1, onset2, onset2_rsun


def get_onsettimes(save=False):
	"""
	Pull the calculated onset times from event txt files. This
	should be ran in a way with the get_quality functionaility but the
	way this worked out, I just did it this way.
	"""
	import time
	t1 = time.time()
	onset_times1, onset_times2, onset2_rsun = [], [], []
	for i in range(0, len(cdaw_data_final)):
		print(100*(i/len(cdaw_data_final)))
		txt_url = get_event_txtfile(cdaw_data_final.iloc[i])
		try:
			qual = read_event_txtfile_times(txt_url)
		except:
			qual=("", "", "")
			print("couldn't read url")
		onset_times1.append(qual[0])
		onset_times2.append(qual[1])
		onset2_rsun.append(qual[2])
	t2 = time.time()
	print(t2 - t1)

	cdaw_data_final["onset_times1"] = onset_times1	
	cdaw_data_final["onset_times2"] = onset_times2
	cdaw_data_final["onset_times2_rsun"] = onset2_rsun
	if save:	
		cdaw_data_final.to_csv("cdaw_2010_2018_w_onset_times.csv", index_label=False)

def get_quality(save=False):
	"""
	Read quality index from associated event txt files and include to cdaw list.

	Takes an age and a half, definitely a cleaner to do it but this will do for now.
	"""
	import time
	t1 = time.time()
	quality_index = []
	for i in range(len(cdaw_data_final)):
		print(100*(i/len(cdaw_data_final)))
		txt_url = get_event_txtfile(cdaw_data_final.iloc[i])
		try:
			qual = read_event_txtfile_quality(txt_url)
		except:
			qual=""
			print("couldn't read url")
		quality_index.append(qual)
	t2 = time.time()
	print(t2 - t1)

	cdaw_data_final["quality_index"] = quality_index
	if save:
		cdaw_data_final.to_csv("cdaw_2010_2018_w_quality.csv", index_label=False)


def merge_lists()
	cdaw_qual = pd.read_csv("cdaw_2010_2018_w_quality.csv")
	cdaw_times = pd.read_csv("cdaw_2010_2018_w_onset_times.csv")

	cdaw_times["quality_index"] = cdaw_qual["quality_index"]


	
	cdaw_times.to_csv("final_cme_list_2010_2018.csv", index_label=False)
#### tests ##################
def check_url_exists(url):
	try:
		urllib.request.urlopen(url).getcode()
	except urllib.error.HTTPError as e:
		print('HTTPError: {}'.format(e.code))
		return "error!"

def random_test_of_urls():
	all_urls = [get_event_txtfile(cdaw_data_final.iloc[i]) for i in range(len(cdaw_data_final))]
	errors = []
	for i in range(100):
		ind = random.randrange(0, len(all_urls))
		aa = check_url_exists(all_urls[ind])
		if aa == "error!":
			errors.append(ind)
	print(errors)












