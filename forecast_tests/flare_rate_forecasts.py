import pandas as pd 
import datetime
import matplotlib.pyplot as plt
import numpy as np 

from metric_utils import calculate_bss, calculate_tss, calculate_tss_threshold
from metric_utils import plot_roc_curve, plot_reliability_curve

# ar data with flares
data_ar = pd.read_csv("AR_flare_ml_23_24.csv")

# evolution data
data_ar_evol = pd.read_csv("AR_flare_ml_23_24_evol.csv")
row_has_NaN = data_ar_evol.isnull().any(axis=1)
data_ar_evol = data_ar_evol[~row_has_NaN]
data_ar_evol["evolution_mcint"] = data_ar_evol["pre_mcint"] + data_ar_evol["McIntosh"]


def get_flare_rates_mcintosh(data):
    """
    Determine flare rates for each McIntosh classification given an input 
    dataframe of AR-flare data.

    Parameters
    ----------
    data: `~pd.DataFrame`
    	dataframe of the active regions per day

    Returns 
    -------
	flare_number_per_group : `~pd.DataFrame`
		a dataframe of each McIntosh classifications and their associated
		flaring rates
    """

    flare_number_per_group = data.groupby(["McIntosh"])[["C+", "M+", "X+"]].sum().reset_index()
    total_per_group = data.groupby(["McIntosh"])["C+"].count().reset_index().rename(columns={"C+":"N"})
    flare_number_per_group["N"] = total_per_group["N"]

    flare_rates_per_group = flare_number_per_group.set_index("McIntosh")[["C+", "M+", "X+"]].div(flare_number_per_group["N"].values, axis=0)

    flare_number_per_group["C_rate"] = flare_rates_per_group["C+"].values
    flare_number_per_group["M_rate"] = flare_rates_per_group["M+"].values
    flare_number_per_group["X_rate"] = flare_rates_per_group["X+"].values

    return flare_number_per_group


def get_flare_rates_mcevol(data):
    """
    Determine flare rates for each McIntosh evolution given an input 
    dataframe of AR-flare data.
    """

    flare_number_per_group = data.groupby(["evolution_mcint"])[["C+", "M+", "X+"]].sum().reset_index()
    total_per_group = data.groupby(["evolution_mcint"])["C+"].count().reset_index().rename(columns={"C+":"N"})
    flare_number_per_group["N"] = total_per_group["N"]

    flare_rates_per_group = flare_number_per_group.set_index("evolution_mcint")[["C+", "M+", "X+"]].div(flare_number_per_group["N"].values, axis=0)

    flare_number_per_group["C_rate"] = flare_rates_per_group["C+"].values
    flare_number_per_group["M_rate"] = flare_rates_per_group["M+"].values
    flare_number_per_group["X_rate"] = flare_rates_per_group["X+"].values

    return flare_number_per_group


def forecast_mcstat(flare_rates, mcint, evol=False):
    """
	Determine the forecast probability based on the flaring rates of McIntosh classifications.

    Parameters
    ----------
    data: `~pd.DataFrame`
    	the flaring rates for each McIntosh classification (created from `get_flare_rates_mcintosh()`)
    mcint : `~str`
    	The McIntosh classification to get predicted forecast

    Returns 
    -------
	c_prob : `~float`
		probability of C-class flare for given `mcint`
	m_prob : `~float`
		probability of M-class flare for given `mcint`
	x_prob : `~float`
		probability of X-class flare for given `mcint`		


	Notes
	-----
	If the passed McIntosh class `mcint` has not been seen before 0 is returned.

    """
    if evol:
    	flare_rate_mcint = flare_rates[flare_rates["evolution_mcint"].isin([mcint])]
    else:
    	flare_rate_mcint = flare_rates[flare_rates["McIntosh"].isin([mcint])]
    if len(flare_rate_mcint)==0:
        return np.nan, np.nan, np.nan # TODO note this is going to effect ROC curve - maybe drop these for metrics 
    c_prob = 1-np.exp(-flare_rate_mcint["C_rate"].values[0])
    m_prob = 1-np.exp(-flare_rate_mcint["M_rate"].values[0])
    x_prob = 1-np.exp(-flare_rate_mcint["X_rate"].values[0])
    return c_prob, m_prob, x_prob	

#--------------------------------------------------------------------------------------#
############## MCSTAT ##################

# # define training and testing data
train_ar = data_ar[~(data_ar["AR issue_date"]>="2016-01-01")&(data_ar["AR issue_date"]<="2017-12-31")]
test_ar = data_ar[(data_ar["AR issue_date"]>="2016-01-01")&(data_ar["AR issue_date"]<="2017-12-31")]

# get flare rates for training data
flare_rates_train = get_flare_rates_mcintosh(train_ar)
# test inputs and outputs (X, y)
X_test = test_ar["McIntosh"].values
y_test_c = test_ar["C+"].map(lambda x: 1 if x>0 else 0).values

