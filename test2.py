#!/usr/bin/env python
 #-*- coding:utf-8 -*-
import fileinput
import gzip
import os
import re


#使用的nginx默认日志格式$remote_addr - $remote_user [$time_local] "$request" $status $body_bytes_sent "$http_referer" "$http_user_agent"              "$http_x_forwarded_for"'
#日志分析正则表达式

#203.208.60.230
ipP = r"?P<ip>[\d.]*";

#[21/Jan/2011:15:04:41 +0800]
timeP = r"""?P<time>\[           #以[开始
            [^\[\]]* #除[]以外的任意字符  防止匹配上下个[]项目(也可以使用非贪婪匹配*?)  不在中括号里的.可以匹配换行外的任意字符  *                    这样地重复是"贪婪的“ 表达式引擎会试着重复尽可能多的次数。
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
#nginxLogPattern = re.compile(r"(%s)\ -\ -\ (%s)\ (%s)\ (%s)\ (%s)\ (%s)\ (%s)" %(ipP, timeP, requestP, statusP, bodyBytesSentP, referP, userAgentP),  re.VERBOSE)
nginxLogPattern = re.compile(r"(%s)\ -\ -\ (%s)\ (%s)\ (%s)\ (%s)\ (%s)\ (%s)" %(ipP, timeP, requestP, statusP, bodyBytesSentP, referP, userAgentP), re.VERBOSE)

def processGZfile(file_proc):
    print "INFO: process file %s" % file_proc
    f = gzip.open(file_proc,'rb')
    s = f.read().splitlines()
    f.close()
    for line in s:
        matchs = nginxLogPattern.match(line)
        if matchs!=None:
            allGroups = matchs.groups()
            ip = allGroups[0]
            time = allGroups[1]
            request = allGroups[2]
            status =  allGroups[3]
            bodyBytesSent = allGroups[4]
            refer = allGroups[5]
#           userAgent = allGroups[6]
            userAgent = matchs.group("userAgent")
            print request
        else:
            raise Exception


if __name__ == "__main__":
    processGZfile("2.gz")
