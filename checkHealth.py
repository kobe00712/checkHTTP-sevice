#!/usr/bin/python
 #coding:utf-8
import MySQLdb
import socket
import time
import urlparse
import sys
import re
import os

from StringIO import StringIO
 

# config mysql 
mysql_host = "123.126.53.109"
mysql_port = 3306
mysql_db = "sax"
mysql_usr = "root"
mysql_passwd = "123456"
#
fails_allow = 0.6
try_counts = 10

socket.setdefaulttimeout(0.01)

def checkConnection(url):
    if not url.startswith('http'):
        url = "http://" +url
    url_args = urlparse.urlparse(url)
    host = url_args[1] 
    path = url_args[2]    
  
    host = host.split(":")
    if len(host) == 1:
        host.append(80)
    else:
        host[1] = int(host[1]) 

    host = tuple(host)
    print 'test %s' %(host[1])
    request = "POST %s HTTP/1.1\r\nHost:%s\r\n\r\n" %(path, host[1])
    result =0
    connected =False
    res = ""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect(host)
        print 'conect is ok'
        s.send(request)
        rsp = s.recv(100)
        connected = True     
    except socket.error,e:
       print e
    finally:
        s.close()
    if connected :
        print rsp
        line = StringIO(rsp).readline()
        print 'line :' +  line

        try:
            (http_version,status,messages) = re.split(r'\s+',line,2)
        except ValueError:
            print "fail to revc"
            return 0

        print "http code is %s" %(status)
  
        if not status in ['502','504']:
            result =1 
    return result

def getDspUrlList():
    urlList = {}
    sql = 'select id, bidurl from dsp where status =1'
    db = MySQLdb.connect(host=mysql_host, user=mysql_usr, passwd=mysql_passwd ,db=mysql_db  , port=mysql_port)
    cursor = db.cursor()
    cursor.execute(sql)
    res = cursor.fetchall()
    for row in res:
        urlList[row[0]] = row[1]
        #print str(row[0]) + ':'+  row[1]
    return urlList  
#def 

def checkResult(check_res):
    for k in check_res:
        if check_res[k]/try_counts < (1 - fails_allow):
            alarm_msg = "dsp id:" + str(k) + " was down " 
               
            cmd =  ''.join([ 'python /usr/local/openresty/nginx/src/script/alarm/send_alert.py', 
                     ' --sv  门户广告',
                     ' --object ALARM',
                     ' --service SAX',
                     ' --subject ',
                     alarm_msg,
                     ' --content  ', 
                     alarm_msg ,   
                     ' --gmailto  sax_alarm ',
                     ' --gmsgto  sax_alarm '])
            print(cmd) 
            os.system(cmd)
                    
def main():
    check_res = {}
    urls = getDspUrlList()

    while True:
        for i in range(1, try_counts):
            for id  in urls:
                res = checkConnection(urls[id])
                if check_res.has_key(id):
                    check_res[id] = check_res[id]+1
                else:
                    check_res[id] = res
        checkResult(check_res)        
        time.sleep(10)               
        
             
main()
#getDspUrlList()


