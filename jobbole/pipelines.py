# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


class JobbolePipeline(object):
    def process_item(self, item, spider):
        return item


#方法2：采用异步的机制写入mysql
import pymysql.cursors
from twisted.enterprise import adbapi

#连接池ConnectionPool
#    def __init__(self, dbapiName, *connargs, **connkw):
class MysqlTwistedPipline(object):
    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        dbparms = dict(
            host = settings["MYSQL_HOST"],
            db = settings["MYSQL_DBNAME"],
            user = settings["MYSQL_USER"],
            passwd = settings["MYSQL_PASSWD"],
            charset='utf8',
            cursorclass=pymysql.cursors.DictCursor,
            use_unicode=True,
        )
        #**dbparms-->("MySQLdb",host=settings['MYSQL_HOST']
        dbpool = adbapi.ConnectionPool("pymysql", **dbparms)#无需直接导入 dbmodule. 只需要告诉 adbapi.ConnectionPool 构造器你用的数据库模块的名称比如pymysql.

        return cls(dbpool)

    def process_item(self, item, spider):
        #使用twisted将mysql插入变成异步执行
        query = self.dbpool.runInteraction(self.do_insert, item)
        query.addErrback(self.handle_error, item, spider) #处理异常

    def handle_error(self, failure, item, spider):
        #处理异步插入的异常
        print (failure)

    def do_insert(self, cursor, item):
        #执行具体的插入
        #根据不同的item 构建不同的sql语句并插入到mysql中
        insert_sql, params = item.get_insert_sql()
        cursor.execute(insert_sql, params)

