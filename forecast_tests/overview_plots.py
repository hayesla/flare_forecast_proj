import numpy as np 
import matplotlib.pyplot as plt 
import pandas as pd 
import seaborn as sns
# plotting setups
plt.rcParams['xtick.direction'] = "in"
plt.rcParams['ytick.direction'] = "in"
plt.rcParams['xtick.minor.visible'] = True
plt.rcParams['ytick.minor.visible'] = True
plt.rcParams['font.family'] = 'Helvetica'
sns.set_context("paper", font_scale=1.2)


# ar data with flares
data_ar = pd.read_csv("AR_flare_ml_23_24.csv")

data_ar["datetime"] = pd.to_datetime(data_ar["AR issue_date"])

data_ar["unique_month"] = data_ar.datetime.dt.strftime("%Y-%m")

monthly_flares = data_ar.groupby(["unique_month"]).sum()[["C", "M", "X"]]
monthly_flares.index = pd.to_datetime(monthly_flares.index)

fig, ax = plt.subplots(figsize=(10, 6))

monthly_flares.plot(ax=ax, drawstyle="steps-mid")
ax.set_xlabel("Time")
ax.set_ylabel("# flares")
ax.set_xlim(monthly_flares.index.min(), monthly_flares.index.max())
ax.set_ylim(-1, 175)

ax.fill_between(monthly_flares.index, 
                monthly_flares["C"].values, 
                step="mid", alpha=0.5)


ax.fill_between(monthly_flares.index, 
                monthly_flares["M"].values, 
                step="mid", alpha=0.5)


ax.fill_between(monthly_flares.index, 
                monthly_flares["X"].values, 
                step="mid", alpha=0.5)

ax.axvspan("2016-01-01", "2017-12-31", color="grey", alpha=0.5,label="test interval")
ax.axvline("2016-01-01", color="g")
ax.axvline("2017-12-31", color="g")
ax.tick_params(which="both", direction="out")
ax.legend()
plt.tight_layout()
plt.savefig("./overview_plots/overview_data.png", dpi=300, bbox_inches="tight")