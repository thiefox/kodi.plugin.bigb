# -*- coding: UTF-8 -*-

import sys
import os
#from tkinter import messagebox
import logging
import time
from datetime import datetime
#import urllib
import json
import re
#from tkinter.messagebox import NO
#from urllib import parse

from urllib.parse import urlencode, parse_qsl, unquote
from vfs_wrapper import vfs_wrapper
#from enum import Enum

#from cv2 import sort

import xbmc
import xbmcgui
import xbmcplugin
import xbmcvfs

#import bigb_window
import pinyin_info
import nfo_filer

ROOTS = (('FGT', 'nfs://10.10.0.3/volume2/BB8/FGT'), ('CHD', 'nfs://10.10.0.3/volume2/BB8/CHD'), ('WIKI', 'nfs://10.10.0.3/volume2/BB8/WIKI/电视剧'), )
MOVIE_ROOTS = ('nfs://10.10.0.3/volume2/BB8/FGT', 'nfs://10.10.0.3/volume2/BB8/CHD', )
TVSHOW_ROOTS = ('nfs://10.10.0.3/volume2/BB8/WIKI/电视剧', )

BIGB_FANART = 'nfs://10.10.0.3/volume2/BB8/CHD/fanart.jpg'

EPISODE_FORMAT = r'(S\d{2}E\d{2})'

#电影根目录=1，电视根目录=2，未知目录=0
def get_root_type(path : str) -> int :
    result = 0
    for MR in MOVIE_ROOTS :
        if path.lower().find(MR.lower()) == 0 :
            result = 1
            break
    if result == 0 :
        for TR in TVSHOW_ROOTS :
            if path.lower().find(TR.lower()) == 0 :
                result = 2
    return result



def get_time_info(timestamp) -> str :
    info = ''
    if timestamp > 0 :
        timeStruct = time.localtime(timestamp)
        info = time.strftime('%Y-%m-%d %H:%M:%S', timeStruct)
    return info

def rip_episode_info(file_name : str) -> str :
    info = ''
    pure_name = os.path.splitext(file_name)[0]
    ep_info = re.search(EPISODE_FORMAT, pure_name, re.I)
    if ep_info is not None :
        info = ep_info.group().upper()
    if info != '' :
        assert(len(info) == 6)
    return info

