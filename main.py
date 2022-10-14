import sqlite3
import time
import requests
import xlsxwriter
import psycopg2
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import pickle
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import re
from requests_html import HTMLSession
from threading import Thread
import json
from html.parser import HTMLParser
import pandas


def get_html_from_selenium(url):
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        # driver = webdriver.Chrome(executable_path="C:\\Users\\jopas\\PycharmProjects\\edugram\\driver_chrome\\chromedriver.exe")
        driver.get(url=url)
        text = driver.page_source
        return text
    except Exception as e:
        print(e)
    finally:
        driver.close()
        driver.quit()


def get_urls():
    # получение названий и ссылок на вузы на вузопедии
    for page in range(1, 100):

        url = f"https://vuzopedia.ru/vuz?page={page}"
        req = requests.get(url, headers=headers)
        # with open("vuzopedia.html", "w", encoding="utf-8") as file:
        #     file.write(req.text)
        # with open("vuzopedia.html", encoding="utf-8") as file:
        #     src = file.read()

        soup = BeautifulSoup(req.text, "lxml")
        list_of_vuzs = soup.find_all("div", class_="vuzesfullnorm")
        for i in list_of_vuzs:
            list_of_names.append(i.find("div", class_="itemVuzTitle").text.strip())
            list_of_urls_vuzopedia.append("https://vuzopedia.ru" + i.find("div", class_="col-md-7").find("a").get("href"))
        if len(list_of_vuzs) == 0:
            break

    # получение ссылок на галвные страницы вузов
    count = 0
    while count < len(list_of_urls_vuzopedia):
        url = list_of_urls_vuzopedia[count] + "/proezd"
        count += 1
        try:
            req = requests.get(url, headers=headers)
            soup = BeautifulSoup(req.text, "lxml")
            tmp = soup.find_all("div", class_="col-lg-8 col-md-8 col-xs-8 col-sm-8")
            if tmp[3].text.find("http") == -1:
                res = ''
                number = tmp[3].text.find("http")
                while tmp[3].text[number].isalpha() or tmp[3].text[number] == '/' or tmp[3].text[number] == ':' or tmp[3].text[number] == '.':
                    res = res + tmp[3].text[number]
                    number += 1
                list_of_urls.append(res)
                continue
            elif tmp[3].text.find("http") != -1 and tmp[3].text[0] != 'h' and tmp[3].text[1] != 't'and tmp[3].text[2] != 't':
                list_of_urls.append('-')
                continue
        except:
            list_of_urls.append('-')
            continue
        list_of_urls.append(tmp[3].text)

    count = 0
    for i in list_of_urls:  # получение vk, yt и tg ссылок с сайтов
        count += 1
        print("Номер ссылки: " + str(count))
        try:
            time.sleep(1)
            req = requests.get(i, headers=headers)
            if req.status_code != 200:
                text = get_html_from_selenium(i)
            else:
                text = req.text
        except requests.exceptions.SSLError:
            text = get_html_from_selenium(i)
        except Exception:
            print("Упс, сслыка не работает " + "Номер в списке: " + str(count) + "  Нерабочая ссылка: " + i)
            list_of_vk.append("-")
            list_of_YT.append("-")
            list_of_tg.append("-")
            continue
        try:
            soup = BeautifulSoup(text, "lxml")
            urls = soup.find_all("a")
        except:
            list_of_vk.append("-")
            list_of_YT.append("-")
            list_of_tg.append("-")
            continue
        is_vk = 0
        is_yt = 0
        is_tg = 0
        for j in urls:
            result = j.get("href")
            try:
                if result.find("vk.com/") != -1 and is_vk == 0 and result.find("vk.com/wall") == -1:
                    if result[0] != 'h' and result[1] != 't' and result[2] != 't' and result[3] != 'p':
                        result = "https://" + result[result.find("vk.com"):]
                    list_of_vk.append(result)
                    is_vk += 1
                if result.find("youtube.com/") != -1 and is_yt == 0 and result.find(
                        "youtube.com/watch") == -1:
                    if result[0] != 'h' and result[1] != 't' and result[2] != 't' and result[3] != 'p':
                        result = "https://" + result[result.find("youtube.com"):]
                    list_of_YT.append(result)
                    is_yt += 1
                if result.find("t.me/") != -1 and is_tg == 0:
                    if result.find("http") == -1:
                        result = "https://" + result[result.find("t.me"):]
                    list_of_tg.append(result)
                    is_tg += 1
            except:
                continue
            if is_vk == 1 and is_yt == 1 and is_tg == 1:
                break
        if is_vk == 0:
            list_of_vk.append("-")
        if is_yt == 0:
            list_of_YT.append("-")
        if is_tg == 0:
            list_of_tg.append("-")


    # парс vk
