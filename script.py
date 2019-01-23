import pandas as pd
import json
import sklearn.svm as svm
from sklearn.linear_model import Lasso, LassoCV
from sklearn.feature_selection import SelectFromModel
from sklearn import preprocessing
import numpy as np
#from sklearn.neural_network import MLPClassifier

## This function will open a JSON file with each of our team members directory info
## Requires person name as strong and filename as string
## Returns that persons filepath
def load_Data(user, filename):
   data = json.load(open('/Users/samhsu/Documents/THESIS/Code/KineseItUp/Capstone/dir.json'))
   return (data[user] + filename)

## Takes the raw dataframe, it's groundtruth, starttime and endtime
## Returns a single DF with the snipet of data that matches the timeStart and timeEnd
## Along with the ground truth encodings for each second
def useable_Data(data, gt, timeStart, timeEnd):
    data['start.time'] = pd.to_datetime(data['start.time'])
    observedData = data[(data['start.time'] >= timeStart) & (data['start.time'] <= timeEnd)]
    observedData['index'] = range(len(observedData))
    gt['index'] = gt['time']
    observedData = pd.merge(observedData,gt[['index', 'coding', 'primary_behavior','primary_posture', 'primary_upperbody', 'primary_intensity',
                                             'secondary_behavior', 'secondary_posture', 'secondary_upperbody', 'secondary_intensity',
                                             'num_postures', 'transition', 'actual_time', 'posture_coding', 'type']])
    observedData.sort_index(inplace=True)
    observedData = observedData[observedData['primary_posture'] != 'private/not coded']
    return observedData

