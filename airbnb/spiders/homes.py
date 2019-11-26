# -*- coding: utf-8 -*-
import scrapy
import re
import json
import copy

from ..items import AirbnbItem


class HomesSpider(scrapy.Spider):
    name = 'homes'
    allowed_domains = ['douban.com',
                       'doubanio.com', 'ydstatic.com', 'boxofficemojo.com', 'cbooo.cn', 'baidu.com', 'dorama.info']
    start_urls = ['https://www.douban.com/']

    def start_requests(self):
        #req_url = 'http://www.cbooo.cn/BoxOffice/getWeekInfoData?sdate=2019-11-04'
        urls = ['http://hk.dorama.info/drama/d_box_idx.php',
                'http://dorama.info/drama/d_box_idx.php']
        #keywords = input('请输入英文名！')
        # yield scrapy.Request(req_url, meta={'site_flow': 'spider-cbooo'}, callback=self.process_cbooo)
        # yield scrapy.Request(req_url, meta={'website': 'check_url'}, callback=self.check_url)
        for req_url in urls:
            yield scrapy.Request(req_url, meta={'site_flow': 'spider-dorama'}, callback=self.process_dorama)

    def process_cbooo(self, response):
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
                yield scrapy.Request(url='https://movie.douban.com', meta={'site_flow': 'cbooo-douban_home', 'movie': copy.deepcopy(movie)}, callback=self.process_doban_home, dont_filter=True)

    def process_doban_home(self, response):
        movie = response.meta['movie']
        site_flow = response.meta['site_flow']
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
                                print(
                                    m_title + '============================================>' + m_detail_url)
                                break

        if site_flow == 'cbooo-douban_home':
            # yield scrapy.Request(url=m_detail_url, meta={'site_flow': 'douban_home-douban_detail', 'movie': copy.deepcopy(movie)}, callback=self.process_douban_detail, dont_filter=True)
            pass
        else:
            ch = re.findall(r'[\u4e00-\u9fff]+', m_title)   # 提取电影中文名
            if len(ch) > 0:
                m_title = ch[0]
                # print(ch[0])
            movie['chtitle'] = m_title
            yield scrapy.Request(url=m_detail_url, meta={'site_flow': 'douban_home-douban_detail', 'movie': copy.deepcopy(movie)}, callback=self.process_douban_detail, dont_filter=True)

        # print(m_title)
        ch = re.findall(r'[\u4e00-\u9fff]+', m_title)   # 提取电影中文名
        if len(ch) > 0:
            m_title = ch[0]
            # print(ch[0])
        movie['chtitle'] = m_title
        # print(movie)

        # self.movie_list.append(movie)
        #imdb_url = 'https://www.imdb.com'
        # yield scrapy.Request(imdb_url, meta={'website': 'imdb_home', 'movie': copy.deepcopy(movie)}, callback=self.search_imdb, dont_filter=True)

    def process_douban_detail(self, response):
        movie = response.meta['movie']

        datas = response.xpath('//div[@id="info"]//a[@rel="nofollow"]')
        if datas:
            imdb_url = datas.pop().xpath('./@href').extract_first()
            # print('============================>' +
            #      movie['chtitle'] + '找到IMDB链接！' + imdb_url)
            yield scrapy.Request(url=imdb_url, meta={'site_flow': 'douban_detail-imdb_detail', 'movie': copy.deepcopy(movie)}, callback=self.process_imdb_detail, dont_filter=True)
        else:
            print('============================>' +
                  movie['chtitle'] + '没有找到IMDB链接！')
        pass

    def process_imdb_detail(self, response):
        movie = response.meta['movie']
        m_en_title = '无英文片名'
        m_rating = '暂无评分'

        datas = response.xpath('//div[@class="title_wrapper"]')
        if datas:
            m_en_title = str(datas[0].xpath(
                '//h1/text()').extract_first()).strip()
            #m_en_title = m_en_title[:-6]
            movie['title'] = m_en_title
            #print('============================>【' + movie['chtitle'] + '】的英文片名是' + movie['title'])
        else:
            #print('============================>【' + movie['chtitle'] + '】没有英文片名')
            pass

        datas = response.xpath('//span[@itemprop="ratingValue"]')
        if datas:
            m_rating = str(datas[0].xpath('./text()').extract_first())
            movie['rating'] = m_rating
        print('============================>【' +
              movie['chtitle'] + '】的英文片名是：【' + movie['title'] + '】 IMDB评分是：' + movie['rating'])

    def check_url(self, response):
        from_link = response.url
        print('=======================>网页地址：' + from_link)

    def process_dorama(self, response):
        #datas = response.xpath('//td[@class="th_g"]/text()').extract_first()
        datas = response.xpath(
            '//table[@class="table_g" and @width="99%"]/tbody/tr')  # tr集合
        if datas:
            print('========================================================>有数据！')
            #print(len(datas))
            i = 0
            for row_data in datas:
                #print('开始执行循环')
                j = 0 # 标记有数据的行
                if i > 0:  # 第一行是表头，跳过
                    movie = AirbnbItem()
                    #print('======================================>第' + str(i) + '行')
                    cell_datas = row_data.xpath('./td')
                    
                    if len(cell_datas)>7:
                        if cell_datas[0] and str(cell_datas[0].xpath('./font/text()').extract_first()) != 'None' and str(cell_datas[0].xpath('./font/text()').extract_first()) != '*':
                            chtitle = str(cell_datas[9].xpath('./table/tbody/tr/td/a')[0].xpath('string(.)').extract_first())
                            end_index = chtitle.find('\n')
                            if end_index != -1:
                                print('找到换行符')
                                chtitle = chtitle[0:end_index].strip()
                            else:
                                print('找不到换行符')
                                chtitle.strip()
                            #chtitle = links[0].xpath('./text()').extract_first()
                            print('排行' + str(cell_datas[0].xpath('./font/text()').extract_first()) + '-----')
                            print(cell_datas[6].xpath('./text()').extract_first())
                            print(chtitle)

                            rank = int(cell_datas[0].xpath('./font/text()').extract_first())
                            if rank == 10:
                                break                       
                i += 1
                


        else:
            print('========================================================>无数据！')

    def parse(self, response):
        pass