# get predicted values based on input test values
y_pred_c = [forecast_mcstat(flare_rates_train, x, evol=False)[0] for x in X_test]


# Brier Skill Score
bss_mcstat = calculate_bss(y_test_c, y_pred_c)

# True Skill Score
prob_thresholds = np.linspace(0.01, 1, 100)
tss_mcstat_thresholds = [calculate_tss_threshold(y_test_c, y_pred_c, x) for x in prob_thresholds]
max_tss_mcstat = np.max(tss_mcstat_thresholds)

print("McStat: The BSS is {:.02f} and the max TSS is {:.02f}".format(bss_mcstat, max_tss_mcstat))

# plot threshold TSS 
fig, ax = plt.subplots()
ax.plot(prob_thresholds*100, tss_mcstat_thresholds, drawstyle="steps-mid", label="C+")
ax.set_xlabel("Threshold Probability (%)")
ax.set_ylabel("Total Skill Score (TSS)")
ax.set_xlim(0, 100)
ax.set_ylim(0, 1)
ax.set_title("McStat ($\geqslant$ C1.0)")
plt.savefig("./flare_rate_plots/threshold_mcstat.png", dpi=300, facecolor="w", bbox_inches="tight"); plt.close()

# plot ROC curve
ax_roc = plot_roc_curve(y_test_c, y_pred_c)
ax_roc.set_title("ROC Curve McStat ($\geqslant$ C1.0)")
plt.savefig("./flare_rate_plots/roc_curve_mcstat.png", dpi=300, bbox_inches="tight"); plt.close()

# plot Reliability curve
ax_rel = plot_reliability_curve(y_test_c, y_pred_c, n_bins=10)
ax_rel[0].set_title("Reliability Curve McStat ($\geqslant$ C1.0)")
plt.savefig("./flare_rate_plots/reliability_mcstat.png", dpi=300, bbox_inches="tight"); plt.close()

#--------------------------------------------------------------------------------------#
############## MCEVOL ##################

train_ar_evol = data_ar_evol[~(data_ar_evol["AR issue_date"]>="2016-01-01")&(data_ar_evol["AR issue_date"]<="2017-12-31")]
test_ar_evol = data_ar_evol[(data_ar_evol["AR issue_date"]>="2016-01-01")&(data_ar_evol["AR issue_date"]<="2017-12-31")]

flare_rates_train_evol = get_flare_rates_mcevol(train_ar_evol)

X_test_evol = test_ar_evol["evolution_mcint"].values
y_test_c_evol = test_ar_evol["C+"].map(lambda x: 1 if x>0 else 0).values

y_pred_c_evol = [forecast_mcstat(flare_rates_train_evol, x, evol=True)[0] for x in X_test_evol]


inds_nans = np.where(np.isnan(y_pred_c_evol))[0]
y_pred_c_evol = np.delete(y_pred_c_evol, inds_nans)
y_test_c_evol = np.delete(y_test_c_evol, inds_nans)


# Brier Skill Score
bss_mcevol = calculate_bss(y_test_c_evol, y_pred_c_evol)

# True Skill Score
tss_mcevol_thresholds = [calculate_tss_threshold(y_test_c_evol, y_pred_c_evol, x) for x in prob_thresholds]
max_tss_mcevol = np.max(tss_mcevol_thresholds)

print("McEvol: The BSS is {:.02f} and the max TSS is {:.02f}".format(bss_mcevol, max_tss_mcevol))


# plot threshold TSS 
fig, ax = plt.subplots()
ax.plot(prob_thresholds*100, tss_mcevol_thresholds, drawstyle="steps-mid", label="C+")
ax.set_xlabel("Threshold Probability (%)")
ax.set_ylabel("Total Skill Score (TSS)")
ax.set_xlim(0, 100)
ax.set_ylim(0, 1)
ax.set_title("McEvol ($\geqslant$ C1.0)")
plt.savefig("./flare_rate_plots/threshold_mcevol.png", dpi=300, facecolor="w", bbox_inches="tight"); plt.close()

# plot ROC curve
ax_roc = plot_roc_curve(y_test_c_evol, y_pred_c_evol)
ax_roc.set_title("ROC Curve McEvol ($\geqslant$ C1.0)")
plt.savefig("./flare_rate_plots/roc_curve_mcevol.png", dpi=300, bbox_inches="tight"); plt.close()

# plot Reliability curve
ax_rel = plot_reliability_curve(y_test_c_evol, y_pred_c_evol, n_bins=10)
ax_rel[0].set_title("Reliability Curve McEvol ($\geqslant$ C1.0)")
plt.savefig("./flare_rate_plots/reliability_mcevol.png", dpi=300, bbox_inches="tight"); plt.close()

