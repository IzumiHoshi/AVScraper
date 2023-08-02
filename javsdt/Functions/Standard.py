# -*- coding:utf-8 -*-
from os import sep, makedirs, rename, rmdir, listdir
from os.path import exists
from configparser import RawConfigParser
from shutil import copyfile

from Functions.Record import record_video_old, record_fail


# 功能：1重命名视频
# 参数：设置settings，重命名视频的命名公式list_name_video，命名信息dict_data，第几集str_cd，处理的影片jav，已失败次数num_fail，视频的相对路径path_relative
# 返回：命名信息dict_data（dict_data['视频']可能改变）、处理的影片jav（文件名改变）、已发生的失败次数num_fail
# 辅助：os.exists, os.rename, record_video_old, record_fail
def rename_mp4(jav, num_fail, settings, dict_data, list_name_video, path_relative, str_cd):
    if settings.bool_rename_video:
        # 构造新文件名，不带文件类型后缀
        name_without_ext = ''
        for j in list_name_video:
            name_without_ext += dict_data[j]
        name_without_ext = name_without_ext.rstrip() + str_cd  # 去除末尾空格，否则windows会自动删除空格，导致程序仍以为带空格
        path_new = jav.root + sep + name_without_ext + jav.type  # 【临时变量】path_new 视频文件的新路径
        # 一般情况，不存在同名视频文件
        if not exists(path_new):
            rename(jav.path, path_new)
            record_video_old(jav.path, path_new)
        # 已存在目标文件，但就是现在的文件
        elif jav.path.upper() == path_new.upper():
            try:
                rename(jav.path, path_new)
            # windows本地磁盘，“abc-123.mp4”重命名为“abc-123.mp4”或“ABC-123.mp4”没问题，但有用户反映，挂载的磁盘会报错“file exists error”
            except:
                num_fail += 1
                record_fail('    >第' + str(num_fail) + '个失败！请自行重命名大小写：' + path_relative + '\n')
        # 存在目标文件，不是现在的文件。
        else:
            num_fail += 1
            record_fail(
                '    >第' + str(num_fail) + '个失败！重命名影片失败，重复的影片，已经有相同文件名的视频了：' + path_new + '\n')
            raise FileExistsError                # 【终止对该jav的整理】
        dict_data['视频'] = name_without_ext      # 【更新】 dict_data['视频']
        jav.name = name_without_ext + jav.type   # 【更新】jav.name，重命名操作可能不成功，但之后的操作仍然围绕成功的jav.name来命名
        print('    >修改文件名' + str_cd + '完成')
        # 重命名字幕
        if jav.subtitle and settings.bool_rename_subtitle:
            subtitle_new = name_without_ext + jav.subtitle_type  # 【临时变量】subtitle_new
            path_subtitle_new = jav.root + sep + subtitle_new    # 【临时变量】path_subtitle_new
            if jav.path_subtitle != path_subtitle_new:
                rename(jav.path_subtitle, path_subtitle_new)
                jav.subtitle = subtitle_new     # 【更新】 jav.subtitle 字幕完整文件名
            print('    >修改字幕名完成')
    return dict_data, jav, num_fail


# 功能：2归类影片，只针对视频文件和字幕文件，无视它们当前所在文件夹
# 参数：设置settings，归类的目标目录路径root_classify，归类标准组合公式list_classify_basis，命名信息dict_data，处理的影片jav，已失败次数num_fail
# 返回：处理的影片jav（所在文件夹路径改变）、已失败次数num_fail
# 辅助：os.exists, os.rename, os.makedirs，
def classify_files(jav, num_fail, settings, dict_data, list_classify_basis, root_classify):
    # 如果需要归类，且不是针对文件夹来归类
    if settings.bool_classify and not settings.bool_classify_folder:
        # 移动的目标文件夹路径
        root_dest = root_classify + sep
        for j in list_classify_basis:
            root_dest += dict_data[j].rstrip()     # 【临时变量】归类的目标文件夹路径    C:\Users\JuneRain\Desktop\测试文件夹\葵司\
        # 还不存在该文件夹，新建
        if not exists(root_dest):
            makedirs(root_dest)
        path_new = root_dest + sep + jav.name      # 【临时变量】新的影片路径
        # 目标文件夹没有相同的影片，防止用户已经有一个“avop-127.mp4”，现在又来一个
        if not exists(path_new):
            rename(jav.path, path_new)
            print('    >归类视频文件完成')
            # 移动字幕
            if jav.subtitle:
                path_subtitle_new = root_dest + sep + jav.subtitle  # 【临时变量】新的字幕路径
                if jav.path_subtitle != path_subtitle_new:
                    rename(jav.path_subtitle, path_subtitle_new)
                    # 不再更新 jav.path_subtitle，下面不会再操作 字幕文件
                print('    >归类字幕文件完成')
            jav.root = root_dest                         # 【更新】jav.root
        else:
            num_fail += 1
            record_fail('    >第' + str(num_fail) + '个失败！归类失败，重复的影片，归类的目标文件夹已经存在相同的影片：' + path_new + '\n')
            raise FileExistsError    # 【终止对该jav的整理】
    return jav, num_fail


