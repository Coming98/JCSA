#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File         :   main.py
@Author       :   JC
@Contact      :   jcqueue@gmail.com
@Department   :   INSTITUTE OF INFORMATION ENGINEERING, CAS
@Desc         :   
'''


from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow
from view.Ui_MainWindow import Ui_MainWindow
from view import init_view
from work_flow import choice_dictionaries, senti_analysis, analysis_show
from work_flow import config
from PyQt5.QtGui import QPixmap
import sys


class JCSnifferWindow(Ui_MainWindow, QMainWindow):

    def __init__(self):
        super(JCSnifferWindow, self).__init__()
        self.setupUi(self)

        self.config_path = './config.json'
        self.setWindowTitle("JCSA System")

        # 初始化界面
        init_view.init_welcome(self)

        # 初始化配置参数
        config.init_config(self)

        # 欢迎界面 选择字典
        choice_dictionaries.main(self)

    def open(self):
        print("open")

    def start_analysis(self):

        opinion = self.opinion_input_edit.toPlainText().strip()

        # 情感分析
        polarity, base_tokens_list, opinion_tokens_list, scores_list, forward_morphology_set, forward_abbreviation_set = senti_analysis.main(self, opinion)
        print(polarity)
        print(base_tokens_list)
        print(opinion_tokens_list)
        print(scores_list)
        print(forward_morphology_set)
        print(forward_abbreviation_set)
        # 显示情感结果 - opinion_input_edit
        analysis_show.show_polarity(self, polarity)

        # 显示可解释性结果 - opinion_analysis_browser
        analysis_show.show_analysis_readable(self, base_tokens_list, opinion_tokens_list, scores_list, forward_morphology_set, forward_abbreviation_set)

    def end_sniff(self):
        print("end")

    def quit(self):
        self.dict_name = ""
        self.opinion_input_edit.clear()
        self.opinion_analysis_browser.clear()
        senti_image = QPixmap("./resource/images/senti0.png")
        self.opinion_senti_label.setPixmap(senti_image)

        self.option_endmark.setChecked(False)
        self.option_morphology.setChecked(False)
        self.option_keep_stop_words.setChecked(False)
        self.option_negative_reversal.setChecked(False)
        self.option_partial_opinion.setChecked(False)

        init_view.taggle_info_window(self, "WELCOME")
        init_view.statusBar_update(self, current_view='welcome')

        init_view.update_welcome_toolbar(self, "show_welcome")

    def save(self):
        print('save')

    def download(self):
        print('download')

    # Events
    def main_dict_infos_table_doubleClicked(self, item):
        table = self.main_dict_infos_table
        row = item.row()
        self.dict_name = table.item(row, 1).text()

        # 进入分析界面
        init_view.taggle_info_window(self, "ANALYSIS")

        init_view.statusBar_update(self, current_view='analyser')

        # ToolBar
        init_view.update_welcome_toolbar(self, "dictiionary_checked")
        self.opinion_input_edit_textChanged()

    def main_dict_infos_table_clicked(self, item):
        table = self.main_dict_infos_table
        row = item.row()
        self.dict_name = table.item(row, 1).text()

        init_view.statusBar_update(self, current_view='welcome')

    def main_dict_infos_table_itemSelectionChanged(self):
        if(not self.main_dict_infos_table.currentItem().isSelected()):
            init_view.statusBar_update(self, current_view='welcome')

    def opinion_input_edit_textChanged(self):
        # opinion_input_edit
        opinion = self.opinion_input_edit.toPlainText().strip()
        if(len(opinion.strip()) == 0):
            self.startAction.setDisabled(True)
        else:
            self.startAction.setDisabled(False)

    def checkboxes_stateChanged(self):
        init_view.statusBar_update(self, current_view='analyser')
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    snifferWindow = JCSnifferWindow()
    snifferWindow.show()
    sys.exit(app.exec_())