def parce_vk():
    for i in list_of_vk:
        time.sleep(2)
        if i == '-':
            list_of_vk_subs.append('-')
            list_of_vk_videos.append('-')
            continue
        try:
            req = requests.get(i, headers=headers)
            soup = BeautifulSoup(req.text, "lxml")
            all_header_label_fl_l = soup.find_all(class_="header_label fl_l")
            all_header_count = soup.find_all(class_="header_count fl_l")
            subs = soup.find("span", class_="group_friends_count")
            if subs is not None:
                list_of_vk_subs.append(subs.text)
            else:
                list_of_vk_subs.append(all_header_count[0].text.replace(" ", ""))
            number_videos = ''
        except:
            list_of_vk_subs.append("-")
            list_of_vk_videos.append("-")
            continue
        flag = 0
        for i in all_header_label_fl_l:
            if i.text.find("Видео") != -1:
                index = all_header_label_fl_l.index(i)
                list_of_vk_videos.append(all_header_count[index].text)
                flag = 1
                break
        if flag == 0:
            list_of_vk_videos.append("-")


# парс YT
def parce_YT():
    count = 1
    for i in list_of_YT:
        if i == "-":
            list_of_YT_subs.append("-")
            count += 1
            continue
        subs = get_YT_info(i, 1)
        if subs != 'hide' and subs != '?':
            subs = subs.replace(u'\xa0', ' ')
            if subs.find("тыс.") != -1:
                subs = subs[:subs.find(" ")] + "K"
            else:
                subs = subs[:subs.find(" ")]
        count += 1
        list_of_YT_subs.append(subs)
        print(f"Добалвено №{count}: {subs}")
        # try:
        #     req = requests.get(i, headers=headers)
        #     tmpslovo = req.text.find("подписч")
        #     tmpkov = req.text.find("{", tmpslovo - 30)
        # except ValueError:
        #     list_of_YT_subs.append("-")
        #     continue
        # if tmpslovo == -1:
        #     list_of_YT_subs.append("hide")
        #     continue
        # subs = ''
        # flag = 0
        # while True:
        #     if req.text[tmpkov] == ',':
        #         subs = subs + ','
        #         flag = 1
        #     if req.text[tmpkov] == ' ' and flag == 0:
        #         break
        #     elif req.text[tmpkov] == ' ' and flag == 1:
        #         subs = subs + 'K'
        #         flag = 0
        #         break
        #     try:
        #         tmp = int(req.text[tmpkov])
        #         subs = subs + req.text[tmpkov]
        #     except ValueError:
        #         pass
        #     tmpkov += 1
        # if subs.replace("K", "").replace(",", "").isdigit():
        #     list_of_YT_subs.append(subs)
        # else:
        #     list_of_YT_subs.append("-")

    #парс колличесва прсомотреов
    for i in list_of_YT:
        if i == '-':
            list_of_YT_views.append("-")
            continue
        url = i
        if url[len(url) - 1] == '/':
            url = url[:len(url) - 1]
        if url.find("?") != -1:
            url = url[:url.find("?")]
        tag = url[url.rfind("/") + 1:]
        if tag == 'videos' or tag == 'featured' or tag == 'about' or tag == 'feed':
            url = url[:url.rfind("/")]
        url = url + '/about'
        view = get_YT_info(url, 0)
        if view != '?':
            view = view.replace(u'\xa0', ' ')
            view = view[:view.rfind(" ")]
            view = view.replace(" ", "")
            list_of_YT_views.append(view)
        else:
            list_of_YT_views.append("?")
        # url = i
        # try:
        #     if url[len(url) - 1] == '/':
        #         url = url[:len(url) - 1]
        #     if url.find("?") != -1:
        #         url = url[:url.find("?")]
        #     tag = url[url.rfind("/") + 1:]
        #     if tag == 'videos' or tag == 'featured':
        #         url = url[:url.rfind("/")]
        #     url = url + '/about'
        #     req = requests.get(url, headers=headers)
        # except ValueError:
        #     list_of_YT_subs.append("-")
        #     continue
        # s = req.text
        # pattern = 'просмот'
        # flag = 0
        # for m in re.finditer(pattern, s):
        #     if s[m.start() - 2].isdigit():
        #         num_start = s.find(":", m.start() - 15)
        #         res = s[num_start + 2:m.start() - 1]
        #         res = res.replace(" ", "")
        #         res = res.replace(" ", "")
        #         list_of_YT_views.append(res)
        #         flag = 1
        #         break
        # if flag == 0:
        #     list_of_YT_views.append("-")


