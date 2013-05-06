#! /usr/bin/env python
# -*- coding: utf-8 -*-
#@author zcwang3@gmail.com
#@version 2011-04-12 16:34
#Nginx日志分析，初始做成

import os
import fileinput
import re

#日志的位置
dir_log  = r"/tmp/logs"

log_content = """
122.227.101.160 - - [01/Apr/2013:06:20:04 +0800] "GET /media/new/2011/10/27/hd_dsj_jwcz20_20111027.ts HTTP/1.0" 206 163840 "-" "-" "-"
122.227.101.166 - - [01/Apr/2013:06:20:05 +0800] "GET /media/new/2012/06/28/hd_dy_tgst_20120628.ts HTTP/1.0" 206 161856 "-" "010133501017470#000000210
000000300000A10000000E2###Feb 25 2013,10:42:24" "-"
122.227.101.163 - - [01/Apr/2013:06:20:05 +0800] "GET /media/new/2011/11/23/hd_dsj_wdmlrs17_20111123.ts HTTP/1.0" 206 163840 "-" "-" "-"
122.227.101.165 - - [01/Apr/2013:06:20:05 +0800] "GET /media/new/2011/11/03/hd_dy_dhw_20111103.ts HTTP/1.0" 416 206 "-" "010106050000890#0000000600000
0060000qhtf201212141204725#1#2.0.9.9#Sep 10 2012,13:42:02" "-"
122.227.101.165 - - [01/Apr/2013:06:20:05 +0800] "GET /media/new/2011/11/03/hd_dy_dhw_20111103.ts HTTP/1.0" 416 206 "-" "010106050000890#0000000600000
0060000qhtf201212141204725#1#2.0.9.9#Sep 10 2012,13:42:02" "-"
122.227.101.160 - - [01/Apr/2013:06:20:05 +0800] "GET /media/new/2012/12/29/sd_dsj_xznhxqc19_20121229.ts HTTP/1.0" 206 81920 "-" "010133501013727#0000
00210000000300000A10000000E2###Feb 25 2013,10:42:24" "-"
122.227.101.163 - - [01/Apr/2013:06:20:05 +0800] "GET /media/new/2011/09/26/hd_dy_lsjq_20110926.ts HTTP/1.0" 206 163840 "-" "010121007006432#000000210
tcc8925000002.0201212291120520#2#4.0.1.30#Jan 30 2013,21:03:31" "-"
122.227.101.160 - - [01/Apr/2013:06:20:05 +0800] "GET /media/new/2012/06/29/hd_dy_wmtw_20120629.ts HTTP/1.0" 206 163840 "-" "-" "-"
122.227.101.164 - - [01/Apr/2013:06:20:06 +0800] "GET /media/new/2012/12/19/hd_dy_xsdzd_20121219.ts HTTP/1.0" 206 163840 "-" "010133501001726#00000021
0000000300000A10000000E2###Feb 25 2013,10:42:24" "-"
122.227.101.159 - - [01/Apr/2013:06:20:06 +0800] "GET /media/new/2013/01/04/sd_zy_fyt04_20130104.ts HTTP/1.0" 206 163840 "-" "010122002019606#00000022
00000022000leshi201212141211979#1#2.0.9.9#Nov  5 2012,22:00:48" "-"
122.227.101.163 - - [01/Apr/2013:06:20:06 +0800] "GET /media/new/2012/12/27/sd_zy_gjyrhwj_20121227.ts HTTP/1.0" 206 163840 "-" "010122002009161#000000
2200000022000leshi201212141211979#1#2.0.9.9#Nov  5 2012,22:00:48" "-"
122.227.101.163 - - [01/Apr/2013:06:20:06 +0800] "GET /media/new/2012/12/27/sd_zy_gjyrhwj_20121227.ts HTTP/1.0" 206 163840 "-" "010122002009161#000000
2200000022000leshi201212141211979#1#2.0.9.9#Nov  5 2012,22:00:48" "-"
122.227.101.164 - - [01/Apr/2013:06:20:06 +0800] "GET /media/new/2013/02/18/hd_dy_slmbz02_20130218.ts HTTP/1.0" 206 81920 "-" "010133501012952#0000002
10000000300000A10000000E2###Feb 25 2013,10:42:24" "-"
"""
#使用的nginx默认日志格式$remote_addr - $remote_user [$time_local] "$request" $status $body_bytes_sent "$http_referer" "$http_user_agent" "$http_x_forwarded_for"'
#日志分析正则表达式

