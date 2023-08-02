# -*- coding:utf-8 -*-
from configparser import RawConfigParser
from os import system
from os.path import exists
# from aip import AipBodyAnalysis


# 设置
class Settings(object):
    def __init__(self, av_type):
        config_settings = RawConfigParser()
        config_settings.read('【点我设置整理规则】.ini', encoding='utf-8')
        ####################################################### nfo ###################################################
        # 是否 跳过已存在nfo的文件夹，不处理已有nfo的文件夹
        self.bool_skip = True if config_settings.get("收集nfo", "是否跳过已存在nfo的文件夹？") == '是' else False
        # 是否 收集nfo
        self.bool_nfo = True if config_settings.get("收集nfo", "是否收集nfo？") == '是' else False
        # 自定义 nfo中title的格式
        self._custom_nfo_title = config_settings.get("收集nfo", "nfo中title的格式")
        # 是否 去除 标题 末尾可能存在的演员姓名
        self.bool_strip_actors = True if config_settings.get("收集nfo", "是否去除标题末尾的演员姓名？") == '是' else False
        # 自定义 将系列、片商等元素作为特征，因为emby不会直接在影片介绍页面上显示片商，也不会读取系列set
        self._custom_genres = config_settings.get("收集nfo", "额外将以下元素添加到特征中")
        # ？是否将“系列”写入到特征中
        self.bool_write_series = True if '系列' in self._custom_genres else False
        # ？是否将“片商”写入到特征中
        self.bool_write_studio = True if '片商' in self._custom_genres else False
        # 是否 将特征保存到风格中
        self.bool_genre = True if config_settings.get("收集nfo", "是否将特征保存到genre？") == '是' else False
        # 是否 将 片商 作为特征
        self.bool_tag = True if config_settings.get("收集nfo", "是否将特征保存到tag？") == '是' else False
        ####################################################### 重命名 #################################################
        # 是否 重命名 视频
        self.bool_rename_video = True if config_settings.get("重命名影片", "是否重命名影片？") == '是' else False
        # 自定义 重命名 视频
        self._custom_video = config_settings.get("重命名影片", "重命名影片的格式")
        # 是否 重命名视频所在文件夹，或者为它创建独立文件夹
        self._bool_rename_folder = True if config_settings.get("修改文件夹", "是否重命名或创建独立文件夹？") == '是' else False
        # 自定义 新的文件夹名
        self._custom_folder = config_settings.get("修改文件夹", "新文件夹的格式")
        ########################################################## 归类 ################################################
        # 是否 归类jav
        self.bool_classify = True if config_settings.get("归类影片", "是否归类影片？") == '是' else False
        # 是否 针对“文件夹”归类jav，“否”即针对“文件”
        self.bool_classify_folder = True if config_settings.get("归类影片", "针对文件还是文件夹？") == '文件夹' else False
        # 自定义 路径 归类的jav放到哪
        self._custom_root = config_settings.get("归类影片", "归类的根目录")
        # 自定义 jav按什么类别标准来归类
        self._custom_classify_basis = config_settings.get("归类影片", "归类的标准")
        ######################################################## 图片 ################################################
        # 是否 下载图片
        self.bool_jpg = True if config_settings.get("下载封面", "是否下载封面海报？") == '是' else False
        # 自定义 命名 大封面fanart
        self._custom_fanart = config_settings.get("下载封面", "DVD封面的格式")
        # 自定义 命名 小海报poster
        self._custom_poster = config_settings.get("下载封面", "海报的格式")
        # 是否 如果视频有“中字”，给poster的左上角加上“中文字幕”的斜杠
        self.bool_watermark_subtitle = True if config_settings.get("下载封面", "是否为海报加上中文字幕条幅？") == '是' else False
        # 是否 如果视频是“无码流出”，给poster的右上角加上“无码流出”的斜杠
        self.bool_watermark_divulge = True if config_settings.get("下载封面", "是否为海报加上无码流出条幅？") == '是' else False
        ###################################################### 字幕 #######################################################
        # 是否 重命名用户已拥有的字幕
        self.bool_rename_subtitle = True if config_settings.get("字幕文件", "是否重命名已有的字幕文件？") == '是' else False
        ###################################################### kodi #######################################################
        # 是否 收集演员头像
        self.bool_sculpture = True if config_settings.get("kodi专用", "是否收集演员头像？") == '是' else False
        # 是否 对于多cd的影片，kodi只需要一份图片和nfo
        self.bool_cd_only = True if config_settings.get("kodi专用", "是否对多cd只收集一份图片和nfo？") == '是' else False
        ###################################################### 代理 ########################################################
        # 是否 使用局部代理
        self._bool_proxy = True if config_settings.get("局部代理", "是否使用局部代理？") == '是' else False
        # 是否 使用http代理，否 就是socks5
        self._bool_http = True if config_settings.get("局部代理", "http还是socks5？") == 'http' else False
        # 代理端口
        self._custom_proxy = config_settings.get("局部代理", "代理端口")
        # 是否 代理javlibrary
        self._bool_library_proxy = True if config_settings.get("局部代理", "是否代理javlibrary（有问题）？") == '是' else False
        # 是否 代理javbus，还有代理javbus上的图片cdnbus
        self._bool_bus_proxy = True if config_settings.get("局部代理", "是否代理javbus？") == '是' else False
        # 是否 代理javbus，还有代理javbus上的图片cdnbus
        self._bool_321_proxy = True if config_settings.get("局部代理", "是否代理jav321？") == '是' else False
        # 是否 代理javdb，还有代理javdb上的图片
        self._bool_db_proxy = True if config_settings.get("局部代理", "是否代理javdb？") == '是' else False
        # 是否 代理arzon
        self._bool_arzon_proxy = True if config_settings.get("局部代理", "是否代理arzon？") == '是' else False
        # 是否 代理dmm图片，javlibrary和javdb上的有码图片几乎都是直接引用dmm
        self._bool_dmm_proxy = True if config_settings.get("局部代理", "是否代理dmm图片？") == '是' else False
        #################################################### 原影片文件的性质 ################################################
        # 自定义 无视的字母数字 去除影响搜索结果的字母数字 xhd1080、mm616、FHD-1080
        self._custom_surplus_words_youma_in_filename = config_settings.get("原影片文件的性质", "有码素人无视多余的字母数字")
        # 自定义 无视的字母数字 去除影响搜索结果的字母数字 full、tokyohot、
        self._custom_surplus_words_wuma_in_filename = config_settings.get("原影片文件的性质", "无码无视多余的字母数字")
        # 自定义 原影片性质 影片有中文，体现在视频名称中包含这些字符
        self._custom_subtitle_words_in_filename = config_settings.get("原影片文件的性质", "是否中字即文件名包含")
        # 自定义 是否中字 这个元素的表现形式
        self.custom_subtitle_expression = config_settings.get("原影片文件的性质", "是否中字的表现形式")
        # 自定义 原影片性质 影片是无码流出片，体现在视频名称中包含这些字符
        self._custom_divulge_words_in_filename = config_settings.get("原影片文件的性质", "是否流出即文件名包含")
        # 自定义 是否流出 这个元素的表现形式
        self.custom_divulge_expression = config_settings.get("原影片文件的性质", "是否流出的表现形式")
        # 自定义 原影片性质 有码
        self._av_type = config_settings.get("原影片文件的性质", av_type)
        ##################################################### 信息来源 ##################################################
        # 是否 收集javlibrary下方用户超过10个人点赞的评论
        self.bool_review = True if config_settings.get("信息来源", "是否用javlibrary整理影片时收集网友的热评？") == '是' else False
        # 是否 收集javlibrary下方用户超过10个人点赞的评论
        self.bool_bus_first = True if config_settings.get("信息来源", "是否用javlibrary整理影片时优先从javbus下载图片？") == '是' else False
        ################################################### 其他设置 ####################################################
        # 是否 使用简体中文 简介翻译的结果和jav特征会变成“简体”还是“繁体”
        self.bool_zh = True if config_settings.get("其他设置", "简繁中文？") == '简' else False
        # 网址 javlibrary
        self._url_library = config_settings.get("其他设置", "javlibrary网址")
        # 网址 javbus
        self._url_bus = config_settings.get("其他设置", "javbus网址")
        # 网址 javdb
        self._url_db = config_settings.get("其他设置", "javdb网址")
        # 自定义 文件类型 只有列举出的视频文件类型，才会被处理
        self._custom_file_type = config_settings.get("其他设置", "扫描文件类型")
        # 自定义 命名格式中“标题”的长度 windows只允许255字符，所以限制长度，但nfo中的标题是全部
        self.int_title_len = int(config_settings.get("其他设置", "重命名中的标题长度（50~150）"))
        ######################################## 百度翻译API ####################################################
        # 是否 需要简介
        self.bool_plot = True if config_settings.get("百度翻译API", "是否需要日语简介？") == '是' else False
        # 是否 把日语简介翻译为中文
        self.bool_tran = True if config_settings.get("百度翻译API", "是否翻译为中文？") == '是' else False
        # 账户 百度翻译api
        self._tran_id = config_settings.get("百度翻译API", "APP ID")
        self._tran_sk = config_settings.get("百度翻译API", "密钥")
        ######################################## 百度人体分析 ####################################################
        # 是否 需要准确定位人脸的poster
        self.bool_face = True if config_settings.get("百度人体分析", "是否需要准确定位人脸的poster？") == '是' else False
        # 账户 百度人体分析
        self._al_id = config_settings.get("百度人体分析", "appid")
        self._ai_ak = config_settings.get("百度人体分析", "api key")
        self._al_sk = config_settings.get("百度人体分析", "secret key")

        ##########################################################################################################
        # 是否 重命名视频所在文件夹，或者为它创建独立文件夹
        self.bool_rename_folder = self.judge_need_rename_folder()

    # ######################[收集nfo]#####################################
    # 命名nfo中title的格式
    def formula_name_nfo_title(self):
        # 给用户命名用的标题可能是删减的，nfo中的标题是完整标题
        return self._custom_nfo_title.replace('标题', '完整标题', 1).split('+')

    # 额外放入特征风格中的元素
    def list_extra_genre(self):
        list_extra_genres = self._custom_genres.split('、') if self._custom_genres else []  # 需要的额外特征
        list_extra_genres = [i for i in list_extra_genres if i != '系列' and i != '片商']
        return list_extra_genres

    # #########################[重命名影片]##############################
    # 得到视频命名格式list
    def formula_rename_video(self):
        return self._custom_video.split('+')

    # #########################[修改文件夹]##############################
    # 是否需要重命名文件夹或者创建新的文件夹
    def judge_need_rename_folder(self):
        if self.bool_classify:  # 如果需要归类
            if self.bool_classify_folder:  # 并且是针对文件夹
                return True  # 那么必须重命名文件夹或者创建新的文件夹
            else:
                return False  # 否则不会操作新文件夹
        else:  # 不需要归类
            if self._bool_rename_folder:  # 但是用户本来就在ini中写了要重命名文件夹
                return True
            else:
                return False

    # 得到文件夹命名格式list    示例：['车牌', '【', '全部演员', '】']
    def formula_rename_folder(self):
        return self._custom_folder.split('+')

    # #########################[归类影片]##############################
    # 功能：检查 归类根目录 的合法性
    # 参数：用户自定义的归类根目录，用户选择整理的文件夹路径
    # 返回：归类根目录路径
    # 辅助：os.sep，os.system
    def check_classify_root(self, root_choose, sep):
        if self.bool_classify:
            custom_root = self._custom_root.rstrip(sep)
            # 用户使用默认的“所选文件夹”
            if custom_root == '所选文件夹':
                return root_choose + sep + '归类完成'
            # 归类根目录 是 用户输入的路径c:\a，继续核实合法性
            else:
                # 用户输入的路径 不是 所选文件夹root_choose
                if custom_root != root_choose:
                    if custom_root[:2] != root_choose[:2]:
                        print('归类的根目录“', custom_root, '”和所选文件夹不在同一磁盘无法归类！请修正！')
                        system('pause')
                    if not exists(custom_root):
                        print('归类的根目录“', custom_root, '”不存在！无法归类！请修正！')
                        system('pause')
                    return custom_root
                # 用户输入的路径 就是 所选文件夹root_choose
                else:
                    return root_choose + sep + '归类完成'
        else:
            return ''

    # 归类标准  比如：影片类型\全部演员
    def custom_classify_basis(self):
        return self._custom_classify_basis

    # #########################[下载封面]##############################
    # 命名fanart的格式
    def formula_name_fanart(self):
        return self._custom_fanart.split('+')

    # 命名poster的格式
    def formula_name_poster(self):
        return self._custom_poster.split('+')

    # #########################[局部代理]##############################
    # 得到proxy
    def get_proxy(self):
        if self._bool_proxy and self._custom_proxy:
            if self._bool_http:
                proxies = {"http": "http://" + self._custom_proxy,
                           "https": "https://" + self._custom_proxy}
            else:
                proxies = {"http": "socks5://" + self._custom_proxy,
                           "https": "socks5://" + self._custom_proxy}
            proxy_library = proxies if self._bool_library_proxy else {}  # 请求javlibrary时传递的参数
            proxy_bus = proxies if self._bool_bus_proxy else {}  # 请求javbus时传递的参数
            proxy_321 = proxies if self._bool_321_proxy else {}  # 请求jav321时传递的参数
            proxy_db = proxies if self._bool_db_proxy else {}  # 请求javdb时传递的参数
            proxy_arzon = proxies if self._bool_arzon_proxy else {}  # 请求arzon时传递的参数
            proxy_dmm = proxies if self._bool_dmm_proxy else {}  # 请求dmm图片时传递的参数
        else:
            proxy_library = {}
            proxy_bus = {}
            proxy_321 = {}
            proxy_db = {}
            proxy_arzon = {}
            proxy_dmm = {}
        return proxy_library, proxy_bus, proxy_321, proxy_db, proxy_arzon, proxy_dmm

    # #########################[原影片文件的性质]##############################
    # 得到代表中字的文字list
    def list_subtitle_word_in_filename(self):
        return self._custom_subtitle_words_in_filename.upper().split('、')

    # 得到代表流出的文字list
    def list_divulge_word_in_filename(self):
        return self._custom_divulge_words_in_filename.upper().split('、')

    # 得到干扰车牌选择的文字list
    def list_surplus_word_in_filename(self, av_type):
        if av_type == '有码':
            return self._custom_surplus_words_youma_in_filename.upper().split('、')
        else:
            return self._custom_surplus_words_wuma_in_filename.upper().split('、')

    # 自定义有码、无码、素人、FC2的对应称谓
    def av_type(self):
        return self._av_type

    # #########################[信息来源]##############################

    # #########################[其他设置]##############################
    # javlibrary网址，是简体还是繁体
    def get_url_library(self):
        url_library = self._url_library
        if not url_library.endswith('/'):
            url_library += '/'
        return url_library + 'cn/'

    # javbus网址
    def get_url_bus(self):
        if not self._url_bus.endswith('/'):
            url_web_bus = self._url_bus + '/'
        else:
            url_web_bus = self._url_bus
        return url_web_bus

    # jav321网址
    def get_url_321(self):
        if self.bool_zh:
            url_search_321 = 'https://www.jav321.com/search'
            url_web_321 = 'https://www.jav321.com/'
        else:
            url_search_321 = 'https://tw.jav321.com/search'
            url_web_321 = 'https://tw.jav321.com/'
        return url_search_321, url_web_321

    # javdb网址
    def get_url_db(self):
        if not self._url_db.endswith('/'):
            url_db = self._url_db + '/'
        else:
            url_db = self._url_db
        return url_db

    # 得到扫描文件类型
    def tuple_video_type(self):
        return tuple(self._custom_file_type.upper().split('、'))

    # #########################[百度翻译API]##############################
    # 百度翻译的目标语言、翻译账户
    def get_translate_account(self):
        if self.bool_zh:
            to_language = 'zh'  # 目标语言，zh是简体中文，cht是繁体中文
        else:
            to_language = 'cht'
        return to_language, self._tran_id, self._tran_sk

    # #########################[百度人体分析]##############################
    def start_body_analysis(self):
        if self.bool_face:
            return AipBodyAnalysis(self._al_id, self._ai_ak, self._al_sk)
        else:
            return None
