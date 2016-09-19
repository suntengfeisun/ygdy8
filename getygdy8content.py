# -*- coding: utf-8 -*-

import sys
import threading
import requests
from lxml import etree
from mysqlpooldao import MysqlDao
import time
from headers import Headers
import simplejson
from config import Config

reload(sys)
sys.setdefaultencoding('utf8')


class Worker(threading.Thread):
    def getContent(self, url, category_id):
        headers = Headers.getHeaders()
        sleep_time = 1
        while True:
            try:
                req = requests.get(url, headers=headers, timeout=30)
                break
            except:
                print('sleep10')
                time.sleep(10 * sleep_time)
                sleep_time = sleep_time + 1
        if req.status_code == 200:
            html = req.content.decode('gb2312', 'ignore')
            selector = etree.HTML(html)
            root_path = selector.xpath('//div[contains(@id,"Zoom")]')
            names = selector.xpath('//div[contains(@class,"title_all")]/h1/font/text()')
            if len(root_path) > 0:
                contents = simplejson.dumps(root_path[0].xpath('descendant::text()'))
                imgs = simplejson.dumps(root_path[0].xpath('descendant::img/@src'))
                if len(names) > 0:
                    name = names[0]
                else:
                    name = ''
                print(name)
                created_at = time.strftime('%Y-%m-%d %H:%M:%S')
                sql_values = (category_id, name, contents, imgs, created_at, url)
                return sql_values
        else:
            pass

    def run(self):
        while True:
            print(self.name)
            mysqlDao = MysqlDao()
            sql = 'select * from ygdy8_url WHERE `status`=0 limit 0,1'
            ret = mysqlDao.execute(sql)
            if (len(ret) > 0):
                res = ret[0]
                id = res[0]
                sql = 'update ygdy8_url set `status`=2 where `id`=' + str(id)
                mysqlDao.execute(sql)
                category_id = res[1]
                url = res[2]
                sql_values = self.getContent(url, category_id)
                if sql_values != None:
                    sql_pattern = 'insert ignore INTO `ygdy8_content`(`category_id`,`name`, `content`, `img`,`created_at`, `url`) VALUES( %s, %s, %s, %s, %s, %s)'
                    mysqlDao.executeValues(sql_pattern, sql_values)
                    sql = 'update ygdy8_url set `status`=1 where `id`=' + str(id)
                    mysqlDao.execute(sql)
                mysqlDao.close()
            else:
                mysqlDao.close()
                break
                # print(self.name + 'sleep')
                # time.sleep(3600)


if __name__ == '__main__':
    worker_num = 10
    threads = []
    for x in xrange(0, worker_num):
        threads.append(Worker())
    for t in threads:
        t.start()
        time.sleep(5)
    for t in threads:
        t.join()
    print('game over')