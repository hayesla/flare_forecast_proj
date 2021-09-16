import numpy as np 
import matplotlib.pyplot as plt 

from sklearn import metrics
from sklearn.calibration import calibration_curve


############## SKILL SCORES #################

def get_tss(Y_test, prediction):
    """
    Get the True Skill Score (TSS) to test the overall predictive 
    abilities of a given forecast.

    Parameters
    ----------
    Y_test : `~np.array`
        The true Y (label) values. The test outputs to compare with the predicted values
    prediction : `~np.array`
        The predicted Y values from the model.

    Returns
    -------
    TSS : ~`float`
        calculated TSS value

    Notes
    -----
    See Bloomfield et al. 2012.

    """
    tn, fp, fn, tp = metrics.confusion_matrix(Y_test, prediction).ravel()
    
    TSS = (tp / (tp + fn)) - (fp / (fp + tn))
    return TSS


def get_tss_threshold(true_vals, pred_vals, thresh):
    """
    This will get the TSS for a given threshold. This should be 
    used when the forecast gives a probability


    Parameters
    ---------
    true_values: `~np.array`
        the true values.
    pred_values: `~np.array`
        the predicted value probabilities.
    thresh : `~float`
        the threshold value to take for binary event (i.e. values above this 
        threshold are taken to be 1 (flare) and those below as 0 (no flare)).
    """
    pred_y_thresh = [1 if x>thresh else 0 for x in pred_vals]
    tn, fp, fn, tp = confusion_matrix(true_vals, pred_y_thresh).ravel()
    TSS = (tp / (tp + fn)) - (fp / (fp + tn))
    return TSS


def get_bss(Y_test, prob_pos):
    """
    Get the Brier Skill Score (BSS) of a predictive model.

    Parameters
    ----------
    Y_test : `~np.array`
        The true Y (label) values. The test outputs to compare with the predicted values
    prediction : `~np.array`
        The predicted probability values of the model. Typically gotten from mdl.predict_proba() function.

    Returns
    -------
    BSS : `float`
        calculated BSS

    """
    bs = metrics.brier_score_loss(Y_test, prob_pos)
    bs_clim = np.mean(Y_test)
    BSS = 1 - bs/bs_clim
    return BSS


############## FORECAST METRIC PLOTS #################


def plot_roc_and_reliability_curve(mdl, X_test, Y_test, ):
    """
    Parameters
    ----------
    mdl : sklearn model that has been already fit
    features : `pd.DataFrame` of features. 
    X_test : `~np.array`
        The true test feature values. The test inputs to the mdl. 
    Y_test : `~np.array`
        The true test Y (label) values. The test outputs to compare with the predicted values.

    """

    if hasattr(mdl, "predict_proba"):
        prob_pos = mdl.predict_proba(X_test)[:, 1]
    else: 
        prob_pos = mdl.decision_function(X_test)
        prob_pos = \
            (prob_pos - prob_pos.min()) / (prob_pos.max() - prob_pos.min())

    fraction_of_positives, mean_predicted_value = \
        calibration_curve(Y_test, prob_pos, n_bins=10)



    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 5))
    # plot ROC curve
    metrics.plot_roc_curve(mdl, X_test, Y_test, drawstyle="steps-mid", ax=ax1)
    # plot reliability diagram
    ax2.plot([0, 1], [0, 1], "k:", label="Perfectly calibrated")
    ax2.plot(mean_predicted_value, fraction_of_positives, "s-")
    ax2.set_ylabel("Fraction of positives")
    ax2.set_xlabel("Mean predicted value")

    plt.tight_layout()

def plot_feature_importance(mdl, features, top=None, title="Feature importance"):
    """
    Function to plot the importance of features from a model. 
    
    Parameters
    ----------
    mdl : sklearn model that has been already fit
    features : `pd.DataFrame` of features. 
    top : `int`, optional, number of top features to plot.
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