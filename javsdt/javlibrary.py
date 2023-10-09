'''
Author: izumihoshi
Date: 2023-05-13 11:58:40
LastEditors: izumihoshi
LastEditTime: 2023-10-09 22:41:34
FilePath: \javsdt\javlibrary.py
Description: TODO

Copyright (c) 2023 by Honor, All Rights Reserved.
'''
# -*- coding:utf-8 -*-
import os, re
from shutil import copyfile
from traceback import format_exc
# ################################################# 相同 ###########################################################
from Class.Settings import Settings
from Class.JavFile import JavFile
from Functions.Status import judge_exist_nfo, judge_exist_extra_folders, count_num_videos
from Functions.User import choose_directory
from Functions.Record import record_start, record_fail, record_warn
from Functions.Process import perfect_dict_data
from Functions.Standard import rename_mp4, rename_folder, classify_files, classify_folder
from Functions.XML import replace_xml, replace_xml_win
from Functions.Process import judge_exist_subtitle
from Functions.Picture import check_picture, add_watermark_subtitle
from Functions.Requests.Download import download_pic
from Functions.Genre import better_dict_genre
# ################################################## 不同 ##########################################################
from Functions.Process import judge_exist_divulge
from Functions.Status import check_actors
from Functions.Car import find_car_library, list_suren_car
from Functions.Standard import collect_sculpture
from Functions.Baidu import translate
from Functions.Picture import add_watermark_divulge, crop_poster_youma
from Functions.Requests.JavlibraryReq import get_library_html,search_library_html
from Functions.Requests.ArzonReq import steal_arzon_cookies, find_plot_arzon
from Functions.Requests.JavbusReq import find_series_cover_bus


#  main开始
print('1、避开21:00-1:00，访问javlibrary和arzon很慢。\n'
      '2、若一直打不开javlibrary，请在ini中更新防屏蔽网址\n')

# 读取配置文件，这个ini文件用来给用户设置
print('正在读取ini中的设置...', end='')
try:
    settings = Settings('有码')
except:
    settings = None
    print(format_exc())
    print('\n无法读取ini文件，请修改它为正确格式，或者打开“【ini】重新创建ini.exe”创建全新的ini！')
    os.system('pause')
print('\n读取ini文件成功!\n')

# 路径分隔符：当前系统的路径分隔符 windows是“\”，linux和mac是“/”
sep = os.sep

# 检查头像：如果需要为kodi整理头像，先检查演员头像ini、头像文件夹是否存在。
check_actors(settings.bool_sculpture)

# 局部代理：哪些站点需要代理。
proxy_library, proxy_bus, proxy_321, proxy_db, proxy_arzon, proxy_dmm = settings.get_proxy()

# arzon通行证：如果需要在nfo中写入日语简介，需要先获得合法的arzon网站的cookie，用于通过成人验证。
cookie_arzon = steal_arzon_cookies(proxy_arzon) if settings.bool_plot and settings.bool_nfo else {}

# jav网址：javlibrary网址 http://www.m45e.com/   javbus网址 https://www.buscdn.work/
url_library = settings.get_url_library()
url_bus = settings.get_url_bus()

# 选择简繁中文以及百度翻译账户：需要简体中文还是繁体中文，影响影片特征和简介。
to_language, tran_id, tran_sk = settings.get_translate_account()


# 信息字典：存放影片信息，用于给用户自定义各种命名。
dict_data = {'车牌': 'ABC-123',
             '车牌前缀': 'ABC',
             '标题': '有码标题',
             '完整标题': '完整有码标题',
             '导演': '有码导演',
             '片商': '有码片商',
             '评分': '0',
             '片长': '0',
             '系列': '有码系列',
             '发行年月日': '1970-01-01', '发行年份': '1970', '月': '01', '日': '01',
             '首个演员': '有码演员', '全部演员': '有码演员',
             '空格': ' ',
             '\\': sep, '/': sep,  # 文件路径分隔符
             '是否中字': '',
             '是否流出': '',
             '影片类型': settings.av_type(),
             '视频': 'ABC-123',  # 当前及未来的视频文件名，不带ext
             '原文件名': 'ABC-123', '原文件夹名': 'ABC-123', }

# nfo中title的写法。
list_name_nfo_title = settings.formula_name_nfo_title()
# 额外将哪些元素放入特征中
list_extra_genres = settings.list_extra_genre()
# 重命名视频的格式
list_name_video = settings.formula_rename_video()
# 重命名文件夹的格式
list_name_folder = settings.formula_rename_folder()

