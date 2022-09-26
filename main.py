import random
from time import localtime
from requests import get, post
from datetime import datetime, date
from zhdate import ZhDate                                                    #农历和公立转化用的
import sys
import os
 
 
def get_color():
    # 获取随机颜色
    get_colors = lambda n: list(map(lambda i: "#" + "%06x" % random.randint(0, 0xFFFFFF), range(n)))
    color_list = get_colors(100)
    return random.choice(color_list)
 
 
def get_access_token():
    # appId
    app_id = config["app_id"]
    # appSecret
    app_secret = config["app_secret"]
    post_url = ("https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={}&secret={}"
                .format(app_id, app_secret))
    try:
        access_token = get(post_url).json()['access_token']
    except KeyError:
        print("获取access_token失败，请检查app_id和app_secret是否正确")
        os.system("pause")
        sys.exit(1)
    # print(access_token)
    return access_token
 
 
def get_weather(region):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
    }
    key = config["weather_key"]
    region_url = "https://geoapi.qweather.com/v2/city/lookup?location={}&key={}".format(region, key)
    response = get(region_url, headers=headers).json()
    if response["code"] == "404":
        print("推送消息失败，请检查地区名是否有误！")
        os.system("pause")
        sys.exit(1)
    elif response["code"] == "401":
        print("推送消息失败，请检查和风天气key是否正确！")
        os.system("pause")
        sys.exit(1)
    else:
        # 获取地区的location--id
        location_id = response["location"][0]["id"]
    weather_url = "https://devapi.qweather.com/v7/weather/now?location={}&key={}".format(location_id, key)
    response = get(weather_url, headers=headers).json()
    # 天气
    weather = response["now"]["text"]
    # 当前温度
    temp = response["now"]["temp"] + u"\N{DEGREE SIGN}" + "C"
    # 风向
    wind_dir = response["now"]["windDir"]
    #体感温度
    feelsLike=response["now"]["feelsLike"] + u"\N{DEGREE SIGN}" + "C"
    #风速
    windScale=response["now"]["windScale"]
    humidity=response["now"]["humidity"]

    #获取穿衣指数等信息
    dressing_url="https://devapi.qweather.com/v7/indices/1d?type=3,5,13&location={}&key={}".format(location_id, key)
    response = get(dressing_url, headers=headers).json()
    #穿衣指数
    dressing_index=response["daily"][0]["name"]+" : "+response["daily"][0]["category"]+" : "+response["daily"][0]["text"]
    #紫外线指数
    UV_index=response["daily"][1]["name"]+" : "+response["daily"][1]["category"]+" : "+response["daily"][1]["text"]
    #化妆指数
    makeup_index = response["daily"][2]["name"]+" : "+response["daily"][2]["category"] + " : " + response["daily"][2]["text"]

    #获取最低气温和最高气温
    temp_url="https://devapi.qweather.com/v7/weather/3d?location={}&key={}".format(location_id, key)
    response = get(temp_url, headers=headers).json()
    temp_max=response['daily'][0]['tempMax']+ u"\N{DEGREE SIGN}" + "C"
    temp_min=response['daily'][0]['tempMin']+ u"\N{DEGREE SIGN}" + "C"

    return weather, temp, wind_dir,feelsLike,windScale,humidity,dressing_index,UV_index,makeup_index,temp_max,temp_min
 

def get_birthday(birthday, year, today):
    birthday_year = birthday.split("-")[0]
    # 判断是否为农历生日
    if birthday_year[0] == "r":
        r_mouth = int(birthday.split("-")[1])
        r_day = int(birthday.split("-")[2])
        # 获取农历生日的今年对应的月和日
        try:
            birthday = ZhDate(year, r_mouth, r_day).to_datetime().date()
        except TypeError:
            print("请检查生日的日子是否在今年存在")
            os.system("pause")
            sys.exit(1)
        birthday_month = birthday.month
        birthday_day = birthday.day
        # 今年生日
        year_date = date(year, birthday_month, birthday_day)
 
    else:
        # 获取国历生日的今年对应月和日
        birthday_month = int(birthday.split("-")[1])
        birthday_day = int(birthday.split("-")[2])
        # 今年生日
        year_date = date(year, birthday_month, birthday_day)
    # 计算生日年份，如果还没过，按当年减，如果过了需要+1
    if today > year_date:
        if birthday_year[0] == "r":
            # 获取农历明年生日的月和日
            r_last_birthday = ZhDate((year + 1), r_mouth, r_day).to_datetime().date()
            birth_date = date((year + 1), r_last_birthday.month, r_last_birthday.day)
        else:
            birth_date = date((year + 1), birthday_month, birthday_day)
        birth_day = str(birth_date.__sub__(today)).split(" ")[0]
    elif today == year_date:
        birth_day = 0
    else:
        birth_date = year_date
        birth_day = str(birth_date.__sub__(today)).split(" ")[0]
    return birth_day
 
 
