#encoding=utf-8
import urllib.parse

def get_url_host(url):
    if not url:
        return ''
    proto,ful_url = urllib.parse.splittype(url)
    host,path = urllib.parse.splithost(ful_url)
    return host
    
def get_url_http(url):
    host = get_url_host(url)
    if not host:
        return ''
    http_list = url.split("//")
    http = http_list[0]+"//"+host
    return http