# -*- coding: UTF-8 -*-
# coding:utf-8
import json, re, time
import requests, sqlite3
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

arl_url = "https://175.178.48.156:5003/"  # ARL地址
username = "admin"  # 用户名
password = "c3ef-enk"  # 密码


def generate():
    conn = sqlite3.connect('./db/arl.db')
    c = conn.cursor()

    # 先去重把targetName查询出来
    c.execute("SELECT DISTINCT targetName FROM A")
    cursor1 = c.fetchall()

    # 生成html文件中的表格部分html代码
    part2 = ''
    for row1 in cursor1:
        targetName = row1[0]

        # 去重targetName循环出来
        select_url = "SELECT DISTINCT url,title,status_code,content_length FROM A WHERE targetName='%s'" % targetName
        c.execute(select_url)  # 去重计算当前targetName的url总数
        cursor2 = c.fetchall()
        url_num = str(len(cursor2))

        part1 = ''
        for row2 in cursor2:
            part1 = part1 + str(
                "<td><a href='" + str(row2[0]) + "' target='_blank'>" + str(row2[0]) + "</a></td><td>" + str(
                    row2[1]) + "</td><td>" + str(row2[2]) + "</td><td>" + str(row2[3]) + "</td></tr><tr>")

        part2 = part2 + "<table width='90%' class='table'><h3 align='center'>" + str(row1[
                                                                                         0]) + "<h3><tr><td width='20%'>targetName</td><td width='50%'>url</td><td width='20%'>title</td><td width='5%'>status_code</td><td width='5%'>content_length</td></tr><tr><td rowspan='" + url_num + "'>" + \
                row1[0] + "</td>" + part1 + "<table width='90%' class='table'>"

    conn.commit()
    conn.close()

    template_demo = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>ARL_fileleak_spider</title>
        <style type="text/css">
        table
        {
            border-collapse: collapse;
            margin: 0 auto;
            text-align: center;
        }
        table td, table th
        {
            border: 1px solid #cad9ea;
            color: #666;
            height: 30px;
        }
        table thead th
        {
            background-color: #CCE8EB;
            width: 100px;
        }
        table tr:nth-child(odd)
        {
            background: #fff;
        }
        table tr:nth-child(even)
        {
            background: #F5FAFA;
        }
    </style>
    </head>
    <body>
        <table width="90%" class="table">

        """ + part2 + """


        </table>
    </body>
    </html>
    """

    html = template_demo
    now = time.strftime("%Y-%m-%d-%H_%M", time.localtime(time.time()))
    filename = "./" + now + ".html"

    with open(filename, 'a', encoding="UTF-8") as f:
        f.write(str(html))
        # print(type(html), html)
        f.close()


def getjson(arl_url, username, password):
    print('Requesting...')
    data = {"username": username, "password": password}
    headers = {'Content-Type': 'application/json; charset=UTF-8'}
    get_size = 999999999  # 一次性获取json数据的数量，一般不用修改，数据太多可以改大

    # 请求Token
    logreq = requests.post(url=arl_url + "/api/user/login", data=json.dumps(data), headers=headers, timeout=30,
                           verify=False)
    result = json.loads(logreq.content.decode())
    if result['code'] == 401:
        print('login fail...')
        exit()
    if result['code'] == 200:
        print('login success...\n')
        Token = result['data']['token']

    headers2 = {'Token': Token, 'Content-Type': 'application/json; charset=UTF-8'}
    print('request fileleak json...')

    # 请求文件泄露json
    req = requests.get(url=arl_url + '/api/fileleak/?page=1&size=' + str(get_size), headers=headers2, timeout=30,
                       verify=False)  # 请求文件泄露json数据
    data = req.json()  # 将返回结果json格式化
    data1 = json.dumps(data)  # 将json数据输出
    # print(type(data),data)

    print('parse json...')

    json_num = data1.count('status_code')

    # 写入数据库
    conn = sqlite3.connect('./db/arl.db')
    c = conn.cursor()

    for i in range(json_num):
        targetName = data['items'][i]['site']

        targetName = re.findall(r'\w+\.edu\.cn|\w+\.cn|\w+\.com|\w+\.net', targetName)  # 只取主域名
        targetName = ''.join(targetName)  # 并将数组形式转换为字符串形式

        url = data['items'][i]['url']
        title = data['items'][i]['title']
        status_code = data['items'][i]['status_code']
        content_length = data['items'][i]['content_length']

        # 插入数据库
        c.execute("INSERT INTO A (targetName,url,title,status_code,content_length) \
                  VALUES (?,?,?,?,?)", (targetName, url, title, status_code, content_length))

    conn.commit()
    conn.close()

    print('generate html_file...')

    # 生成html文件输出
    generate()

    # 删除数据库
    print('generate html_file successfully!...')
    conn = sqlite3.connect('./db/arl.db')
    c = conn.cursor()
    c.execute("DELETE FROM A")
    conn.commit()
    conn.close()


def main():
    print('''
      ____  ____   _      _____  ____  _        ___  _        ___   ____  __  _ 
 /    ||    \ | |    |     ||    || |      /  _]| |      /  _] /    ||  |/ ]
|  o  ||  D  )| |    |   __| |  | | |     /  [_ | |     /  [_ |  o  ||  ' / 
|     ||    / | |___ |  |_   |  | | |___ |    _]| |___ |    _]|     ||    \ 
|  _  ||    \ |     ||   _]  |  | |     ||   [_ |     ||   [_ |  _  ||     \
|  |  ||  .  \|     ||  |    |  | |     ||     ||     ||     ||  |  ||  .  |
|__|__||__|\_||_____||__|   |____||_____||_____||_____||_____||__|__||__|\_|

    ''')
    getjson(arl_url, username, password)


if __name__ == '__main__':
    main()