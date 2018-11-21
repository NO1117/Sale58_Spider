#!/usr/bin/env/ python 
# -*- coding:utf-8 -*-
# Author:Mr.Xu

import requests
import time
import re
import random
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from Sale.db import MongoDB
from multiprocessing import Process
from Sale.config import *

class Sale_58():
    def __init__(self):

        self.temp_api = "http://app.zhuanzhuan.com/zz/transfer/getgoodsdetaildata?infoId={}"
        self.main_url = "http://bj.58.com/sale.shtml"
        self.ua = UserAgent()
        self.headers = {
            "User-Agent": self.ua.random,
            "Connection": "close",
        }
        self.proxy = None
        self.parse_times = 0
        self.wait_time = random.randint(2, 5)
        self.DB = MongoDB()

    def get_proxy(self):
        proxy_html = requests.get('http://{0}:{1}/random'.format(API_HOST, API_PORT))
        proxy = BeautifulSoup(proxy_html.text, "lxml").get_text()
        print("proxy: ", proxy)
        proxies = {'http': proxy}
        return proxies

    # 请求相应URL,并返回HTML文档
    def parse_url(self, url):
        response = requests.get(url,headers=self.headers,proxies=self.proxy)
        # 请求前睡眠2秒
        time.sleep(self.wait_time)
        if response.status_code != 200:
            print('parsing not success!--',url)
            # 请求不成功
            if self.parse_times < 3:
                # 重复请求三次
                self.parse_times += 1
                return self.parse_url(url)
            else:
                # 请求不成功, parse_times置为0
                self.parse_times = 0
                return None
        else:
            if self.error_404(response):
                # 请求成功
                print('parsing success!--',url)
                # 请求成功, parse_times重置为0
                return response
            else:
                print('Html is None')
                return None

    def error_404(self, html):
        soup = BeautifulSoup(html.text, 'lxml')
        error = soup.select("p.et")
        if error:
            if 'ERROR' in error[0].get_text():
                return  False
        return True

    # 解析main_url = "http://bj.58.com/sale.shtml" 获取分类URL
    def parse_index(self):
        category_urls = []
        html = self.parse_url(self.main_url)
        soup = BeautifulSoup(html.text, 'lxml')
        links = soup.select("ul.ym-submnu > li > b > a")
        for link in links:
            link_url = urljoin(self.main_url, link.attrs['href'])
            category_urls.append(link_url)
        item = dict(
            category_urls=category_urls
        )
        self.DB.insert(collection='Category_urls', items=item)

    # 解析分类链接并提取获取商品详情URL
    def parse_page_url(self):
        items = self.DB.find_data(collection='Category_urls')
        for item in items:
            cate_urls = item['category_urls']
            for cate_url in cate_urls:
                page_urls = []
                self.proxy = self.get_proxy()
                if 'tongxunyw' in cate_url:
                    print("error", cate_url)
                    pass
                elif 'ershouqiugou' in cate_url:
                    print("error", cate_url)
                    pass
                else:
                    print(cate_url)
                    for i in range(1, 100):
                        print("Parse page ", i)
                        url = cate_url + 'pn{}/'.format(i)
                        html = self.parse_url(url)
                        soup = BeautifulSoup(html.text, 'lxml')
                        trs = soup.select("tr[_pos='0']")
                        for tr in trs:
                            price = tr.select("b.pri")[0].get_text()
                            if price != '面议':
                                temp_link = tr.select("td.t > a:nth-of-type(1)")[0].attrs['href']
                                page_url = urljoin(self.main_url, temp_link)
                                page_urls.append(page_url)
                    item = dict(
                        page_urls=page_urls,
                    )
                    self.DB.insert(collection='Page_urls', items=item)

    # 根据详情URL，解析网页
    def parse_page(self):
        items = self.DB.find_data(collection='Page_urls')
        for item in items:
            self.proxy = self.get_proxy()
            for page_url in item['page_urls']:
                if 'www.zhuanzhuan.com' in page_url:
                    self.parse_page_zz(page_url)
                elif 'hhpcpost.58.com' in page_url:
                    self.parse_page_now58(page_url)
                else:
                    self.parse_page_58(page_url)

    # 解析Old58_urls网页，pp
    def parse_page_58(self, page_url):
        html = self.parse_url(page_url)
        soup = BeautifulSoup(html.text, 'lxml')
        temp_title = soup.title.get_text()
        title = temp_title.split(" - ")[0]
        try:
            temp_time = soup.select("div.detail-title__info > div")[0].get_text()
            time = temp_time.split(" ")[0]
            temp_price = soup.select("span.infocard__container__item__main__text--price")[0].get_text()
            price = temp_price.split()[0]
            temp = soup.select("div.infocard__container > div:nth-of-type(2) > div:nth-of-type(2)")[0].get_text()
            if '成新' in temp:
                color = temp
                temp_area = soup.select("div.infocard__container > div:nth-of-type(3) > div:nth-of-type(2)")[0]
            else:
                color = None
                temp_area = soup.select("div.infocard__container > div:nth-of-type(2) > div:nth-of-type(2)")[0]
            temp_area = list(temp_area.stripped_strings)
            area = list(filter(lambda x: x.replace("-", ''), temp_area))
            temp_cate = list(soup.select("div.nav")[0].stripped_strings)
            cate = list(filter(lambda x: x.replace(">", ''), temp_cate))
            item = dict(
                title=title,
                time=time,
                price=price,
                color=color,
                area=area,
                cate=cate,
                )
            print(item)
            self.DB.insert(collection='Page_data', items=item)
        except:
            print("Error 404!")

    # 解析New58_urls网页，并提取数据
    def parse_page_now58(self, page_url):
        html = self.parse_url(page_url)
        soup = BeautifulSoup(html.text, 'lxml')
        try:
            title = soup.select("div.detail-info-tit")[0].get_text()
            temp_cate = soup.select("div.nav")[0]
            temp_cate = list(temp_cate.stripped_strings)
            cate = list(filter(lambda x: x.replace(">", ''), temp_cate))
            ul = soup.select("ul.detail-info-bd")[0]
            time = ul.select("li:nth-of-type(1) > span:nth-of-type(2)")[0].get_text()
            color = ul.select("li:nth-of-type(2) > span:nth-of-type(2)")[0].get_text()
            area = ul.select("li:nth-of-type(3) > span:nth-of-type(2)")[0].get_text()
            temp_price = soup.select("span.info-price-money")[0].get_text()
            price = temp_price.split("￥")[-1]
            item = dict(
                title=title,
                time=time,
                price=price,
                color=color,
                area=area,
                cate=cate,
            )
            print(item)
            self.DB.insert(collection='Page_data', items=item)
        except:
            print("Error 404!")

    # 解析来自ZZ58_urls网页，并提取json数据
    def parse_page_zz(self, page_url):
        pattern = re.compile('infoId=(.*?)&', re.S)
        infoId = re.findall(pattern, page_url)
        html = self.parse_url(self.temp_api.format(infoId[0]))
        try:
            data_json = html.json()
            data = data_json.get('respData')
            local = data.get("location")
            item = dict(
                title=data.get('title'),
                browse_times=data.get("browseCount"),
                price=data.get("nowPrice"),
                origin_price=data.get("oriPrice"),
                area=local.get("local"),
            )
            print(item)
            self.DB.insert(collection='Page_data', items=item)
        except:
            print("Error 404!")

    # 逻辑实现
    def run(self):
        if INDEX_ENABLED:
            Index_process = Process(target=self.parse_index)
            Index_process.start()

        if LINK_ENABLED:
            PageUrl_process = Process(target=self.parse_page_url)
            PageUrl_process.start()

        if ITEM_ENABLED:
            Page_process = Process(target=self.parse_page)
            Page_process.start()

if __name__=='__main__':
    spider = Sale_58()
    spider.run()