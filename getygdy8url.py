# -*- coding: utf-8 -*-

import sys
import requests
from lxml import etree
from headers import Headers
from config import Config
from mysqlpooldao import MysqlDao
import time
from selenium import webdriver

reload(sys)
sys.setdefaultencoding('utf8')


def getUrl(mysqlDao, category_id, url):
    time.sleep(1)
    driver = webdriver.PhantomJS(service_args=['--load-images=no'])
    driver.get(url)
    dr = driver
    # 获取url
    data = driver.find_elements_by_xpath('//*[@class="co_content8"]/descendant::a')
    for d in data:
        url_content = d.get_attribute("href")
        if 'index' in url_content or 'list' in url_content:
            pass
        else:
            created_at = time.strftime('%Y-%m-%d %H:%M:%S')
            sql_pattern = 'insert ignore into ygdy8_url (`url`,`category_id`,`status`,`created_at`) values(%s,%s,%s,%s)'
            sql_values = (url_content, category_id, 0, created_at)
            print(sql_values)
            mysqlDao.executeValues(sql_pattern, sql_values)

    # 获取翻页
    data = dr.find_elements_by_xpath('//a[contains(text(),"%s")]' % (u'下一页'))
    if len(data) > 0:
        url_next = data[0].get_attribute("href")
        driver.quit()
        print(111, url_next, 2222)
        getUrl(mysqlDao, category_id, url_next)


if __name__ == '__main__':
    mysqlDao = MysqlDao()
    sql = 'select * FROM ygdy8_category'
    res = mysqlDao.execute(sql)
    for r in res:
        category_id = r[0]
        url = r[2]
        getUrl(mysqlDao, category_id, url)
    mysqlDao.close()
