# -*- coding: UTF-8 -*-

import sys
import os
from datetime import datetime 
import re
import string

DIGITAL_MAP = (('一', '1'), ('二', '2'), ('三', '3'), ('四', '4'), ('五', '5'), ('六', '6'), ('七', '7'), ('八', '8'), ('九', '9'), ('十', 'a'), )
EPISODE_FORMAT = r'(S\d{2}E\d{2})'

def is_eng_ascii(c : str) -> bool :
    #return ord(c) < 127 and c in string.printable
    return (ord(c) >= 65 and ord(c) <= 90) or (ord(c) >= 97 and ord(c) <= 122)

#简体中文数字转阿拉伯数字
def chs_to_digital(chn : str) -> int :
    
    def _trans(s : str) -> int :
        digit = {'一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9 }
        num = 0
        if s:
            idx_q, idx_b, idx_s = s.find('千'), s.find('百'), s.find('十')
            if idx_q != -1:
                num += digit[s[idx_q - 1:idx_q]] * 1000
            if idx_b != -1:
                num += digit[s[idx_b - 1:idx_b]] * 100
            if idx_s != -1:
                # 十前忽略一的处理
                num += digit.get(s[idx_s - 1:idx_s], 1) * 10
            if s[-1] in digit:
                num += digit[s[-1]]
        return num

    chn = chn.replace('零', '')
    idx_y, idx_w = chn.rfind('亿'), chn.rfind('万')
    if idx_w < idx_y:
        idx_w = -1
    num_y, num_w = 100000000, 10000
    if idx_y != -1 and idx_w != -1:
        return chs_to_digital(chn[:idx_y]) * num_y + _trans(chn[idx_y + 1:idx_w]) * num_w + _trans(chn[idx_w + 1:])
    elif idx_y != -1:
        return chs_to_digital(chn[:idx_y]) * num_y + _trans(chn[idx_y + 1:])
    elif idx_w != -1:
        return _trans(chn[:idx_w]) * num_w + _trans(chn[idx_w + 1:])
    return _trans(chn)

#返回剧集文件的剧集信息元组，如（1，5），（0，3）。无法获取为None
def rip_se_info(file_episode) :
    se_info = None
    ep_info = re.search(EPISODE_FORMAT, file_episode, re.I)
    if ep_info is not None :
        info = ep_info.group().upper()
        if len(info) == 6 :
            try :
                ss = int(info[1:3])
                es = int(info[4:])
                se_info = (ss, es)
            except :
                pass
    return se_info

#解析季号，支持S01, S01.1984, 第1季，第一季格式。
def rip_season_num(dir_name : str) -> int :
    VALID_CHS_NUMS = ['一', '二', '三', '四', '五', '六', '七', '八', '九', '十', ]
    def _all_chs_nums(info : str) -> bool :
        all = True
        for c in info :
            if c not in VALID_CHS_NUMS :
                all = False
                break
        return all
    num = -1
    if len(dir_name) == 0 :
        return -1
    pure = ''
    end = dir_name.find('.')
    if end > 0 :
        pure = dir_name[:end]
    else :
        pure = dir_name

    if pure[0] == '第' and pure[-1] == '季' :
        info = pure[1:-1]
        if len(info) <= 3 :
            if info.isdigit() :
                num = int(info)
            else :
                if info == '零' :
                    num = 0
                elif _all_chs_nums(info) :
                    num = chs_to_digital(info)
    else :
        if pure[0].upper() == 'S' :
            info = pure[1:]
            if len(info) <= 2 and info.isdigit() :
                num = int(info)
        else :
            if len(pure) <= 2 and pure.isdigit() :
                num = int(pure)
    return num

def is_char_chinese(c) -> bool :
    ZH_SYMBOLS = '！？｡＂＃＄％＆＇（）＊＋，－／：；＜＝＞＠［＼］＾＿｀｛｜｝～｟｠｢｣､、〃》「」『』【】〔〕〖〗〘〙〚〛〜〝〞〟〰〾〿–—‘’‛“”„‟…‧﹏.。'
    is_zh = False
    if '\u4e00' <= c <= '\u9fa5' :
        is_zh = True
    elif c in ZH_SYMBOLS :
        is_zh = True
    return is_zh

#字符串全部为中文
def is_all_chinese(str) -> bool :
    for _c in str:
        if not is_char_chinese(_c) :
            return False
    return True

def is_symbol(c) -> bool :
    symbol = False
    ENG_SYMBOL = string.punctuation
    CHS_SYMBOL = '！？｡＂＃＄％＆＇（）＊＋，－／：；＜＝＞＠［＼］＾＿｀｛｜｝～｟｠｢｣､、〃》「」『』【】〔〕〖〗〘〙〚〛〜〝〞〟〰〾〿–—‘’‛“”„‟…‧﹏.。'
    if c in ENG_SYMBOL :
        symbol = True
    elif c in CHS_SYMBOL :
        symbol = True
    return symbol


def name_2_pinyin(name : str, trans_num : bool = False) -> str :
    curPath = os.path.abspath(os.path.dirname(__file__))
    libPath = os.path.join(curPath, 'lib')
    sys.path.append(libPath)
    import pypinyin

    IGNORE_ENG_SYMBOL = string.punctuation
    IGNORE_CHS_SYMBOL = '！？｡＂＃＄％＆＇（）＊＋，－／：；＜＝＞＠［＼］＾＿｀｛｜｝～｟｠｢｣､、〃》「」『』【】〔〕〖〗〘〙〚〛〜〝〞〟〰〾〿–—‘’‛“”„‟…‧﹏.。'
    DIGITAL_PY_MAP = ( ('0', 'L'), ('1', 'Y'), ('2', 'E'), ('3', 'S'), ('4', 'S'), ('5', 'W'), ('6', 'L'), ('7', 'Q'), ('8', 'B'), ('9', 'J') )
    def del_ignore(name : str) :
        clean = name
        for ies in IGNORE_ENG_SYMBOL :
            clean = clean.replace(ies, '')
        for ics in IGNORE_CHS_SYMBOL :
            clean = clean.replace(ics, '')
        return clean
    def digital_2_pinyin(input : str) :
        py = input
        for DM in DIGITAL_PY_MAP :
            py = py.replace(DM[0], DM[1])
        return py
    def _add_word(w, flag, wl) :
        clean = del_ignore(w).strip()
        if clean != '' :
            if flag == 3 :              
                if not clean.isupper() :    #混合大小写的英文单词，取首字母
                    clean = clean[0]
            wl.append((clean, flag))
        return
    def _name_2_frags(name : str) -> list :
        frags = list()
        cur = ''
        flag = 0            #=1中文，=2数字，=3英文。=4其它语种。=0开头或丢弃字符，如标点符号。
        for i in range(len(name)) :
            c = name[i]
            if c.isdigit() :    #数字
                #print('find digital=%s.' %c)
                if flag == 2 :
                    cur = cur + c
                else :
                    if flag != 0 :
                        _add_word(cur, flag, frags)
                    cur = c
                    flag = 2
            #elif is_pure_eng(c) :   #英文字符
            elif c.encode().isalpha() :
                #print('find alpha=%s.' %c)
                if flag == 3 :
                    cur = cur + c
                else :
                    if flag != 0 :
                        _add_word(cur, flag, frags)
                    cur = c
                    flag = 3
            elif is_all_chinese(c) :         #中文字符
                #print('found chs=%s.' %c)
                if flag == 1 :
                    cur = cur + c
                else :
                    if flag != 0 :
                        _add_word(cur, flag, frags)
                    cur = c
                    flag = 1
            
            elif is_symbol(c) :              #无法识别的字符，如标点符号
                #print('found ignore char=%s.' %c)
                if flag != 0 :
                    _add_word(cur, flag, frags)
                    cur = ''
                    flag = 0
            else :          #无法识别的字符，日韩德等其它语种
                if flag == 4 :
                    cur = cur + c
                else :
                    if flag != 0 :
                        _add_word(cur, flag, frags)
                    cur = c
                    flag = 4
        if cur != '' and flag != 0 :            #最后一个词
            _add_word(cur, flag, frags)

        return frags

    py_list = list()
    frags = _name_2_frags(name)
    for f in frags :
        #print('data=%s, flag=%s.' %(f[0], f[1]))
        if f[1] == 1 :      #中文
            first_list = pypinyin.lazy_pinyin(f[0])
            first = ''
            for f in first_list :
                first += f[0].upper()
            py_list.append(first)
        elif f[1] == 2 :  #数字
            if trans_num :
                first = digital_2_pinyin(f[0])
            else :
                first = f[0]
            py_list.append(first)
        elif f[1] == 3 :    #英文
            first = f[0].upper()
            py_list.append(first)
        elif f[1] == 4 :    #其它语种，跟英语一样保留第一个字符
            first = f[0].upper()
            py_list.append(first)
    first_py = ''
    for py in py_list :
        first_py += py
    return first_py

def _season_adjust(input : str) -> str :
    output = input.strip()
    if len(output) >= 3 and output[0] == '第' and output[-1] == '季' :
        for DM in DIGITAL_MAP :
            output = output.replace(DM[0], DM[1])
    return output

#取得固定长度的拼音缩写, fix_len=0为取全部长度
#首字母是否更高层面已排序
def get_fixed_PINYIN(data : str, fix_len : int, FIRST_SORTED=False) -> str :
    FULL_WITH = '0'
    fixed = ''
    if data == '' :
        return ''
    assert(fix_len >= 0)
    first = ''
    if FIRST_SORTED :
        first = data[0]
        data = data[1:]
    sn = rip_season_num(data)   #检查是否季目录
    if sn >= 0 :
        fixed = 'D' + str(sn) + 'J'
    else :
        #sa = _season_adjust(data)
        PY = name_2_pinyin(data)
        if fix_len == 0 :
            fix_len = len(PY)
        if len(PY) >= fix_len :
            fixed = PY[ : fix_len]
        else :
            fixed = PY.ljust(fix_len, FULL_WITH)
    if FIRST_SORTED :
        fixed = first + fixed
    return fixed

def test_py_sort() :
    #INFOS = ('第0季', '第二季.2021', '第三季', '第一季.2019', '第几个季节才会这样.1984', )
    INFOS = ('3第1名', '3好汉罗宾逊', '第三季', '2第几个季节才会这样.1984', )
    for info in INFOS :
        py = get_fixed_PINYIN(info, 0)
        print('data={}, py={}.'.format(info, py))
        #py = name_2_pinyin(info)
        #print(py)
    return

    INFOS = ('第十二季', '我的', '七', 'S03', 'S12.2004', '第五季', 'S02545', '1', '111')
    for info in INFOS :
        num = rip_season_num(info)
        print(num)
    return
    names = ['FKDMKS21981', 'FKDMKS1979', 'FKDMKS4KBZL2015', 'FKDMKS31985', ]
    names.sort()
    print(names)
    return

#test_py_sort()