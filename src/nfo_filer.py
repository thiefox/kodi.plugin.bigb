# -*- coding: UTF-8 -*-

import os
import sys

#curPath = os.path.abspath(os.path.dirname(__file__))
#libPath = os.path.join(curPath, 'lib')
#sys.path.append(libPath)
#from lib.lxml import etree
#import lib.lxml.etree
#import lib.lxml.etree.ElementTree as etree
import xml.etree.cElementTree as etree

import xbmcvfs

from vfs_wrapper import vfs_wrapper

#生成国家映射表
def gen_bigb_country_map() :
    FIXED_COUNTRYS = ('台湾', '日本', '韩国', '泰国', '印度', '美国', '加拿大', '俄罗斯', '澳大利亚', '新西兰', \
        '英国', '爱尔兰', '法国', '德国', '意大利', '西班牙', '中国大陆', '香港', '澳门', )
    UPDATE_COUNTRYS = ( ('中国', '中国大陆'), ('中国香港特别行政区', '香港'), ('中国澳门特别行政区', '澳门'), ('苏联', '俄罗斯'), )
    SOUTHEAST_ASIA_COUNTRYS = ('马来西亚', '印度尼西亚', '柬埔寨', '新加坡', '越南', )
    EASTERN_EUROPE_COUNTRYS = ('波兰', '白俄罗斯', '捷克', '罗马尼亚', '波斯尼亚和黑塞哥维那', '立陶宛', '塞尔维亚', '匈牙利', '保加利亚', '爱沙尼亚', \
        '克罗地亚', '格鲁吉亚', '乌克兰', 'Soviet Union', '前苏联', 'Yugoslavia', '南斯拉夫', 'East Germany', '东德', '北马其顿', '斯洛文尼亚', )
    NORTHERN_EUROPE_COUNTRYS = ('瑞典', '丹麦', '冰岛', '芬兰', '挪威', )
    OTHER_EUROPE_COUNTRYS = ('比利时', '荷兰', '奥地利', '希腊', '土耳其', '塞浦路斯', '瑞士', '卢森堡', '葡萄牙', '马耳他', )
    NORTH_AMERICA_COUNTRYS = ('古巴', '墨西哥')
    LATIN_AMERICA_COUNTRYS = ('巴西', '秘鲁', '智利', '阿根廷', '哥伦比亚', '乌拉圭', '波多黎各', )
    OTHER_AAL_COUNTRYS = ('南非', '阿拉伯联合酋长国', '摩洛哥', '哈萨克斯坦', '卢旺达', '巴基斯坦', '约旦', '卡塔尔', '黎巴嫩', '巴哈马', '伊朗', '伊拉克', '刚果（布）', '朝鲜', )
    country_map = dict()
    for c in FIXED_COUNTRYS :
        country_map[c] = c
    for cm in UPDATE_COUNTRYS :
        country_map[cm[0]] = cm[1]
    for c in SOUTHEAST_ASIA_COUNTRYS :
        country_map[c] = '东南亚'
    for c in EASTERN_EUROPE_COUNTRYS :
        country_map[c] = '东欧'
    for c in NORTHERN_EUROPE_COUNTRYS :
        country_map[c] = '北欧'
    for c in OTHER_EUROPE_COUNTRYS :
        country_map[c] = '欧洲其他'
    for c in NORTH_AMERICA_COUNTRYS :
        country_map[c] = '北美'
    for c in LATIN_AMERICA_COUNTRYS :
        country_map[c] = '南美洲'
    for c in OTHER_AAL_COUNTRYS :
        country_map[c] = '亚非其他'

    BIG_COUNTRYS = set()
    BIG_COUNTRYS.update(FIXED_COUNTRYS)
    BIG_COUNTRYS.update(('东南亚', '东欧', '北欧', '欧洲其他', '北美', '南美洲', '亚非其他', ))
    return (country_map, BIG_COUNTRYS)

