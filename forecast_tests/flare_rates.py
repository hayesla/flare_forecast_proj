import pandas as pd 
import datetime
import matplotlib.pyplot as plt
import numpy as np 

# ar data with flares
data_ar = pd.read_csv("AR_flare_ml_23_24.csv")

# evolution data
data_ar_evol = pd.read_csv("AR_flare_ml_23_24_evol.csv")
row_has_NaN = data_ar_evol.isnull().any(axis=1)
data_ar_evol = data_ar_evol[~row_has_NaN]

def get_flare_rates(data):
	"""
	Determine flare rates for each McIntosh classification given an input 
	dataframe of AR-flare data.
	"""

	flare_number_per_group = data.groupby(["McIntosh"])[["C", "M", "X"]].sum().reset_index()
	total_per_group = data.groupby(["McIntosh"])["C"].count().reset_index().rename(columns={"C":"N"})
	flare_number_per_group["N"] = total_per_group["N"]

	flare_rates_per_group = flare_number_per_group.set_index("McIntosh")[["C", "M", "X"]].div(flare_number_per_group["N"].values, axis=0)

	flare_number_per_group["C_rate"] = flare_rates_per_group["C"].values
	flare_number_per_group["M_rate"] = flare_rates_per_group["M"].values
	flare_number_per_group["X_rate"] = flare_rates_per_group["X"].values

	return flare_number_per_group

flare_rates = get_flare_rates(data_ar)



i = 100
mcint = data_ar.iloc[i]["McIntosh"]
flare_rate_mcint = flare_rates[flare_rates["McIntosh"].isin([mcint])]

c_prob = 1-np.exp(-flare_rate_mcint["C_rate"].values[0])
m_prob = 1-np.exp(-flare_rate_mcint["M_rate"].values[0])
x_prob = 1-np.exp(-flare_rate_mcint["X_rate"].values[0])

print("Probability of C-class flare: {:f}".format(c_prob))
print("Probability of M-class flare: {:f}".format(m_prob))
print("Probability of X-class flare: {:f}".format(x_prob))



test_set = data_ar.iloc[np.random.random_integers(0, len(data_ar), 1000)]

test_x = test_set["McIntosh"].values
test_y_c = test_set["C"].map(lambda x: 1 if x>0 else 0).values
test_y_m = test_set["M"].map(lambda x: 1 if x>0 else 0).values
test_y_x = test_set["X"].map(lambda x: 1 if x>0 else 0).values

pred_y_c = [get_predicted_flare_rates(x)[0] for x in test_x]
pred_y_m = [get_predicted_flare_rates(x)[1] for x in test_x]
pred_y_x = [get_predicted_flare_rates(x)[2] for x in test_x]



thresholds = np.linspace(0.01, 1, 100)
tss_c, tss_m, tss_x = [], [], []
for t in thresholds:
	tss_c.append(get_tss(test_y_c, pred_y_c, t))
	tss_m.append(get_tss(test_y_m, pred_y_m, t))
	tss_x.append(get_tss(test_y_x, pred_y_x, t))


fig, ax = plt.subplots()
ax.plot(thresholds*100, tss_c, drawstyle="steps-mid", label="C-class")
ax.plot(thresholds*100, tss_m, drawstyle="steps-mid", label="M-class")
ax.plot(thresholds*100, tss_x, drawstyle="steps-mid", label="X-class")

ax.legend()
ax.set_xlim(0, 100)
ax.set_ylim(0, 0.8)
ax.set_xlabel("Threshold Probability (%)")
ax.set_ylabel("Total Skill Score (TSS)")


def get_predicted_flare_rates(mcint):
	flare_rate_mcint = flare_rates[flare_rates["McIntosh"].isin([mcint])]

	c_prob = 1-np.exp(-flare_rate_mcint["C_rate"].values[0])
	m_prob = 1-np.exp(-flare_rate_mcint["M_rate"].values[0])
	x_prob = 1-np.exp(-flare_rate_mcint["X_rate"].values[0])
	return c_prob, m_prob, x_prob	

def cm(true_vals, pred_vals, thres1, thres2):

    TP = TN = FP = FN = 0
    for i in range(len(pred_vals)):
        if true_vals[i] >= thres1 and pred_vals[i] >= thres2:
            TP +=1
        elif true_vals[i]  >= thres1 and pred_vals[i] <thres2:
            FN +=1
        elif true_vals[i] < thres1 and pred_vals[i] > thres2:
            FP +=1
        elif true_vals[i] < thres1 and pred_vals[i] < thres2:
            TN +=1
    precision = TP / (TP + FP)
    recall = TP / (TP + FN)
    specificity = TN / (TN + FP)
    TSS = (TP / (TP + FN)) - (FP / (FP + TN))
    return precision, recall, specificity, TSS
    

def get_tss(true_vals, pred_vals, thresh):

    pred_y_thresh = [1 if x>thresh else 0 for x in pred_vals]
    tn, fp, fn, tp = confusion_matrix(true_vals, pred_y_thresh).ravel()
    TSS = (tp / (tp + fn)) - (fp / (fp + tn))
    return TSS




def roc_and_pr_curves(y_test, pred, physical_threshold = 0.1, filename = None):
    y_true_binarized = [1 if elem > physical_threshold else 0 for elem in (y_test)]

    fpr_grd, tpr_grd, _ = roc_curve(y_true=y_true_binarized, y_score=(pred))
    roc_auc = auc(fpr_grd, tpr_grd)

    average_precision = average_precision_score(y_true_binarized, (pred))
    precision, recall, _ = precision_recall_curve(y_true_binarized, (pred))

    
    #plot the ROC curve
    
    fig, ax = plt.subplots(1,2, figsize = (12, 5))
   
    lw = 2
    ax[0].plot(fpr_grd, tpr_grd, color='darkorange',
             lw=lw, label='ROC curve (area = %0.2f)' % roc_auc)
    ax[0].plot([0, 1], [0, 1], color='navy', lw=lw, linestyle='--')
    ax[0].set_xlim([0.0, 1.0])
    ax[0].set_ylim([0.0, 1.05])
    ax[0].set_xlabel('False Positive Rate')
    ax[0].set_ylabel('True Positive Rate')
    ax[0].set_title('Receiver operating characteristic')
    ax[0].legend(loc="lower right")
    


    #plot the precision and recall
    #fig, ax = plt.subplots()
    ax[1].step(recall, precision, color='b', alpha=0.2,
             where='post')
    ax[1].fill_between(recall, precision, step='post', alpha=0.2,
                     color='b')

    ax[1].set_xlabel('Recall')
    ax[1].set_ylabel('Precision')
    ax[1].set_ylim([0.0, 1.05])
    ax[1].set_xlim([0.0, 1.0])

def plot_tss(y_test, pred_gbr, filename = None):
    fig, ax = plt.subplots()
    res = []
    vals = np.arange(0.01, 0.7, 0.01)
    for i in vals:
    	print(i)
        p,r,s,t = cm(np.array(y_test), pred_gbr, 0.1, i)
        res.append((p,r,s,t))

    res = np.array(res)
    # plt.plot(vals, res[:,0], label = 'Precision')
    # plt.plot(vals, res[:,1], label = 'Recall')
    # plt.plot(vals, res[:,2], label = 'Specificity')
    plt.plot(vals, res[:,3], label = 'TSS')
    plt.title( 'TSS: '+str(round(np.max(res[:,3]),3)))
    
    ind = np.where(res[:,3] == np.max(res[:,3]))[0][0]
    plt.axvline(vals[ind])
    plt.legend(loc = 'upper right')
    plt.xlabel('Threshold')
    plt.ylabel('Value')
