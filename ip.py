#!/usr/bin/python3
# -*- coding: utf8 -*-


"""
 * ipsearch
 * @Author Suroy
 * Created by preference on 2022/09/17
"""

import re, time, requests
from urllib.parse import urlparse 
from faker import Faker
from bs4 import BeautifulSoup
from socket import gethostbyname
from IPy import IP



def get_domain_root(url, dotBack=False):
    """
    取根域名 ｜ [模式2]复用为检测当前url是否是域名
    :param url: 待检测待URL 或 网站地址[模式2]
    :param dotBack: True时启用模式2
    :return:
    """
    """取根域名"""

    topRootDomain = (
    '.com', '.la', '.cn', '.io', '.co', '.info', '.net', '.org', '.me', '.mobi',
    '.us', '.biz', '.xxx', '.ca', '.co.jp', '.com.cn', '.net.cn',
    '.org.cn', '.mx', '.tv', '.ws', '.ag', '.com.ag', '.net.ag',
    '.org.ag', '.am', '.asia', '.at', '.be', '.com.br', '.net.br',
    '.bz', '.com.bz', '.net.bz', '.cc', '.com.co', '.net.co',
    '.nom.co', '.de', '.es', '.com.es', '.nom.es', '.org.es',
    '.eu', '.fm', '.fr', '.gs', '.in', '.co.in', '.firm.in', '.gen.in',
    '.ind.in', '.net.in', '.org.in', '.it', '.jobs', '.jp', '.ms',
    '.com.mx', '.nl', '.nu', '.co.nz', '.net.nz', '.org.nz',
    '.se', '.tc', '.tk', '.tw', '.com.tw', '.idv.tw', '.org.tw',
    '.hk', '.co.uk', '.me.uk', '.org.uk', '.vg', ".com.hk")

    # 检测是否包含后缀名列表 | 返回判断是否为域名
    if dotBack:
        for v in topRootDomain:
            if v in url: return True
        return False

    domain_root = ""
    try:
        # 若不是 http或https开头，则补上方便正则匹配规则
        if len(url.split("://")) <= 1 and url[0:4] != "http" and url[0:5] != "https":
            url = "http://" + url

        reg = r'[^\.]+(' + '|'.join([h.replace('.', r'\.')
                                     for h in topRootDomain]) + ')$'
        pattern = re.compile(reg, re.IGNORECASE)

        host = urlparse(url).netloc
        m = pattern.search(host)
        res = m.group() if m else host
        domain_root = "" if not res else res
    except Exception as ex:
        print("error_msg: " + str(ex))
    return domain_root



def getByIps(url, page, directWrite=False):
    """从网页中获取IP地址"""
    try:
        header = {
            "user-agent": Faker().user_agent()
        }
        s = requests.get(url, headers=header)
        if s.status_code != 200: return False
        str = s.text
        ips = re.findall(r'(?<![\.\d])(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?)(?![\.\d])',str)

        # 直接写入
        if directWrite:
            with open("result-ip.txt","a+",encoding="utf-8") as f:
                f.write("\n".join(ips))
            print("[IP]写入完成")
        return ips

    except:
        print(("[IP]抓取异常 {", page, "}"))



def ipCrawl(id, pages=1):
    """
    IP获取工具
    :param id: 资源ID号
    :param pages: 页码，仅部分有用
    :return:
    """
    errorPage = []  # 错误页码
    mip = []  # ip
    pages = pages if pages > 1 else 2
    for i in range(1, pages):
        try:
            src = sources(id, i)
            content = getByIps(src["url"], src["fix"])
            if content:
                mip.extend(content)
                print("抓取成功: {", i, "/", len(mip), "}")
                # print(content)

            else:
                print("抓取异常: {", i, "}")
                errorPage.append(i)
        except:
            print("程序异常：延时5秒继续")
            time.sleep(5)

        time.sleep(5)  # 冷静

    # 异常重试
    if len(errorPage) > 0:
        print("[异常重试]")
        err_mip = getByIps(id, errorPage)
        mip.extend(err_mip)

    # 整理数据
    these = []
    [these.append(u) for u in mip if u not in these]  # 去重

    # 写入文件
    with open("result-ip.txt", mode="a+") as f:
        for str in these:
            if str: f.writelines(str + "\n")

    print(these, "[IP] 获取完成")