class nfo_filer :
    NODE_NAME_TAG = 'tag'
    NODE_NAME_GENRE = 'genre'
    NODE_NAME_ARTIST = 'actor'
    NODE_NAME_ARTIST_CHILD_NAME = 'name'
    NODE_NAME_ARTIST_CHILD_ORI_NAME = 'role'
    NODE_NAME_SERIES = 'series'
    NODE_NAME_SET = 'set'
    NODE_NAME_SET_CHILD_NAME = 'name'
    def get_tvshow_nfo(path_name : str) -> str :
        nfo_file = ''
        nfo_file = os.path.join(path_name, 'tvshow.nfo')
        if not xbmcvfs.exists(nfo_file) :
            nfo_file = ''
        return nfo_file
    #取得视频文件对应的nfo文件
    def get_video_nfo(video_name : str) -> str :
        nfo_file = ''
        head_tail = os.path.split(video_name)
        pure_name = os.path.splitext(head_tail[1])[0]
        nfo_file = pure_name + '.nfo'
        nfo_file = os.path.join(head_tail[0], nfo_file)
        if not xbmcvfs.exists(nfo_file) :
            nfo_file = ''
            vf_wrap = vfs_wrapper(head_tail[0])
            videos = vf_wrap.get_video_files()
            if len(videos) == 1 and videos[0].lower() == video_name.lower() :   #当前目录下只有video_name这一个视频文件
                nfo_file = os.path.join(head_tail[0], 'movie.nfo')
                if not xbmcvfs.exists(nfo_file) :
                    nfo_file = ''
        return nfo_file

    def __init__(self) :
        self.file_name = ''
        self.tree = None
        self.root = None
        self.type = 0           #=1,电影。=2,电视剧(总览)。=3，电视集。=0，未知。        
        self.changed = False
        return
    def load(self, path_file) -> bool :
        #parser = etree.XMLParser(recover=True, remove_blank_text=True) 
        parser = etree.XMLParser(encoding='utf-8') 
        vf_wrap = vfs_wrapper(path_file)
        nfo_data = vf_wrap.read()
        tree = etree.fromstring(nfo_data, parser=parser)
        if tree is None :
            return False
        
        #root = tree.getroot()
        root = tree
        type = 0
        if (root is None) or (root.tag is None) :
            return False
        if root.tag.lower() == 'movie' :
            type = 1
        elif root.tag.lower() == 'tvshow' :
            type = 2
        elif root.tag.lower() == 'episodedetails' :
            type = 3

        if type > 0 :
            self.type = type
            self.tree = tree
            self.root = root
            self.file_name = path_file
            self.changed = False
        return type > 0
    def get_file_name(self) :
        return self.file_name
    def is_movie(self) :
        return self.type == 1
    def is_tvshow(self) :
        return self.type == 2
    def is_episode(self) :
        return self.type == 3
    def save(self) -> str :
        data = ''
        #to do : 内部先做规整化处理，比如去掉actor的type
        if self.tree is not None :
            data = etree.tostrings(self.tree, pretty_print=True, encoding="utf-8")
        return data
    #删除子节点。如MustOnlyOne=True，则只在key只有一个的情况下才执行删除操作。
    #返回删除的元素个数。
    def del_sub_items(self, parent, key, MustOnlyOne=True) :
        assert(parent is not None)
        assert(key != '')
        count = 0
        nodes = parent.findall(key)
        if nodes is not None :
            if MustOnlyOne and len(nodes) != 1 :
                return -1
            for node in nodes :
                parent.remove(node)
                count += 1
        return count

    #取得子节点的text值    
    def get_child_text(node, key) -> str :
        value = ''
        if node is not None :
            sub_node = node.find(key)
            if (sub_node is not None) and (sub_node.text is not None) :
                value = sub_node.text.strip()
        return value
    def get_node_text(node) :
        value = ''
        if node is not None and node.text is not None :
            value = node.text.strip()
        return value
    #设置子节点的text值
    #如子节点不存在，则添加到最后一个NewAfterKey的后面。如NewAfterKey=''或者不存在，则添加到node的最后面
    def set_child_text(self, node, key, value, NewAfterKey='') :
        changed = False
        if node is not None :
            sub_node = node.find(key)
            if sub_node is None :       #子节点不存在，需要添加
                sn = etree.Element(key)
                sn.text = value
                if NewAfterKey == '' :  #用户没有指定添加位置，添加在末尾
                    node.append(sn)
                else :
                    index = nfo_filer.get_node_index(node, NewAfterKey, True)
                    if index >= 0 :     #找到了用户指定的添加位置
                        node.insert(index +1, sn)
                    else :              #用户指定了不存在的添加位置，还是添加在末尾
                        node.append(sn)
                changed = True
            elif sub_node.text is None or sub_node.text != value :
                sub_node.text = value
                changed = True
        return changed
    #设置子节点的text值
    #如子节点不存在则添加。First优先于PosList，都不指定或PosList找不到则添加到尾部。
    def set_child_text_ex(self, node, key, value, First=False, PosList=None) :
        changed = False
        if (node is None) or (key == '') :
            return False
        sub_nodes = node.findall(key)
        if (sub_nodes is None) or (len(sub_nodes) == 0) :
            sub_node = etree.Element(key)
            sub_node.text = value
            if First :
                node.insert(0, sub_node)
                changed = True
            else :
                if nfo_filer._add_node(node, key, value, PosList) :
                    changed = True
        elif len(sub_nodes) == 1 :
            sub_node = sub_nodes[0]
            if sub_node.text is None or sub_node.text != value :
                sub_node.text = value
                changed = True
        else :
            #print('异常：nfo(%s)的node(%s)有多个(%s)子节点，无法进行赋值=(%s)操作。' %(self.file_name, node.tag, key, value))
            pass
        return changed

    def get_title(self) :
        return self._get_value('title')
    def get_num(self) :
        return self._get_value('num')
    def get_country(self) :
        return self._get_value('country')
    def get_year(self) :
        return self._get_value('year')
    def get_plot(self) :
        return self._get_value('plot')
    def get_original_title(self) :
        return self._get_value('originaltitle')
    def get_sort_title(self) :
        return self._get_value('sorttitle')
    def set_sort_title(self, value) :
        INSERT_AFTER = ('originaltitle', 'title', )
        self.set_child_text_ex(self.root, 'sorttitle', value, PosList=INSERT_AFTER)
        return
    #剧集nfo取得电视剧title
    def get_show_title(self) -> str :
        return self._get_value('showtitle')
    def get_media_file(self) :
        return self._get_value('original_filename')
    #从tvshow的nfo文件里读取全部季信息, key为字符串形式的季序号，value为字符串形式的季名称
    def get_season_dict(self) -> dict :
        seasons = dict()
        for s in self.root.findall('namedseason') :
            num = str(s.attrib.get('number'))
            name = nfo_filer.get_node_text(s).strip()
            if num.isdigit() and name != '' :
                if num in seasons :
                    print('异常：nfo文件(%s)有重复的季信息，num=%s, name=%s.' %(self.file_name, num, name))
                assert(num not in seasons)
                seasons[num] = name
            else :
                print('异常：nfo文件(%s)的季信息异常，num=%s, name=%s.' %(self.file_name, num, name))
                assert(False)
        return seasons

    #从episode的nfo文件里读取季信息
    def get_season(self) -> int :
        s = -1
        season = self._get_value('season')
        if season.isdigit() :
            s = int(season)
        return s
    #从episode的nfo文件里读取季信息
    def get_episode(self) -> int :
        e = -1
        episode = self._get_value('episode')
        if episode.isdigit() :
            e = int(episode)
        return e
    def get_episode_info(self) -> str :
        info = ''
        s = self.get_season()
        e = self.get_episode()
        if s >= 0 and e >= 0 :
            info = 'S{:0>2d}E{:0>2d}'.format(s, e)
        return info
    #kind type=movie/tvshow/season/episode
    def get_thumb_dict(self, kind='movie', num=-1) -> dict :
        thumbs = dict()
        thumb_nodes = self.root.findall("thumb")
        for t in thumb_nodes :
            sort = t.attrib.get('aspect')
            type = t.attrib.get('type')
            season = t.attrib.get('season')
            url = nfo_filer.get_node_text(t).strip()
            if sort == '' and len(thumb_nodes) == 1 :
                sort = 'thumb'
            if sort != '' and url != '' :
                if kind == 'season' :
                    if type is None :
                        continue
                    sn = -1
                    try :
                        sn = int(season)
                    except :
                        print('异常：season=%s非整数, kind=%s, aspect=%s, type=%s。' %(season, kind, sort, type))
                        assert(False)
                    if type == 'season' and (num == -1 or  num == sn)  :
                        assert(sort not in thumbs)
                        thumbs[sort] = url
                else :
                    if type is None or type == '' :
                        assert(sort not in thumbs)
                        thumbs[sort] = url
        return thumbs
    def get_thumbs_info(self) :
        info = ''
        for thumb in self.root.findall("thumb") :
            info += etree.tostring(thumb, encoding='utf-8').decode('utf-8')
        return info
    def get_thumb_poster_info(self) :
        info = ''
        thumb = self.root.find("thumb[@aspect='poster']")
        if thumb is not None :
            info = etree.tostring(thumb, encoding='utf-8').decode('utf-8')
        return info
    def get_fanart_info(self) :
        info = ''
        fanart = self.root.find('fanart')
        if fanart is not None :
            info = etree.tostring(fanart, encoding='utf-8').decode('utf-8')
        return info
    def get_outline(self) :
        return self._get_value('outline')
    def get_tagline(self) :
        return self._get_value('tagline')
    def get_MPAA(self) :
        return self._get_value('mpaa')
    def get_director(self) :
        return self._get_value('director')
    def get_top250(self) :
        top_n = 0
        value = self._get_value('top250')
        if value.isdigit() :
            top_n = int(value)
        return top_n
    #电视剧是否完结。只对tvshow的nfo文件有效。Continuing/Ended
    def get_status(self) :
        return self._get_value('status')
    #预告片
    def get_trailer(self) :
        return self._get_value('trailer')
    #首映时间，字符串格式的日期：'2021-04-18'
    def get_premiered(self) :
        return self._get_value('premiered')
    def get_studios(self, SPLIT=' / ') :
        return self._get_values('studio', SPLIT)
    def get_studio_list(self) -> list :
        return self._get_value_list('studio')
    def get_countries(self, SPLIT=' / ') :
        return self._get_values('country', SPLIT)
    def get_country_list(self) -> list :
        return self._get_value_list('country')
    def get_minutes(self) :
        min = 0
        s_min = self._get_value('runtime')
        if s_min.isdecimal() :
            min = int(s_min)
        return min
    def get_credits(self, SPLIT=' / ') :
        return self._get_values('credits', SPLIT)
    def get_credit_list(self) -> list :
        return self._get_value_list('credits')
    def get_genres_str(self, SPLIT=' / ') :
        return self._get_values('genre', SPLIT)
    def get_genre_list(self) -> list :
        return self._get_value_list('genre')
    def _get_value(self, key) -> str :
        return nfo_filer.get_child_text(self.root, key)
    def _get_values(self, key, split) :
        values = ''
        for v in self._get_value_list(key) :
            if values != '' :
                values += split
            values += v
        return values
    def _get_value_list(self, key : str) -> list :
        values = list()
        for node in self.root.findall(key) :
            value = nfo_filer.get_node_text(node).strip()
            if value != '' :
                values.append(value)
        return values

    #取得合集名字，如不属于合集则返回''    
    def get_collect_name(self) :
        return self.get_set_name()
    def get_set_name(self) :
        return nfo_filer.get_child_text(self.root, 'set')
    def get_set_info(self) : 
        name = ''
        overview = ''
        set_node = self.root.find('set')
        if set_node is not None :
            name = nfo_filer.get_child_text(set_node, 'name')
            overview = nfo_filer.get_child_text(set_node, 'overview')
            if name == '' and set_node.text is not None :
                name = set_node.text.strip()
        return name, overview
    def get_series_name(self) :
        return nfo_filer.get_child_text(self.root, 'series')
    #取得唯一的艺人名，如存在多个艺人则返回''
    def get_one_actor_name(self) :
        name = ''
        actors_node = self.root.findall('actor')
        if len(actors_node) == 1 :
            actor_node = actors_node[0]
            name = nfo_filer.get_child_text(actor_node, 'name')
        return name
    #取得评分（电影）('imdb', '6.5', '10247')。平台，分数，投票数。
    def get_ratings(self) :
        result = list()
        ratings = self.root.findall("ratings/rating")
        if ratings is not None :
            for r in ratings :
                name = r.attrib.get('name')
                value = nfo_filer.get_child_text(r, 'value')
                votes = nfo_filer.get_child_text(r, 'votes')
                result.append((name, value, votes))
        return result

    def get_user_rating(self) -> float :
        fr = float(0.0)
        rate = nfo_filer.get_child_text(self.root, 'userrating')
        if rate != '' :
            try :
                fr = round(float(rate), 1)
            except :
                pass
        return fr

    def get_scrapers(self) -> list :
        result = list()
        infos = self.root.findall('uniqueid')
        for i in infos :
            if i.text is not None :
                id = i.text.strip()
                name = i.attrib.get('type')
                result.append((name, id))
        return result
    #取得评分(AV)
    def get_rating(self) -> float :
        rating = 0
        rate_str = nfo_filer.get_child_text(self.root, 'rating')
        if rate_str != '' :
            rating = float(rate_str)
            rating = round(rating, 2)
        return rating
    
    #删除子节点的原子操作。
    #MustOnlyOne，只存在一个key节点时才执行删除操作
    def _del_nodes(parent, key, MustOnlyOne=True) -> int:
        count = 0
        if parent is None or key == '' :
            return -1
        nodes = parent.findall(key)
        if nodes is None or len(nodes) == 0:
            return 0
        if len(nodes) > 1 and MustOnlyOne :
            return -len(nodes)
        for n in nodes :
            parent.remove(n)
            count += 1
        return count
    #添加子节点的原子操作。
    #NonExist，必须不存在和key同名的节点才添加。
    def _add_node(parent, key, value, after_list, NonExist=True) :
        added = False
        if parent is None :
            return False
        if key == '' :
            return False
        if NonExist and parent.find(key) is not None :
            return False
        node = etree.Element(key)
        if value != '' :
            node.text = value
        if after_list is not None :
            for after_key in after_list :
                after_key = after_key.strip()
                if after_key == '' :
                    continue
                index = nfo_filer.get_node_index(parent, after_key, TAIL=True)
                if index >= 0 :     #找到了用户指定的添加位置
                    parent.insert(index+1, node)
                    added = True
                    break
        if not added :
            parent.append(node)
            added = True
        return added
    def is_same_value(nodes, str_list) :
        samed = False
        if len(nodes) == len(str_list) and len(nodes) == 0 :
            return True
        if len(nodes) != len(str_list) :
            return False
        for node in nodes :
            if node.text not in str_list :
                return False
        return True
    def repalce_str_nodes(parent, key, str_list, after_list) :
        if key is None or key == '' :
            return False
        nodes = parent.findall(key)
        if nfo_filer.is_same_value(nodes, str_list) :
            return False
        nodes = []
        for str in str_list :
            node = etree.Element(key)
            node.text = str
            nodes.append(node)
        return nfo_filer.replace_nodes(parent, key, nodes, after_list)
    def replace_nodes(parent, key, new_nodes, after_list) :
        if parent is None or key is None or key == '' :
            return False
        insert_pos = -1
        key_index = nfo_filer.get_node_index(parent, key, TAIL=False)
        if key_index >= 0 :
            n_result = nfo_filer._del_nodes(parent, key, MustOnlyOne=False)
            if n_result < 0 :
                return False
            insert_pos = key_index
        else :
            for after_key in after_list :
                after_index = nfo_filer.get_node_index(parent, after_key, TAIL=True)
                if after_index >= 0 :
                    insert_pos = after_index + 1
                    break
        
        if insert_pos >= 0 :    #找到了插入位置
            for new_node in new_nodes :
                parent.insert(insert_pos, new_node)
                insert_pos += 1
        else :                  #加入在尾部
            for new_node in new_nodes :
                parent.append(new_node)
        return True

    #get和set符合emby规范
    def emby_get_set_value(self, SetNode=None) :
        value = ''
        set_node = SetNode
        if set_node is None :
            set_node = self.root.find(nfo_filer.NODE_NAME_SET)
        if set_node is not None :
            if set_node.text is not None :
                value = set_node.text.strip()       #优先取set节点本身的text
            if value == '' :
                name_node = set_node.find('name')
                if name_node is not None and name_node.text is not None :
                    value = name_node.text.strip()      #次取name子节点的text
        return value
    def _set_set_value(self, value, SetNode=None) :
        changed = False
        set_node = SetNode
        if set_node is None :
            set_node = self.root.find(nfo_filer.NODE_NAME_SET)
        if set_node is not None :
            name_node = set_node.find('name')
            if name_node is not None :          #优先置name子节点的text
                if value != name_node.text :
                    name_node.text = value
                    changed = True
            else :                              #次置set节点本身的text
                if value != set_node.text :
                    set_node.text = value
                    changed = True
        return changed

    #删除所有的标签节点
    def del_tags(self) :
        if self.root.find('tag') is None :
            return False
        for t_node in self.root.findall('tag') :
            self.root.remove(t_node)
            self.changed = True
        return True

    def get_node_index(parent_node, child_name, TAIL=True) :
        index = -1
        begin = -1
        pos = -1
        for i in parent_node :
            pos += 1
            if i.tag.strip().lower() == child_name.strip().lower() :
                index = pos
                if not TAIL :
                    break
            if (index >= 0) and (i.tag.strip().lower() != child_name.strip().lower()) :
                assert(TAIL)
                break
        return index

    def get_insert_pos(parent_node, key, AfterPosList=None) :
        index = nfo_filer.get_node_index(parent_node, key, TAIL=True)
        if index < 0 and AfterPosList is not None :      #不存在key节点
            for ak in AfterPosList :
                index = nfo_filer.get_node_index(parent_node, ak, TAIL=True)
                if index >= 0 :
                    break
        return index

    def video_file_exist(self) :
        exist = False
        file_name = self.get_media_file()
        if file_name != '' :
            dir_name = os.path.dirname(self.file_name)
            video_file = os.path.join(dir_name, file_name)
            if xbmcvfs.exists(video_file) :
                exist = True
        return exist

    def _save_original_country(self) :
        original = ''
        index = nfo_filer.get_node_index(self.root, 'country', True)
        #print('country node的index=%d.' %index)
        node = self.root.find('originalcountry')
        if node is not None and node.text is not None :
            original = node.text.strip()
        if original == '' :
            nodes = self.root.findall('country')
            for n in nodes :
                if n.text is not None and n.text.strip() != '' :
                    original += n.text.strip() + '|'
            if original[-1] == '|' :
                original = original[:len(original)-1]
            if original != '' :
                on = etree.Element('originalcountry')
                on.text = original
                if index >= 0 :
                    self.root.insert(index +1, on)
                else :
                    print('异常：nfo文件(%s)定位国家失败，无法修改。' %self.file_name)
                #self.root.append(on)
        return

    def remove_same_country(self) :
        removed = False
        #删除相同的国家信息，debug
        c_set = set()
        rm_list = []
        c_nodes = self.root.findall('country')
        for c in c_nodes :
            if c.text is None :
                continue
            if c.text not in c_set :
                c_set.add(c.text)
            else :
                rm_list.append(c)
        for  node in rm_list :
            print('通知1：nfo文件(%s)删除重复的国家=%s.' %(self.file_name, node.text))
            self.root.remove(node)
            self.changed = True
            removed = True
        return removed

    #用老大哥模式更新国家信息
    def update_country_info(self, country_map, merged_set) :
        changed = False
        changed = self.remove_same_country()
        c_set = set()
        rm_list = []
        c_nodes = self.root.findall('country')
        for c in c_nodes :
            if c.text is not None :
                old_c = c.text.strip()
                if old_c == '' :        #剧的集没有国家信息
                    continue
                if (old_c not in country_map) and (old_c not in merged_set)  :
                    print('异常：nfo(%s)发现未知的国家信息=%s.' %(self.file_name, old_c))
                big_c = country_map.get(old_c, old_c)
                if big_c != c.text :
                    if big_c not in c_set :
                        self._save_original_country()
                        c.text = big_c
                        c_set.add(big_c)
                    else :
                        rm_list.append(c)
                    changed = True
        for c in rm_list :
            print('通知2：nfo文件(%s)删除重复的国家=%s.' %(self.file_name, c.text))
            self.root.remove(c)
        if changed :
            self.changed = True
        return changed
    def get_tags(self) -> list :
        tag_list = []
        tags_node = self.root.findall('tag')
        for t_node in tags_node :  
            if t_node.text is not None :
                tag = t_node.text.strip()
                if tag != '' :
                    tag_list.append(tag)
        return tag_list
    def get_genres(self) -> list :
        return self.get_genre_list()


