#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File         :   analysis_show.py
@Desc         :   show analysis result
'''


from PyQt5.QtGui import QPixmap
from view import init_view

def show_polarity(window, polarity):
    if(polarity == 1):
        # window.opinion_senti_label.setStyleSheet("background-color: #AFFFAF;")
        # window.opinion_senti_label.setText("Positive")
        senti_image = QPixmap("./resource/images/senti1.png")
        window.opinion_senti_label.setPixmap(senti_image)
    elif(polarity == 0):
        # window.opinion_senti_label.setStyleSheet("background-color:gray;")
        # window.opinion_senti_label.setText("这条评论难到我了...")
        senti_image = QPixmap("./resource/images/senti0.png")
        window.opinion_senti_label.setPixmap(senti_image)
    else:
        # window.opinion_senti_label.setStyleSheet("background-color:#FFAFAF;")
        # window.opinion_senti_label.setText("预测为负面评论")
        senti_image = QPixmap("./resource/images/senti-1.png")
        window.opinion_senti_label.setPixmap(senti_image)
    init_view.statusBar_update(window, current_view='analyser', polarity=polarity)

def show_analysis_readable(window, base_tokens_list, opinion_tokens_list, scores_list, forward_morphology_set, forward_abbreviation_set):

    worked_tokens_list = []
    worked_scores_list = []
    for sent_index in range(len(opinion_tokens_list)):
        worked_tokens = []
        worked_scores = []
        for token_index in range(len(opinion_tokens_list[sent_index])):
            if(scores_list[sent_index][token_index] != 0):
                worked_tokens.append(opinion_tokens_list[sent_index][token_index])
                worked_scores.append(scores_list[sent_index][token_index])
        worked_tokens_list.append(worked_tokens)
        worked_scores_list.append(worked_scores)

    
    content = ""
    _support_negative_words = ['no', 'not', 'never', 'little', 'few', 'nobody', 'noone', 'nothing', 'none', 'neither', 'seldom', 'hardly']

    # partial opinion
    if(window.option_partial_opinion.isChecked()):
        last_effective_index = len(worked_scores_list) - 1
        first_effective_index = 0
        while(sum(worked_scores_list[last_effective_index]) == 0):
            last_effective_index -= 1
            if(last_effective_index < 0):
                break
        while(sum(worked_scores_list[first_effective_index]) == 0):
            first_effective_index += 1
            if(first_effective_index >= len(worked_scores_list)):
                break

    for sent_index in range(len(base_tokens_list)):
        if(window.option_partial_opinion.isChecked()):
            if(sent_index == first_effective_index or sent_index == last_effective_index):
                normal_process_flag = True
            else:
                normal_process_flag = False
        for base_token in base_tokens_list[sent_index]:
            if(base_token in forward_morphology_set):
                token = forward_morphology_set[base_token]
            elif(base_token in forward_abbreviation_set):
                token = forward_abbreviation_set[base_token].split()[-1]
            else:
                token = base_token

            if(window.option_partial_opinion.isChecked()):
                if(not normal_process_flag):
                    content += "&nbsp;" + base_token
                    continue

            if(token.lower() in worked_tokens_list[sent_index] ):
                target_index = worked_tokens_list[sent_index].index(token.lower())
                content = _add_token(content, base_token, score=worked_scores_list[sent_index][target_index])
            elif(token == '?' and window.option_endmark.isChecked()):
                content = _add_token(content, base_token, score=-1)
            elif(token == '!' and window.option_endmark.isChecked()):
                content = _add_token(content, base_token, score=1)
            elif(window.option_negative_reversal.isChecked() and token.lower() in _support_negative_words and len(worked_tokens_list[sent_index]) != 0):
                content = _add_token(content, base_token, score=sum(worked_scores_list[sent_index]))
            else:
                content += "&nbsp;" + base_token
    window.opinion_analysis_browser.setHtml(f'<p> {content} </p>')

def _add_token(content, token, score):
    if(score > 0):
        return content + f'<font style="color:red" >&nbsp;{token}</font>'
    else:
        return content + f'<font style="color:blue" >&nbsp;{token}</font>'
