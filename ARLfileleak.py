# -*- coding: UTF-8 -*-
# coding:utf-8
from bottle import template
import json,re,os,time
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

arl_url = "https://xx.xx.xx.xx:5003/"   # ARL地址
username = "admin"                      # 用户名
password = "passwword"                   # 密码



def generate(targetName_fnl,url_count,url,title,status_code,content_length):
    # 定义想要生成的Html的基本格式
    # 使用%来插入python代码


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
        %
        <h3 align="center">{{targetName_fnl}}<h3>
            <tr>
                <td width="20%">targetName</td>
                <td width="50%">url</td>
                <td width="20%">title</td>
                <td width="5%">status_code</td>
                <td width="5%">content_length</td>
            </tr>

            <tr>	
                <td rowspan="{{url_count}}">{{targetName_fnl}}</td>
            % for i in range(url_count):
                <td><a href="{{url[i]}}" target="_blank">{{url[i]}}</a></td>
                <td>{{title[i]}}</td>
                <td>{{status_code[i]}}</td>
                <td>{{content_length[i]}}</td>
            </tr>
            <tr>
            %end


        </table>
    </body>
    </html>
    """

    html = template(template_demo, url_count=url_count, targetName_fnl=targetName_fnl, url=url, title=title,
                    status_code=status_code, content_length=content_length)
    now = time.strftime("%Y-%m-%d-%H_%M", time.localtime(time.time()))
    filename = "./" + now + ".html"

    with open(filename, 'a', encoding="UTF-8") as f:
        f.write(str(html))
        # print(type(html), html)
        f.close()

def parse():

    os.popen("copy 1.json 2.json")
    with open('1.json', 'r', encoding='UTF-8') as f:
        data2 = f.read()
    json_num = data2.count('status_code')  # json的总数量
    # print(json_num)
    f.close()




    with open('1.json', 'r', encoding='UTF-8') as f:
        data = json.load(f)
    # 生成缓存文件循环
    for i in range(json_num): # 循环json


        # 获取site值，对应url
        site = data['items'][i]['site'] # json的site值
        targetName = re.findall(r'\w+\.edu\.cn|\w+\.cn|\w+\.com|\w+\.net',site) # 匹配域名

        targetName = targetName[0]
        # if True:
            # print(data['items'][i]['_id'])

        with open("./url/%s.txt" %targetName, 'a', encoding="UTF-8") as f2: # 以域名为文本名
            f2.writelines(data['items'][i]['url']+'\n') # 将json url的值写入
            f2.close()


        # 获取title值
        title = data['items'][i]['title']  # json的title值
        if len(title) != 0:
            title = title[0]
        else:
            title = 'null'
        # print(title)  # 打印title

        with open("./title/%s.txt" % targetName, 'a', encoding="UTF-8") as f2:  # 以域名为文本名
            f2.writelines(data['items'][i]['title'] + '\n')  # 将title json的值写入
            f2.close()

        # 获取content_length值
        content_length = data['items'][i]['content_length']  # json的content_length值
        # content_length = content_length[0]
        # print(content_length)  # 打印content_length

        with open("./content_length/%s.txt" % targetName, 'a', encoding="UTF-8") as f2:  # 以域名为文本名
            f2.writelines(str(data['items'][i]['content_length']) + '\n')  # 将content_length json的值写入
            f2.close()


        # 获取status_code值
        status_code = data['items'][i]['status_code']  # json的status_code值
        # status_code = status_code[0]
        # print(status_code)  # 打印status_code

        with open("./status_code/%s.txt" % targetName, 'a', encoding="UTF-8") as f2:  # 以域名为文本名
            f2.writelines(str(data['items'][i]['status_code']) + '\n')  # 将title status_code的值写入
            f2.close()


    # 遍历文件夹下的文件
    print('generate html_file...')
    for files in os.listdir("./url"):  # 不仅仅是文件，当前目录下的文件夹也会被认为遍历到
        # print("files", files)

        url_count=sum(1 for _ in open('./url/%s' % files))  # 统计该文件下的行数
        # targetName=targetName #targetName
        url = open('./url/%s' % files,'r',encoding='UTF-8').readlines()  # 逐行读取url
        title = open('./title/%s' % files,'r',encoding='UTF-8').readlines()  # 逐行读取title
        status_code = open('./status_code/%s' % files,'r',encoding='UTF-8').readlines()  # 逐行读取status_code
        content_length = open('./content_length/%s' %files,'r',encoding='UTF-8').readlines()  # 逐行读取content_length

        targetName_fnl = files.replace('.txt','')
        generate(targetName_fnl,url_count,url,title,status_code,content_length)
    print('generate html_file successfully!')



def getjson(arl_url,username,password):

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
    data = req.json()   # 将返回结果json格式化
    data = json.dumps(data)  # 将json数据输出
    # print(data)

    with open("1.json",'a',encoding="UTF-8") as f:
        f.write(str(data))
        f.close()

    print('parse json file..')
    parse()


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
    getjson(arl_url,username,password)

    # Delete cache file
    print('Delete cache file....')
    for files in os.listdir("./url"):  # 不仅仅是文件，当前目录下的文件夹也会被认为遍历到
        os.remove('./url/'+files)
    for files in os.listdir("./title"):  # 不仅仅是文件，当前目录下的文件夹也会被认为遍历到
        os.remove('./title/'+files)
    for files in os.listdir("./status_code"):  # 不仅仅是文件，当前目录下的文件夹也会被认为遍历到
        os.remove('./status_code/'+files)
    for files in os.listdir("./content_length"):  # 不仅仅是文件，当前目录下的文件夹也会被认为遍历到
        os.remove('./content_length/'+files)
    os.remove('1.json')
    os.remove('2.json')
    print('Delete successfully!')


if __name__ == '__main__':
    main()