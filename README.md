# CLEAVER
CLassification of Everyday Activities Via Ensemble Recognizers

MakeAGData.R - creates 7 Staudenmayer features for the 7 days of wrist data

Features.R - creates features for observed time in raw Biostamp data

makeSecBySec.R - makes ground truth for all observations

editGroundTruth - adds edited posture_coding

make_complete.py - makes complete dataset merging features with sec-by-sec ground truth for Actigraph (adds activity domain type column for each observation)

Merge_ThighChest - merges thigh and chest features

make_complete_Biostamp - takes merged thigh + chest features and the ground truth and adds activity domain type column for each observation

run_models.py - runs machine learning models

