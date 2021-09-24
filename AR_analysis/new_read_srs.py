import pandas as pd 
from sunpy.time import TimeRange
from dateutil.relativedelta import relativedelta
import os
import datetime

def get_df_from_srs(filepath):
    with open(filepath) as srs2:
        file_lines = srs2.readlines()


    date1 = datetime.datetime.strptime(filepath.split("/")[-1], "%Y%m%dSRS.txt").strftime("%Y-%m-%d 00:30")
    file_lines = [f.upper() for f in file_lines]
    
    for i in range(len(file_lines)):
        if "MAG TYPE" in file_lines[i]:
            file_lines[i] = file_lines[i].replace("MAG TYPE", "MAGTYPE")


    section_line_indices = []
    for i, line in enumerate(file_lines):
        if line.startswith(("I.", "IA.", "II.")):
            section_line_indices.append(i+1)

    header = file_lines[0:section_line_indices[0]]
    for h in header:
        if h.startswith(":ISSUED"):
            date = datetime.datetime.strptime(h, ":ISSUED: %Y %b %d %H%M UTC\n").strftime("%Y-%m-%d %H:%M")

    lines1 = file_lines[section_line_indices[0]: section_line_indices[1]-1]
    if len(lines1)==0:
        return 
    else:
        dict_cols = lines1[0].split()
        rows_raw = [l.split() for l in lines1[1:]]
        rows = [r for r in rows_raw if len(r)==8]

        df = pd.DataFrame(rows, columns=dict_cols)
        df["date"] = [date]*len(df)

        return df


def get_all_srs_csv(tstart, tend, csv_filename=None):

    filedir = "{:s}%Y_SRS/%Y%m%dSRS.txt".format('/Users/laurahayes/ml_project_flares/flare_analysis/AR_analysis/srs_data/')
    timerange = TimeRange(tstart, tend)
    t0 = timerange.start.datetime
    files = [t0.strftime(filedir)]
    while timerange.end.datetime>t0:
        t0 = t0 + relativedelta(days=1)
        files.append(t0.strftime(filedir))
    files.sort()

    files2 = []
    for f in files:
        if os.path.exists(f):
            files2.append(f)

    dfs = []
    for i in range(len(files2)):
        print(i)
        df = get_df_from_srs(files2[i])
        dfs.append(df)

    final_srs_df = pd.concat(dfs)
    final_srs_df.reset_index(inplace=True, drop=True)

    final_srs_df["NMBR"] = final_srs_df["NMBR"].astype(int).map(lambda x: x + 10000 if x < 4000 else x)

    final_srs_df.rename(columns={"NMBR":"ar_noaanum", "LO": "Carrington_long", "LL":"Longitude_extent", "NN":"No_sunspots"}, 
                        inplace=True)

    if csv_filename is None:
        csv_filename = "SRS_data_new_{:s}_{:s}.csv".format(timerange.start.strftime("%Y%m%d"), timerange.end.strftime("%Y%m%d"))
    final_srs_df.to_csv(csv_filename, index_label=False)


tstart = "1996-01-01"
tend = "2018-12-31"
get_all_srs_csv(tstart, tend)
