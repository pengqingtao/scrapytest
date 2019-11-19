# -*- coding: utf-8 -*-
import scrapy
import re
import json
import copy

from ..items import AirbnbItem


class HomesSpider(scrapy.Spider):
    name = 'homes'
    allowed_domains = ['douban.com',
                       'doubanio.com', 'ydstatic.com', 'boxofficemojo.com', 'cbooo.cn', 'baidu.com']
    start_urls = ['https://www.douban.com/']

    def start_requests(self):
        req_url = 'http://www.cbooo.cn/BoxOffice/getWeekInfoData?sdate=2019-11-04'
        #keywords = input('请输入英文名！')
        yield scrapy.Request(req_url, meta={'from_site': 'origin', 'to_site': 'cbooo'}, callback=self.search_cbooo)
        # yield scrapy.Request(req_url, meta={'website': 'check_url'}, callback=self.check_url)

    def search_cbooo(self, response):
        #from_link = response.url
        #print('======================>' + from_link)
        # rs =  json.loads(response.body_as_unicode())
        strjson = response.xpath('//body/text()').extract_first()
        # print(strjson)

        rs = json.loads(strjson)
        if rs.get('data1'):
            m_list = rs.get('data1')
            for m in m_list:
                movie = AirbnbItem()
                movie['rank'] = m.get('MovieRank')
                movie['chtitle'] = m.get('MovieName')
                movie['gross'] = m.get('SumWeekAmount')
                #print(rank + '.' + title + ' ' + amount +'万')
                yield scrapy.Request(url='https://movie.douban.com', meta={'from_site': 'cbooo', 'to_site': 'douban_home', 'movie': copy.deepcopy(movie)}, callback=self.search_doban, dont_filter=True)

    def search_doban(self, response):
        movie = response.meta['movie']
        from_site = response.meta['from_site']
        to_site = response.meta['to_site']
        datas = response.xpath('//div[@class="title"]')
        m_title = ''
        m_detail_url = ''
        if datas:
            for data in datas:
                if not data.xpath('./span'):    # 类型不是电视剧
                    regex = re.compile(r'\d{4}')
                    if data.xpath('./a/text()').extract_first():
                        if re.search(regex, data.xpath('./a/text()').extract_first()):  # 必须要有年份才是电影
                            m_year = re.search(regex, data.xpath(
                                './a/text()').extract_first()).group()
                            if any([str(m_year) == '2019', str(m_year) == '2018']):   # 时间是2019
                                m_title = data.xpath(
                                    './a/text()').extract_first()
                                m_detail_url = data.xpath(
                                    './a/@href').extract_first()
                                print(m_title + '============================================>' + m_detail_url)
                                break

        if from_site == 'cbooo' and to_site == 'douban_home':
            yield scrapy.Request(url=m_detail_url, meta={'from_site': 'douban_home', 'to_site': 'douban_detail', 'movie': copy.deepcopy(movie)}, callback=self.search_douban_detail, dont_filter=True)

        # print(m_title)
        ch = re.findall(r'[\u4e00-\u9fff]+', m_title)   # 提取电影中文名
        if len(ch) > 0:
            m_title = ch[0]
            # print(ch[0])
        movie['chtitle'] = m_title
        # print(movie)

        # self.movie_list.append(movie)
        imdb_url = 'https://www.imdb.com'
        # yield scrapy.Request(imdb_url, meta={'website': 'imdb_home', 'movie': copy.deepcopy(movie)}, callback=self.search_imdb, dont_filter=True)

    def search_douban_detail(self, response):
        movie = response.meta['movie']
        from_site = response.meta['from_site']
        to_site = response.meta['to_site']

        datas = response.xpath('//div[@id="info"]//a[@rel="nofollow"]')
        if datas:
            imdb_url = datas.pop().xpath('./@href').extract_first()
            print('============================>' +
                  movie['chtitle'] + '找到IMDB链接！' + imdb_url)
        else:
            print('============================>' +
                  movie['chtitle'] + '没有找到IMDB链接！')
        pass

    def check_url(self, response):
        from_link = response.url
        print('=======================>网页地址：' + from_link)

    def parse(self, response):
        datas = response.xpath('//div[@class="title"]')
        m_title = ''
        if datas:
            for data in datas:
                if not data.xpath('./span'):    # 类型不是电视剧
                    regex = re.compile(r'\d{4}')
                    if data.xpath('./a/text()').extract_first():
                        if re.search(regex, data.xpath('./a/text()').extract_first()):  # 必须要有年份才是电影
                            m_year = re.search(regex, data.xpath(
                                './a/text()').extract_first()).group()
                            if any([str(m_year) == '2019', str(m_year) == '2018']):   # 时间是2019
                                m_title = data.xpath(
                                    './a/text()').extract_first()
                                break

        print(m_title)
        ch = re.findall(r'[\u4e00-\u9fff]+', m_title)   # 提取电影中文名
        if len(ch) > 0:
            m_title = ch[0]
            print(ch[0])

        req_url = 'https://www.boxofficemojo.com/weekly/2019W45/'
        yield scrapy.Request(req_url, meta={'ch_title': m_title, 'website': 'mojo'}, callback=self.search_mojo)

    def search_mojo(self, response):
        datas = response.xpath(
            '//table[@class="a-bordered a-horizontal-stripes a-size-base a-span12 mojo-body-table mojo-body-table-compact scrolling-data-table" and @style="table-layout: fixed;"]')
        if datas:
            rows = datas.xpath('//tr')
            i = 0
            for row in rows:
                if i > 0:
                    mrank = str(row.xpath('./td[1]/text()').extract_first())
                    mtitle = str(row.xpath('./td[3]/a/text()').extract_first())
                    print(mrank + ': ' + mtitle)
                i += 1
                if i > 29:
                    break
