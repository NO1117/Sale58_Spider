#!/usr/bin/env/ python 
# -*- coding:utf-8 -*-
# Author:Mr.Xu

import pymongo
from Sale.config import *

class MongoDB(object):

    def __init__(self, host=MONGO_HOST, port=MONGO_PORT, password=MONGO_PASSWORD, db=MONGO_DB):
        """
        初始化
        :param host: Redis 地址
        :param port: Redis 端口
        :param password: Redis 密码
        """
        if password:
            self._client = pymongo.MongoClient(host=host, port=port, password=password)
        else:
            self._client = pymongo.MongoClient(host=host, port=port)
            self._db = self._client[db]

    def insert(self, collection=None, item=None):
        collections = self._db[collection]
        collections.insert(item)
        print("Save to Mongo success!")

    def find_data(self, collection=None):
        collections = self._db[collection]
        return collections.find()

if __name__=='__main__':
    db = MongoDB()
    # db.find_data()