#203.208.60.230
ipP = r"?P<ip>[\d.]*";

#[21/Jan/2011:15:04:41 +0800]
timeP = r"""?P<time>\[           #以[开始
            [^\[\]]* #除[]以外的任意字符  防止匹配上下个[]项目(也可以使用非贪婪匹配*?)  不在中括号里的.可以匹配换行外的任意字符  *这样地重复是"贪婪的“ 表达式引擎会试着重复尽可能多的次数。
            \]           #以]结束
        """

#"GET /EntpShop.do?method=view&shop_id=391796 HTTP/1.1"
requestP = r"""?P<request>\"          #以"开始
            [^\"]* #除双引号以外的任意字符 防止匹配上下个""项目(也可以使用非贪婪匹配*?)
            \"          #以"结束
            """

statusP = r"?P<status>\d+"

bodyBytesSentP = r"?P<bodyByteSent>\d+"

#"http://test.myweb.com/myAction.do?method=view&mod_id=&id=1346"
referP = r"""?P<refer>\"          #以"开始
            [^\"]* #除双引号以外的任意字符 防止匹配上下个""项目(也可以使用非贪婪匹配*?)
            \"          #以"结束
        """

#"Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"'
userAgentP = r"""?P<userAgent>\"              #以"开始
        [^\"]* #除双引号以外的任意字符 防止匹配上下个""项目(也可以使用非贪婪匹配*?)
        \"              #以"结束
            """

#原理：主要通过空格和-来区分各不同项目，各项目内部写各自的匹配表达式
nginxLogPattern = re.compile(r"(%s)\ -\ -\ (%s)\ (%s)\ (%s)\ (%s)\ (%s)\ (%s)" %(ipP, timeP, requestP, statusP, bodyBytesSentP, referP, userAgentP), re.VERBOSE)

def processDir(dir_proc):
    for file in os.listdir(dir_proc):
        if os.path.isdir(os.path.join(dir_proc, file)):
            print "WARN:%s is a directory" %(file)
            processDir(os.path.join(dir_proc, file))
            continue

        if not file.endswith(".log"):
            print "WARN:%s is not a log file" %(file)
            continue

        print "INFO:process file %s" %(file)
        for line in fileinput.input(os.path.join(dir_proc, file)):
            matchs = nginxLogPattern.match(line)
            if matchs!=None:
                allGroups = matchs.groups()
                ip = allGroups[0]
                time = allGroups[1]
                request = allGroups[2]
                status =  allGroups[3]
                bodyBytesSent = allGroups[4]
                refer = allGroups[5]
#                userAgent = allGroups[6]
                userAgent = matchs.group("userAgent")
                print userAgent

                #统计HTTP状态码的数量
                GetResponseStatusCount(userAgent)
                #在这里补充其他任何需要的分析代码
            else:
                raise Exception

        fileinput.close()

allStatusDict = {}
#统计HTTP状态码的数量
def GetResponseStatusCount(status):
    if allStatusDict.has_key(status):
        allStatusDict[status] += 1;
    else:
        allStatusDict[status] = 1;


if __name__ == "__main__":
    processDir(dir_log)
    print allStatusDict
    #根据值进行排序（倒序）
    print sorted(allStatusDict.items(), key=lambda d:d[1], reverse=True)
    print "done, python is great!"
