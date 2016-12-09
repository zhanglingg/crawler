#!/usr/bin/python
# -*- coding: UTF-8 -*-
import django
import os

import time
from multiprocessing import Pool
from tornado import httpclient, gen, ioloop, queues

from mobo360.sina.controller import Login
from mobo360.sina.controller import CrawlerFans
from mobo360.sina.controller import CrawlerPersonal
from mobo360.sina.model.user import sina_user

os.environ['DJANGO_SETTINGS_MODULE'] = 'untitled.settings'
if django.VERSION >= (1,7):
    django.setup()

class AsySpider(object):

    def __init__(self,driver,num):
        self.num = num
        self.driver = driver
        self._q = queues.Queue()
        self._fetching = set()
        self._fetched = set()

    @gen.coroutine
    def _run(self):
        @gen.coroutine
        def run_first_get_fans(list):
            CrawlerFans.first_main(self.driver,list)

        @gen.coroutine
        def run_person_get_fans():
            CrawlerFans.person_main(self.driver)

        @gen.coroutine
        def run_person_get_info():
            list = sina_user.UserInfo.objects.filter(crTime__istartswith='2016-11-25')
            for user in list:
                CrawlerPersonal.personal_info_main(self.driver, user)

        @gen.coroutine
        def worker():
            if self.num == 3:
                list = ["至上励合","至上励合张远","至上励合_马雪阳MARS","至上励合小五金恩圣"]
                run_first_get_fans(list)
            elif self.num == 2:
                run_person_get_fans()
            elif self.num == 3:
                run_person_get_info()
        worker()

    def run(self):
        io_loop = ioloop.IOLoop.current()
        io_loop.run_sync(self._run)


def run_login():
    driver = Login.main("","");
    return driver;


def run_spider(driver,num):
    s = AsySpider(driver,num)
    s.run()

if __name__ == '__main__':
    driver = run_login()
    _st = time.time()
    p = Pool()
    all_num = 73000
    num = 3  # number of cpu cores
    per_num, left = divmod(all_num, num)
    s = range(0, all_num, per_num)
    res = []
    for i in range(len(s) - 2):
        res.append((s[i], s[i + 1]))
    res.append((s[len(s) - 1], all_num))
    print res
    for i in res:
        p.apply_async(run_spider(driver, num, ), args=(i[0], i[1],))
        num = num - 1
    p.close()
    p.join()
    print time.time() - _st