# fanart的格式
list_name_fanart = settings.formula_name_fanart()
# poster的格式
list_name_poster = settings.formula_name_poster()

# 视频文件名包含哪些多余的字母数字，需要无视
list_surplus_words_in_filename = settings.list_surplus_word_in_filename('有码')
# 文件名包含哪些特殊含义的文字，判断是否中字
list_subtitle_words_in_filename = settings.list_subtitle_word_in_filename()
# 文件名包含哪些特殊含义的文字，判断是否是无码流出片
list_divulge_words_in_filename = settings.list_divulge_word_in_filename()

# 素人番号：得到事先设置的素人番号，让程序能跳过它们
list_suren_cars = list_suren_car()

# 需要扫描的文件的类型
tuple_video_types = settings.tuple_video_type()

# 完善dict_data，如果用户自定义了一些文字，不在元素中，需要将它们添加进dict_data；list_classify_basis，归类标准，归类目标文件夹的组成公式。
dict_data, list_classify_basis = perfect_dict_data(list_extra_genres, list_name_video, list_name_folder,
                                                   list_name_nfo_title, list_name_fanart, list_name_poster,
                                                   settings.custom_classify_basis(), dict_data)

# 优化特征的字典
dict_genre = better_dict_genre('Javlibrary', to_language)