def getContent(url, fixStr=None):
    """
    获取内容
    :param url:
    :param fixStr:
    :return:
    """
    header = {
        "user-agent": Faker().user_agent()
    }
    s = requests.get(url, headers=header)
    if s.status_code != 200: return False
    soup = BeautifulSoup(s.text, 'lxml')
    # print(soup.find_all('a'))

    urls = [autoFixUrlPre(a['href'], True, fixStr) for a in soup.find_all('a')]
    # 整理数据
    these = []
    [these.append(u) for u in urls if u not in these] # 去重
    return these


def autoFixUrlPre(str, onlySaveDomain=False, fixStr=None):
    """自动修正内容"""
    # 资源定义修正内容
    if type(fixStr) is list:
        for v in fixStr:
            fill = '' if len(v) == 1 else v[1]
            str = str.replace(v[0], fill)

    if(onlySaveDomain): str = get_domain_root(str) # 仅仅保存主域名


    # 白名单
    white = ['aizhan.com', 'so.com', '163.com', 'bing.com', 'aizhan.cn', 'dnsdaquan.com', 'ipjisuanqi.com', 'chaziyu.com', 'icplishi.com', "ipchaxun.com", 'zhaokuaizhao.com', "rdnsdb.com", 'cha001.com', 'ipshuidi.com', 'rdnsdb.com', 'api.cn', 'chajiechi.com', 'fangfanche.com', 'chapangzhan.com', 'chayoulian.com', 'baoantang.com', 'baidu.com', 'youku.com', 'sohu.com', 'bilibili.com', 'ip138.com', '1688.com', 'zhihu.com', 'kugou.com', 'sina.com.cn', 'jd.com', 'qq.com', 'sogou.com', 'jianshu.com', 'lianjia.com', 'renrendoc.com', 'taobao.com', 'doc88.com', 'people.com.cn', 'fang.com', 'pp.cn', '51aijia.cn', 'autoimg.cn', 'pconline.com.cn', 'weibo.com', 'qcc.com', 'gov.cn']
    # 修正
    if "javascript" in str or str in white or not get_domain_root(str, True):
        return ''

    remove = ['#', '"']
    for i in remove:
        str = str.replace(i, '')
    return str


def sources(id, page=1):
    """
    配置资源 | 开发者自行添加模版
    :note {"ip", 获取IP模式，auto即可IP也可以域名；} {"fix", "修正模版内容"}
    :param id:
    :param page:
    :return:
    """
    page = str(page)
    src = [
        {
            "id": 3,
            "url": "https://suroy.cn/",
            "fix": [
                ("suroy.cn",)
            ],
            "ip": "true"
        }, {
            "id": 4,
            "url": "https://suroy.cn/",
            "fix": [
                ("baidu.com",),
                ("suroy.cn",)
            ],
            "ip": "auto"
        }
    ]
    return src[id] if int(id) <= src.__len__()-1 else False


def domainWorker(id, pageList):
    """
    域名获取工具异常重试程序
    :param id: 资源ID
    :param pageList: 需要异常重试页码列表
    :return:
    """
    errorPage = []  # 错误页码
    domains = []  # 域名
    status = True
    for i in pageList:
        try:
            src = sources(id, i)
            content = getContent(src["url"], src["fix"])
            if content:
                domains.extend(content)
                print("抓取成功: {", i, "}")
                # pageList.pop()
            else:
                print("抓取异常: {", i, "}")
                errorPage.append(i)
        except:
            print("程序异常：延时5秒继续")
            time.sleep(5)
        time.sleep(5)  # 冷静
    return domains


def domainCrawl(id, pages):
    """
    域名获取工具
    :param id: 资源ID
    :param pages: 页码
    :return:
    """
    errorPage = [] # 错误页码
    domains = [] # 域名
    pages = pages if pages > 1 else 2
    for i in range(1, pages):
        try:
            src = sources(id, i)
            content = getContent(src["url"], src["fix"])
            if content:
                domains.extend(content)
                print("抓取成功: {", i, "/", len(domains), "}")
                # print(content)
            else:
                print("抓取异常: {", i, "}")
                errorPage.append(i)
        except:
            print("程序异常：延时5秒继续")
            time.sleep(5)

        time.sleep(5) # 冷静

    # 异常重试
    if len(errorPage) > 0:
        print("[异常重试]")
        err_domains = domainWorker(id, errorPage)
        domains.extend(err_domains)

    # 整理数据
    these = []
    [these.append(u) for u in domains if u not in these] # 去重

    # 写入文件
    with open("domains.txt",mode="a+") as f:
        for str in these:
            if str: f.writelines(str+"\n")

    print(these)