#парс подписчиков tg
def parce_tg():
    for j in list_of_tg:
        try:
            req = requests.get(j, headers=headers)
            soup = BeautifulSoup(req.text, "lxml")
            res = soup.find("div", class_="tgme_page_extra").text
            res = res.replace(" ", '')
            subs = ''
            for i in res:
                if i.isdigit():
                    subs = subs + i
            list_of_tg_subs.append(subs)
        except Exception:
            list_of_tg_subs.append("-")
            continue


# записить в таблицу exel
def write_exel():
    workbook = xlsxwriter.Workbook('data_csv.xlsx')
    worksheet = workbook.add_worksheet('Лист1')
    worksheet.set_column(0, 0, 100)
    worksheet.set_column(1, 1, 25)
    worksheet.set_column(2, 2, 17)
    worksheet.set_column(3, 3, 17)
    worksheet.set_column(4, 4, 30)
    worksheet.set_column(5, 5, 12)
    worksheet.set_column(6, 6, 10)
    worksheet.set_column(7, 7, 68)
    worksheet.set_column(8, 8, 12)
    worksheet.set_column(9, 9, 10)
    worksheet.set_column(10, 10, 26)
    worksheet.set_column(11, 11, 12)
    worksheet.write(f'A1', "Название")
    worksheet.write(f'B1', "Ссылка на вуз")
    worksheet.write(f'C1', "Кол-во просмотров")
    worksheet.write(f'D1', "Кол-во посетителей")
    worksheet.write(f'E1', "VK")
    worksheet.write(f'F1', "VK Subscribers")
    worksheet.write(f'G1', "VK Videos")
    worksheet.write(f'H1', "YT")
    worksheet.write(f'I1', "YT Subscribers")
    worksheet.write(f'J1', "YT Views")
    worksheet.write(f'K1', "Tg")
    worksheet.write(f'L1', "Tg Subscribers")
    count = 2
    for i, k, tv, tgu, v, y, vks, vkv, yts, ytv, tg, tgs in zip(list_of_names, list_of_urls, list_of_ftafic_views, list_of_ftafic_guests, list_of_vk, list_of_YT, list_of_vk_subs, list_of_vk_videos, list_of_YT_subs, list_of_YT_views, list_of_tg, list_of_tg_subs):
        if tv == '-' or tv == 'hide':
            tv = 0
        if tgu == '-' or tgu == 'hide':
            tgu = 0
        if vks == '-' or vks == 'hide':
            vks = 0
        if vkv == '-' or vks == 'hide':
            vkv = 0
        if yts == '-' or yts == 'hide':
            yts = 0
        if tgs == '-' or tgs == 'hide':
            tgs = 0
        if ytv == '-' or ytv == 'hide':
            ytv = 0
        worksheet.write(f'A{count}', i)
        worksheet.write(f'B{count}', k)
        worksheet.write(f'C{count}', int(tv))
        worksheet.write(f'D{count}', int(tgu))
        worksheet.write(f'E{count}', v)
        worksheet.write(f'F{count}', int(vks))
        worksheet.write(f'G{count}', int(vkv))
        worksheet.write(f'H{count}', y)
        worksheet.write(f'I{count}', yts)
        worksheet.write(f'J{count}', int(ytv))
        worksheet.write(f'K{count}', tg)
        worksheet.write(f'L{count}', int(tgs))
        count += 1
    workbook.close()


