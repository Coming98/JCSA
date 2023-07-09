#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QFont, QPixmap
from PyQt5.QtWidgets import QAction, QHeaderView, QAbstractItemView, QFrame
import os
import sys
sys.path.append('../')

ICON_DIR = './resource/icon'
MAIN_IMAGE_PATH = './resource/images/main.png'


def taggle_info_window(window, state_info):

    flag = True if state_info.upper() == 'WELCOME' else False

    window.main_image_label.setVisible(flag)
    window.main_header_label.setVisible(flag)
    window.main_dict_infos_table.setVisible(flag)
    window.main_footer_text.setVisible(flag)

    window.advanced_options_groupBox.setVisible(not flag)
    window.opinion_input_edit.setVisible(not flag)
    window.opinion_senti_label.setVisible(not flag)
    window.opinion_analysis_browser.setVisible(not flag)

# main_dict_infos_table


def init_welcome_main_dict_infos_table(window):
    table = window.main_dict_infos_table
    table.setColumnHidden(0, True)  # 隐藏 index 列
    table.verticalHeader().setVisible(False)  # 隐藏列名
    table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # 自适应宽度
    table.horizontalHeader().setSectionsClickable(False)  # 禁止点击表头
    table.setSelectionBehavior(QAbstractItemView.SelectRows)  # 只能选择一行
    table.setEditTriggers(QAbstractItemView.NoEditTriggers)  # 不可更改
    font = QFont('微软雅黑', 14)
    font.setBold(True)
    table.horizontalHeader().setFont(font)  # 设置表头字体
    table.horizontalHeader().setStyleSheet(
        'QHeaderView::section{background:gray; color:white}')
    table.setAlternatingRowColors(True)
    table.setFrameStyle(QFrame.NoFrame)
    table.setStyleSheet('gridline-color:white;'
                        'border:0px solid gray')
    table.itemClicked.connect(window.main_dict_infos_table_clicked)
    table.itemSelectionChanged.connect(
        window.main_dict_infos_table_itemSelectionChanged)
# main_image_label


def init_welcome_main_image_label(window):
    main_image_obj = QPixmap(MAIN_IMAGE_PATH)
    window.main_image_label.setPixmap(main_image_obj)
    window.main_image_label.setScaledContents(True)  # 让图片自适应label大小

# ToolBar


def init_welcome_toolbar(window):

    window.toolBar.setStyleSheet(
        "QToolBar{spacing:16px;padding-left:12px;}")  # 间距

    # 开始按钮
    startAction = QAction(
        QIcon(os.path.join(ICON_DIR, 'start')), 'Start (Ctrl+B)', window)
    startAction.setShortcut('Ctrl+B')
    startAction.triggered.connect(window.start_analysis)
    window.toolBar.addAction(startAction)
    startAction.setDisabled(True)
    window.startAction = window.toolBar.actions(
    )[len(window.toolBar.actions()) - 1]

    # 退出按钮
    quitAction = QAction(QIcon(os.path.join(ICON_DIR, 'quit')),
                         'Quit (Ctrl+Q)', window)
    quitAction.setShortcut('Ctrl+Q')
    quitAction.triggered.connect(window.quit)
    window.toolBar.addAction(quitAction)
    quitAction.setDisabled(True)
    window.quitAction = window.toolBar.actions(
    )[len(window.toolBar.actions()) - 1]


def init_checkboxes(window):
    window.option_endmark.stateChanged.connect(window.checkboxes_stateChanged)
    window.option_morphology.stateChanged.connect(
        window.checkboxes_stateChanged)
    window.option_keep_stop_words.stateChanged.connect(
        window.checkboxes_stateChanged)
    window.option_negative_reversal.stateChanged.connect(
        window.checkboxes_stateChanged)
    window.option_partial_opinion.stateChanged.connect(
        window.checkboxes_stateChanged)


def update_welcome_toolbar(window, state_name):
    # 开始, 后退
    status = {
        'dictiionary_checked': [False, True],
        'show_welcome': [False, False],
    }

    for i, state in enumerate(status[state_name]):
        if(state is None):
            continue
        window.toolBar.actions()[i].setEnabled(state)


# MainWindow
def init_welcome_mainwindow(window):
    window.setStyleSheet("#MainWindow{background-color: white}")  # 背景色
    window.main_header_label.setAlignment(Qt.AlignCenter)  # 欢迎内容剧中
    window.main_footer_text.setStyleSheet(
        "QTextBrowser{border-width:0;border-style:outset}")  # 页脚文字去除边框
    window.resize(1867, 1198)  # resize

# opinion_input_edit


def init_opinion_input_edit(window):
    window.opinion_input_edit.setStyleSheet(
        'border: 1px solid black; padding: 10px; font-size:22px;')
    window.opinion_input_edit.setAcceptRichText(False)
    window.opinion_input_edit.textChanged.connect(
        window.opinion_input_edit_textChanged)


#     opinion_senti_label
def init_opinion_senti_label(window):
    init_senti_image = QPixmap("./resource/images/senti0.png")
    window.opinion_senti_label.setPixmap(init_senti_image)


def init_advanced_options_groupBox(window):
    # window.advanced_options_groupBox.setStyleSheet("border: 1px solid black")
    pass


def init_opinion_analysis_browser(window):
    window.opinion_analysis_browser.setStyleSheet("border: 1px solid black")


def statusBar_update(window, current_view="welcome", polarity=None):
    dict_name, state_endmark, state_morphology, state_keep_stop_word, state_negative_reversal, state_partial_opinion, polarity_info = [
        None, ] * 7

    if(window.dict_name is not None):
        dict_name = window.dict_name

    if(current_view == 'analyser'):
        state_endmark = "%s句末标点分析" % (
            "启用" if window.option_endmark.isChecked() else "关闭")
        state_morphology = "%s词形统一" % (
            "启用" if window.option_morphology.isChecked() else "关闭")
        state_keep_stop_word = "%s停用词" % (
            "保留" if window.option_keep_stop_words.isChecked() else "清洗")
        state_negative_reversal = "%s否定词反转" % (
            "启用" if window.option_negative_reversal.isChecked() else "关闭")
        state_partial_opinion = "%s有效首尾句分析" % (
            "启用" if window.option_partial_opinion.isChecked() else "关闭")
        if(polarity is not None):
            polarity_info = "预测为负面评论" if polarity < 0 else (
                "预测为正面评论" if polarity > 0 else "这条评论难到我了...")

    infos = [item for item in (dict_name, state_endmark, state_morphology, state_keep_stop_word,
                               state_negative_reversal, state_partial_opinion, polarity_info) if item is not None]

    if(len(infos)):
        infos = ' | '.join(infos)
    else:
        infos = ''

    window.statusBar().showMessage(infos)


def init_welcome(window):

    window.setWindowIcon(QIcon('./resource/icon/jcsa.png'))

    # MainWindow
    init_welcome_mainwindow(window)

    # ToolBar
    init_welcome_toolbar(window)

    # CheckBox
    init_checkboxes(window)

    # main_image_label
    init_welcome_main_image_label(window)

    # main_dict_infos_table
    init_welcome_main_dict_infos_table(window)

    # opinion_input_edit
    init_opinion_input_edit(window)

    # opinion_senti_label
    init_opinion_senti_label(window)

    # advanced_options_groupBox
    init_advanced_options_groupBox(window)

    # opinion_analysis_browser
    init_opinion_analysis_browser(window)

    # taggle_info_window
    taggle_info_window(window, "WELCOME")

    window.showMaximized()
