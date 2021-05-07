import matplotlib.pyplot as plt 
import numpy as np 
import pandas as pd 
from matplotlib import dates
import seaborn as sns
from sunpy.time import parse_time
import matplotlib
from mpl_toolkits.axes_grid1 import make_axes_locatable
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
    
sns.set_context("paper", font_scale=1.3)
plt.rcParams['font.family'] = 'Helvetica'

flares = pd.read_csv("final_flare_list.csv")
flares["datetime"] = pd.to_datetime(flares["event_starttime"])
flares["unique_month"] = pd.to_datetime(flares.datetime.dt.strftime("%Y-%m"))
flares = flares.set_index("datetime")
flares["tt"] = [x.total_seconds() for x in flares.index - flares.index[0]]

flares["counts"] = np.ones(len(flares))
flares_c = flares[flares["goes_class_ind"].isin(["C"])].groupby("unique_month")["counts"].sum()
flares_cm = flares[flares["goes_class_ind"].isin(["M", "C"])].groupby("unique_month")["counts"].sum()
flares_cmx = flares[flares["goes_class_ind"].isin(["X", "M", "C"])].groupby("unique_month")["counts"].sum()

def plot_monthly_rate():
    fig, ax = plt.subplots(figsize=(8, 6))
    flares.groupby("unique_month")["goes_class_ind"].count().plot(drawstyle="steps-mid", axes=ax)


    ax.xaxis.set_major_locator(dates.MonthLocator(interval=12))
    ax.xaxis.set_minor_locator(dates.MonthLocator(interval=4))
    ax.xaxis.set_major_formatter(dates.DateFormatter("%Y-%b"))
    ax.set_xlabel("Time")
    ax.set_ylabel("# Flares (C+)")
    ax.set_title("Month Flare Rate Solar Cycle 24")
    ax.tick_params(which="both", direction="in")
    ax.set_xlim('2010-01-01', '2018-12-31')
    ax.set_ylim(0, 260)
    ax.fill_between(flares.groupby("unique_month")["goes_class_ind"].count().index, 
                    flares.groupby("unique_month")["goes_class_ind"].count().values, 
                    step="mid", alpha=0.5)

    plt.tight_layout()

def monthly_rate_seperate():
    fig, ax = plt.subplots(figsize=(10, 7))

    ax.fill_between(flares_cmx.index, 
                    flares_cmx.values, 
                    step="mid", 
                    color="tab:green", 
                    label="X flares")


    ax.fill_between(flares_cm.index, 
                    flares_cm.values, 
                    step="mid", 
                    color="tab:orange", 
                    label="M flares")


    ax.fill_between(flares_c.index, 
                    flares_c.values, 
                    step="mid", 
                    color="tab:blue", 
                    label="C flares")

    ax.set_ylim(0, 260)
    ax.set_xlim(parse_time('2010-01-01').datetime, parse_time('2018-12-31').datetime)

    ax.xaxis.set_major_locator(dates.MonthLocator(interval=12))
    ax.xaxis.set_minor_locator(dates.MonthLocator(interval=4))

    ax.xaxis.set_major_formatter(dates.DateFormatter("%Y"))
    ax.legend(loc="upper right")
    ax.set_xlabel("Time")
    ax.set_ylabel("# Flares")
    plt.tight_layout()
    plt.savefig("overall_monthly_flares.png", dpi=200)
    plt.close()

def plot_positions():
    flares_p = flares[flares["hgs_lat"]>-60]
    
    fig, ax = plt.subplots(figsize=(8, 8))

    cmap = matplotlib.cm.get_cmap('magma_r')
    cc = cmap(0.75)


    axins1 = inset_axes(ax, 
                        width="50%",  # width = 50% of parent_bbox width
                        height="3%",  # height : 5%
                        loc='lower center')

    # the scatter plot:
    im = ax.scatter(flares_p["hpc_x"], flares_p["hpc_y"], alpha=0.4, s=5*flares_p["goes_class_val"]*1e6,
                c=flares_p["tt"]/60/60/60/60, cmap=cmap)
    circle1 = plt.Circle((0, 0), 960, color='grey', fill=False)
    ax.add_artist(circle1)
    # Set aspect of the main axes.
    ax.set_aspect("equal")
    ax.set_xlim(-1100, 1100)
    ax.set_ylim(-1100, 1100)


    # create new axes on the right and on the top of the current axes
    divider = make_axes_locatable(ax)
    # below height and pad are in inches
    ax_histx = divider.append_axes("top", 1.4, pad=0.1, sharex=ax)
    ax_histy = divider.append_axes("right", 1.4, pad=0.1, sharey=ax)

    ax_histx.tick_params(labelbottom=False, direction="in")
    ax_histy.tick_params(labelleft=False, direction="in")
    # ax.tick_params(direction="in", right="in", top="in")

    _ = ax_histx.hist(flares_p["hpc_x"], bins=35, color=cc, alpha=0.7,  edgecolor="grey")
    _ = ax_histy.hist(flares_p["hpc_y"], bins=35, orientation='horizontal', color=cc, alpha=0.7, edgecolor="grey")

    ax.set_xlabel("Helioprojective X (arcsec)")
    ax.set_ylabel("Helioprojective Y (arcsec)")
    ax_histx.set_ylabel("# flares")
    ax_histy.set_xlabel("# flares")

    ax_histx.set_title("Solar Cyle 24 Flares > C1.0")

    cbar = fig.colorbar(im, cax=axins1, orientation="horizontal", ticks=[0, 5, 10, 15, 20])
    axins1.set_xticklabels(['2010', '2012', '2014', '2016', '2018'], rotation=0) 
    axins1.xaxis.tick_top()


    ax.scatter(np.nan, np.nan, s=5*1e6*(1e-4), color=cmap(0.8), alpha=0.3, edgecolor="k", label="X")
    ax.scatter(np.nan, np.nan, s=5*1e6*(1e-5), color=cmap(0.8), alpha=0.3, edgecolor="k", label="M")
    ax.scatter(np.nan, np.nan, s=5*1e6*(1e-6), color=cmap(0.8), alpha=0.3, edgecolor="k", label="C")
    ax.legend()
    plt.tight_layout()
    plt.savefig("flare_positions.png", dpi=200)

def plot_flares_as_fn_of_time():

    fig, ax = plt.subplots(figsize=(10, 6))
    cc = cmap(0.75)

    plt.scatter(flares.index, flares["goes_class_val"], color=cc,#, c=flares["tt"], cmap=cmap, 
                alpha=0.4)
    
    ax.xaxis.set_major_locator(dates.MonthLocator(interval=12))
    ax.xaxis.set_minor_locator(dates.MonthLocator(interval=4))
    ax.xaxis.set_major_formatter(dates.DateFormatter("%Y"))

    ax.set_xlabel("Time")
    ax.set_ylabel("GOES peak flux (Wm$^{-2}$")
    ax.set_yscale("log")
    ax.set_ylim(1e-6, 1e-3)

    ax.tick_params(which="both", direction="in", right=True, top=True)
    plt.tight_layout()
    plt.savefig("flares_during_time_onecolor.png", dpi=200)
    plt.close()
