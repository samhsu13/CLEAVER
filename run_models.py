## Authors: Yash Mehra, Gus Moir, Andrew Rose, Hans Schumann
## Version: June 2018
##
## This file will be run from command line to create a user-specified model
##

# preliminary things to get the script.py file
import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,currentdir)

# import the necessary files
import getopt
import pandas as pd
import numpy as np
import json
import sklearn
import sklearn.ensemble
import sklearn.neural_network

import sklearn.neighbors
import pickle
import script as sc
import samboost
import CoMBo

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


# helper_functions
def save_pkl(classifier, filename):
    with open(filename, 'wb') as f:
        pickle.dump(classifier, f)
        print("Classifier saved as " + filename)

## functions for the various models -- these take in the training set
## and return the fitted model
def svm(trainX, trainY):
    clf = sklearn.svm.LinearSVC(max_iter = 100)
    print("clf made")
    clf.fit(trainX, trainY)
    print("fit complete")
    return clf

def neural_net(trainX, trainY):
    n_net = sklearn.neural_network.MLPClassifier(solver='lbfgs', alpha=1e-5, hidden_layer_sizes=(2000, 1000),
                                                 random_state=1, verbose=True)
    n_net.fit(trainX, trainY)
    return n_net

def random_forest(trainX, trainY):
   rf = sklearn.ensemble.RandomForestClassifier(max_depth=5, random_state=0)
   rf.fit(trainX, trainY)
   return rf

def knn(trainX, trainY):
    knn = sklearn.neighbors.KNeighborsClassifier(n_neighbors=100)
    knn.fit(trainX, trainY)
    return knn

def gradient_boost(trainX, trainY):
    grad_boost = sklearn.ensemble.GradientBoostingClassifier(n_estimators=100, max_depth=7)
    grad_boost.fit(trainX, trainY)
    return grad_boost

def adaboost(trainX, trainY):
    aboost = sklearn.ensemble.AdaBoostClassifier(algorithm='SAMME', base_estimator=sklearn.ensemble.RandomForestClassifier(max_depth=15), n_estimators=100)
    aboost.fit(trainX, trainY)
    return aboost

def sam_boost(trainX, trainY):
    sam_boost = samboost.SamBoost(base_estimator=sklearn.ensemble.RandomForestClassifier(max_depth=15), n_estimators=100)
    sam_boost.fit(trainX, trainY)
    return sam_boost

def cmboost(trainX, trainY):
    cm_boost = CoMBo.CoMBo(base_estimator=sklearn.ensemble.RandomForestClassifier(max_depth=15), n_estimators=50)
    cm_boost.fit(trainX, trainY)
    return cm_boost

