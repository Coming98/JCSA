#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File         :   SAonDict.py
@Desc         :   Sentiment Analysis based on Sentiment Dicts
'''
import os
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
from nltk import pos_tag
import json
import re
from nltk.corpus import stopwords
from nltk.corpus import sentiwordnet as swn
class ModelOnDict:

    def __init__(self, dictname, opinion):
        self._support_dict_name = ['random', 'dict_swn', "dict_liub", "dict_imdb", "sentitfidf"]
        self._support_endmarks = ['.', '?', '!']
        self._support_function_words = ['a', 'an', 'the', 'in', 'on', 'to', 'of', 'by', 'as', 'for', 'and', 'but', 'with', 'not']
        self._support_negative_words = ['no', 'not', 'never', 'little', 'few', 'nobody', 'noone', 'nothing', 'none', 'neither', 'seldom', 'hardly']
        self.tag_split = "@TAG@"
        self.forward_morphology_set = {} # 词形统一后用于还原可视化
        self.forward_abbreviation_set = {} # 缩写展开后用于还原可视化
        assert dictname.lower() in self._support_dict_name, f"Unsupport Dictname, please input: `{', '.join(self._support_dict_name)}`."
        self.dictname = dictname.lower()
        if(self.dictname == 'sentitfidf'): self.dictname = 'dict_stif'
        self.opinion = opinion

        self.current_dict = load_dict(self.dictname)

    def transform(self, ignore_case=True, consider_endmarks=False, replace_abbreviation=True, replace_propernouns=True,
                  union_morphology=True, remove_stops=True, consider_negative_word=True, partial_sent=False, part_of_speech=['n', 'v', 'a', 'r']):
        """_control_parameters_

        Args:
            ignore_case (bool, optional): 是否忽略大小写, True - 忽略大小写
            consider_endmarks (bool, optional): 是否关注结尾标点符号, True - 将结尾标点符号应用到情感分析中
            replace_abbreviation (bool, optional): 是否替换缩写形式, True - 将缩写展开
            replace_propernouns (bool, optional): 是否替换专有名词, True - 查找并合并专有名词, 避免与情感词典匹配
            union_morphology (bool, optional): 是否合并多种词形, True - 如名词单数复数都转为单, 形容词比较级最高级都转为普通形式
            remove_stops (bool, optional): 是否去除停用词, True - 去除常见的停用词
            consider_negative_word (bool, optional): 是否考虑否定词反转, True - 在情绪词前查找否定词是否存在, 存在则反转情绪
            partial_sent (bool, optional): 是否只考虑有效首尾句, True - 只通过两个有效首尾句的情感判断整个评论文本的情感
            part_of_speech (list, optional): 参与情感词典匹配的词性列表, 目前最多只考虑 ['n', 'v', 'a', 'r']; 如果关闭了合并词形, 会自动匹配到形容词的多种形态, 以在目标情感词典中查找
        """
        self.ignore_case = ignore_case
        self.consider_endmarks = consider_endmarks
        self.replace_abbreviation = replace_abbreviation
        self.replace_propernouns = replace_propernouns
        self.union_morphology = union_morphology
        self.remove_stops = remove_stops
        self.consider_negative_word = consider_negative_word
        self.partial_sent = partial_sent
        self.part_of_speech = part_of_speech
        self._support_abbreviations_map = json.loads(open('./resource/abbreviations.json', 'r').read())

        polarity, opinion_tokens_list, scores_list = self.transform_iter(self.opinion)
        clean_opinion_tokens_list = []
        for tokens_list in opinion_tokens_list:
            clean_opinion_tokens_list.append([token.split(self.tag_split)[0] for token in tokens_list])

        return polarity, self.base_opinion_tokens_list, clean_opinion_tokens_list, scores_list, self.forward_morphology_set, self.forward_abbreviation_set
    
    
    def transform_iter(self, opinion):

        # 基本的预处理, 在处理下方清洗时遇到的问题: `<br />` 删除; `"` 双引号替换为空格
        self.base_opinion_tokens_list = self.jc_get_base_opinion_tokens_list(opinion)

        opinion = self.jc_basic_clean(opinion)

        opinion_tokens_list, params_list = self.transform_iter_clean(opinion)

        predict, scores_list = self.transform_iter_predict(opinion_tokens_list, params_list)

        return predict, opinion_tokens_list, scores_list

    def transform_iter_predict(self, opinion_tokens_list, params_list):

        scores_list = self.jc_get_scores_list(opinion_tokens_list, params_list)
        
        sent_scores = []
        for scores, param in zip(scores_list, params_list):
            sent_score = sum(scores)
            if(self.consider_endmarks):
                if('!' in param): sent_score = max(1, sent_score * 2)
                elif('?' in param): sent_score = min(-1, sent_score * -2)
            sent_scores.append(sent_score)
        if(self.partial_sent):
            sent_scores = [score for score in sent_scores if score != 0]
            if(len(sent_scores) == 0):
                sent_scores = [0., ]
            total = sent_scores[0] + sent_scores[-1]
        else:
            total = sum(sent_scores)

        predict = 1 if total > 0. else (-1 if total < 0 else 0)

        return predict, scores_list

    def transform_iter_clean(self, opinion):

        # 1. 分句. consider_endmarks(分句时如果考虑句末标点, 则将句末标点放到 params 列表中返回)
        opinion_sents, params_list = self.jc_sent_tokenize(opinion)
        assert len(opinion_sents) == len(params_list), "Exists empty sentence"

        # 2. 缩写处理: 借助维基百科中的缩略词列表进行处理
        opinion_sents = self.jc_replace_abbreviations(opinion_sents)
        assert len(opinion_sents) == len(params_list), "Exists empty sentence"

        # 3. 空格分词 + 命名实体识别: 连续两个
        opinion_tokens_list = self.jc_replace_propernouns(opinion_sents)
        assert len(opinion_tokens_list) == len(params_list), "Exists empty sentence"

        # 4. 小写 + 词形统一/词形还原
        opinion_tokens_list = self.jc_union_morphology(opinion_tokens_list)
        assert len(opinion_tokens_list) == len(params_list), "Exists empty sentence"

        # 5. 去除停用词 + 标点符号, 保留关键单词, 进行词典匹配
        opinion_tokens_list = self.jc_remove_punctuations_and_stops(opinion_tokens_list)
        assert len(opinion_tokens_list) == len(params_list), "Exists empty sentence"

        return opinion_tokens_list, params_list

    def jc_get_base_opinion_tokens_list(self, opinion):
        sents = sent_tokenize(opinion)
        tokens_list = [ sent.split() for sent in sents]
        return tokens_list

    def jc_basic_clean(self, opinion):
        opinion = opinion.replace("<br />", "")
        opinion = opinion.replace('"', ' ')

        # 替换网址为 <URL>
        url_regex = r'(https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]+\.[^\s]{2,}|www\.[a-zA-Z0-9]+\.[^\s]{2,})'
        opinion = re.sub(url_regex, "<URL>", opinion)

        # 去除重复的标点, 如 `!!!`
        opinion = re.sub(r'([!?,;])\1+', r'\1', opinion)
        opinion = re.sub(r'\.{3,}', r'...', opinion)
        return opinion

    def jc_sent_tokenize(self, opinion):
        opinion_sents = sent_tokenize(opinion)
        params_list = []

        for opinion_sent in opinion_sents:
            if(len(opinion_sent.strip()) == 0): continue
            endmark = opinion_sent[-1]
            print(endmark)
            if(endmark in self._support_endmarks):
                params_list.append([endmark, ])
            else:
                params_list.append(['.', ])

        return opinion_sents, params_list

    def jc_replace_abbreviations(self, opinion_sents):
        opinion = " @@ ".join(opinion_sents)

        opinion_words = opinion.split(" ")
        for index in range(len(opinion_words)):
            word = opinion_words[index]
            if(not len(word)): continue
            first_upper = True if word[0].isupper() else False

            if(word.lower() in self._support_abbreviations_map.keys()):
                target = self._support_abbreviations_map[word.lower()]
                self.forward_abbreviation_set[word] = target.lower()
                if(first_upper):
                    target = target[0].upper() + target[1:]
                opinion_words[index] = target
        opinion = " ".join(opinion_words)
        opinion_sents = opinion.split(" @@ ")
        return opinion_sents

    def jc_replace_propernouns(self, opinion_sents):
        
        opinion_tokens_list = []
        for opinion_sent in opinion_sents:
            # opinion_sent = re.sub(r'[^\w]', '', opinion_sent)
            opinion_tokens = []
            # tokens = opinion_sent.split()
            tokens = []
            raw_tokens = word_tokenize(opinion_sent)
            for token in raw_tokens:
                if(token.count(".") == 1):
                    token = token.split('.')
                    tokens.extend(token)
                else:
                    tokens.append(token)

            if(len(tokens) <= 1): # 句子里就一个词
                opinion_tokens = [tokens[0], ]
            else:
                start_index = 0
                while start_index < len(tokens):
                    token = tokens[start_index]

                    if(len(token) == 0): 
                        start_index += 1
                        continue
                    else: token = token.strip()

                    if(token[0].isupper()):
                        # 尝试寻找专有名词
                        target_index = start_index + 1
                        union_index = start_index # 虚词能够向下寻找, 但是只有虚词不能认定为专有名词
                        while target_index < len(tokens):
                            target_token = tokens[target_index]
                            if(len(target_token) != 0):
                                if(target_token not in self._support_function_words and target_token[0].islower()):
                                    break
                            target_index += 1
                            if(len(target_token) == 0 or target_token[0].isupper()): union_index = target_index - 1

                        if(start_index < union_index):
                            opinion_tokens.append("_".join(tokens[start_index:union_index + 1]))
                            start_index = union_index + 1
                            continue
                    opinion_tokens.append(token)
                    start_index += 1
            opinion_tokens_list.append(opinion_tokens)
        return opinion_tokens_list
        # ![](https://raw.githubusercontent.com/Coming98/pictures/main/202206162210670.png)

    def jc_union_morphology(self, opinion_tokens_list):

        wnl = WordNetLemmatizer()
        for tokens in opinion_tokens_list:
            pos_tags = pos_tag(tokens)
            for token_index in range(len(tokens)):
                token = tokens[token_index]
                jc_pos_tag = pos_tags[token_index]

                token = token.lower()

                if("_" in token): continue # 专有名词不需要词形归一化也不需要词性标注

                token_tag = get_wordnet_pos(token, jc_pos_tag)

                if(token_tag is None): # 未知词性
                    tokens[token_index] = token
                    continue

                if(self.union_morphology is False): # 不进行词性归一化只进行词性标注
                    union_token = token
                else:
                    union_token = wnl.lemmatize(token, token_tag)
                    self.forward_morphology_set[token] = union_token
                tokens[token_index] = union_token + self.tag_split + token_tag
        return opinion_tokens_list
        # ![](https://raw.githubusercontent.com/Coming98/pictures/main/202206170005368.png)
    
    def jc_remove_punctuations_and_stops(self, opinion_tokens_list):
        english_punctuations = [',', '.', ':', ';', '?', '(', ')', '[', ']', '&', '!', '*', '@', '#', '$', '%', '\'']
        stops = list(set(stopwords.words("english"))) if self.remove_stops else []
        remove_set = english_punctuations + stops

        ret_opinion_tokens_list = []
        for tokens_list in opinion_tokens_list:
            tokens_list = [ token for token in tokens_list if token not in remove_set or token in ['not'] ]
            ret_opinion_tokens_list.append(tokens_list)

        return ret_opinion_tokens_list
            
    def jc_get_scores_list(self, opinion_tokens_list, params_list):
        
        scores_list = []

        for tokens_list, param in zip(opinion_tokens_list, params_list):
            scores = []
            for token_index, token in enumerate(tokens_list):
                score = self.jc_get_token_polarity_score(token)
                scores.append(score)
            if(self.consider_negative_word):
                reverse_flag = self.jc_check_negative_word_and_update(tokens_list)
                if(reverse_flag):
                    scores = [ score * -1 for score in scores ]
            scores_list.append(scores)
        return scores_list

    # 词典不同, 处理方式也不同
    def jc_get_token_polarity_score(self, token):
        if(self.dictname == 'dict_swn'):
            return self.jc_get_token_polarity_score_swn(token)
        elif(self.dictname == 'dict_liub'):
            return self.jc_get_token_polarity_score_outside(token)
        elif(self.dictname == 'dict_imdb'):
            return self.jc_get_token_polarity_score_outside(token)
        elif(self.dictname == 'dict_stif'):
            return self.jc_get_token_polarity_score_outside(token)

    def jc_get_token_polarity_score_outside(self, token):
        if(self.tag_split in token): token = token.split(self.tag_split)[0]

        if(token in self.current_dict):
            return self.current_dict[token]['score']
        return 0.

    def jc_get_token_polarity_score_swn(self, token):
        score = 0.
        # 获取单词与词性
        if(self.tag_split in token):
            token, tag = token.split(self.tag_split)
            if(tag not in self.part_of_speech):
                tag = None
        else:
            tag = None

        if(tag is None): return 0.

        items = swn.senti_synsets(token, tag)
        # 一个词性多种意思
        for index, item in enumerate(items, 0):
            score += (item.pos_score() - item.neg_score()) * (1 / (2 ** index))
        
        return score

    def jc_check_negative_word_and_update(self, tokens_list):

        for token in tokens_list:
            if(self.tag_split in token): token = token.split(self.tag_split)[0]
            if(token in self._support_negative_words): return True
        return False


############################# TOOL
def get_wordnet_pos(token, jc_pos_tag):
    tag = jc_pos_tag[1]
    if tag.startswith('J'):
        return wordnet.ADJ
    elif tag.startswith('V'):
        return wordnet.VERB
    elif tag.startswith('N') or tag in ['UH', ]:
        return wordnet.NOUN
    elif tag.startswith('R') or tag in ['WRB', ]:
        return wordnet.ADV
    else:
        return None

def load_dict(dictname):
    dictpath = f"./resource/dictionaries/{dictname.lower()}.json"
    if(os.path.exists(dictpath)):
        with open(dictpath, 'r') as f:
            current_dict = json.load(f)
    else:
        current_dict = None
    return current_dict

