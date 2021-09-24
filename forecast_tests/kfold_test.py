import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt 
plt.ion()
import seaborn as sns

from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, GradientBoostingClassifier, GradientBoostingRegressor, AdaBoostClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.svm import SVC, SVR
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn import preprocessing
from sklearn.model_selection import StratifiedKFold, TimeSeriesSplit
import xgboost as xgb

from metric_utils import *

###-------READ IN DATA------###

# ar data with flares
data_ar = pd.read_csv("AR_flare_ml_23_24.csv")

# evolution data
data_ar_evol = pd.read_csv("AR_flare_ml_23_24_evol.csv")
# replace nans with 0's with pre-flare feature
data_ar_evol["pre_flare"].replace(np.nan, 0, inplace=True)

data_ar_evol["C+"] = data_ar_evol["C+"].map(lambda x: 1 if x>0 else 0)
data_ar_evol.drop(columns=["M+", "X+"], inplace=True)

data_ar_evol.sort_values(by="AR issue_date", inplace=True)
data_ar_evol.reset_index(inplace=True, drop=True)

###-------FEATURES------###


ml_columns = ["AREA", "Longitude_extent", "No_sunspots", "MAGTYPE", "McIntosh", "C+"]
data_ml = data_ar_evol[ml_columns]

# sort out categorical data


# encode the categorical data (MAGTYPE & McIntosh)
magtype_encode = pd.get_dummies(data_ml["MAGTYPE"])
mcintosh_encode = pd.get_dummies(data_ml["McIntosh"])
data_ml = pd.concat([data_ml, magtype_encode, mcintosh_encode], axis=1).drop(columns=["MAGTYPE", "McIntosh"])

# le1 = preprocessing.LabelEncoder()
# le2 = preprocessing.LabelEncoder()
# data_ml["MAGTYPE"] = le1.fit_transform(data_ar_evol["MAGTYPE"])
# data_ml["McIntosh"] = le2.fit_transform(data_ar_evol["McIntosh"])

# scale the numerical data 
scaled_numerical = preprocessing.MinMaxScaler().fit_transform(data_ml[["AREA", "Longitude_extent", "No_sunspots"]].apply(np.log1p).values)
data_ml = pd.concat([data_ml, pd.DataFrame(scaled_numerical, columns=["AREA_scaled", "Longitude_scaled", "NoSunspots_scaled"])], axis=1)
data_ml.drop(columns=["AREA", "Longitude_extent", "No_sunspots"], inplace=True)

## get features and labels
features = data_ml.drop(columns=["C+"])
labels = data_ml["C+"]


###-------K-FOLD------###
X = features.values
Y = labels.values


models = [LogisticRegression(), LinearDiscriminantAnalysis(), RandomForestClassifier(), GradientBoostingClassifier(), xgb.XGBClassifier()]
model_names = ["LR", "LDA", "RF", "GB", "XGB"]

tss_all = []
bss_all = []
kfl = StratifiedKFold(n_splits=10)
for i in range(len(models)):
    mdl = models[i]
    print(mdl)
    tss = []
    bss = []

    fig1, ax1 = plt.subplots()
    fig2, ax2 = plt.subplots()

    for k, (train_ind, test_ind) in enumerate(kfl.split(X, Y)):
        print("Doing {:d} fold".format(k))
        xtrain, xtest = X[train_ind], X[test_ind]
        ytrain, ytest = Y[train_ind], Y[test_ind]
        mdl.fit(xtrain, ytrain)
        prediction = mdl.predict(xtest)
        tss.append(calculate_tss(ytest, prediction))
        bss.append(calculate_bss(ytest, mdl.predict_proba(xtest)[:, 1]))
        # plot roc curve
        metrics.plot_roc_curve(mdl, xtest, ytest, drawstyle="steps-mid", ax=ax1)
        ax1.set_title("ROC Curve {:s}".format(model_names[i]))
        if hasattr(mdl, "predict_proba"):
            prob_pos = mdl.predict_proba(xtest)[:, 1]
        else: 
            prob_pos = mdl.decision_function(xtest)
            prob_pos = \
                (prob_pos - prob_pos.min()) / (prob_pos.max() - prob_pos.min())

        fraction_of_positives, mean_predicted_value = \
            calibration_curve(ytest, prob_pos, n_bins=10)

        ax2.plot([0, 1], [0, 1], "k:", label="Perfectly calibrated")
        ax2.plot(mean_predicted_value, fraction_of_positives, "s-")
        ax2.set_ylabel("Fraction of positives")
        ax2.set_xlabel("Mean predicted value")


    tss_all.append(tss)
    bss_all.append(bss)
    fig1.tight_layout()
    fig1.savefig("./overview_plots/ROC_kfold_{:s}.png".format(model_names[i]), dpi=300, bbox_inches="tight")


    fig2.tight_layout()
    fig2.savefig("./overview_plots/reliability_kfold_{:s}.png".format(model_names[i]), dpi=300, bbox_inches="tight")

    plt.close()
    plt.close()

tss_df = pd.DataFrame(np.array(tss_all).T, columns=model_names)
bss_df = pd.DataFrame(np.array(bss_all).T, columns=model_names)
    
fig, ax = plt.subplots()
sns.boxplot(data=tss_df, ax=ax)
ax.set_ylabel("TSS")
ax.set_xlabel("ML Classifier")
ax.set_title("K-Fold cross-validation (all data)")
plt.tight_layout()
plt.savefig("./overview_plots/tss_cross_val.png", dpi=300)



fig, ax = plt.subplots()
sns.boxplot(data=bss_df, ax=ax)
ax.set_ylabel("BSS")
ax.set_xlabel("ML Classifier")
ax.set_title("K-Fold cross-validation (all data)")
plt.tight_layout()
plt.savefig("./overview_plots/bss_cross_val.png", dpi=300)