def get_YT_info(url, mode):
    session = HTMLSession()
    response = session.get(url)
    # response.html.render(timeout=60)
    try:
        soup = BeautifulSoup(response.html.html, "html.parser")
        data = re.search(r"var ytInitialData = ({.*?});", soup.prettify()).group(1)
        data_json = json.loads(data)
    except:
        return "?"
    try:
        if mode == 1:
            subs = data_json['header']['c4TabbedHeaderRenderer']['subscriberCountText'].get('simpleText')
        else:
            if len(data_json['contents']['twoColumnBrowseResultsRenderer']['tabs']) == 7:
                view = data_json['contents']['twoColumnBrowseResultsRenderer']['tabs'][5]['tabRenderer']['content']['sectionListRenderer']['contents'][0]['itemSectionRenderer']['contents'][0]['channelAboutFullMetadataRenderer']['viewCountText'].get('simpleText')
            elif len(data_json['contents']['twoColumnBrowseResultsRenderer']['tabs']) == 6:
                view = data_json['contents']['twoColumnBrowseResultsRenderer']['tabs'][4]['tabRenderer']['content'][
                    'sectionListRenderer']['contents'][0]['itemSectionRenderer']['contents'][0][
                    'channelAboutFullMetadataRenderer']['viewCountText'].get('simpleText')
        if mode == 1:
            return subs
        else:
            return view
    except Exception:
        if mode == 1:
            return "hide"
        else:
            return "?"


def get_trafic():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    count = 1
    driver.get(url="https://pr-cy.ru/")
    driver.delete_all_cookies()
    for cookie in pickle.load(open("cookies", 'rb')):
        driver.add_cookie(cookie)
    driver.refresh()
    for i in list_of_urls:
        try:
            driver.get(url="https://pr-cy.ru/")
            input_tag = driver.find_element(by=By.ID, value="url")
            input_tag.send_keys(i)
            input_tag.send_keys(Keys.ENTER)
            time.sleep(1)
            text = driver.page_source
            soup = BeautifulSoup(text, "lxml")
            t = soup.find_all("div", class_="prcy-0 e1a2a9ru2")
            if len(t) > 0:
                str1 = t[0].text[t[0].text.find("≈")+2:t[0].text.rfind(" ")-2].replace(u'\xa0', '')
                str2 = t[1].text[t[1].text.find("≈")+2:t[1].text.rfind(" ")-2].replace(u'\xa0', '')
                list_of_ftafic_views.append(str(max(int(str1), int(str2))))
                list_of_ftafic_guests.append(str(min(int(str1), int(str2))))
            else:
                list_of_ftafic_views.append("-")
                list_of_ftafic_guests.append("-")
        except Exception as e:
            list_of_ftafic_views.append("-")
            list_of_ftafic_guests.append("-")
            print(e)
        print(f"№{count}")
        count += 1
    driver.close()
    driver.quit()


def create_db():
    con = psycopg2.connect(
        database="DB",
        user="postgres",
        password="1111",
        host="127.0.0.1",
        port="5432"
    )
    cur = con.cursor()
    create_table_query = '''CREATE TABLE persons
                          (ID INT PRIMARY KEY     NOT NULL,
                          NAME TEXT,
                          WIKI TEXT,
                          VK TEXT,
                          VK_SUBS INT); '''
    cur.execute(create_table_query)
    con.commit()
    cur.execute('''CREATE TABLE communication
                          (ID INT PRIMARY KEY NOT NULL,
                          UNIVERSITY_ID INT,
                          PERSON_ID INT); ''')
    con.commit()