def ipActByDomain(fileName = None, setOnly=True):
    """
    域名反查IP
    :param fileName:
    :return:
    """

    fileName = fileName if fileName else "./domains.txt"

    # 文件去重复
    if setOnly:
        remove_duplicates(fileName)
        fileName = fileName.replace(".txt","")+"-only.txt"

    with open(fileName,'r') as f:
         for line in f.readlines():
            try:
                host = gethostbyname(line.strip('\n'))  #域名反解析得到的IP
            except Exception as e:
                with open('error.txt','a+') as ERR:  #error.txt为没有IP绑定的域名
                    ERR.write(line.strip()+ '\n')
            else:
                with open('result.txt','a+') as r: #  ****.txt 里面存储的是批量解析后的结果
                    r.write(line.strip('\n') + ' ')   #显示有ip绑定的域名，用空格隔开
                    print(line, host)
                    r.write(host + '\n')
                    if host != "suroy.cn":   #筛选特定结果，具体代码实现如下
                        if "127.0.0" not in host and "192.168." not in host:
                            with open('result-select.txt', 'a+') as f:
                                f.write(line.strip() +'  ') #存储筛选后的域名
                                f.write(host + '\n') #存储筛选后的IP

                            with open('result-select-host.txt', 'a+') as fh:
                                fh.write(host + '\n')  # 只存储筛选后的IP
                        else:
                            pass
                    else:
                        pass


def remove_duplicates(fileName):
    """文件去重复"""
    f_read=open(fileName,'r',encoding='utf-8')     #将需要去除重复值的txt文本重命名text.txt
    f_write=open(fileName.replace(".txt","")+"-only.txt",'w',encoding='utf-8')  #去除重复值之后，生成新的txt文本 --“去除重复值后的文本.txt”
    data=set()
    for a in [a.strip('\n') for a in list(f_read)]:
        if a not in data:
            f_write.write(a+'\n')
            data.add(a)
    f_read.close()
    f_write.close()
    # remove_duplicates(fileName)
    print('[去重] 完成')


def createIPS(fileName, input_Netmask="255.255.255.0"):
    """生成IP段：BUG"""
    fileNameIPS = fileName.replace(".txt","")+"-ips.txt"
    with open(fileName, "r", encoding="utf-8") as f:
        with open(fileNameIPS, "a+", encoding="utf-8") as fn:
            for input_IP in f.readlines():
                ip = IP(input_IP).make_net(input_Netmask)
                fn.writelines(ip+"\n")
                print(ip)
    print("IP段创建成功")


def createIPSHuman(fileName, mask=24):
    """
    直接生成IP段｜C段/24
    :param fileName: 文件名
    :param mask: 子网掩码 32
    :return:
    """
    fileNameIPS = fileName.replace(".txt","")+"-ips.txt"
    with open(fileName, "r", encoding="utf-8") as f:
        with open(fileNameIPS, "a+", encoding="utf-8") as fn:
            for input_IP in f.readlines():
                input_IP = input_IP.replace("\n", "/"+str(mask)+"\n")
                fn.writelines(input_IP)
                print(input_IP)
    print("IP段创建成功")


if __name__ == "__main__":
    print("Hi, Suroy!")
    # 取域名模式
    print("...[Domain]...")
    domainCrawl(0,10)
    domainCrawl(1,10)
    domainCrawl(2,1)
    ipActByDomain() # 域名转IP
    remove_duplicates("result-select-host.txt") # 去重复

    # IP模式
    print("...[Ip]...")
    ipCrawl(3, 1)
    ipCrawl(4, 1)
    ipCrawl(5, 1)
    ipCrawl(6, 3)
    remove_duplicates("result-ip.txt") # 去重复


    # 创建IP段
    print("...[Ips]...")
    createIPSHuman("result-ip.txt", 22) #of iptool
    createIPSHuman("result-select-host-only.txt", 22) # ofdomains
    # createIPS("result-select-host.txt")