def get_ciba():
    url = "http://open.iciba.com/dsapi/"
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
    }
    r = get(url, headers=headers)
    note_en = r.json()["content"]
    note_ch = r.json()["note"]
    return note_ch
 
 
def send_message(to_user, access_token, region_name, weather, temp, wind_dir, note_ch, note_en,WeChat_ID):
    url = "https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={}".format(access_token)
    week_list = ["星期日", "星期一", "星期二", "星期三", "星期四", "星期五", "星期六"]
    year = localtime().tm_year
    month = localtime().tm_mon
    day = localtime().tm_mday
    today = datetime.date(datetime(year=year, month=month, day=day))
    week = week_list[today.isoweekday() % 7]
    # 获取在一起的日子的日期格式
    love_year = int(config["love_date"].split("-")[0])
    love_month = int(config["love_date"].split("-")[1])
    love_day = int(config["love_date"].split("-")[2])
    love_date = date(love_year, love_month, love_day)
    # 获取在一起的日期差
    love_days = str(today.__sub__(love_date)).split(" ")[0]
    #计算今年恋爱纪念日
    love_year_date = date(year, love_month, love_day) #今年的纪念日
    if today > love_year_date:
        love_date1 = date((year + 1), love_month, love_day)
        love_day2 = str(love_date1.__sub__(today)).split(" ")[0]
        love_data="今天距离恋爱纪念日还有{}天".format(love_day2)
        love_year_num=year-love_year
        love_days_num=str(today.__sub__(love_year_date)).split(" ")[0]
        love_year_days_data="我们在一起{}年零{}天啦".format(love_year_num,love_days_num)
    elif today == love_year_date:
        love_y=year-love_year                          #几周年
        love_data="宝贝，我们在一起{}周年了，爱你！！！".format(love_y)
        love_year_days_data="宝贝，我们在一起{}周年了，爱你！！！".format(love_y)
    else:
        love_day2 = str(love_year_date.__sub__(today)).split(" ")[0]
        love_data = "今天距离恋爱纪念日还有{}天".format(love_day2)
        love_year_num = year - love_year-1
        #去年的纪念日
        love_last_year_date=date(year-1, love_month, love_day)
        love_days_num = str(today.__sub__(love_last_year_date)).split(" ")[0]
        love_year_days_data = "我们在一起{}年零{}天啦".format(love_year_num, love_days_num)


    #距离毕业的天数
    graduate_days=str(date(2025,6,1).__sub__(today)).split(" ")[0]

    # 获取所有生日数据
    birthdays = {}
    for k, v in config.items():
        if k[0:5] == "birth":
            birthdays[k] = v
    data = {
        "touser": to_user,
        "template_id": WeChat_ID,
        "url": "http://weixin.qq.com/download",
        "topcolor": "#FF0000",
        "data": {
            "date": {
                "value": "{} {}".format(today, week),
                "color": get_color()
            },
            "region": {
                "value": region_name,
                "color": get_color()
            },
            "weather": {
                "value": weather,
                "color": get_color()
            },
            "temp": {
                "value": temp,
                "color": get_color()
            },
            "wind_dir": {
                "value": wind_dir,
                "color": get_color()
            },
            "love_day": {
                "value": love_days,
                "color": get_color()
            },
            "note_en": {
                "value": note_en,
                "color": get_color()
            },
            "graduate_days":{
                "value": graduate_days,
                "color": get_color()
            },
            "note_ch": {
                "value": note_ch,
                "color": get_color()
            },
            "love_data": {
                "value": love_data,
                "color": get_color()
            },
            "love_year_days_data": {
                "value": love_year_days_data,
                "color": get_color()
            },
            "feelsLike": {
                "value": feelsLike,
                "color": get_color()
            },
            "windScale": {
                "value": windScale,
                "color": get_color()
            },
            "humidity": {
                "value": humidity,
                "color": get_color()
            },
            "temp_max": {
                "value": temp_max,
                "color": get_color()
            },
            "temp_min": {
                "value": temp_min,
                "color": get_color()
            }
        }
    }

    # 获取课程表信息并传送给DATA
    # 当学期第一周周一的日期
    first_day_team_year = int(config["first_day_team"].split("-")[0])
    first_day_team_month = int(config["first_day_team"].split("-")[1])
    first_day_team_day = int(config["first_day_team"].split("-")[2])
    first_day_team_date = date(first_day_team_year, first_day_team_month, first_day_team_day)
    # 计算今天是上课的总天数第几周,星期几：
    studay_days = int(str(today.__sub__(first_day_team_date)).split(" ")[0]) + 1
    dijizhou_of_today = studay_days // 7 + 1
    xingqiji_of_today = studay_days % 7
    # 从配置文件中读取当学期的上课总数
    class_num = config["class_num"]
    # 状态标志位，若有课则置为1，无课置为0
    state = 0
    # 课程数据缓冲区
    class_buff=["","","","","",""]
    # 循环读入当天课程数据，
    for i in range(class_num):
        a = "class" + str(i + 1)
        class_x = config[a]
        xingqi = class_x["xingqi"]
        start_week = class_x["start_week"]
        over_week = class_x["over_week"]
        if ((dijizhou_of_today >= start_week) & (dijizhou_of_today <= over_week)):
            if (xingqi == xingqiji_of_today):
                state+=1
                class_buff[state]=class_x["name"]
    if (state == 0):
        class_buff[0]="你今天没有课哎"
    else:
        class_buff[0]="你今天有{}节课".format(state)
    #将数据写入DATA
    for i in range(6):
        a = "class" + str(i)
        data["data"][a] = {"value": class_buff[i], "color": get_color()}
    #将穿衣指数等信息写入data
    data["data"]["dressing_index"] = {"value": dressing_index, "color": get_color()}
    data["data"]["UV_index"] = {"value": UV_index, "color": get_color()}
    data["data"]["makeup_index"] = {"value": makeup_index, "color": get_color()}



    for key, value in birthdays.items():
        # 获取距离下次生日的时间
        birth_day = get_birthday(value["birthday"], year, today)
        if birth_day == 0:
            birthday_data = "今天{}生日哦，祝{}生日快乐！".format(value["name"], value["name"])
        else:
            birthday_data = "距离{}的生日还有{}天".format(value["name"], birth_day)
        # 将生日数据插入data
        data["data"][key] = {"value": birthday_data, "color": get_color()}
    #print(data)
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
    }
    response = post(url, headers=headers, json=data).json()
    if response["errcode"] == 40037:
        print("推送消息失败，请检查模板id是否正确")
    elif response["errcode"] == 40036:
        print("推送消息失败，请检查模板id是否为空")
    elif response["errcode"] == 40003:
        print("推送消息失败，请检查微信号是否正确")
    elif response["errcode"] == 0:
        print("推送消息成功")
    else:
        print(response)
 
 
if __name__ == "__main__":
    try:
        with open("config.txt", encoding="utf-8") as f:            config = eval(f.read())
    except FileNotFoundError:
        print("推送消息失败，请检查config.txt文件是否与程序位于同一路径")
        os.system("pause")
        sys.exit(1)
    except SyntaxError:
        print("推送消息失败，请检查配置文件格式是否正确")
        os.system("pause")
        sys.exit(1)
 
    # 获取accessToken
    accessToken = get_access_token()
    # 接收的用户
    users = config["user"]
    # 传入地区获取天气信息
    region = config["region"]
    weather, temp, wind_dir,feelsLike,windScale,humidity,dressing_index,UV_index,makeup_index,temp_max,temp_min= get_weather(region)
    note_ch = config["note_ch"]
    note_en = config["note_en"]
    if note_ch == "" :
        # 获取词霸每日金句
        note_ch = get_ciba()
    # 公众号推送消息
    for user in users:
        WeChat_ID=config["template_id1"]
        send_message(user, accessToken, region, weather, temp, wind_dir, note_ch, note_en,WeChat_ID)
        WeChat_ID = config["template_id2"]
        send_message(user, accessToken, region, weather, temp, wind_dir, note_ch, note_en, WeChat_ID)
    os.system("pause")
