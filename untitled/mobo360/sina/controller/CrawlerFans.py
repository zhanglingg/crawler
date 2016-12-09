#!/usr/bin/python
# -*- coding: UTF-8 -*-
import django
import os
import re
import time

from mobo360.sina.model.user import sina_user
from mobo360.core.utils import DateUtils
from mobo360.sina.controller import Login
import  AnalysisData

os.environ['DJANGO_SETTINGS_MODULE'] = 'untitled.settings'
if django.VERSION >= (1,7):
    django.setup()


def first_main(driver,list):
    for topic in list:
        try:
            get_fans_from_search(topic, driver)
            AnalysisData.first_get(driver)
        except Exception:
            continue
    driver.close()


# 使用搜索名称操作跳转粉丝页面
def get_fans_from_search(topic,driver):
    time.sleep(20)
    driver.get('http://s.weibo.com/weibo/{}?topnav=1&wvr=6&b=1'.format(topic))
    print "已到目标页面........"
    time.sleep(10)
    Login.to_bottom(driver)
    e = driver.find_elements_by_tag_name("a")
    nextHref = ''
    for x in e:
        href = x.get_attribute("href")
        # print href
        if isinstance(href, basestring):
            searchFlag = re.search('/fans', href, re.M | re.I)
            if (searchFlag):
                nextHref = href;
                break
    if nextHref.strip() != '':
        print "Go to next href:", nextHref
        driver.get(nextHref)
    return driver


# 通过个人首页跳转粉丝页面
def get_fans_from_person_info(uid,driver):
    nextHref = 'http://weibo.com/'+uid+'/fans?rightmod=1&wvr=6'
    print "Go to next href:", nextHref
    driver.get(nextHref)
    return driver


def person_main(driver):
    # 获得当天用户信息
    user_list = sina_user.UserInfo.objects.filter(crTime__istartswith=DateUtils.now_date())
    for user in user_list:
        try :
            uid = user.sinaNo
            print uid
            get_fans_from_person_info(user.sinaNo, driver)
            time.sleep(2)
            print '解析粉丝信息。。。。。。。'
            AnalysisData.analysis_fans(driver)
            AnalysisData.page_fans(driver)

            print user.sinaNo
        except Exception:
            continue


if __name__ == '__main__':
    driver = Login.main("771539058@qq.com", "cbyz.0820")
    time.sleep(2)
    # person_main(driver)
    list = ['至上励合张远', '至上励合_马雪阳MARS']
    first_main(driver,list)