def write_db():
    con = psycopg2.connect(
        database="DB",
        user="postgres",
        password="1111",
        host="127.0.0.1",
        port="5432"
    )
    cur = con.cursor()
    count = 1
    for i, k, tv, tgu, v, y, vks, vkv, yts, ytv, tg, tgs in zip(list_of_names, list_of_urls, list_of_ftafic_views, list_of_ftafic_guests, list_of_vk, list_of_YT, list_of_vk_subs, list_of_vk_videos, list_of_YT_subs, list_of_YT_views, list_of_tg, list_of_tg_subs):
        insert_query = """ INSERT INTO parce_data 
                            (NAME, URL, VIEWS, guests, VK, VK_SUBS, VK_VIDEOS, YT, YT_SUBS, YT_VIEWS, TG, TG_SUBS) 
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"""
        if tv == '-' or tv == 'hide':
            tv = -1
        if tgu == '-' or tgu == 'hide':
            tgu = -1
        if vks == '-' or vks == 'hide':
            vks = -1
        if vkv == '-' or vks == 'hide':
            vkv = -1
        if yts == '-' or yts == 'hide':
            yts = -1
        if tgs == '-' or tgs == 'hide':
            tgs = -1
        if ytv == '-' or ytv == 'hide':
            ytv = -1
        item_tuple = (i, k, int(tv), int(tgu), v, int(vks), int(vkv), y, yts, int(ytv), tg, int(tgs))
        cur.execute(insert_query, item_tuple)
        con.commit()
        count += 1


def write_db1():
    sqlite_connection = sqlite3.connect('C://edugram//edugram//db.sqlite3')
    cursor = sqlite_connection.cursor()
    for i, k, tv, tgu, v, y, vks, vkv, yts, ytv, tg, tgs in zip(list_of_names, list_of_urls, list_of_ftafic_views, list_of_ftafic_guests, list_of_vk, list_of_YT, list_of_vk_subs, list_of_vk_videos, list_of_YT_subs, list_of_YT_views, list_of_tg, list_of_tg_subs):
        insert_with_param = """INSERT INTO step1_vuz
                                      (title, url, count_views, count_guests, VK, VK_Subs, VK_Video, YT, YT_Subs, YT_Views, TG, TG_Subs)
                                      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"""
        if tv == '-' or tv == 'hide':
            tv = None
        else:
            tv = int(tv)
        if tgu == '-' or tgu == 'hide':
            tgu = None
        else:
            tgu = int(tgu)
        if vks == '-' or vks == 'hide':
            vks = None
        else:
            vks = int(vks)
        if vkv == '-' or vks == 'hide':
            vkv = None
        else:
            vkv = int(vkv)
        if yts == '-' or yts == 'hide':
            yts = None
        if tgs == '-' or tgs == 'hide':
            tgs = None
        else:
            tgs = int(tgs)
        if ytv == '-' or ytv == 'hide':
            ytv = None
        else:
            ytv = int(ytv)
        data_tuple = (i, k, tv, tgu, v, vks, vkv, y, yts, ytv, tg, tgs)
        cursor.execute(insert_with_param, data_tuple)
        sqlite_connection.commit()
    cursor.close()


if __name__ == '__main__':

    ua = UserAgent()
    headers = {
        'user-agent': f'{ua.chrome}'
    }
    list_of_names = []
    list_of_urls_vuzopedia = []
    list_of_urls = []
    list_of_vk = []
    list_of_YT = []
    list_of_tg = []
    list_of_vk_subs = []
    list_of_vk_videos = []
    list_of_YT_subs = []
    list_of_YT_views = []
    list_of_tg_subs = []
    list_of_ftafic_guests = []
    list_of_ftafic_views = []

    th1 = Thread(target=parce_vk)
    th1.start()
    th2 = Thread(target=parce_YT())
    th2.start()
    th3 = Thread(target=parce_tg())
    th3.start()
    th1.join()
    th2.join()
    th3.join()
    write_exel()