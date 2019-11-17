# -*- coding: utf-8 -*-
import scrapy
import re
import json


class HomesSpider(scrapy.Spider):
    name = 'homes'
    allowed_domains = ['douban.com',
                       'doubanio.com', 'ydstatic.com', 'boxofficemojo.com', 'cbooo.cn', 'baidu.com']
    start_urls = ['https://www.douban.com/']

    def start_requests(self):
        req_url = 'http://www.cbooo.cn/BoxOffice/getWeekInfoData?sdate=2019-11-04'
        #keywords = input('请输入英文名！')
        yield scrapy.Request(req_url, meta={'website': 'cbooo'}, callback=self.search_cbooo)

    def search_cbooo(self, response):
        # rs =  json.loads(response.body_as_unicode())
        strjson = response.xpath('//body/text()').extract_first()
        print(strjson)
        
        rs =  json.loads(strjson)
        if rs.get('data1'):
            m_list = rs.get('data1')
            for m in m_list:
                rank = m.get('MovieRank')
                title = m.get('MovieName')
                amount = m.get('SumWeekAmount')
                print(rank + '.' + title + ' ' + amount +'万')
        

        '''
        datas = response.xpath('//tbody[@id="tbcontent"]/tr')
        m_title = ''
        i = 0

        
        if datas:
            for row_data in datas:
                i += 1
                if i<4:
                    continue
                cell_datas = row_data.xpath('//td[@class="one"]/a/p')
                if cell_datas:
                    m_title = cell_datas.xpath('string(.)').extract_first()
                    print(str(i) + ':' + m_title)
                else:
                    print('找不到！')
                
        else:
            print('无数据！')
        '''

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
