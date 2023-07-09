#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File         :   choice_dictionaries.py
@Desc         :   选择字典
'''


def update_double_clicked_event(window):
    table = window.main_dict_infos_table
    table.itemDoubleClicked.connect(window.main_dict_infos_table_doubleClicked)

def main(window):
    
    # 绑定双击选定字典事件
    update_double_clicked_event(window)