## Takes a DF and an integer value for the number of lag variables wanted.
## Returns a similar DF with extra columns for the number of lags you requested.
def get_lags(data, monitor, lags):
    if monitor == "actigraph_wrist":
        prev_data = data[['mean.vm', 'sd.vm', 'mean.ang', 'sd.ang', 'p625', 'dfreq', 'ratio.df']]
    elif monitor == "actigraph_wrist23":
        prev_data = data[['mean.vm', 'sd.vm', 'mean.ang', 'sd.ang', 'p625', 'dfreq',
                          'ratio.df', 'min.x', 'min.y', 'min.z', 'max.x', 'max.y',
                          'max.z', 'mean.x', 'mean.y', 'mean.z', 'sd.x', 'sd.y',
                          'sd.z', 'mean.xy', 'mean.yz', 'mean.xz', 'mean.xyz']]
    elif monitor == "biostamp_thigh":
        prev_data = data[['thigh.mean.vm', 'thigh.sd.vm', 'thigh.mean.ang', 'thigh.sd.ang', 'thigh.p625', 'thigh.dfreq',
                          'thigh.ratio.df', 'thigh.min.x', 'thigh.min.y', 'thigh.min.z', 'thigh.max.x', 'thigh.max.y',
                          'thigh.max.z', 'thigh.mean.x', 'thigh.mean.y', 'thigh.mean.z', 'thigh.sd.x', 'thigh.sd.y',
                          'thigh.sd.z', 'thigh.mean.xy', 'thigh.mean.yz', 'thigh.mean.xz', 'thigh.mean.xyz']]
    elif monitor == "biostamp_chest":
        prev_data = data[['chest.mean.vm', 'chest.sd.vm', 'chest.mean.ang', 'chest.sd.ang', 'chest.p625', 'chest.dfreq',
                          'chest.ratio.df', 'chest.min.x', 'chest.min.y', 'chest.min.z', 'chest.max.x', 'chest.max.y',
                          'chest.max.z', 'chest.mean.x', 'chest.mean.y', 'chest.mean.z', 'chest.sd.x', 'chest.sd.y',
                          'chest.sd.z', 'chest.mean.xy', 'chest.mean.yz', 'chest.mean.xz', 'chest.mean.xyz']]
    elif monitor == "biostamp_thigh_chest":
        prev_data = data[['thigh.mean.vm', 'thigh.sd.vm', 'thigh.mean.ang', 'thigh.sd.ang', 'thigh.p625','thigh.dfreq',
                      'thigh.ratio.df', 'thigh.min.x', 'thigh.min.y', 'thigh.min.z', 'thigh.max.x', 'thigh.max.y',
                      'thigh.max.z', 'thigh.mean.x', 'thigh.mean.y', 'thigh.mean.z', 'thigh.sd.x', 'thigh.sd.y',
                      'thigh.sd.z', 'thigh.mean.xy', 'thigh.mean.yz', 'thigh.mean.xz', 'thigh.mean.xyz',
                      'chest.mean.vm', 'chest.sd.vm', 'chest.mean.ang', 'chest.sd.ang', 'chest.p625', 'chest.dfreq',
                      'chest.ratio.df', 'chest.min.x', 'chest.min.y', 'chest.min.z', 'chest.max.x', 'chest.max.y',
                      'chest.max.z', 'chest.mean.x', 'chest.mean.y', 'chest.mean.z', 'chest.sd.x',  'chest.sd.y',
                      'chest.sd.z', 'chest.mean.xy', 'chest.mean.yz', 'chest.mean.xz', 'chest.mean.xyz']]
    elif monitor == "biostamp_thigh_chest7":
        prev_data = data[['thigh.mean.vm', 'thigh.sd.vm', 'thigh.mean.ang', 'thigh.sd.ang', 'thigh.p625', 'thigh.dfreq',
                          'thigh.ratio.df', 'chest.mean.vm', 'chest.sd.vm', 'chest.mean.ang', 'chest.sd.ang', 'chest.p625',
                          'chest.dfreq', 'chest.ratio.df']]
    elif monitor == "biostamp_thigh7":
        prev_data = data[['thigh.mean.vm', 'thigh.sd.vm', 'thigh.mean.ang', 'thigh.sd.ang', 'thigh.p625', 'thigh.dfreq',
                          'thigh.ratio.df']]
    elif monitor == "biostamp_chest7":
        prev_data = data[['chest.mean.vm', 'chest.sd.vm', 'chest.mean.ang', 'chest.sd.ang',
                          'chest.p625', 'chest.dfreq', 'chest.ratio.df']]

    for i in range(lags):
        copy = prev_data.copy(deep=True)
        copy.loc[-1] = copy.loc[0]
        copy.index = copy.index + 1  # shifting index
        copy.sort_index(inplace=True)
        copy.columns = 'last.' + str(i+1) + "." + copy.columns
        prev_data = copy
        data = pd.concat([data, copy], axis = 1)
        data = data.drop(data.index[len(data)-1])
    return data

## Simple Feature selection function.
## Returns list of selected features.
def select_features_from_lasso(X, y, alpha):
    # fit lasso model and pass to select from model
    lasso = LassoCV().fit(X, y)
    model = SelectFromModel(lasso, prefit=True)

    # new features
    X_new = model.transform(X)
    return X.columns[model.get_support()]

## Simple Function that loads a JSON file struct.json
## returns JSON structure.
def load_struct():
    data = json.load(open('/Users/samhsu/Documents/THESIS/Code/KineseItUp/Capstone/struct.json'))
    return data

## Loads a JSON file. This file is the same as struct.json,
## but contains information for all of the videos
def load_full_struct():
    data = json.load(open('fullStruct.json'))
    return data