# 功能：3重命名文件夹【相同】如果已进行第2操作，第3操作不会进行，因为用户只需要归类视频文件，不需要管文件夹。
# 参数：设置settings，重命名文件夹的公式list_name_folder，命名信息dict_data，是否是独立文件夹bool_separate_folder，
#      处理的影片jav，该车牌总共多少cd num_all_episodes，已失败次数num_fail
# 返回：处理的影片jav（所在文件夹路径改变）、已失败次数num_fail
# 辅助：os.exists, os.rename, os.makedirs，record_fail
def rename_folder(jav, num_fail, settings, dict_data, list_name_folder, bool_separate_folder, num_all_episodes):
    if settings.bool_rename_folder:
        # 构造 新文件夹名folder_new
        folder_new = ''
        for j in list_name_folder:
            folder_new += (dict_data[j])
        folder_new = folder_new.rstrip(' .')  # 【临时变量】新的所在文件夹。去除末尾空格和“.”
        # 是独立文件夹，才会重命名文件夹
        if bool_separate_folder:
            # 当前视频是该车牌的最后一集，他的兄弟姐妹已经处理完成，才会重命名它们的“家”。
            if jav.episode == num_all_episodes:
                list_root_now = jav.root.split(sep)
                del list_root_now[-1]
                root_new = sep.join(list_root_now) + sep + folder_new  # 【临时变量】新的影片所在文件夹路径。
                # 想要重命名的目标影片文件夹不存在
                if not exists(root_new):
                    rename(jav.root, root_new)
                    jav.root = root_new            # 【更新】jav.root
                # 目标影片文件夹存在，但就是现在的文件夹，即新旧相同
                elif jav.root == root_new:
                    pass
                # 真的有一个同名的文件夹了
                else:
                    num_fail += 1
                    record_fail('    >第' + str(num_fail) + '个失败！重命名文件夹失败，已存在相同文件夹：' + root_new + '\n')
                    raise FileExistsError    # 【终止对该jav的整理】
                print('    >重命名文件夹完成')
        # 不是独立的文件夹，建立独立的文件夹
        else:
            path_separate_folder = jav.root + sep + folder_new  # 【临时变量】需要创建的的影片所在文件夹。
            # 确认没有同名文件夹
            if not exists(path_separate_folder):
                makedirs(path_separate_folder)
            path_new = path_separate_folder + sep + jav.name   # 【临时变量】新的影片路径
            # 如果这个文件夹是现成的，在它内部确认有没有“abc-123.mp4”。
            if not exists(path_new):
                rename(jav.path, path_new)
                # 移动字幕
                if jav.subtitle:
                    path_subtitle_new = path_separate_folder + sep + jav.subtitle  # 【临时变量】新的字幕路径
                    rename(jav.path_subtitle, path_subtitle_new)
                    # 下面不会操作 字幕文件 了，jav.path_subtitle不再更新
                    print('    >移动字幕到独立文件夹')
                jav.root = path_separate_folder                # 【更新】jav.root
            # 里面已有“avop-127.mp4”，这不是它的家。
            else:
                num_fail += 1
                record_fail('    >第' + str(num_fail) + '个失败！创建独立文件夹失败，已存在相同的视频文件：' + path_new + '\n')
                raise FileExistsError    # 【终止对该jav的整理】
    return jav, num_fail


