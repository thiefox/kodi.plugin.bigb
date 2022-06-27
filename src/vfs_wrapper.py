import sys
import os
import time
from datetime import datetime
import re

import xbmcvfs

VIDEO_FILE_SUFFIXS = (".mp4", ".wmv", ".avi", ".mkv", ".iso", ".mpg", ".ts", ".mov", ".m2ts", )
INVISIBLE_DIRS = ('@eadir', 'kodi lib', 'tmp', )
ENG_SEASON_NAME = r"(S\d{1,2})"

class vfs_wrapper :
    def is_season_dir(dir_name : str) -> int :
        serial = -1
        return serial
    def is_hidden_items(name : str) -> bool :
        hidden = False
        for ID in INVISIBLE_DIRS :
            if name.lower() == ID :
                hidden = True
                break
        return hidden

    def is_video_file(file_name : str) -> bool :
        video = False
        suffix = os.path.splitext(file_name)[1]
        for VFS in VIDEO_FILE_SUFFIXS :
            if suffix.lower() == VFS :
                video = True
                break
        return video 

    def del_file(path_file : str) -> bool :
        result = True
        if xbmcvfs.exists(path_file) :
            result = xbmcvfs.delete(path_file)
        return result
        
    #检查某个目录下是否有唯一的视频文件
    def check_single_playable_file(path_name : str) -> str :
        playable_file = ''
        dir_count = 0
        video_count = 0
        dirs, files = xbmcvfs.listdir(path_name)
        for dir in dirs :
            if not vfs_wrapper.is_hidden_items(dir) :
                dir_count += 1
                if dir_count > 0 :
                    break
        if dir_count == 0 :
            for file in files :
                if vfs_wrapper.is_video_file(file) :    #视频文件
                    video_count += 1
                    if playable_file == '' :
                        playable_file = file
                    if video_count > 1 :
                        break
        if dir_count != 0 or video_count != 1 :
            playable_file = ''
        return playable_file

    def _get_dir_general_pics(path_dir : str) -> dict :
        pics = dict()
        file = os.path.join(path_dir, 'poster.jpg')
        if xbmcvfs.exists(file) :
            pics['poster'] = file
        file = os.path.join(path_dir, 'fanart.jpg')
        if xbmcvfs.exists(file) :
            pics['fanart'] = file
        file = os.path.join(path_dir, 'thumb.jpg')
        if xbmcvfs.exists(file) :
            pics['thumb'] = file                
        file = os.path.join(path_dir, 'landscape.jpg')
        if xbmcvfs.exists(file) :
            pics['landscape'] = file
        file = os.path.join(path_dir, 'banner.jpg')
        if xbmcvfs.exists(file) :
            pics['banner'] = file
        file = os.path.join(path_dir, 'clearlogo.png')
        if xbmcvfs.exists(file) :
            pics['clearlogo'] = file
        else :
            file = os.path.join(path_dir, 'clearlogo.jpg')
            if xbmcvfs.exists(file) :
                pics['clearlogo'] = file
            else :
                file = os.path.join(path_dir, 'logo.png')
                if xbmcvfs.exists(file) :
                    pics['clearlogo'] = file
                else :
                    file = os.path.join(path_dir, 'logo.jpg')
                    if xbmcvfs.exists(file) :
                        pics['clearlogo'] = file
        file = os.path.join(path_dir, 'clearart.png')
        if xbmcvfs.exists(file) :
            pics['clearart'] = file
        else :
            file = os.path.join(path_dir, 'clearart.jpg')
            if xbmcvfs.exists(file) :
                pics['clearart'] = file
        return pics        
    def get_tvshow_pics(path_dir : str) -> dict :
        return vfs_wrapper._get_dir_general_pics(path_dir)
    def get_movie_pics(path_video : str) -> dict :
        pics = dict()
        path_dir = os.path.split(path_video)[0]
        return vfs_wrapper._get_dir_general_pics(path_dir)
    def get_season_pics(path_tvshow : str, season : int) -> dict :
        pics = dict()
        info = ''
        if season == 0 :
            info = 'season-specials'
        elif season < 10 :
            info = 'season0' + str(season)
        else :
            info = 'season' + str(season)
        file = os.path.join(path_tvshow, info + '-poster.jpg')
        if xbmcvfs.exists(file) :
            pics['poster'] = file
        file = os.path.join(path_tvshow, info + '-thumb.jpg')
        if xbmcvfs.exists(file) :
            pics['thumb'] = file        
        file = os.path.join(path_tvshow, info + '-banner.jpg')
        if xbmcvfs.exists(file) :
            pics['banner'] = file
        file = os.path.join(path_tvshow, info + '-fanart.jpg')
        if xbmcvfs.exists(file) :
            pics['fanart'] = file
        return pics
    def get_episode_pics(path_video : str) -> dict :
        pics = dict()
        path_pure = os.path.splitext(path_video)[0]
        file = path_pure + '-thumb.jpg'
        if xbmcvfs.exists(file) :
            pics['thumb'] = file

        path_parent = os.path.split(os.path.split(path_video)[0])[0]
        file = os.path.join(path_parent, 'clearlogo.png')
        if xbmcvfs.exists(file) :
            pics['clearlogo'] = file
        else :
            file = os.path.join(path_parent, 'clearlogo.jpg')
            if xbmcvfs.exists(file) :
                pics['clearlogo'] = file
            else :
                file = os.path.join(path_parent, 'logo.png')
                if xbmcvfs.exists(file) :
                    pics['clearlogo'] = file
                else :
                    file = os.path.join(path_parent, 'logo.jpg')
                    if xbmcvfs.exists(file) :
                        pics['clearlogo'] = file

        return pics        

    #path_name可以是目录，也可以是文件
    def __init__(self, path_name) -> None :
        self.path = path_name           
        return

    def read(self) -> str :
        data = ''
        with xbmcvfs.File(self.path, 'r') as f:         #test content with utf-8
            data = f.read()
        return data

    def write(self, data : str) -> bool :
        result = False
        with xbmcvfs.File(self.path, 'w') as f:         #test content with utf-8
            result = f.write(data)
        return result

    #取得目录下的视频文件列表（不含子目录）
    def get_video_files(self) -> list :
        videos = list()
        _, files = xbmcvfs.listdir(self.path)
        for file in files :
            if vfs_wrapper.is_video_file(file) :    #视频文件
                videos.append(file)
        return videos