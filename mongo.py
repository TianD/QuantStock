#!/usr/bin/env python
# coding=utf-8
# Copyright (c) 2019 MoreVFX. All rights reserved.
# created by huiguoyu @ 2020/8/15 17:53
import time

import pandas as pd
import pymongo
import StockGetter

client = pymongo.MongoClient("mongodb://localhost:27017")


db = client['quantstock']

stock_collection = ["stocks"]


date_list = pd.date_range('2020-08-04', '2020-08-15')
for date in date_list:
    if StockGetter.request_date_is_holiday(date._date_repr):
        am_start_time = pd.to_datetime('%s 09:30:00' % date._date_repr)




# 1596378520000
# 1596499200000000000


# x = stock_collection.insert_one(mydict)