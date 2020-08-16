#!/usr/bin/env python
# coding=utf-8
# Copyright (c) 2019 MoreVFX. All rights reserved.
# created by huiguoyu @ 2020/8/15 17:53
import time

import pandas as pd
import pymongo
import StockGetter
#
# client = pymongo.MongoClient("mongodb://192.168.31.169:27017")
#
#
# db = client['quantstock']
#
# stock_collection = ["stocks"]


date_list = pd.date_range('2020-08-04', '2020-08-15')
for date in date_list:
    if StockGetter.request_date_is_holiday(date._date_repr):
        am_start_time = pd.to_datetime('%s 09:30:00' % date._date_repr)
        am_end_time = pd.to_datetime('%s 11:30:00' % date._date_repr)
        am_time_list = pd.date_range(am_start_time, am_end_time, freq='S')
        pm_start_time = pd.to_datetime('%s 13:00:00' % date._date_repr)
        pm_end_time = pd.to_datetime('%s 15:00:00' % date._date_repr)
        pm_time_list = pd.date_range(pm_start_time, pm_end_time, freq='S')
        time_combined = pd.concat([am_time_list.to_series(),
                               pm_time_list.to_series()])
        time_list = pd.DatetimeIndex(time_combined)
        for query_time in time_list:
            print query_time.value

            "https://hq.sinajs.cn /rn = 1597556518326 & list = s_sz000002, s_sh600377, s_sh600036, s_sh600050, s_sh601398, s_sh600111, s_sh601857, s_sh600028, s_sh601899"
            a = StockGetter.request_stock(query_time.value/1000000, 's_sz002668')
            print a[0]
            break
        break


# 1596378520000
# 1596499200000000000


# x = stock_collection.insert_one(mydict)