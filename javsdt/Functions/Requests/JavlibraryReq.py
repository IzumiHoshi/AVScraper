'''
Author: izumihoshi
Date: 2023-05-13 11:58:40
LastEditors: izumihoshi
LastEditTime: 2023-10-09 23:32:31
FilePath: \AVScraper\javsdt\Functions\Requests\JavlibraryReq.py
Description: TODO

Copyright (c) 2023 by Honor, All Rights Reserved.
'''
# -*- coding:utf-8 -*-
import re, os, requests
from bs4 import BeautifulSoup

# from traceback import format_exc
# import cfscrape
# 功能：请求各大jav网站和arzon的网页
# 参数：网址url，请求头部header/cookies，代理proxy
# 返回：网页html，请求头部


#################################################### javlibrary ########################################################
# 搜索javlibrary，或请求javlibrary上jav所在网页，返回html
def search_library_html(url_library, car, proxy, retry_times=1):
    url_web = url_library + 'vl_searchbyid.php?keyword=' + car[:-1]
    for retry in range(retry_times):
        try:
            if proxy:
                rqs = requests.get(url_web, proxies=proxy, timeout=(6, 7))
            else:
                rqs = requests.get(url_web, timeout=(6, 7))
        except requests.exceptions.ProxyError:
            # print(format_exc())
            print('    >通过局部代理失败，重新尝试...')
            continue
        except:
            print(format_exc())
            print('    >打开网页失败，重新尝试...')
            continue
        rqs.encoding = 'utf-8'
        rqs_content = rqs.text
        # print(rqs_content)
        web_data = find_herf(rqs_content, car)  # 得到想要的网页，直接返回
        # print(type(web_data), web_data)
        if web_data is not None:
            web_data = web_data.replace("./", url_library)
            return web_data
        else:  # 代理工具返回的错误信息
            print('    >代理工具返回的错误信息，重新尝试...')
            continue
    print('>>请检查你的网络环境是否可以打开：', url_web)
    os.system('pause')


def get_library_html(url, proxy):
    for retry in range(10):
        try:
            if proxy:
                rqs = requests.get(url, proxies=proxy, timeout=(6, 7))
            else:
                rqs = requests.get(url, timeout=(6, 7))
        except requests.exceptions.ProxyError:
            # print(format_exc())
            print('    >通过局部代理失败，重新尝试...')
            continue
        except:
            # print(format_exc())
            print('    >打开网页失败，重新尝试...')
            continue
        rqs.encoding = 'utf-8'
        rqs_content = rqs.text
        # print(rqs_content)
        if re.search(r'JAVLibrary', rqs_content):  # 得到想要的网页，直接返回
            return rqs_content
        else:  # 代理工具返回的错误信息
            print('    >代理工具返回的错误信息，重新尝试...')
            continue
    print('>>请检查你的网络环境是否可以打开：', url)
    os.system('pause')


def find_herf(html_text, car):
    soup = BeautifulSoup(html_text, 'html.parser')
    video_divs = soup.select('div.video')
    target_href = None

    for video_div in video_divs:
        id_div = video_div.find('div', class_='id')
        if id_div and re.search(car, id_div.text):
            a_tag = video_div.find('a')
            if a_tag:
                target_href = a_tag['href']
                break
    return target_href