def main(argv):
   input_file = "Not found"
   output_file = "Not found"
   user = "Not found"
   model = "Not found"
   transition = "Not found"
   coding_scheme = "Not found"
   monitor = "Not found"

   try:
      opts, args = getopt.getopt(argv,"hi:m:u:o:a:c:t:",["ifile=","mfile=","ufile=", "ofile=", "afile=", "cfile=", "tfile="])
   except getopt.GetoptError:
      print ('run_models.py -i <inputfile> -m <model name> -u <user> -o <outputfile> -a <monitor> -c <codingscheme> -t <transitionflag>')
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         print ('run_models.py -i <inputfile> -m <model name> -u <user> -o <outputfile> -a <monitor> -c <codingscheme> -t <transitionflag>')
         sys.exit()
      elif opt in ("-i", "--ifile"):
         input_file = arg
      elif opt in ("-m", "--kvalue"):
         model = arg
      elif opt in ("-u", "--kvalue"):
         user = arg
      elif opt in ("-o", "--kvalue"):
         output_file = arg
      elif opt in ("-a", "--kvalue"):
          monitor = arg
      elif opt in ("-c", "--kvalue"):
          coding_scheme = arg
      elif opt in ("-t", "--kvalue"):
          transition = arg


   print ('input file name given :', input_file)
   print ('model given :', model)
   print ('user given :', user)
   print ('output file name given :', output_file)
   print ('coding scheme :', coding_scheme)
   print ('monitor :', monitor)

   model = model.lower()

   ## cross validation by person (leave-one-out)
   data = pd.DataFrame(sc.get_complete(user,input_file))
   data = get_lags(data, monitor, 1)

   if transition == "clean":
      data = data[data['transition'] != 1]

   data = data.drop(['Unnamed: 0', 'Unnamed: 0.1', 'Unnamed: 0.1.1', 'start.time', 'primary_behavior', 'primary_posture',
                     'primary_upperbody', 'primary_intensity', 'secondary_behavior', 'secondary_posture',
                     'secondary_upperbody', 'secondary_intensity', 'num_postures', 'transition', 'actual_time'], axis=1)

   if (monitor == "biostamp_thigh_chest7") or (monitor == "biostamp_thigh7") or (monitor == "biostamp_chest7"):
       data = data.drop(['thigh.min.x', 'thigh.min.y', 'thigh.min.z', 'thigh.max.x', 'thigh.max.y',
                         'thigh.max.z', 'thigh.mean.x', 'thigh.mean.y', 'thigh.mean.z', 'thigh.sd.x', 'thigh.sd.y',
                         'thigh.sd.z', 'thigh.mean.xy', 'thigh.mean.yz', 'thigh.mean.xz', 'thigh.mean.xyz',
                         'chest.min.x', 'chest.min.y', 'chest.min.z', 'chest.max.x', 'chest.max.y',
                         'chest.max.z', 'chest.mean.x', 'chest.mean.y', 'chest.mean.z', 'chest.sd.x', 'chest.sd.y',
                         'chest.sd.z', 'chest.mean.xy', 'chest.mean.yz', 'chest.mean.xz', 'chest.mean.xyz'], axis=1)
   if (monitor == "biostamp_thigh7"):
       data = data.drop(['chest.mean.vm', 'chest.sd.vm', 'chest.mean.ang', 'chest.sd.ang',
                         'chest.p625', 'chest.dfreq', 'chest.ratio.df'], axis=1)
   if (monitor == "biostamp_chest7"):
       data = data.drop(['thigh.mean.vm', 'thigh.sd.vm', 'thigh.mean.ang', 'thigh.sd.ang', 'thigh.p625', 'thigh.dfreq',
                         'thigh.ratio.df'], axis=1)
   if (monitor == "actigraph_wrist"):
       data = data.drop(['min.x', 'min.y', 'min.z', 'max.x', 'max.y',
                         'max.z', 'mean.x', 'mean.y', 'mean.z', 'sd.x', 'sd.y',
                         'sd.z', 'mean.xy', 'mean.yz', 'mean.xz', 'mean.xyz'
                         ], axis=1)


   if coding_scheme == "sedentary":
       data = data.drop(['posture_coding', 'posture_coding_ordinal', 'MET_coding', 'Ellis_coding'], axis=1) # don't need posture_coding
       y_var = 'coding' # y_var is coding
   elif coding_scheme == "full":
       data = data.drop(['coding', 'posture_coding_ordinal', 'MET_coding', 'general_coding'], axis=1) # don't need coding
       y_var = 'posture_coding' # y_var is posture_coding
   elif coding_scheme == "ordinal":
       data = data.drop(['posture_coding', 'coding', 'MET_coding', 'general_coding'], axis=1)
       y_var = 'posture_coding_ordinal'
   elif coding_scheme == "MET":
       data = data.drop(['posture_coding', 'coding', 'posture_coding_ordinal', 'general_coding'], axis=1)
       y_var = 'MET_coding'
   elif coding_scheme == "Ellis":
       data = data.drop(['posture_coding', 'coding', 'posture_coding_ordinal', 'MET_coding'], axis=1)
       y_var = 'general_coding'

   print(data.head())
   data_with_predictions = pd.DataFrame()

   for person in np.unique(data['type']):
       print(person)
       ## split training and testing by one person
       train = data[data['type'] != person].copy(deep=True)
       test = data[data['type'] == person].copy(deep=True)

       #print(train.head())
       #print(test.head())

       ## subset x and y variables
       if coding_scheme == "sedentary":
           train_x = train.drop(['type', 'coding'], axis=1)
       elif coding_scheme == "full":
           train_x = train.drop(['type', 'posture_coding'], axis=1)
       elif coding_scheme == "ordinal":
           train_x = train.drop(['type', 'posture_coding_ordinal'], axis=1)
       elif coding_scheme == "MET":
           train_x = train.drop(['type', 'MET_coding'], axis=1)
       elif coding_scheme == "Ellis":
           train_x = train.drop(['type', 'general_coding'], axis=1)

       train_y = train[y_var]
       train_y.reset_index(drop=True, inplace=True)

       if coding_scheme == "sedentary":
           test_x = test.drop(['type', 'coding'], axis=1)
       elif coding_scheme == "full":
           test_x = test.drop(['type', 'posture_coding'], axis=1)
       elif coding_scheme == "ordinal":
           test_x = test.drop(['type', 'posture_coding_ordinal'], axis=1)
       elif coding_scheme == "MET":
           test_x = test.drop(['type', 'MET_coding'], axis=1)
       elif coding_scheme == "Ellis":
           test_x = test.drop(['type', 'general_coding'], axis=1)

       test_y = test[y_var]

       #print(train_x.head())

       classifier = None
       print("here")

       if model == "gradient_boosting":
           classifier = gradient_boost(train_x, train_y)
       elif model == "svm":
           print("inside")
           classifier = svm(train_x, train_y)
           print("Finished SVM class")
       elif model == "knn":
           classifier = knn(train_x, train_y)
       elif model == "rf":
           classifier = random_forest(train_x, train_y)
       elif model == "neural_network":
           classifier = neural_net(train_x, train_y)
       elif model == "adaboost":
           classifier = adaboost(train_x, train_y)
       elif model == "samboost":
           classifier = sam_boost(train_x, train_y)
       elif model == "combo":
           classifier = cmboost(train_x, train_y)
       else:
           print("why?")
           exit(1)
       print("out of condtional")
       ## use classifier to predict
       pred = classifier.predict(test_x)
       test['predicted'] = pred
       print("outside")
       ## print the accuracy of current person

       if coding_scheme == "sedentary":
           corr = test['predicted'] == test['coding']
       elif coding_scheme == "full":
           corr = test['predicted'] == test['posture_coding']
       elif coding_scheme == "ordinal":
           corr = test['predicted'] == test['posture_coding_ordinal']
       elif coding_scheme == "MET":
           corr = test['predicted'] == test['MET_coding']
       elif coding_scheme == "Ellis":
           corr = test['predicted'] == test['general_coding']

       print(str(person + " accuracy = "), sum(corr) / len(corr))

       ## append the data set with predictions for that person
       data_with_predictions = data_with_predictions.append(test)
       print("bottom")

   ## train classifier on all the data
   if coding_scheme == "sedentary":
       if model == "gradient_boosting":
           classifier = gradient_boost(data.drop(['coding', 'type'], axis=1), data[y_var])
       elif model == "svm":
           print("inside")
           classifier = svm(data.drop(['coding', 'type'], axis=1), data[y_var])
           print("Finished SVM class")
       elif model == "knn":
           classifier = knn(data.drop(['coding', 'type'], axis=1), data[y_var])
       elif model == "rf":
           classifier = random_forest(data.drop(['coding', 'type'], axis=1), data[y_var])
       elif model == "neural_network":
           classifier = neural_net(data.drop(['coding', 'type'], axis=1), data[y_var])
       elif model == "adaboost":
           classifier = adaboost(data.drop(['coding', 'type'], axis=1), data[y_var])
       elif model == "samboost":
           classifier = adaboost(data.drop(['coding', 'type'], axis=1), data[y_var])
   elif coding_scheme == "full":
       if model == "gradient_boosting":
           classifier = gradient_boost(data.drop(['posture_coding', 'type'], axis=1), data[y_var])
       elif model == "svm":
           print("inside")
           classifier = svm(data.drop(['posture_coding', 'type'], axis=1), data[y_var])
           print("Finished SVM class")
       elif model == "knn":
           classifier = knn(data.drop(['posture_coding', 'type'], axis=1), data[y_var])
       elif model == "rf":
           classifier = random_forest(data.drop(['posture_coding', 'type'], axis=1), data[y_var])
       elif model == "neural_network":
           classifier = neural_net(data.drop(['posture_coding', 'type'], axis=1), data[y_var])
       elif model == "adaboost":
           classifier = adaboost(data.drop(['posture_coding', 'type'], axis=1), data[y_var])
       elif model == "samboost":
           classifier = adaboost(data.drop(['posture_coding', 'type'], axis=1), data[y_var])
       elif model == "combo":
           classifier = adaboost(data.drop(['posture_coding', 'type'], axis=1), data[y_var])
   elif coding_scheme == "ordinal":
       if model == "gradient_boosting":
           classifier = gradient_boost(data.drop(['posture_coding_ordinal', 'type'], axis=1), data[y_var])
       elif model == "svm":
           print("inside")
           classifier = svm(data.drop(['posture_coding_ordinal', 'type'], axis=1), data[y_var])
           print("Finished SVM class")
       elif model == "knn":
           classifier = knn(data.drop(['posture_coding_ordinal', 'type'], axis=1), data[y_var])
       elif model == "rf":
           classifier = random_forest(data.drop(['posture_coding_ordinal', 'type'], axis=1), data[y_var])
       elif model == "neural_network":
           classifier = neural_net(data.drop(['posture_coding_ordinal', 'type'], axis=1), data[y_var])
       elif model == "adaboost":
           classifier = adaboost(data.drop(['posture_coding_ordinal', 'type'], axis=1), data[y_var])
       elif model == "samboost":
           classifier = adaboost(data.drop(['posture_coding_ordinal', 'type'], axis=1), data[y_var])
   elif coding_scheme == "MET":
       if model == "gradient_boosting":
           classifier = gradient_boost(data.drop(['MET_coding', 'type'], axis=1), data[y_var])
       elif model == "svm":
           print("inside")
           classifier = svm(data.drop(['MET_coding', 'type'], axis=1), data[y_var])
           print("Finished SVM class")
       elif model == "knn":
           classifier = knn(data.drop(['MET_coding', 'type'], axis=1), data[y_var])
       elif model == "rf":
           classifier = random_forest(data.drop(['MET_coding', 'type'], axis=1), data[y_var])
       elif model == "neural_network":
           classifier = neural_net(data.drop(['MET_coding', 'type'], axis=1), data[y_var])
       elif model == "adaboost":
           classifier = adaboost(data.drop(['MET_coding', 'type'], axis=1), data[y_var])
       elif model == "samboost":
           classifier = adaboost(data.drop(['MET_coding', 'type'], axis=1), data[y_var])
   elif coding_scheme == "Ellis":
       if model == "gradient_boosting":
           classifier = gradient_boost(data.drop(['general_coding', 'type'], axis=1), data[y_var])
       elif model == "svm":
           print("inside")
           classifier = svm(data.drop(['general_coding', 'type'], axis=1), data[y_var])
           print("Finished SVM class")
       elif model == "knn":
           classifier = knn(data.drop(['general_coding', 'type'], axis=1), data[y_var])
       elif model == "rf":
           classifier = random_forest(data.drop(['general_coding', 'type'], axis=1), data[y_var])
       elif model == "neural_network":
           classifier = neural_net(data.drop(['general_coding', 'type'], axis=1), data[y_var])
       elif model == "adaboost":
           classifier = adaboost(data.drop(['general_coding', 'type'], axis=1), data[y_var])
       elif model == "samboost":
           classifier = adaboost(data.drop(['general_coding', 'type'], axis=1), data[y_var])
   else:
        print("why?")
        exit(1)

   ## output the classifer and data_set with predictions
   save_pkl(classifier, output_file)

   ## write the data to a csv
   data_with_predictions.to_csv(monitor+"_"+str(model)+"100_"+coding_scheme+"_"+transition+"_"+input_file,index = False)
   ## print the cross-val score

   if coding_scheme == "sedentary":
       correct = data_with_predictions['coding'] == data_with_predictions['predicted']
   elif coding_scheme == "full":
       correct = data_with_predictions['posture_coding'] == data_with_predictions['predicted']
   elif coding_scheme == "ordinal":
       correct = data_with_predictions['posture_coding_ordinal'] == data_with_predictions['predicted']
   elif coding_scheme == "MET":
       correct = data_with_predictions['MET_coding'] == data_with_predictions['predicted']
   elif coding_scheme == "Ellis":
       correct = data_with_predictions['general_coding'] == data_with_predictions['predicted']

   print ("Overall Model Accuracy = ",sum(correct) / len(correct))

if __name__ == "__main__":
   main(sys.argv[1:])