# 功能：6为当前jav收集演员头像到“.actors”文件夹中
# 参数：演员们 list_actors，jav当前所处文件夹的路径root_now
# 返回：无
# 辅助：os.path.exists，os.makedirs, configparser.RawConfigParser, shutil.copyfile
def collect_sculpture(list_actors, root_now):
    for each_actor in list_actors:
        path_exist_actor = '演员头像' + sep + each_actor[0] + sep + each_actor  # 事先准备好的演员头像路径
        if exists(path_exist_actor + '.jpg'):
            pic_type = '.jpg'
        elif exists(path_exist_actor + '.png'):
            pic_type = '.png'
        else:
            config_actor = RawConfigParser()
            config_actor.read('【缺失的演员头像统计For Kodi】.ini', encoding='utf-8')
            try:
                each_actor_times = config_actor.get('缺失的演员头像', each_actor)
                config_actor.set("缺失的演员头像", each_actor, str(int(each_actor_times) + 1))
            except:
                config_actor.set("缺失的演员头像", each_actor, '1')
            config_actor.write(open('【缺失的演员头像统计For Kodi】.ini', "w", encoding='utf-8'))
            continue
        # 已经收录了这个演员头像
        root_dest_actor = root_now + sep + '.actors' + sep  # 头像的目标文件夹
        if not exists(root_dest_actor):
            makedirs(root_dest_actor)
        # 复制一份到“.actors”
        copyfile(path_exist_actor + pic_type, root_dest_actor + each_actor + pic_type)
        print('    >演员头像收集完成：', each_actor)


# 功能：7归类影片，针对文件夹（如果已进行第2操作，第7操作不会进行，因为用户只需要归类视频文件，不需要管文件夹）
# 参数：设置settings，处理的影片jav，该车牌总共多少cd num_all_episodes，是否是独立文件夹bool_separate_folder，
#      归类的目标目录路径root_classify，当前处理的文件夹路径root，命名信息dict_data
# 返回：处理的影片jav（所在文件夹路径改变）、已失败次数num_fail
# 辅助：os.exists, os.rename, os.makedirs，
def classify_folder(jav, num_fail, settings, dict_data, list_classify_basis, root_classify, root, bool_separate_folder, num_all_episodes):
    if settings.bool_classify and settings.bool_classify_folder and jav.episode == num_all_episodes:  # 需要移动文件夹，且，是该影片的最后一集
        # 用户选择的文件夹是一部影片的独立文件夹，为了避免在这个文件夹里又生成新的归类文件夹
        if bool_separate_folder and root_classify.startswith(root):
            print('    >无法归类，请选择该文件夹的上级文件夹作它的归类根目录')
            return num_fail
        # 归类放置的目标文件夹
        root_dest = root_classify + sep
        # 移动的目标文件夹
        for j in list_classify_basis:
            root_dest += dict_data[j].rstrip(' .')  # 【临时变量】 文件夹移动的目标上级文件夹  C:\Users\JuneRain\Desktop\测试文件夹\1\葵司\
        root_new = root_dest + sep + jav.folder  # 【临时变量】 文件夹移动的目标路径   C:\Users\JuneRain\Desktop\测试文件夹\1\葵司\【葵司】AVOP-127\
        # print(root_new)
        # 还不存在归类的目标文件夹
        if not exists(root_new):
            makedirs(root_new)
            # 把现在文件夹里的东西都搬过去
            jav_files = listdir(jav.root)
            for i in jav_files:
                rename(jav.root + sep + i, root_new + sep + i)
            # 删除“旧房子”，这是javsdt唯一的删除操作，而且os.rmdir只能删除空文件夹
            rmdir(jav.root)
            print('    >归类文件夹完成')
        # 用户已经有了这个文件夹，可能以前处理过同车牌的视频
        else:
            num_fail += 1
            record_fail('    >第' + str(num_fail) + '个失败！归类失败，归类的目标位置已存在相同文件夹：' + root_new + '\n')
            raise FileExistsError
    return num_fail
