#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File         :   senti_analysis.py
@Desc         :   进行情感分析
'''

from work_flow.onDict import ModelOnDict

def main(window, opinion):
    # 通过 window 配置参数

    dictname = window.dict_name
    if(dictname == 'SentiWordNet'):
        dictname = 'dict_swn'

    model = ModelOnDict(dictname=dictname, opinion=opinion)
    
    return model.transform(consider_endmarks=window.option_endmark.isChecked(),
                            union_morphology=window.option_morphology.isChecked(),
                            remove_stops=not window.option_keep_stop_words.isChecked(),
                            consider_negative_word=window.option_negative_reversal.isChecked(),
                            partial_sent=window.option_partial_opinion.isChecked())