## This function is a mid step function using the struct.json file.
## Gets the info from that file. Subject is an integer. See get_all_subjects for more info.
## Returns a DF with that persons data, gt, gt2 (if there is one)
def get_observed_data_for_subject(user, subject, files):
    data = pd.read_csv(load_Data(user, files["AG"]), header=0)
    gt1 = pd.read_csv(load_Data(user, files["GT1"]), header=0)
    type1 = files["Type1"]
    start1 = files["StartTime1"]
    end1 = files["EndTime1"]
    observedData = pd.DataFrame(useable_Data(data, gt1, start1, end1))
    #observedData['type'] = type1 + '-' + str(subject)

    if("GT2" in files):
        gt2 = pd.read_csv(load_Data(user, files["GT2"]), header=0)
        type2 = files["Type2"]
        start2 = files["StartTime2"]
        end2 = files["EndTime2"]
        observedData1 = pd.DataFrame(useable_Data(data, gt2, start2, end2))
        #observedData1['type'] = type2 + '-' + str(subject)
        observedData = pd.concat([observedData, observedData1])

    if ("GT3" in files):
        gt3 = pd.read_csv(load_Data(user, files["GT3"]), header=0)
        type3 = files["Type3"]
        start3 = files["StartTime3"]
        end3 = files["EndTime3"]
        observedData2 = pd.DataFrame(useable_Data(data, gt3, start3, end3))
        #observedData2['type'] = type3 + '-' + str(subject)
        observedData = pd.concat([observedData, observedData2])

    return observedData

def get_all_subjects(user, files):
    observedData = pd.DataFrame()

    for i in files:
            observedData1 = get_observed_data_for_subject(user, i, files[str(i)])
            observedData = pd.concat([observedData, observedData1])

    return observedData

def write_observedData(observedData, user, filename):
    data = json.load(open('dir.json'))
    observedData.to_csv(data[user] + filename)

def get_complete(user,filename):
     data = pd.read_csv(load_Data(user, filename))
     return data

def write_staudenmeyer_observedData(observedData, user):
    data = json.load(open('dir.json'))
    observedData.to_csv(data[user]+'staudenmeyer_complete.csv')

## Reads in the dataset made by update_staudenmeyer_complete
def get_staudenmeyer_complete(user):
     data = pd.read_csv(load_Data(user, 'staudenmeyer_complete.csv'))
     return data

def update_complete(user, filename):
    files = load_struct()
    observedData = get_all_subjects(user, files)
    write_observedData(observedData, user, filename)

## Builds a dataset containing the predictions
## made by the Staudenmeyer random forest method
def update_staudenmeyer_complete(user):
    files = load_full_struct()
    observedData = get_all_subjects(user, files)
    write_staudenmeyer_observedData(observedData, user)

def get_test_train(data, lag):
    ## shuffle the data (for training and testing)
    #data = data.drop(['Unnamed: 0', 'Unnamed: 0.1', 'start.time', 'index', 'type'], axis = 1)
    #data = data.drop(['Unnamed: 0', 'Unnamed: 0.1', 'start.time', 'index', 'primary_behavior', 'primary_posture',
     #                 'primary_upperbody', 'primary_intensity', 'secondary_behavior', 'secondary_posture',
      #                'secondary_upperbody', 'secondary_intensity', 'num_postures', 'transition', 'actual_time'], axis = 1)
    observedData = data.sample(frac = 1)

    n = int(0.75 * len(observedData))

    train = observedData[:n]
    test = observedData[n:]
    ## this might be an issue since there is ordinality and that makes things weird.  The later parts of this trial
    ## were more likely to be sedentary.
    trainY = train['activity']
    testY = test['activity']

    if (lag == 0):
        trainX = train[['mean.vm','sd.vm','mean.ang','sd.ang','p625','dfreq','ratio.df']]
        testX = test[['mean.vm','sd.vm','mean.ang','sd.ang','p625','dfreq','ratio.df']]

    if (lag == 1):
        trainX = train[train.columns]
        testX = test[train.columns]
        trainX = trainX.drop('coding', axis = 1)
        testX = testX.drop('coding', axis = 1)
        trainX = trainX.drop('activity', axis = 1)
        testX = testX.drop('activity', axis = 1)


    trainX = preprocessing.scale(trainX)
    testX = preprocessing.scale(testX)

    return trainX, trainY, testX, testY