# 用户输入“回车”就继续选择文件夹整理
input_start_key = ''
while input_start_key == '':
    # 用户：选择需要整理的文件夹
    print('请选择要整理的文件夹：', end='')
    root_choose = choose_directory()
    print(root_choose)
    # 日志：在txt中记录一下用户的这次操作，在某个时间选择了某个文件夹
    record_start(root_choose)
    # 归类：用户自定义的归类根目录，如果不需要归类则为空
    root_classify = settings.check_classify_root(root_choose, sep)
    # 计数：失败次数及进度
    num_fail = 0  # 已经或可能导致致命错误，比如整理未完成，同车牌有不同视频
    num_warn = 0  # 对整理结果不致命的问题，比如找不到简介
    num_all_videos = count_num_videos(root_choose, tuple_video_types)  # 所选文件夹总共有多少个视频文件
    num_current = 0  # 当前视频的编号
    print('...文件扫描开始...如果时间过长...请避开夜晚高峰期...\n')
    # root【当前根目录】 dirs【子文件夹】 files【文件】，root是str，后两个是list
    for root, dirs, files in os.walk(root_choose):
        # 什么文件都没有
        if not files:
            continue
        # 当前root是已归类的目录，无需处理
        if '归类完成' in root.replace(root_choose, ''):
            continue
        # 跳过已存在nfo的文件夹，判断这一层文件夹中有没有nfo
        if settings.bool_skip and judge_exist_nfo(files):
            continue
        # 对这一层文件夹进行评估,有多少视频，有多少同车牌视频，是不是独立文件夹
        list_jav_struct = []  # 存放：需要整理的jav的结构体
        dict_car_pref = {}  # 存放：每一车牌的集数， 例如{'abp-123': 1, avop-789': 2}是指 abp-123只有一集，avop-789有cd1、cd2
        num_videos_include = 0  # 计数：当前文件夹中视频的数量，可能有视频不是jav
        dict_subtitle_files = {}  # 存放：jav的字幕文件和车牌对应关系 {'c:\a\abc_123.srt': 'abc-123'}
        # 判断文件是不是字幕文件，放入dict_subtitle_files中
        for file_raw in files:
            file_temp = file_raw.upper()
            if file_temp.endswith(('.SRT', '.VTT', '.ASS', '.SSA', '.SUB', '.SMI',)):
                # 当前模式不处理FC2
                if 'FC2' in file_temp:
                    continue
                # 去除用户设置的、干扰车牌的文字
                for word in list_surplus_words_in_filename:
                    file_temp = file_temp.replace(word, '')
                # 得到字幕文件名中的车牌
                subtitle_car = find_car_library(file_temp, list_suren_cars)
                # 将该字幕文件和其中的车牌对应到dict_subtitle_files中
                if subtitle_car:
                    dict_subtitle_files[file_raw] = subtitle_car
        # print(dict_subtitle_files)
        # 判断文件是不是视频，放入list_jav_struct中
        for file_raw in files:
            file_temp = file_raw.upper()
            if file_temp.endswith(tuple_video_types) and not file_temp.startswith('.'):
                num_videos_include += 1
                num_current += 1
                if 'FC2' in file_temp:
                    continue
                for word in list_surplus_words_in_filename:
                    file_temp = file_temp.replace(word, '')
                # 得到视频中的车牌
                car = find_car_library(file_temp, list_suren_cars)
                if car:
                    try:
                        dict_car_pref[car] += 1  # 已经有这个车牌了，加一集cd
                    except KeyError:
                        dict_car_pref[car] = 1  # 这个新车牌有了第一集
                    # 这个车牌在dict_subtitle_files中，有它的字幕。
                    if car in dict_subtitle_files.values():
                        subtitle_file = list(dict_subtitle_files.keys())[list(dict_subtitle_files.values()).index(car)]
                        del dict_subtitle_files[subtitle_file]
                    else:
                        subtitle_file = ''
                    # 将该jav的各种属性打包好，包括原文件名带扩展名、所在文件夹路径、第几集、所属字幕文件名
                    jav_struct = JavFile(file_raw, root, car, dict_car_pref[car], subtitle_file, num_current)
                    list_jav_struct.append(jav_struct)
                else:
                    print('>>无法处理：', root.replace(root_choose, '') + sep + file_raw)

        # 判定影片所在文件夹是否是独立文件夹，独立文件夹是指该文件夹仅用来存放该影片，而不是大杂烩文件夹
        # 这一层文件夹下有jav
        if dict_car_pref:
            # 当前文件夹下，车牌不止一个；还有其他非jav视频；有其他文件夹，除了演员头像文件夹“.actors”和额外剧照文件夹“extrafanart”；
            if len(dict_car_pref) > 1 or num_videos_include > len(list_jav_struct) or judge_exist_extra_folders(dirs):
                bool_separate_folder = False  # 不是独立的文件夹
            else:
                bool_separate_folder = True  # 这一层文件夹是这部jav的独立文件夹
        else:
            continue

        # 开始处理每一部jav
        for jav in list_jav_struct:
            # 告诉用户进度
            print('>> [' + str(jav.number) + '/' + str(num_all_videos) + ']:', jav.name)
            print('    >发现车牌：', jav.car)

            # 判断是否有中字的特征，条件有三满足其一即可：1有外挂字幕 2文件名中含有“-C”之类的字眼 3旧的nfo中已经记录了它的中字特征
            if jav.subtitle:
                bool_subtitle = True  # 判定成功
                dict_data['是否中字'] = settings.custom_subtitle_expression  # '是否中字'这一命名元素被激活
            else:
                bool_subtitle = judge_exist_subtitle(root, jav.name_no_ext, list_subtitle_words_in_filename)
                dict_data['是否中字'] = settings.custom_subtitle_expression if bool_subtitle else ''
            # 判断是否是无码流出的作品，同理
            bool_divulge = judge_exist_divulge(root, jav.name_no_ext, list_divulge_words_in_filename)
            dict_data['是否流出'] = settings.custom_divulge_expression if bool_divulge else ''

            # 影片的相对于所选文件夹的路径，用于报错
            path_relative = sep + jav.path.replace(root_choose, '')

            # 程序接下来是在javlibrary搜索信息，但可以设置去javbus下载图片。如果javlibrary上的搜索结果不唯一，那么再去javbus下载图片可能导致张冠李戴。
            bool_unique = True  # javlibrary有唯一的搜素结果。如果 bool_unique 变化为 false，就不会去javbus下载图片。

            # 获取nfo信息的javlibrary网页
            try:
                # 用户指定了网址，则直接得到jav所在网址
                if '图书馆' in jav.name:
                    url_appointg = re.search(r'图书馆(jav.+?)\.', jav.name)
                    if str(url_appointg) != 'None':
                        url_search_web = url_library + '?v=' + url_appointg.group(1)
                    else:
                        num_fail += 1
                        record_fail('    >第' + str(num_fail) + '个失败！你指定的library网址有错误：' + path_relative + '\n')
                        continue  # 【退出对该jav的整理】
                # 用户没有指定网址，则去搜索
                else:
                    url_search_web = search_library_html(url_library, jav.car, proxy_library)

                # 得到javlibrary搜索网页html
                print('    >搜索车牌：', url_search_web)
                html_web = get_library_html(url_search_web, proxy_library)
                # 从前：搜索结果，大部分情况就是这个影片的网页（搜索结果唯一，javlibrary会自动跳转到该jav唯一的网页），另一种情况是多个搜索结果的网页
                # 1.1.2版本请无视这一行：访问javlibrary需要cloudflare的通行证，自动跳转时，cookie会发生变化，导致用现有cookie无权访问跳转后的页面。所以现在程序不希望requests帮助自动跳转，而是只得到跳转前网页上的线索，再自行访问这个跳转目标网页。
                # 尝试找标题，第一种情况：找得到，就是这个影片的网页。
                titleg = re.search(r'<title>([A-Z].+?) - JAVLibrary</title>', html_web)  # 匹配处理“标题”
                # 搜索结果就是AV的页面。事实上，现在只有用户指定了网址，这一步判定才能成功。现在要么是多个搜索结果的网页，要么是跳转前的几句html语句，根本不可能“搜索一下就是AV的页面”。
                if str(titleg) != 'None':
                    title = titleg.group(1)
                # 第二种情况：搜索结果可能是两个以上，所以这种匹配找不到标题，None！
                else:  # 找“可能是多个结果的网页”上的所有“box”
                    list_search_results = re.findall(r'v=jav(.+?)" title="(.+?-\d+?[a-z]? .+?)"',
                                                     html_web)  # 这个正则表达式可以忽略avop-00127bod，它是近几年重置的，信息冗余
                    # print(list_search_results)
                    # 从这些搜索结果中，找到最正确的一个
                    if list_search_results:
                        # 默认用第一个搜索结果
                        url_jav_web = url_library + '?v=jav' + list_search_results[0][0]
                        # 在javlibrary上搜索 SSNI-589 SNIS-459 这两个车牌，你就能看懂下面的if
                        if len(list_search_results) > 1 and not list_search_results[1][1].endswith('ク）'):  # ク）是蓝光重置版
                            # print(list_search_results)
                            # 排在第一个的是蓝光重置版，比如SSNI-589（ブルーレイディスク），它的封面不正常，跳过它
                            if list_search_results[0][1].endswith('ク）'):
                                url_jav_web = url_library + '?v=jav' + list_search_results[1][0]
                            # 不同的片，但车牌完全相同，比如id-020。警告用户，但默认用第一个结果。
                            elif list_search_results[1][1].split(' ', 1)[0] == jav.car:
                                bool_unique = False
                                num_fail += 1
                                record_fail('    >第' + str(
                                    num_fail) + '个警告！javlibrary搜索到同车牌的不同视频：' + jav.car + '，' + path_relative + '\n')
                            # else: 还有一种情况，不同片，车牌也不同，但搜索到一堆，比如搜“AVOP-039”，还会得到“AVOP-390”，正确的肯定是第一个。
                        # 打开这个jav在library上的网页
                        print('    >获取信息：', url_jav_web)
                        html_web = get_library_html(url_jav_web, proxy_library)
                        # 找到标题，留着马上整理信息用
                        title = re.search(r'<title>([A-Z].+?) - JAVLibrary</title>', html_web).group(1)
                    # 第三种情况：搜索不到这部影片，搜索结果页面什么都没有
                    else:
                        num_fail += 1
                        record_fail('    >第' + str(
                            num_fail) + '个失败！javlibrary找不到该车牌的信息：' + jav.car + '，' + path_relative + '\n')
                        continue  # 【跳出对该jav的整理】

                print('    >影片标题：', title)
                # 去除xml文档和windows路径不允许的特殊字符 &<>  \/:*?"<>|
                title = replace_xml_win(title)
                # 正则匹配 影片信息 开始！
                # title的开头是车牌号，想要后面的纯标题
                car_titleg = re.search(r'(.+?) (.+)', title)
                # 车牌号
                jav_temp = car_titleg.group(1)
                # 在javlibrary中，T-28 和 ID 的车牌很奇特。javlibrary是T-28XXX，而其他网站是T28-XXX；ID-20XXX，而其他网站是20ID-XXX。
                if 'T-28' in jav_temp:
                    jav_temp = jav_temp.replace('T-28', 'T28-', 1)
                elif 'ID-' in jav_temp:
                    jav_tempg = re.search(r'ID-(\d\d)(\d\d\d)', jav_temp)
                    if jav_tempg:
                        jav_temp = jav_tempg.group(1) + 'ID-' + jav_tempg.group(2)
                dict_data['车牌'] = car = jav_temp  # car可能发生了变化
                dict_data['车牌前缀'] = car.split('-')[0]
                # 不包含车牌的标题
                title_only = car_titleg.group(2)
                # javlibrary的精彩影评   (.+?\s*.*?\s*.*?\s*.*?) 下面的匹配可能很奇怪，没办法，就这么奇怪
                if settings.bool_review:
                    list_all_reviews = re.findall(
                        r'(textarea style="display: none;" class="hidden">[\s\S]*?scoreup">\d\d+)', html_web, re.DOTALL)
                    if list_all_reviews:
                        review = '【精彩影评】：'
                        for rev in list_all_reviews:
                            list_reviews = re.findall(r'hidden">([\s\S]*?)</textarea>', rev, re.DOTALL)
                            if list_reviews:
                                review = review + list_reviews[-1] + '////'
                        review = replace_xml(review)
                    else:
                        review = ''
                else:
                    review = ''
                # print(review)
                # 有大部分信息的html_web
                html_all = html_web
                #print(html_all)
                html_web = re.search(r'video_title"([\s\S]*?)favorite_edit', html_web, re.DOTALL).group(1)
                # DVD封面cover
                coverg = re.search(r'src="(.+?)" width="600', html_web)
                if str(coverg) != 'None':
                    url_cover = coverg.group(1)
                else:
                    url_cover = ''
                # 发行日期
                premieredg = re.search(r'(\d\d\d\d-\d\d-\d\d)', html_web)
                if str(premieredg) != 'None':
                    dict_data['发行年月日'] = time_premiered = premieredg.group(1)
                    dict_data['发行年份'] = time_premiered[0:4]
                    dict_data['月'] = time_premiered[5:7]
                    dict_data['日'] = time_premiered[8:10]
                else:
                    dict_data['发行年月日'] = time_premiered = '1970-01-01'
                    dict_data['发行年份'] = '1970'
                    dict_data['月'] = '01'
                    dict_data['日'] = '01'
                # 片长 <td><span class="text">150</span> 分钟</td>
                runtimeg = re.search(r'span class="text">(\d+?)</span>', html_web)
                if str(runtimeg) != 'None':
                    dict_data['片长'] = runtimeg.group(1)
                else:
                    dict_data['片长'] = '0'
                # 导演
                directorg = re.search(r'director\.php.+?>(.+?)<', html_web)
                if str(directorg) != 'None':
                    dict_data['导演'] = replace_xml_win(directorg.group(1))
                else:
                    dict_data['导演'] = '有码导演'
                # 片商 制作商
                studiog = re.search(r'maker\.php.+?>(.+?)<', html_web)
                if str(studiog) != 'None':
                    dict_data['片商'] = studio = replace_xml_win(studiog.group(1))
                else:
                    dict_data['片商'] = '有码片商'
                    studio = ''
                # 演员们 和 第一个演员
                actors = re.findall(r'star\.php.+?>(.+?)<', html_web)
                if actors:
                    if len(actors) > 7:
                        dict_data['全部演员'] = ' '.join(actors[:7])
                    else:
                        dict_data['全部演员'] = ' '.join(actors)
                    dict_data['首个演员'] = actors[0]
                    # 有些用户需要删去 标题末尾 可能存在的 演员姓名
                    if settings.bool_strip_actors and title_only.endswith(dict_data['全部演员']):
                        title_only = title_only[:-len(dict_data['全部演员'])].rstrip()
                else:
                    actors = ['有码演员']
                    dict_data['首个演员'] = dict_data['全部演员'] = '有码演员'
                # 处理影片的标题过长  给用户重命名用的标题是 短的title，nfo中是“完整标题”，但用户在ini中只用写“标题”
                dict_data['完整标题'] = title_only
                if len(title_only) > settings.int_title_len:
                    dict_data['标题'] = title_only[:settings.int_title_len]
                else:
                    dict_data['标题'] = title_only
                # 特点风格
                genres = re.findall(r'category tag">(.+?)<', html_web)
                if bool_subtitle:  # 有“中字“，加上特征”中文字幕”
                    genres.append('中文字幕')
                if bool_divulge:  # 是流出无码片，加上特征'无码流出'
                    genres.append('无码流出')
                try:
                    genres = [dict_genre[i] for i in genres if dict_genre[i] != '删除']
                except KeyError as error:
                    num_fail += 1
                    record_fail('    >第' + str(num_fail) + '个失败！发现新的特征需要添加至【特征对照表】：' + str(error) + '\n')
                    continue
                # print(genres)
                # 评分
                userswant = re.search(r'<a href="userswanted.+?">(.+?)</a>', html_all)
                #print(str(userswant))
                usersNum = int(re.compile(r'(?<=">)\d+').findall(str(userswant))[0])
                #pattern
                # print(usersNum)

                scoreg = re.search(r'score">\((.+?)\)<', html_web)
                if str(scoreg) != 'None':
                    float_score = float(scoreg.group(1))
                    #print(float_score)
                    #float_score = (float_score - 4) * 5 / 3  # javlibrary上稍微有人关注的影片评分都是6分以上（10分制），强行把它差距拉大
                    #start 避免小众高分影片霸榜的算法
                    if ("蓝光" in genres): #防止蓝光版被误伤
                        float_score = float_score
                    # 降低某些genre的权重，可以自行添加，以下两种"肛交"和"灌肠"仅用于示例，没有附带任何观点和立场。
                    elif (("肛交" in genres) or ("灌肠" in genres)) and (usersNum < 300) and (float_score > 8):
                        float_score = float_score * 0.7
                    elif (usersNum < 100) and (float_score > 8):
                        float_score = float_score * 0.75
                    elif (usersNum < 200) and (float_score > 8):
                        float_score = float_score * 0.85
                    elif (usersNum < 300) and (float_score > 8.4):
                        float_score = float_score * 0.9
                    #end 避免小众高分影片霸榜的算法
                    if float_score >= 0:
                        score = '%.1f' % float_score
                    else:
                        score = '0'
                else:
                    print("error: no score")
                    score = '0'
                #print(score)
                dict_data['评分'] = score
                # 烂番茄评分 用上面的评分*10
                criticrating = str(float(score) * 10)
                ################################################################################
                # 去arzon找简介
                if settings.bool_nfo and settings.bool_plot and jav.episode == 1:
                    # 获得简介或失败信息
                    plot, status_arzon, cookie_arzon = find_plot_arzon(car, cookie_arzon, proxy_arzon)
                    if status_arzon == 0:
                        pass
                    elif status_arzon == 1:
                        num_warn += 1
                        record_warn('    >第' + str(num_warn) + '个失败！找不到简介，尽管arzon上有搜索结果：' + path_relative + '\n')
                    else:
                        num_warn += 1
                        record_warn('    >第' + str(num_warn) + '个失败！找不到简介，影片被arzon下架：' + path_relative + '\n')
                    # 需要翻译简介
                    if settings.bool_tran:
                        plot = translate(tran_id, tran_sk, plot, to_language)
                        if plot.startswith('【百度'):
                            num_fail += 1
                            record_fail('    >第' + str(num_fail) + '个失败！翻译简介失败：' + path_relative + '\n')
                    # 去除xml文档不允许的特殊字符 &<>
                    plot = replace_xml(plot)
                    # print(plot)
                else:
                    plot = ''
                #######################################################################
                # 前往javbus查找系列，顺便查找图片url，因为javlibrary引用dmm的图片，晚上下载很慢，可以设置优先从javbus下载
                series, url_cover_bus, status_series = (None, None, None) # find_series_cover_bus(car, url_bus, proxy_bus)
                if status_series:
                    num_warn += 1
                    record_warn(
                        '    >第' + str(num_warn) + '个警告！系列可能错误，javbus搜索到同车牌的不同视频：' + car + '，' + path_relative + '\n')
                if series:
                    dict_data['系列'] = series
                else:
                    dict_data['系列'] = '有码系列'
                #######################################################################
                dict_data['视频'] = dict_data['原文件名'] = jav.name_no_ext  # dict_data['视频']，先定义为原文件名，即将发生变化。
                dict_data['原文件夹名'] = jav.folder
                # 是CD1还是CDn？
                num_all_episodes = dict_car_pref[jav.car]  # 该车牌总共多少集
                if num_all_episodes > 1:
                    str_cd = '-cd' + str(jav.episode)
                else:
                    str_cd = ''

                # 1重命名视频
                try:
                    dict_data, jav, num_temp = rename_mp4(jav, num_fail, settings, dict_data, list_name_video,
                                                          path_relative, str_cd)
                    num_fail = num_temp
                except FileExistsError:
                    num_fail += 1
                    continue

                # 2 归类影片，只针对视频文件和字幕文件。注意：第2操作和下面（第3操作+第7操作）互斥，只能执行第2操作或（第3操作+第7操作）
                try:
                    jav, num_temp = classify_files(jav, num_fail, settings, dict_data, list_classify_basis,
                                                   root_classify)
                    num_fail = num_temp
                except FileExistsError:
                    num_fail += 1
                    continue

                # 3重命名文件夹。如果是针对“文件”归类（即第2步），这一步会被跳过，因为用户只需要归类视频文件，不需要管文件夹。
                try:
                    jav, num_temp = rename_folder(jav, num_fail, settings, dict_data, list_name_folder,
                                                  bool_separate_folder, num_all_episodes)
                    num_fail = num_temp
                except FileExistsError:
                    num_fail += 1
                    continue

                # 更新一下path_relative
                path_relative = sep + jav.path.replace(root_choose, '')  # 影片的相对于所选文件夹的路径，用于报错

                # 4写入nfo【独特】
                if settings.bool_nfo:
                    # 如果是为kodi准备的nfo，不需要多cd
                    if settings.bool_cd_only:
                        path_nfo = jav.root + sep + jav.name_no_ext.replace(str_cd, '') + '.nfo'
                    else:
                        path_nfo = jav.root + sep + jav.name_no_ext + '.nfo'
                    # nfo中tilte的写法
                    title_in_nfo = ''
                    for i in list_name_nfo_title:
                        title_in_nfo += dict_data[i]
                    # 开始写入nfo，这nfo格式是参考的kodi的nfo
                    f = open(path_nfo, 'w', encoding="utf-8")
                    f.write("<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\" ?>\n"
                            "<movie>\n"
                            "  <plot>" + plot + review + "</plot>\n"
                            "  <title>" + title_in_nfo + "</title>\n"
                            "  <originaltitle>" + title + "</originaltitle>\n"
                            "  <director>" + dict_data['导演'] + "</director>\n"
                            "  <rating>" + score + "</rating>\n"
                            "  <criticrating>" + criticrating + "</criticrating>\n"
                            "  <year>" +
                            dict_data['发行年份'] + "</year>\n"
                            "  <mpaa>NC-17</mpaa>\n"
                            "  <customrating>NC-17</customrating>\n"
                            "  <countrycode>JP</countrycode>\n"
                            "  <premiered>" + time_premiered + "</premiered>\n"
                            "  <release>" + time_premiered + "</release>\n"
                            "  <runtime>" + dict_data['片长'] + "</runtime>\n"
                            "  <country>日本</country>\n"
                            "  <studio>" + studio + "</studio>\n"
                            "  <id>" + car + "</id>\n"
                            "  <num>" + car + "</num>\n"
                            "  <set>" + series + "</set>\n")  # emby不管set系列，kodi可以
                    # 需要将特征写入genre
                    if settings.bool_genre:
                        for i in genres:
                            f.write("  <genre>" + i + "</genre>\n")
                        if settings.bool_write_series and series:
                            f.write("  <genre>系列:" + series + "</genre>\n")
                        if settings.bool_write_studio and studio:
                            f.write("  <genre>片商:" + studio + "</genre>\n")
                        if list_extra_genres:
                            for i in list_extra_genres:
                                f.write("  <genre>" + dict_data[i] + "</genre>\n")
                    # 需要将特征写入tag
                    if settings.bool_tag:
                        for i in genres:
                            f.write("  <tag>" + i + "</tag>\n")
                        if settings.bool_write_series and series:
                            f.write("  <tag>系列:" + series + "</tag>\n")
                        if settings.bool_write_studio and studio:
                            f.write("  <tag>片商:" + studio + "</tag>\n")
                        if list_extra_genres:
                            for i in list_extra_genres:
                                f.write("  <tag>" + dict_data[i] + "</tag>\n")
                    # 写入演员
                    for i in actors:
                        f.write("  <actor>\n    <name>" + i + "</name>\n    <type>Actor</type>\n  </actor>\n")
                    f.write("</movie>\n")
                    f.close()
                    print('    >nfo收集完成')

                # 5需要两张封面图片【独特】
                if settings.bool_jpg:
                    # 下载海报的地址 cover    有一些图片dmm没了，是javlibrary自己的图片，缺少'http:'
                    if not url_cover.startswith('http'):
                        url_cover = 'http:' + url_cover
                    # url_cover = url_cover.replace('pics.dmm.co.jp', 'jp.netcdn.space')    # 有人建议用avmoo的反代图片地址代替dmm
                    # fanart和poster路径
                    path_fanart = jav.root + sep
                    path_poster = jav.root + sep
                    for i in list_name_fanart:
                        path_fanart += dict_data[i]
                    for i in list_name_poster:
                        path_poster += dict_data[i]
                    # kodi只需要一份图片，不管视频是cd几，图片仅一份不需要cd几。
                    if settings.bool_cd_only:
                        path_fanart = path_fanart.replace(str_cd, '')
                        path_poster = path_poster.replace(str_cd, '')
                    # emby需要多份，现在不是第一集，直接复制第一集的图片
                    elif jav.episode != 1:
                        try:
                            copyfile(path_fanart.replace(str_cd, '-cd1'), path_fanart)
                            print('    >fanart.jpg复制成功')
                            copyfile(path_poster.replace(str_cd, '-cd1'), path_poster)
                            print('    >poster.jpg复制成功')
                        except FileNotFoundError:
                            pass
                    # kodi或者emby需要的第一份图片
                    if check_picture(path_fanart):
                        # print('    >已有fanart.jpg')
                        pass
                    else:
                        # javlibrary上有唯一的搜索结果，优先去取javbus下载封面，已经去过javbus并找到封面，用户没有指定javbus的网址
                        if bool_unique and settings.bool_bus_first and url_cover_bus and '图书馆' not in jav.name:
                            print('    >从javbus下载封面：', url_cover_bus)
                            try:
                                download_pic(url_cover_bus, path_fanart, proxy_bus)
                                print('    >fanart.jpg下载成功')
                            except:
                                print('    >从javbus下载fanart.jpg失败!')
                                # 还是用javlibrary的dmm图片
                                print('    >从dmm下载封面：', url_cover)
                                try:
                                    download_pic(url_cover, path_fanart, proxy_dmm)
                                    print('    >fanart.jpg下载成功')
                                except:
                                    num_fail += 1
                                    record_fail('    >第' + str(
                                        num_fail) + '个失败！下载fanart.jpg失败：' + url_cover + '，' + path_relative + '\n')
                                    continue  # 【退出对该jav的整理】
                        # 用户没有去javbus获取系列，或者指定“图书馆”网址，还是从javlibrary的dmm图片地址下载
                        else:
                            print('    >从dmm下载封面：', url_cover)
                            try:
                                download_pic(url_cover, path_fanart, proxy_dmm)
                                print('    >fanart.jpg下载成功')
                            except:
                                num_fail += 1
                                record_fail('    >第' + str(
                                    num_fail) + '个失败！下载javlibrary上的封面失败：' + url_cover + '，' + path_relative + '\n')
                                continue  # 【退出对该jav的整理】
                    # 裁剪生成 poster
                    if check_picture(path_poster):
                        # print('    >已有poster.jpg')
                        pass
                    else:
                        crop_poster_youma(path_fanart, path_poster)
                        # 需要加上条纹
                        if settings.bool_watermark_subtitle and bool_subtitle:
                            add_watermark_subtitle(path_poster)
                        if settings.bool_watermark_divulge and bool_divulge:
                            add_watermark_divulge(path_poster)

                # 6收集演员头像【相同】
                if settings.bool_sculpture and jav.episode == 1:
                    if actors[0] == '有码演员':
                        print('    >未知演员，无法收集头像')
                    else:
                        collect_sculpture(actors, jav.root)
                # 7归类影片，针对文件夹【相同】
                try:
                    num_temp = classify_folder(jav, num_fail, settings, dict_data, list_classify_basis, root_classify,
                                               root, bool_separate_folder, num_all_episodes)
                    num_fail = num_temp
                except FileExistsError:
                    num_fail += 1
                    continue

            except:
                num_fail += 1
                record_fail('    >第' + str(
                    num_fail) + '个失败！发生错误，如一直在该影片报错请截图并联系作者：' + path_relative + '\n' + format_exc() + '\n')
                continue  # 【退出对该jav的整理】

    # 完结撒花
    print('\n当前文件夹完成，', end='')
    if num_fail > 0:
        print('失败', num_fail, '个!  ', root_choose, '\n')
        line = -1
        with open('【可删除】失败记录.txt', 'r', encoding="utf-8") as f:
            content = list(f)
        while 1:
            if content[line].startswith('已'):
                break
            line -= 1
        for i in range(line + 1, 0):
            print(content[i], end='')
        print('\n“【可删除】失败记录.txt”已记录错误\n')
    else:
        print(' “0”失败！  ', root_choose, '\n')
    if num_warn > 0:
        print('“警告信息.txt”还记录了', num_warn, '个警告信息！\n')
    # os.system('pause')
    input_start_key = input('回车继续选择文件夹整理：')
