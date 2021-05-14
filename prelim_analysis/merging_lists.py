import pandas as pd 
import matplotlib.pyplot as plt 
from sunpy.coordinates import frames
import sunpy.map
from astropy.coordinates import SkyCoord
from astropy import units as u 
import datetime
from astropy.coordinates import SkyCoord, CylindricalRepresentation
import numpy as np 

flare_list = pd.read_csv("/Users/laurahayes/ml_project_flares/flare_analysis/goes_flare_list/final_flare_list.csv")
flare_list = flare_list.set_index(pd.to_datetime(flare_list["event_starttime"]))
flare_list.sort_index(inplace=True)
flare_list["event_starttime"] = pd.to_datetime(flare_list["event_starttime"])


hpc_coords = SkyCoord(flare_list["hpc_x"]*u.arcsec, flare_list["hpc_y"]*u.arcsec, 
					  frame=frames.Helioprojective, obstime=flare_list["event_starttime"], 
					  observer="earth")

hcr_coords = hpc_coords.transform_to(frames.Heliocentric)
phi = hcr_coords.cylindrical.phi.wrap_at(360*u.deg).value

# 90 degrees offset in the way sunpy makes it
flare_list["phi"] = phi-90

def test_positions():
	from sunpy.sun import constants
	R_sun = constants.radius
	hcc = SkyCoord(CylindricalRepresentation(2*R_sun, 190*u.deg, 0*u.km),
	               frame=frames.Heliocentric(observer="earth", obstime=flare_list.iloc[8586]["event_starttime"]))

	hcc_cme = SkyCoord(CylindricalRepresentation(2*R_sun, (330)*u.deg, 0*u.km),
	               frame=frames.Heliocentric(observer="earth", obstime=flare_list.iloc[8586]["event_starttime"]))


	hcc_flare = SkyCoord(CylindricalRepresentation(0.8*R_sun, (350)*u.deg, 0*u.km),
	               frame=frames.Heliocentric(observer="earth", obstime=flare_list.iloc[8586]["event_starttime"]))


	ref_coord = SkyCoord(0*u.arcsec, 0*u.arcsec, frame=frames.Helioprojective(observer="earth", obstime=flare_list.iloc[8586]["event_starttime"]))
	my_header = sunpy.map.make_fitswcs_header(np.zeros((25, 25)), ref_coord, scale=[100, 100]*u.arcsec/u.pixel)
	my_map = sunpy.map.Map(np.zeros((25, 25)), my_header)

	center = SkyCoord(0*u.arcsec, 0*u.arcsec, frame=frames.Helioprojective, obstime=flare_list.iloc[8586]["event_starttime"], observer="earth")
	center_hcc = center.transform_to(frames.Heliocentric)

	my_map.plot(alpha=0, title="")
	my_map.draw_limb(color="k")
	ax = plt.gca()
	ax.plot_coord(SkyCoord((center_hcc, hcc)), marker='x', color="k")
	ax.plot_coord(hcc_flare, marker='x', color="b")
	ax.plot_coord(hcc_cme, marker='x', color="r")
	my_map.draw_grid(color="k", annotate=False)


cme_list = pd.read_csv("/Users/laurahayes/ml_project_flares/flare_analysis/cme_lists/final_cme_list_2010_2018.csv")
cme_list["start_time_c2"] = pd.to_datetime(cme_list.date + cme_list.time, format="%Y/%m/%d%H:%M:%S") 
#cme_list = cme_list.set_index(pd.to_datetime(cme_list.date + cme_list.time, format="%Y/%m/%d%H:%M:%S"))
def get_times(x):
	xx = x.split()
	if len(xx)==3:
		return pd.to_datetime(" ".join(xx[1:]))
	else:
		return np.nan

cme_list["onset_times1"] = cme_list.onset_times1.map(get_times)
cme_list["onset_times2"] = cme_list.onset_times2.map(get_times)

def check_benchmark_numbers(flare_list):
	"""
	In table 2 of https://arxiv.org/pdf/1907.02905.pdf the number of flare days 
	are listed, lets just make sure ours are the same.

	Which is correct (C+ :188, M+: 26, X+: 3)
	"""
	flare_list = flare_list.set_index(pd.to_datetime(flare_list["event_starttime"]))
	flare_list_test = flare_list.truncate("2016-01-01", "2017-12-31")
	flare_list_test["date"] = pd.to_datetime(flare_list_test["event_starttime"]).dt.strftime("%Y-%m-%d")

	print("C+", len(flare_list_test["date"].unique()))
	print("M+", len(flare_list_test[flare_list_test["goes_class_ind"].isin(["M", "X"])]["date"].unique()))
	print("X+", len(flare_list_test[flare_list_test["goes_class_ind"].isin(["X"])]["date"].unique()))