class PY_data :
    #PY_MAP_FILE = '.PY_info'
    SORT_MAP_FILE = '.BB_sortinfo'
    DIR_DICT_NAME = 'DIR'
    VIDEO_DICT_NAME = 'VIDEO'
    SORT_CUSTOM_LEVEL_1 = ('#', '0')
    SORT_CUSTOM_LEVEL_2 = ('【', '1')
    SORT_CUSTOM_LEVEL_3_ENG = '2'
    SORT_CUSTOM_LEVEL_CHS = '7'
    #FIXED_PY_MAP = (('#', '0'), ('【', '1'), )
    #PY_LENGTH = 3
    PY_LENGTH = 0       #取全部长度
    def __init__(self, path) -> None :
        self.path = path
        return
    def rip_year(dir_name : str) -> int :
        year = 0
        pos = dir_name.rfind('.')
        if pos > 0 :
            data = dir_name[pos+1:]
            if len(data) == 4 and data.isdigit() :
                year = int(data)
        return year
    def rip_display_name(dir_name : str) -> str :
        display = ''
        if PY_data.rip_year(dir_name) > 0 :
            pos = dir_name.rfind('.')
            display = dir_name[:pos]
        else :
            display = dir_name
        return display
    #BIGB的电影都以四位数年份结尾
    def is_single_movie_dir(path : str) -> bool :
        dir_name = os.path.split(path)[1]
        return PY_data.rip_year(dir_name) > 0
    def get_art_pics(path : str, root_type : int) -> dict :
        pics = dict()
        if root_type == 0 or root_type == 1 :
            if PY_data.is_single_movie_dir(path) :
                pics = vfs_wrapper._get_dir_general_pics(path)
        elif root_type == 2 :       #电视根目录
            nfo_file = nfo_filer.nfo_filer.get_tvshow_nfo(path)
            if nfo_file != '' :
                pics = vfs_wrapper.get_tvshow_pics(path)
            else :
                path_info = os.path.split(path)
                parent_dir = path_info[0]
                nfo_file = nfo_filer.nfo_filer.get_tvshow_nfo(parent_dir)
                if nfo_file != '' :
                    sn = pinyin_info.rip_season_num(path_info[1])
                    if sn >= 0 :
                        pics = vfs_wrapper.get_season_pics(parent_dir, sn)
        return pics

    #返回子目录列表和视频文件列表的列表（嵌套map）
    def _gen_sub_items(self) -> dict :
        dir_map = dict()
        video_map = dict()
        root_type = get_root_type(self.path)
        dirs, files = xbmcvfs.listdir(self.path)
        for dir in dirs :
            if vfs_wrapper.is_hidden_items(dir) :   #忽略系统目录
                continue
            input = None
            if PY_data.PY_LENGTH == 0 :
                input = dir
            else :
                input = dir[:PY_data.PY_LENGTH]
            
            if input[0] == PY_data.SORT_CUSTOM_LEVEL_1[0] :
                input = PY_data.SORT_CUSTOM_LEVEL_1[1] + input
            elif input[0] == PY_data.SORT_CUSTOM_LEVEL_2[0] :
                input = PY_data.SORT_CUSTOM_LEVEL_2[1] + input
            elif pinyin_info.is_eng_ascii(input[0]) :
                input = PY_data.SORT_CUSTOM_LEVEL_3_ENG + input
            else :
                input = PY_data.SORT_CUSTOM_LEVEL_CHS + input
            '''
            if pinyin_info.is_eng_ascii(input[0]) :     #第一个为ascii字符
                input = '2' + input
            else :
                for fp in PY_data.FIXED_PY_MAP :
                    if input[0] == fp[0] :
                        input = fp[1] + input[1:]
                        break
            '''
            py = pinyin_info.get_fixed_PINYIN(input, PY_data.PY_LENGTH, FIRST_SORTED=True)
            #logging.info('the PY of dir{} is ({}).'.format(dir, py))
            info_dict = dict()
            info_dict['sorttitle'] = py
            info_dict['year'] = PY_data.rip_year(dir)
            date_add = ''
            path_dir = os.path.join(self.path, dir)
            playable_file = vfs_wrapper.check_single_playable_file(path_dir)
            st = xbmcvfs.Stat(path_dir)
            modified = st.st_mtime()
            if modified > 0 :
                date_add = get_time_info(modified)
            info_dict['dateadded'] = date_add
            if playable_file != '' :
                info_dict['playable_file'] = playable_file
                path_file = os.path.join(path_dir, playable_file)
                nfo_file = nfo_filer.nfo_filer.get_video_nfo(path_file)
                if nfo_file != '' :
                    nfo_obj = nfo_filer.nfo_filer()
                    if nfo_obj.load(nfo_file) :
                        plot = nfo_obj.get_plot()
                        if plot != '' :
                            info_dict['plot'] = plot
            else :
                nfo_file = nfo_filer.nfo_filer.get_tvshow_nfo(path_dir)
                if nfo_file != '' :
                    nfo_obj = nfo_filer.nfo_filer()
                    if nfo_obj.load(nfo_file) :
                        plot = nfo_obj.get_plot()
                        if plot != '' :
                            info_dict['plot'] = plot
            dir_map[dir] = info_dict      

        for file in files :
            if vfs_wrapper.is_video_file(file) :    #视频文件
                info_dict = dict()
                if root_type == 1 :         #电影根目录下的视频
                    info_dict['sorttitle'] = file
                    path_file = os.path.join(self.path, file)
                    nfo_file = nfo_filer.nfo_filer.get_video_nfo(path_file)
                    if nfo_file != '' :
                        nfo_obj = nfo_filer.nfo_filer()
                        if nfo_obj.load(nfo_file) :
                            plot = nfo_obj.get_plot()
                            if plot != '' :
                                info_dict['plot'] = plot
                elif root_type == 2 :     #电视剧根目录下的视频
                    episode = rip_episode_info(file)
                    if episode != '' :      #萃取到剧集信息SXXEXX
                        path_file = os.path.join(self.path, file)
                        nfo_file = nfo_filer.nfo_filer.get_video_nfo(path_file)
                        if nfo_file != '' :
                            disp = episode
                            nfo_obj = nfo_filer.nfo_filer()
                            if nfo_obj.load(nfo_file) :
                                title = nfo_obj.get_title()
                                if title != '' :
                                    disp += ' - ' + title    
                                plot = nfo_obj.get_plot()
                                if plot != '' :
                                    info_dict['plot'] = plot
                            info_dict['sorttitle'] = disp
                        else :
                            info_dict['sorttitle'] = episode
                    else :
                        info_dict['srottitle'] = file
                else :                  #电影根目录下的视频
                    info_dict['sorttitle'] = file
                video_map[file] = info_dict
        sub_map = dict()
        if len(dir_map) > 0 :
            sub_map[PY_data.DIR_DICT_NAME] = dir_map
        if len(video_map) > 0 :
            sub_map[PY_data.VIDEO_DICT_NAME] = video_map
        return sub_map

    #返回根目录的时间戳字符串，到分钟
    def get_lm_time_minute(self) -> str :
        lm = ''
        st = xbmcvfs.Stat(self.path)
        modified = st.st_mtime()
        if modified > 0 :
            timeStruct = time.localtime(modified)
            lm = time.strftime('%Y-%m-%d %H:%M', timeStruct)
        return lm

    def _write_sort_file(self, subs : dict) :
        #logging.info('begin _write_sort_file...')
        file_name = os.path.join(self.path, PY_data.SORT_MAP_FILE)
        info_map = dict()
        '''
        now_t = datetime.now()
        lm = datetime.strftime(now_t, '%Y-%m-%d %H-%M')
        '''
        lm = self.get_lm_time_minute()
        #logging.info('base dir {} LM={}.'.format(self.path, lm))
        info_map[lm] = subs
        #tp = xbmcvfs.translatePath(file_name)
        vp = xbmcvfs.validatePath(file_name)
        #logging.info('sort cache file name={}.'.format(file_name))
        #logging.info('vp sort cache file name={}.'.format(vp))
        with xbmcvfs.File(vp, 'w') as f:         #test content with utf-8
            s_data = json.dumps(info_map, ensure_ascii=False, indent=1)
            #logging.info('write data size={}.'.format(len(s_data)))
            result = f.write(s_data)
            '''
            if result :
                logging.info('write sort file success.')
            else :
                logging.error('write sort file failed!')
            '''
        #logging.info('end _write_sort_file.')        
        return

    def _read_sort_file(self) -> dict :
        #logging.info('begin _read_sort_file...')
        file_name = os.path.join(self.path, PY_data.SORT_MAP_FILE)
        if not xbmcvfs.exists(file_name) :
            #logging.info('sort cache not exists.')
            return None
        s_time = ''
        sub_map = None
        with xbmcvfs.File(file_name, 'r') as f:         #test content with utf-8
            s_data = f.read()
            #xbmc.log(msg='print cache sort data...', level=xbmc.LOGINFO)
            #xbmc.log(msg=s_data, level=xbmc.LOGINFO)
            #logging.info('read data from sort cache file, len={}.'.format(len(s_data)))
            try :
                info_map = json.loads(s_data, encoding='utf-8')
                if len(info_map) == 1 :
                    for info in info_map :
                        s_time = info
                        sub_map = info_map[info]
                else :
                    #logging.error('sort data size failed, count={}.'.format(len(info_map)))
                    pass
            except Exception as err :
                #logging.error('load py cache file failed, ignore...')
                sub_map = None
        if sub_map is not None :
            #检查目录时间戳和文件时间戳是否一致
            dir_lm = self.get_lm_time_minute()
            #logging.info('dir {} LM={}, py file LM={}.'.format(self.path, dir_lm, s_time))
            if s_time != dir_lm :       #缓存建立时间和目录最后修改时间不一致
                sub_map = None   #放弃缓存
                #logging.error('LM different, ignore sort cache.')
            #logging.info('end _read_sort_file.')
        return sub_map

    #获取子目录的排序信息
    def get_sub_items(self, fresh : bool = False) -> dict :
        sub_map = None 
        if not fresh :
            sub_map = self._read_sort_file()       #优先从缓存读取
        if sub_map is None :                 #缓存不存在或过期
            sub_map = self._gen_sub_items()
            if sub_map is not None :
                self._write_sort_file(sub_map)
            else :
                #logging.error('_gen_sub_items return None.')
                pass
        else :
            #logging.info('sort cache found.')
            pass
        return sub_map      

