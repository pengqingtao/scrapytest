# -*- coding: utf-8 -*-
import scrapy
import re


class HomesSpider(scrapy.Spider):
    name = 'homes'
    allowed_domains = ['douban.com',
                       'doubanio.com', 'ydstatic.com', 'boxofficemojo.com', 'cbooo.cn']
    start_urls = ['https://www.douban.com/']

    def start_requests(self):
        req_url = 'https://movie.douban.com'
        keywords = input('请输入英文名！')
        yield scrapy.Request(req_url, meta={'douban_search_keys': keywords, 'website': 'douban'}, callback=self.parse)

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
                if i>0:
                    mrank = str(row.xpath('./td[1]/text()').extract_first())
                    mtitle = str(row.xpath('./td[3]/a/text()').extract_first())
                    print(mrank + ': ' + mtitle)
                i += 1
                if i>29:
                    break
