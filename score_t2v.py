import io
import os
import json
import zipfile
import argparse

import sys
from glob import glob
from scripts.constant import *


def get_nomalized_score(upload_data):
    # get the normalize score
    normalized_score = {}
    for key in TASK_INFO:
        min_val = NORMALIZE_DIC[key]['Min']
        max_val = NORMALIZE_DIC[key]['Max']
        normalized_score[key] = (upload_data[key] - min_val) / (max_val - min_val)
        normalized_score[key] = normalized_score[key] * DIM_WEIGHT[key]
    return normalized_score

def get_quality_score(normalized_score):
    quality_score = []
    for key in QUALITY_LIST:
        quality_score.append(normalized_score[key])
    quality_score = sum(quality_score)/sum([DIM_WEIGHT[i] for i in QUALITY_LIST])
    return quality_score

def get_semantic_score(normalized_score):
    semantic_score = []
    for key in SEMANTIC_LIST:
        semantic_score.append(normalized_score[key])
    semantic_score  = sum(semantic_score)/sum([DIM_WEIGHT[i] for i in SEMANTIC_LIST ])
    return semantic_score

def get_final_score(quality_score,semantic_score):
    return (quality_score * QUALITY_WEIGHT + semantic_score * SEMANTIC_WEIGHT) / (QUALITY_WEIGHT + SEMANTIC_WEIGHT)

if __name__=="__main__":
    parser = argparse.ArgumentParser(description='Load submission file')
    parser.add_argument('--folder', type=str, required=True, help='Name of the zip file', default='evaluation_results.zip')
    args = parser.parse_args()
    json_files = glob(os.path.join(args.folder, '*_eval_results.json'))
    score_dict = {}
    for json_file in json_files:
        data = json.load(open(json_file))
        for key in data:
            score_dict[key.replace('_',' ')] = data[key][0]
    
    upload_dict = score_dict
    print(f"your submission info: \n{upload_dict} \n")
    normalized_score = get_nomalized_score(upload_dict)
    quality_score = get_quality_score(normalized_score)
    semantic_score = get_semantic_score(normalized_score)
    final_score = get_final_score(quality_score, semantic_score)
    print('+------------------|------------------+')
    print(f'|     quality score|{quality_score}|')
    print(f'|    semantic score|{semantic_score}|')
    print(f'|       total score|{final_score}|')
    print('+------------------|------------------+')
