#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import time

import django
from selenium.webdriver.chrome.webdriver import WebDriver

import CrawlerFans
from mobo360.sina.model.user import sina_user
from mobo360.core.utils import DateUtils
from mobo360.sina.controller import Login

os.environ['DJANGO_SETTINGS_MODULE'] = 'untitled.settings'
if django.VERSION >= (1,7):
    django.setup()


# 初始化数据
def first_get(driver):
    try:
        time.sleep(2)
        print '解析个人信息。。。。。。。。。'
        try :
            pf_opt = driver.find_element_by_class_name('pf_opt')
            btn_bed = pf_opt.find_element_by_class_name('btn_bed')
            action_data = btn_bed.get_attribute('action-data')
            uidArray = action_data.split('&', action_data.count("&"))
            uid = uidArray[0].split("=", action_data.count("="))[1]

            pf_photo = driver.find_element_by_class_name('pf_photo')
            img = pf_photo.find_elements_by_tag_name('img')
            headerPath = img[0].get_attribute('src')

            pf_username = driver.find_element_by_class_name('pf_username')
            h1_username = pf_username.find_elements_by_tag_name('h1')
            username = h1_username[0].text

            user = sina_user.UserInfo()
            user.sinaNo = uid
            user.headerPath = headerPath
            user.nickName = username
            user.crTime = DateUtils.now_time()
            sina_user.UserInfo.save(user)

        except Exception:
            pass
        print '解析粉丝主页信息。。。。。。。'
        analysis_fans(driver)
        page_fans(driver)
    except Exception:
        raise Exception


# 获得个人粉丝页面的所有分页地址
def page_fans(driver):
    try:
        w_pages = driver.find_element_by_class_name('W_pages')
        page_a = w_pages.find_elements_by_tag_name('a')
        href_list = list()
        for a in page_a:
            href = a.get_attribute("href")
            href_list.append(href)
        for href in href_list:
            if isinstance(href, basestring):
                print 'fans_page url :', href
                next_url = href;
                driver.get(next_url)
                time.sleep(3)
                try:
                    time.sleep(2)
                    analysis_fans(driver)
                except Exception:
                    break
    except Exception:
        raise Exception


# 解析每页粉丝信息
def analysis_fans(driver):
    if isinstance(driver,WebDriver):
        Login.to_bottom(driver)
    try:
        follow_list = driver.find_element_by_class_name('follow_list')
        li_list = follow_list.find_elements_by_tag_name('li')
        for li in li_list:
            try :
                # uid=6011451430&amp;fnick=喜欢姓王的&amp;sex=f
                user_info = li.get_attribute('action-data')

                mod_pic = li.find_element_by_tag_name('img')
                user = get_li_info(user_info)
                if user:
                    img = mod_pic.get_attribute('src')
                    user.headerPath = img
                    user.save()
            except Exception:
                continue
    except Exception:
        print Exception.message
        raise Exception


# 分解粉丝信息
def get_li_info(user_info):
    if isinstance(user_info, basestring): # uid=5234670682&fnick=菠萝包胖次&sex=m
        info = user_info.split('&',user_info.count("&"))
        #uid
        uidArray = info[0].split("=", user_info.count("="))
        uid = uidArray[1]
        # fnick
        fnickArray = info[1].split("=",user_info.count("="))
        fnick = fnickArray[1]
        # sex
        sexArray = info[2].split("=",user_info.count("="))
        sex = sexArray[1]
        a = sina_user.UserInfo.objects.filter(sinaNo=uid)
        if len(a) <= 0:
            user = sina_user.UserInfo()
        else:
            user = a[0]
        user.sinaNo = uid
        user.nickName = fnick
        user.gender = sex

        user.crTime = DateUtils.now_time()
    else :
        user = sina_user.UserInfo()
    return user

