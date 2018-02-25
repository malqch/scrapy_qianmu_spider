# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import logging
import pymysql
import redis
from scrapy.exceptions import DropItem

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class CheckPipeline(object):
    def process_item(self, item, spider):
        if not item['undergraduate_num'] or not item['postgraduate_num']:
            raise DropItem('Missing field in %s' % item)
        return item

class RedisPipeline(object):
    def __init__(self):
        self.r = redis.Redis()

    def process_item(self, item, spider):
        self.r.sadd(spider.name, item['name'])
        logger.info('redis: add %s to %s' % (item['name'], spider.name))
        return item

class MysqlPipeline(object):
    def __init__(self):
        self.conn = None
        self.cur = None

    def open_spider(self, spider):
        self.conn = pymysql.connect(
            host='localhost',
            port=3306,
            user='root',
            password='rock1204',
            db='qianmu',
            charset='utf8',
        )
        self.cur = self.conn.cursor()

    def close_spider(self, spider):
        self.cur.close()
        self.conn.close()

    def process_item(self, item, spider):
        # sql = "INSERT INTO `universities`(`name`, `rank`,"\
        #        "`country`, `state`, `city`, `undergraduate_num`,"\
        #        "`postgraduate_num`, `website`) VALUES "\
        #         "(%s, %s, %s, %s, %s, %s, %s, %s);"
        # self.cur.execute(sql, (item['name'], item['rank'],
        #                        item['country'], item['state'],
        #                        item['city'], item['undergraduate_num'],
        #                        item['postgraduate_num'], item['website']))
        # cols = item.keys()
        # values = [item[col] for col in cols]
        # cols = ['`%s`' % key for key in cols]
        # sql = "INSERT INTO `universities`(" + ','.join(cols) + ") VALUES "\
        #       "(" + ','.join(['%s'] * len(cols)) + ");"
        # print(sql)
        # cols, values = zip(*[(col, item[col]) for col in item.keys()])
        cols, values = zip(*item.items())
        sql = "INSERT INTO `universities`(%s) VALUES (%s)" % \
              (','.join(['`%s`' % col for col in cols]), ','.join(['%s'] * len(cols)))
        self.cur.execute(sql, values)
        self.conn.commit()
        logger.info(self.cur._last_executed)
        return item