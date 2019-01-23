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
import CoMBo2

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



def cmboost(trainX, trainY):
    cm_boost = CoMBo2.CoMBo2(base_estimator=sklearn.ensemble.RandomForestClassifier(max_depth=15), n_estimators=50)
    cm_boost.fit(trainX, trainY)
    return cm_boost

def main(argv):
   input_file = "Not found"
   output_file = "Not found"
   user = "Not found"
   model = "Not found"
   monitor = "Not found"

   try:
      opts, args = getopt.getopt(argv,"hi:m:u:o:a:",["ifile=","mfile=","ufile=", "ofile=", "afile="])
   except getopt.GetoptError:
      print ('run_models.py -i <inputfile> -m <model name> -u <user> -o <outputfile> -a <monitor>')
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         print ('run_models.py -i <inputfile> -m <model name> -u <user> -o <outputfile> -a <monitor>')
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


   print ('input file name given :', input_file)
   print ('model given :', model)
   print ('user given :', user)
   print ('output file name given :', output_file)
   print ('monitor :', monitor)

   model = model.lower()

   ## cross validation by person (leave-one-out)
   data = pd.DataFrame(sc.get_complete(user,input_file))
   data = get_lags(data, monitor, 1)

   data = data.drop(['Unnamed: 0'], axis=1)
   y_var = 'ordinal' # y_var is posture_coding

   print(data.head())
   data_with_predictions = pd.DataFrame()

   for person in np.unique(data['type']):
      if person == 'W-15' or person == 'W-16' or person == 'W-17' or person == 'W-19' or person == 'W-21' or person == 'W-4' or person == 'W-9':
          print(person)
          ## split training and testing by one person 
          train = data[data['type'] != person].copy(deep=True)
          test = data[data['type'] == person].copy(deep=True)
          train_x = train.drop(['type', 'ordinal'], axis=1)
          train_y = train[y_var]
          train_y.reset_index(drop=True, inplace=True)
          test_x = test.drop(['type', 'ordinal'], axis=1)
          test_y = test[y_var]
          classifier = None
          print("fitting")
          classifier = cmboost(train_x, train_y)
          print("predicting")
          ## use classifier to predict 
          pred = classifier.predict(test_x)
          test['predicted'] = pred
          ## print the accuracy of current person  
          corr = test['predicted'] == test['ordinal']
          print(str(person + " accuracy = "), sum(corr) / len(corr))
          ## append the data set with predictions for that person 
          data_with_predictions = data_with_predictions.append(test)
          data_with_predictions.to_csv(monitor+"_"+str(model)+"_"+input_file, index = False)

   ## train classifier on all the data
   y = data[y_var]
   y.reset_index(drop=True, inplace=True)
   classifier = cmboost(data.drop(['ordinal', 'type'], axis=1), y)
   ## output the classifier and data set with predictionsy
   ## wrist the data to a csv
   data_with_predictions.to_csv(monitor+"_"+str(model)+"_"+input_file, index = False)
   ## print the cross-val score
   correct = data_with_predictions['ordinal'] == data_with_predictions['predicted']
   print("Overall Model Accuracy = ", sum(correct) / len(correct))

if __name__ == "__main__":
    main(sys.argv[1:])