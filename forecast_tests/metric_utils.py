import numpy as np 
import matplotlib.pyplot as plt 
from sklearn import metrics
from sklearn.calibration import calibration_curve


"""
This script holds some useful functions for calculating forcast verification metrics.
"""

############## SKILL SCORES #################

def calculate_tss(true_vals, pred_vals):
    """
    Calculate the True Skill Score (TSS) to test the overall predictive 
    abilities of a given forecast.

    Parameters
    ----------
    true_vals : `~np.array`
        The true Y (label) values. The test outputs to compare with the predicted values
    pred_vals : `~np.array`
        The predicted Y values from the model.

    Returns
    -------
    TSS : ~`float`
        calculated TSS value

    Notes
    -----
    See Bloomfield et al. 2012.

    """
    tn, fp, fn, tp = metrics.confusion_matrix(true_vals, pred_vals).ravel()
    
    TSS = (tp / (tp + fn)) - (fp / (fp + tn))
    return TSS


def calculate_tss_threshold(true_vals, prob_vals, thresh):
    """
    Calculate the TSS for a given threshold. This should be 
    used when the forecast gives a probability.

    Parameters
    ---------
    true_values: `~np.array`
        the true values.
    prob_vals: `~np.array`
        the predicted value probabilities.
    thresh : `~float`
        the threshold value to take for binary event (i.e. values above this 
        threshold are taken to be 1 (flare) and those below as 0 (no flare)).
    """
    pred_thresh = [1 if x>thresh else 0 for x in prob_vals]
    tn, fp, fn, tp = metrics.confusion_matrix(true_vals, pred_thresh).ravel()
    TSS = (tp / (tp + fn)) - (fp / (fp + tn))
    return TSS


def calculate_bss(true_vals, prob_vals):
    """
    Calculate the Brier Skill Score (BSS) of a predictive model.

    Parameters
    ----------
    Y_test : `~np.array`
        The true Y (label) values. The test outputs to compare with the predicted values.
    prob_vals : `~np.array`
        The predicted probability values of the model. If using sklearn model - use mdl.predict_proba() function.

    Returns
    -------
    BSS : `float`
        calculated BSS

    """
    bs = metrics.brier_score_loss(true_vals, prob_vals)
    bs_clim = np.mean(true_vals)
    BSS = 1 - bs/bs_clim
    return BSS



############## FORECAST METRIC PLOTS #################


def plot_roc_curve(true_vals, prob_vals, ax=None):
    """
    Plot the receiver operating characteristic (ROC) curve

    Parameters
    ----------
    true_vals : `~np.array`
        The true Y (label) values. The test outputs to compare with the predicted values.
    prob_vals : `~np.array`
        The predicted probability values of the model.
    ax : `~matplotlib.axes.Axes`, optional
        If provided the image will be plotted on the given axes.
    
    Returns
    -------
    Plots the ROC curve

    ax : ~`matplotlib axes`
    """
    fpr, tpr, _ = metrics.roc_curve(true_vals, prob_vals)
    auc_mcstat = metrics.auc(fpr, tpr)
    climatology = np.mean(true_vals)
    
    if ax is None:
        fig, ax = plt.subplots()

    ax.plot(fpr, tpr, label="(AUC = {:.2f})".format(auc_mcstat))
    ax.plot([0, 1], [0, 1], color='grey', linestyle='--')
    ax.set_xlabel("False Positive Rate")
    ax.set_ylabel("True Positive Rate")
    ax.legend(loc="lower right")
    ax.set_title("ROC Curve")
    plt.show()



def plot_reliability_curve(true_vals, pred_vals, n_bins=10):
    """
    Plot the reliability curve (also known as a calibration curve).

    Parameters
    ----------
    true_vals : `~np.array`
        The true Y (label) values. The test outputs to compare with the predicted values
    pred_vals : `~np.array`
        The predicted Y values from the model.
    n_bins : `int`, optional, default 10.
        Number of bins to discretize the [0, 1] interval (input to sklearn `calibration_curve` function).
    
    Returns
    -------
    Plots the reliability diagram

    ax : ~`matplotlib axes`
    
    """

    fraction_of_positives, mean_predicted_value = calibration_curve(true_vals, pred_vals, n_bins=n_bins)
    climatology = np.mean(true_vals)

    fig = plt.figure(figsize=(6,6))
    gs1 = fig.add_gridspec(nrows=4, ncols=1)
    ax1 = fig.add_subplot(gs1[0:3, 0])
    ax2 = fig.add_subplot(gs1[3, 0], sharex=ax1)


    ax1.plot([0, 1], [0, 1], "k:", label="Perfectly calibrated")
    ax1.plot(mean_predicted_value, fraction_of_positives, "s-")
    
    ax1.set_ylabel("Fraction of positives")
    ax1.tick_params(which="both", labelbottom=False)
    ax1.axhline(climatology, color="grey", label="climatology")
    ax1.legend()
    ax1.set_title("Reliability Curve")

    ax2.hist(pred_vals, range=(0, 1), bins=10, 
             histtype="step", lw=2)
    ax2.set_xlabel("Mean predicted value")
    ax2.set_ylabel("# events")

    plt.tight_layout()
    plt.subplots_adjust(hspace=0.05)
    plt.show()


def plot_feature_importance(mdl, features, top=None, title="Feature importance"):
    """
    Function to plot the importance of features from a sklearn model. 
    
    Parameters
    ----------
    mdl : sklearn model that has been already fit
    features : `pd.DataFrame` of features. 
    top : `int`, number of top features to plot, optional.
          default is to plot all. 
    
    """

    if not hasattr(mdl, "feature_importances_"):
        print("{:s} doesn't have feature importance attribute".format(str(mdl)))
        return

    feature_importance = mdl.feature_importances_
    if top is not None:
        sorted_idx = np.argsort(feature_importance)[::-1][0:top]
    else:
        sorted_idx = np.argsort(feature_importance)[::-1]
    np.array(features.columns)[sorted_idx]
    
    pos = np.arange(0, sorted_idx.shape[0]*2, 2)
    
    fig = plt.figure(figsize=(10, 8))
    plt.barh(pos, feature_importance[sorted_idx], 2, align='center', edgecolor="k")
    plt.gca().invert_yaxis()
    plt.yticks(pos, np.array(features.columns)[sorted_idx])
    plt.title(title)