## First focus only on M and X class flares:

flare_xm = flare_list[flare_list["goes_class_ind"].isin(["X", "M"])]

#cme_list = cme_list[cme_list.quality_val>1]

eruptive = []
quality_cme = []
index = []
for i in range(len(flare_xm)):

	cme_list_compare = cme_list[(cme_list["start_time_c2"]>=flare_xm.iloc[i]["event_starttime"]-datetime.timedelta(hours=1)) &
								(cme_list["start_time_c2"]<=flare_xm.iloc[i]["event_starttime"]+ datetime.timedelta(hours=2))]
	if len(cme_list_compare)==0:
		eruptive.append("no")
		quality_cme.append(np.nan)
		index.append(np.nan)
	elif len(cme_list_compare)>0:
		eruptive.append("yes")
		quality_cme.append(int(cme_list_compare.quality_val.values[0]))
		index.append(int(cme_list_compare.index.values[0]))	

	# elif (len(cme_list_compare)==1):
	# 	# if (np.abs(cme_list_compare.MPA - flare_xm.iloc[i].phi) <= 45).values[0]:
	# 		eruptive.append("yes")
	# 		quality_cme.append(int(cme_list_compare.quality_val.values))
	# 		index.append(int(cme_list_compare.index.values))			
	# 	else:
	# 		eruptive.append("no")
	# 		quality_cme.append(np.nan)
	# 		index.append(np.nan)
	# elif len(cme_list_compare)>1:
	# 	find_angles = cme_list_compare[np.abs(cme_list_compare.MPA - flare_xm.iloc[i].phi) <=45]
	# 	if len(find_angles)==1:
	# 		eruptive.append("yes")
	# 		quality_cme.append(int(find_angles.quality_val.values))
	# 		index.append(int(find_angles.index.values))		
	# 	elif len(find_angles)==0:
	# 		eruptive.append("no")
	# 		quality_cme.append(np.nan)
	# 		index.append(np.nan)
	# 	else:
	# 		print("issue with", i)
	# 		eruptive.append("yes")
	# 		quality_cme.append(int(find_angles.quality_val.values[0]))
	# 		index.append(int(find_angles.index.values[0]))		


flare_xm["eruptive"] = eruptive
flare_xm["cme_quality"] = quality_cme
flare_xm["cme_index_df"] = index

flare_x = flare_xm[flare_xm["goes_class_ind"].isin(["X"])]

flare_m = flare_xm[flare_xm["goes_class_ind"].isin(["M"])]

print("X", 100*flare_x["eruptive"].value_counts()/len(flare_x))
print("M", 100*flare_m["eruptive"].value_counts()/len(flare_m))
# test = []
# for i in range(len(flare_xm)):
# 	# cme_list_compare = cme_list.truncate(flare_xm.iloc[i]["event_starttime"], 
# 	# 					flare_xm.iloc[i]["event_starttime"] + datetime.timedelta(hours=1))

# 	cme_list_compare = cme_list[(cme_list["start_time_c2"]>=flare_xm.iloc[i]["event_starttime"]) &
# 								(cme_list["start_time_c2"]<=flare_xm.iloc[i]["event_starttime"]+ datetime.timedelta(hours=1))]

# 	# test.append(len(cme_list_compare))
# 	# print(i)
# 	if len(cme_list_compare)==0:
# 	 	test.append(np.nan)
# 	elif (len(cme_list_compare)==1):
# 		if (np.abs(cme_list_compare.MPA - flare_xm.iloc[i].phi) <= 45).values[0] :
# 			test.append(cme_list_compare.index.to_numpy())
# 		else:
# 			test.append(np.nan)
# 	elif len(cme_list_compare)>1:
# 		find_angles = cme_list_compare[np.abs(cme_list_compare.MPA - flare_xm.iloc[i].phi) <=45]
# 		if len(find_angles)==1:
# 			test.append(find_angles.index.to_numpy())
# 		elif len(find_angles)==0:
# 			test.append(np.nan)
# 		else:
# 			test.append(np.nan)
# 			print(i, "Problemoooo too many CMEs for this event", len(cme_list_compare), cme_list_compare.quality_val.values)



