## Authors: Yash Mehra, Gus Moir, Andrew Rose, Hans Schumann
## Version: June 2018
##
## This file will be run from command line to evaluate the generated models
##

# preliminary things to get the script.py file
import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,currentdir)

# import the necessary files
import getopt
import sys
import pandas as pd
import numpy as np
from sklearn.metrics import confusion_matrix
from sklearn.metrics import mean_absolute_error
import pickle


def label_posture (row):
    if row['posture_coding'] == 'SB- lying' :
        return 0
    if row['posture_coding'] == 'SB-sitting':
        return 1
    if row['posture_coding'] == 'LA- stand' :
        return 2
    if row['posture_coding'] == 'LA- stand and move light':
        return 3
    if row['posture_coding']  == 'LA- stand and move moderate':
        return 4
    if row['posture_coding'] == 'LA- stand and move vigorous':
        return 5
    if row['posture_coding'] == 'WA- walk light':
        return 6
    if row['posture_coding'] == 'WA- walk moderate':
        return 7
    if row['posture_coding'] == 'WA- walk vigorous':
        return 8
    if row['posture_coding'] == 'WA- ascend stairs':
        return 9
    if row['posture_coding'] == 'WA- descend stairs':
        return 10
    if row['posture_coding'] == 'WA- running':
        return 11
    if row['posture_coding'] == 'SP- other sport movement':
        return 12
    if row['posture_coding'] == 'SP- bike':
        return 13
    return -1


def label_predicted (row):
    if row['predicted'] == 'SB- lying' :
        return 0
    if row['predicted'] == 'SB-sitting':
        return 1
    if row['predicted'] == 'LA- stand' :
        return 2
    if row['predicted'] == 'LA- stand and move light':
        return 3
    if row['predicted']  == 'LA- stand and move moderate':
        return 4
    if row['predicted'] == 'LA- stand and move vigorous':
        return 5
    if row['predicted'] == 'WA- walk light':
        return 6
    if row['predicted'] == 'WA- walk moderate':
        return 7
    if row['predicted'] == 'WA- walk vigorous':
        return 8
    if row['predicted'] == 'WA- ascend stairs':
        return 9
    if row['predicted'] == 'WA- descend stairs':
        return 10
    if row['predicted'] == 'WA- running':
        return 11
    if row['predicted'] == 'SP- other sport movement':
        return 12
    if row['predicted'] == 'SP- bike':
        return 13
    return -1


def ma_mae(y_true, y_pred):
    y_labels = sorted(list(set(y_true)))
    maes = np.zeros([len(y_labels)])
    mae_sum = 0.0

    for label in y_labels:
        y = y_true[y_true['posture_coding_ordinal'] == label]
        pred = y_pred[y_pred['predicted_ordinal'] == label]
        mae = mean_absolute_error(y, pred)
        max_error = max(len(y_labels) - label, label)
        mae_sum += mae / label

    return 1 - mae_sum / len(y_labels)


def CM2DF(CM, labels):
    df = pd.DataFrame()
    # rows
    for i, row_label in enumerate(labels):
        rowdata={}
        # columns
        for j, col_label in enumerate(labels):
            rowdata[col_label]=CM[i,j]
        df = df.append(pd.DataFrame.from_dict({row_label:rowdata}, orient='index'))
    return df[labels]


def print_confusion_matrix(data, labels, coding):
    if coding == 'MET':
        CM = confusion_matrix(data['MET_coding'], data['predicted'], labels=labels)
    elif coding == 'Ellis':
        CM = confusion_matrix(data['general_coding'],data['predicted'], labels=labels)
    elif coding == 'ordinal':
        CM = confusion_matrix(data['posture_coding_ordinal'], data['predicted'], labels=labels)
    elif coding == 'core':
        CM = confusion_matrix(data['posture1'], data['predicted'], labels=labels)
    else:
        CM = confusion_matrix(data['posture_coding'], data['predicted'], labels=labels)

    print (CM)
    return CM


def main(argv):
    input_file = "Not found"
    coding = "Not found"
    model = "Not found"
    output_file = "Not found"

    try:
        opts, args = getopt.getopt(argv, "hi:c:m:u:o:", ["ifile=", "cfile=", "mfile=", "ufile=", "ofile="])
    except getopt.GetoptError:
        print('run_models.py -i <inputfile> -c <coding_scheme> -m <model file> -u <user> -o <outputfile>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('eval_models.py -i <inputfile> -c <coding_scheme> -m <model file> -u <user> -o <outputfile>')
            sys.exit()
        elif opt in ("-i", "--ifile"):
            input_file = arg
        elif opt in ("-c", "--coding"):
            coding = arg
        elif opt in ("-m", "--model"):
            model = arg
        elif opt in ("-u", "--user"):
            user = arg
        elif opt in ("-o", "--output"):
            output_file = arg

    print('input file name given :', input_file)
    print('coding scheme :', coding)
    print('user given :', user)
    print('model file : ', model)
    print('output file name given :', output_file)

    data = pd.read_csv(input_file)

    if coding == 'full':
        labels = ['SB- lying',
                  'SB-sitting',
                  'LA- stand',
                  'LA- stand and move light',
                  'LA- stand and move moderate',
                  'LA- stand and move vigorous',
                  'WA- walk light',
                  'WA- walk moderate',
                  'WA- walk vigorous',
                  'WA- ascend stairs',
                  'WA- descend stairs',
                  'WA- running',
                  'SP- other sport movement',
                  'SP- bike']
    elif coding == 'MET':
        labels = ['sedentary', 'light', 'moderate', 'vigorous']
    elif coding == 'Ellis':
        labels = ['sit', 'standing', 'walk/run', 'riding in vehicle', 'other']
    elif coding == 'core':
        labels = ['SB- lying', 'SB-sitting', 'LA- stand', 'WA- walk', 'SP- other sport movement', 'SP- bike']
    elif coding == 'ordinal':
        labels =[0, 1, 2, 3, 4, 5, 6, 7,8, 9, 10, 11, 12, 13]

    CM = print_confusion_matrix(data, labels, coding)
    if coding == 'MET':
        print("Accuracy = ", sum(data['MET_coding'] == data['predicted']) / len(data['MET_coding']))
    elif coding == 'Ellis':
        print("Accuracy = ", sum(data['general_coding'] == data['predicted']) / len(data['general_coding']))
    elif coding == 'ordinal':
        print ("Accuracy = ",sum(data['posture_coding_ordinal'] == data['predicted']) / len(data['posture_coding_ordinal']))
    else:
        print ("Accuracy = ",sum(data['posture_coding'] == data['predicted']) / len(data['posture_coding']))

    df = CM2DF(CM, labels)
    df.to_csv(output_file + "_CM.csv")

    #with open(model, 'rb') as m:
        #data = pickle.load(m)
        #print(data)

if __name__ == "__main__":
    main(sys.argv[1:])
