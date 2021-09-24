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




