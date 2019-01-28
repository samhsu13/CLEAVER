# CLEAVER
CLassification of Everyday Activities Via Ensemble Recognizers

MakeAGData.R - creates 7 Staudenmayer features for the 7 days of wrist data

Features.R - creates features for observed time in raw Biostamp data

makeSecBySec.R - makes ground truth for all observations

Edit_GroundTruth.ipynb - adds edited posture_coding

make_complete.py - makes complete dataset merging features with sec-by-sec ground truth for Actigraph (adds activity domain type column for each observation)

Merge_ThighChest.ipynb - merges thigh and chest features

make_complete_Biostamp.ipynb - takes merged thigh + chest features and the ground truth and adds activity domain type column for each observation

run_models.py - runs machine learning models based on commandline args

eval_models.py - reports confusion matrices of models based on commandline args

make_core_column.ipynb - notebook for creating columns for hierarchical classification 

AggregateMETs.ipynb - notebook for METs coding scheme using aggregation

CoMBo2.py - confusion matrix boosting class

KL_divergence.ipynb - notebook for calculating KL div

MAEs.ipynb - notebook for calculating MAE and MA-MAE

eval_staudenmeyer_acc.ipynb - notebook for evaluating staudenmeyer RF accuracy on our Actigraph wrist data





