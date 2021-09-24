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

# replicate rows for rows that have flares C+ > 1
new_rows = []
for i in range(len(data_ar_evol)):
    df = data_ar_evol.iloc[i]
    no_flares = df["C+"].astype(int)
    if no_flares > 1:
        nr = [df]*(no_flares-1)
        for n in nr:
            new_rows.append(n)

data_ar_evol = data_ar_evol.append(new_rows, ignore_index=True)
data_ar_evol["C+"] = data_ar_evol["C+"].map(lambda x: 1 if x>0 else 0)
data_ar_evol.drop(columns=["M+", "X+"], inplace=True)

data_ar_evol.sort_values(by="AR issue_date", inplace=True)
data_ar_evol.reset_index(inplace=True, drop=True)
###-------PREP DATA FOR MACHINE LEARNING------###

# categorical data fix

# ohe = preprocessing.OneHotEncoder()
# transformed_magtype = ohe.fit_transform(data_ar_evol["MAGTYPE"].values.reshape(-1, 1)).toarray()
# magtype_cats = pd.DataFrame(transformed_magtype, columns=ohe.get_feature_names())
# data_ar_evol = pd.concat([data_ar_evol, magtype_cats, magtest], axis=1).drop(["MAGTYPE"], axis=1)

ml_columns = ["AREA", "Longitude_extent", "No_sunspots", "MAGTYPE", "McIntosh", "C+"]
data_ml = data_ar_evol[ml_columns]

# encode the categorical data (MAGTYPE & McIntosh)
# magtype_encode = pd.get_dummies(data_ml["MAGTYPE"])
# mcintosh_encode = pd.get_dummies(data_ml["McIntosh"])
# data_ml = pd.concat([data_ml, magtype_encode, mcintosh_encode], axis=1).drop(columns=["MAGTYPE", "McIntosh"])


le1 = preprocessing.LabelEncoder()
le2 = preprocessing.LabelEncoder()
data_ml["MAGTYPE"] = le1.fit_transform(data_ar_evol["MAGTYPE"])
data_ml["McIntosh"] = le2.fit_transform(data_ar_evol["McIntosh"])



# scale the numerical data 
scaled_numerical = preprocessing.MinMaxScaler().fit_transform(data_ml[["AREA", "Longitude_extent", "No_sunspots"]].apply(np.log1p).values)
data_ml = pd.concat([data_ml, pd.DataFrame(scaled_numerical, columns=["AREA_scaled", "Longitude_scaled", "NoSunspots_scaled"])], axis=1)
data_ml.drop(columns=["AREA", "Longitude_extent", "No_sunspots"], inplace=True)



## get features and labels
features = data_ml.drop(columns=["C+"])#, "M+", "X+"])
labels = data_ml["C+"].map(lambda x: 1 if x>0 else 0)

## split testing and training data
X_train, X_test, Y_train, Y_test = train_test_split(features.values, labels.values, test_size=0.3, shuffle=False)


climatology = np.mean(Y_test)

####-------------------–--###
####  APPLY AN ML APPROACH ##

def do_ml(mdl, X_train, X_test, Y_train, Y_test):#, X_train=X_train, X_test=X_test, Y_train=Y_train, Y_test=Y_test):
    mdl.fit(X_train, Y_train)
    prediction = mdl.predict(X_test)

    bss = get_bss(Y_test, mdl.predict_proba(X_test)[:, 1])
    tss = get_tss(Y_test, prediction)
    print("The TSS score is {:f} and the BSS score is {:f}".format(tss, bss))

    plot_roc_and_reliability_curve(mdl, X_test, Y_test)
    plot_feature_importance(mdl, features, top=10)

    return tss, bss, mdl


mdl = LogisticRegression()
tss, bss, trained_mdl = do_ml(mdl, X_train, X_test, Y_train, Y_test)

####-------------------–--###
#### K-fold cross-validation ##

X = features.values
Y = labels.values

mdl = LogisticRegression()

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
        tss.append(get_tss(ytest, prediction))
        bss.append(get_bss(Y_test, mdl.predict_proba(X_test)[:, 1]))
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

    # metrics.plot_roc_curve(mdl, xtest, ytest, drawstyle="steps-mid", ax=ax)


    # if hasattr(mdl, "predict_proba"):
    #     prob_pos = mdl.predict_proba(xtest)[:, 1]
    # else: 
    #     prob_pos = mdl.decision_function(xtest)
    #     prob_pos = \
    #         (prob_pos - prob_pos.min()) / (prob_pos.max() - prob_pos.min())

    # fraction_of_positives, mean_predicted_value = \
    #     calibration_curve(ytest, prob_pos, n_bins=10)

    # ax1.plot([0, 1], [0, 1], "k:", label="Perfectly calibrated")
    # ax1.plot(mean_predicted_value, fraction_of_positives, "s-")
    # ax1.set_ylabel("Fraction of positives")
    # ax1.set_xlabel("Mean predicted value")





def plot_dist_flare():

    flare = data_ml[data_ml["C+"]>0]
    no_flare = data_ml[data_ml["C+"]==0]

    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(12, 4))

    sns.distplot(flare["AREA_scaled"], ax=ax1, label="Flare")
    sns.distplot(no_flare["AREA_scaled"], ax=ax1, label="No flare")

    sns.distplot(flare["Longitude_scaled"], ax=ax2, label="Flare")
    sns.distplot(no_flare["Longitude_scaled"], ax=ax2, label="No flare")

    sns.distplot(flare["NoSunspots_scaled"], ax=ax3, label="Flare")
    sns.distplot(no_flare["NoSunspots_scaled"], ax=ax3, label="No flare")

    for a in (ax1, ax2, ax3):
        a.legend()