class PY_sort_file_system :
    def __init__(self) -> None:
        #logging.info('PY_sort_file_system obj init...')
        self.content_type = 'movies'
        self.path = ''
        self.rebuild = False
        self.add_on = sys.argv[0]
        self.handle = int(sys.argv[1])
        #logging.info('the raw params data={}.'.format(sys.argv[2]))
        self.params = dict(parse_qsl(sys.argv[2][1:]))
        #logging.info('param count={}.'.format(len(self.params)))
        for param in self.params :
            dp = unquote(self.params[param], encoding='utf-8', errors='replace') 

            #logging.info('param {}={}, decode={}.'.format(param, self.params[param], dp))
            
            if param.lower() == 'path' :
                self.path = self.params[param]
                self.path = unquote(self.path, encoding='utf-8', errors='replace') 
                self.path = xbmcvfs.validatePath(self.path)
                #logging.info('find path param, value={}.'.format(self.path))
            if param.lower() == 'rebuild' :
                #logging.info('find rebuld param, value={}.'.format(self.params[param]))
                if self.params[param] == '1' :
                    self.rebuild = True
        return

    def run(self) :
        #logging.info('PY_sort_fs run(type(path)={})...'.format(type(self.path)))
        #logging.info('PY_sort_fs run(path={})...'.format(self.path))
        if self.path == '' :
            self.router()
        else :
            if self.rebuild :
                self._rebuild()
            else :
                self._list_dir(self.path)
        return

    #path_name为nfs://打头的全路径目录名
    def gen_url(self, path_name : str) -> str :
        #params = {'action':'_list_dir', 'path':path_name, 'content_type':'movies'}
        #params = {'action':'listdir', 'path':'abc', 'contenttype':'movies'}
        #注：action和category是必要的参数，不然会导致kodi报错
        params = {'action':'listdir', 'category':'video', 'path':path_name}
        url = self.add_on + '?' + urlencode(params)
        return url

    def gen_rebuild_syntax(self, path_name : str) -> str :
        params = {'action':'listdir', 'category':'video', 'path':path_name, 'rebuild':'1' }
        params = urlencode(params)
        syntax = 'RunPlugin({0}?{1})'.format(self.add_on, params)
        return syntax

    def _rebuild(self) : 
        info_file = os.path.join(self.path, PY_data.SORT_MAP_FILE)
        #logging.info('old cache file={}...'.format(info_file))
        info_file = xbmcvfs.validatePath(info_file)
        #logging.info('begin del cache file={}...'.format(info_file))
        if not vfs_wrapper.del_file(info_file) :
            #logging.error('del bigb info cache file failed, file={}.'.format(info_file))
            pass
        self._list_dir(self.path, fresh=True)
        return

    #列出path_name目录下的所有子目录和文件, UI操作
    def _list_dir(self, root : str, fresh : bool = False) :
        if not xbmcvfs.exists(root) : 
            #logging.error('root dir failed, path=({}) is not a legal path.'.format(root))
            return
        st = xbmcvfs.Stat(root)
        modified = st.st_mtime()
        info = get_time_info(modified)
        #logging.info('the root dir({}) LM = {}.'.format(root, info))
    
        #设置内容类别，'movies/videos'
        root_type = get_root_type(root) 
        #logging.info('cur dir={}, type={}.'.format(root, root_type))

        xbmcplugin.setPluginFanart(self.handle, BIGB_FANART)
        dir_name = os.path.split(root)[1]
        display_name = PY_data.rip_display_name(dir_name)
        xbmcplugin.setPluginCategory(self.handle, display_name)
        #按显示标题排序
        xbmcplugin.addSortMethod(self.handle, xbmcplugin.SORT_METHOD_VIDEO_SORT_TITLE)  #排序标题，检查跟SORT_TITLE有什么不同
        xbmcplugin.addSortMethod(self.handle, xbmcplugin.SORT_METHOD_VIDEO_YEAR)        #电影上映年份
        xbmcplugin.addSortMethod(self.handle, xbmcplugin.SORT_METHOD_DATEADDED)         #检查跟第二个哪个是加入时间？

        py_info = PY_data(root)
        sub_map = py_info.get_sub_items(fresh=fresh)

        #logging.info('all sub dir with sort count={}.'.format(len(sub_map)))
        dir_type = 0        #目录类型（=1一个视频文件，=2多个视频文件，=3一个或多个子目录。视频文件优先于子目录）
        listing = []		#节点list（每个节点即界面中显示的一项）
        if py_info.VIDEO_DICT_NAME in sub_map : #视频文件列表
            video_map = sub_map[py_info.VIDEO_DICT_NAME]
            if len(video_map) == 1 :
                dir_type = 1
            elif len(video_map) > 1 :
                dir_type = 2
            for video in video_map :
                disp_name = video
                info_dict = video_map[video]
                if info_dict is not None :
                    if 'sorttitle' in info_dict :
                        disp_name = info_dict['sorttitle']
                path_video = os.path.join(root, video)
                #list_item = xbmcgui.ListItem(video)
                list_item = xbmcgui.ListItem(disp_name)
                
                list_item.setInfo('video', info_dict)
                pics = None
                if root_type == 1 :     #电影目录下的视频
                    pics = vfs_wrapper.get_movie_pics(path_video)
                elif root_type == 2 :   #电视目录下的视频
                    se_info = pinyin_info.rip_se_info(video)
                    if se_info is None :
                        pics = vfs_wrapper.get_episode_pics(path_video, -1)
                    else :
                        pics = vfs_wrapper.get_episode_pics(path_video, se_info[0])

                if pics is not None and len(pics) > 0 :
                    list_item.setArt(pics)
                #url = os.path.join(root, video)             #直接nfs://路径格式
                url = path_video
                listing.append((url, list_item, False))     #False非目录

        if py_info.DIR_DICT_NAME in sub_map :       #子目录列表
            dir_map = sub_map[py_info.DIR_DICT_NAME]
            if len(dir_map) > 0 :
                if dir_type == 0 :
                    dir_type = 3
            for item in dir_map :
                list_item = xbmcgui.ListItem(item)   #label名称
                info_dict = dir_map[item]       #包含拼音，加入时间，发行时间三种排序数据
                isDir = True
                playable_file = ''
                if 'playable_file' in info_dict :
                    playable_file = info_dict['playable_file']
                    del info_dict['playable_file'] 
                #assert('sorttitle' in sort_dict)
                #assert('year' in sort_dict)
                #assert('dateadded' in sort_dict)
                #logging.info('sub dir name={}, PY={}, year={}, dateadd={}.'.format(item, sort_dict['sorttitle'], sort_dict['year'], sort_dict['dateadded']))
                #year	integer (2009)
                #dateadded	string (Y-m-d h:m:s = 2009-04-05 23:16:04)
                #list_item.setInfo('video', { 'sorttitle': py, 'year': year, 'dateadded': lm })
                if info_dict is not None :
                    list_item.setInfo('video', info_dict)
                path = os.path.join(root, item)
                pics = PY_data.get_art_pics(path, root_type)
                if len(pics) > 0 :
                    list_item.setArt(pics)
                url = ''
                if playable_file == '' :
                    url = self.gen_url(path)
                    isDir = True
                    rebuild_syntax = self.gen_rebuild_syntax(path)
                    context_menu = list()
                    context_menu.append(('清除缓存', rebuild_syntax))
                    import_syntax = 'UpdateLibrary(video, {})'.format(path)
                    context_menu.append(('导入到资料库', import_syntax))
                    #logging.info('context menu rebuild syanx={}.'.format(rebuild_syntax))
                    #list_item.addContextMenuItems([('清除缓存', rebuild_syntax)])
                    list_item.addContextMenuItems(context_menu)
                else :
                    url = os.path.join(path, playable_file)
                    isDir = False
                    context_menu = list()
                    import_syntax = 'UpdateLibrary(video, {})'.format(path)
                    context_menu.append(('导入到资料库', import_syntax))
                    #logging.info('context menu rebuild syanx={}.'.format(rebuild_syntax))
                    #list_item.addContextMenuItems([('清除缓存', rebuild_syntax)])
                    list_item.addContextMenuItems(context_menu)

                listing.append((url, list_item, isDir))     #True目录

        xbmcplugin.addDirectoryItems(self.handle, listing, len(listing))		#把节点列表加入到UI

        content_type = 'videos'
        if root_type == 1 :  #电影
            content_type = 'movies'
        elif root_type == 2 :    #电视
            if dir_type == 1 or dir_type == 2 :     #有视频文件
                content_type = 'episodes'
            else :
                content_type = 'tvshows'
        else :
            content_type = 'videos'
        #logging.info('set dir ({}) content type = ({}).'.format(root, content_type))
        xbmcplugin.setContent(self.handle, content_type)

        #503,上下排列，上面文件夹图标，下面文件夹名字。
        #51, 横向单行，每列一个文件夹大图标
        #52，标准三列模式，是这个52的设置无效吗？
        #53，选项里的“平移”模式(跟51一样？)
        #54，我需要的剧集展示方式，左右两列，右边列显示视频文件的预览图列表***标题显示仍有问题
        #55，选项里的“宽列表”模式（我需要的展示）***
        #502, 两列模式，左边文件名列表，右边显示一张图片。
        #59，又是标准三列模式
        #504,505,507，508，509又是标准三列模式
        #logging.info('cur dir={}, view mode type={}.'.format(root, dir_type))
        if dir_type == 1 :      #一个视频文件
            xbmc.executebuiltin('Container.SetViewMode(%d)' %(55))
        elif dir_type == 2 :    #多个视频文件
            xbmc.executebuiltin('Container.SetViewMode(%d)' %(54))
            xbmc.executebuiltin('Container.SortDirection(ascending)')
        else :                  #没有视频文件，只有子目录
            xbmc.executebuiltin('Container.SetViewMode(%d)' %(55))
            xbmc.executebuiltin('Container.SortDirection(ascending)')
        xbmcplugin.endOfDirectory(self.handle, True)		#加入结束
        return
    
    def router(self) :
        #logging.info('PY_sort_fs router...')
        #设置内容类别，'files/movies/videos/tvshows/episodes'
        xbmcplugin.setContent(self.handle, 'movies')
        xbmcplugin.setPluginFanart(self.handle, BIGB_FANART)
        #按显示标题排序
        #按显示标题排序
        xbmcplugin.addSortMethod(self.handle, xbmcplugin.SORT_METHOD_VIDEO_SORT_TITLE)  #排序标题，检查跟SORT_TITLE有什么不同
        xbmcplugin.addSortMethod(self.handle, xbmcplugin.SORT_METHOD_DATEADDED)         #检查跟第二个哪个是加入时间？
       
        path_name = 'nfs://10.10.0.3/volume2/BB8/FGT'
        url = self.gen_url(path_name)
        li = xbmcgui.ListItem('FGT')
        xbmcplugin.addDirectoryItem(handle=self.handle, url=url, listitem=li, isFolder=True)

        path_name = 'nfs://10.10.0.3/volume2/BB8/CHD'
        url = self.gen_url(path_name)
        li = xbmcgui.ListItem('CHD')
        #logging.info('CHD inner url={}'.format(url))
        xbmcplugin.addDirectoryItem(handle=self.handle, url=url, listitem=li, isFolder=True)

        path_name = 'nfs://10.10.0.3/volume2/BB8/WIKI/电视剧'
        url = self.gen_url(path_name)
        li = xbmcgui.ListItem('电视剧')
        xbmcplugin.addDirectoryItem(handle=self.handle, url=url, listitem=li, isFolder=True)

        xbmc.executebuiltin('Container.SetViewMode(%d)' %(50))
        #已测试503/504/515无效果
        #51分两列，右边为大的文件夹图标
        #xbmc.executebuiltin('Container.SetViewMode(%d)' %(51))

        xbmcplugin.endOfDirectory(self.handle)
        return

def init() -> bool :
    LOG_FILE_NAME_BASE = 'D:\\src\\python\\win-bigma\\log\\kodi-bigb-log'
    success = False

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s: %(message)s')
    
    str_now = datetime.strftime(datetime.now(), '%Y-%m-%d %H-%M-%S')
    file_name = LOG_FILE_NAME_BASE + '-' + str_now + '.txt'

    #logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s')

    handle = logging.FileHandler(filename=file_name, mode='w+', encoding='utf-8')
    handle.setLevel(level=logging.DEBUG)
    handle.setFormatter(formatter)

    #handle.setFormatter('%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s')
    logging.getLogger().addHandler(hdlr=handle)

    success = True
    return success

def run() :
    '''
    if not init() : 
        return
    logging.info('argv[0]={}.'.format(sys.argv[0]))
    logging.info('argv[1]={}.'.format(sys.argv[1]))
    logging.info('argv[2]={}.'.format(sys.argv[2]))
    '''
    py_sort_fs = PY_sort_file_system()
    py_sort_fs.run()
    return

run()
