# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
from scrapy.http import HtmlResponse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import time


class AirbnbSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class AirbnbDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    def __init__(self):
        
        self.timeout = 5
        
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # 使用无头谷歌浏览器模式
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        # 使用无头模式浏览器，必须指定user-agent，否则会被识别为bot
        chrome_options.add_argument('user-agent=[Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36]')
        prefs = {
            'profile.default_content_setting_values': {
                'images': 2
            }
        }
        chrome_options.add_experimental_option('prefs', prefs)

        self.browser = webdriver.Chrome(executable_path=r'D:/GreenProgram/webdriver/chromedriver.exe', chrome_options=chrome_options)
        self.wait = WebDriverWait(self.browser, self.timeout)

    def __del__(self):
        self.browser.close()    # 关闭浏览器
        pass

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called

        self.browser.get(request.url)
        time.sleep(1)
        html = self.browser.page_source
        # request.meta['key'] 与 request.meta.get('key') 等同
        if request.meta['site_flow'] == 'cbooo-douban_home' or request.meta['site_flow'] == 'dorama-douban_home':
            print('===============================================>processing cbooo,dorama-->douban_home')
            movie = request.meta['movie']
            if self.check_element(By.XPATH, '//*[@id="inp-query"]', 'located'):
                input = self.browser.find_element_by_xpath('//*[@id="inp-query"]')
                #input = self.wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="inp-query"]')))
                input.click()
                input.clear()
                input.send_keys(movie['chtitle'])
            if self.check_element(By.XPATH, '//*[@type="submit"]', 'clickable'):
            #if self.browser.find_elements_by_xpath('//*[@type="submit"]'):
                print('---------------------------------------》找到搜索按钮！')
                #submit = self.wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@type="submit"]')))
                submit = self.browser.find_element_by_xpath('//*[@type="submit"]')
                submit.click()
                time.sleep(1)
            html = self.browser.page_source
        elif request.meta['site_flow'] == 'douban_home-douban_detail':
            #html = self.browser.page_source
            pass
        elif request.meta['site_flow'] == 'douban_detail-imdb_detail':
            pass
        elif request.meta['site_flow'] == 'spider-dorama':
            print('===============================================>processing spider-dorama')
            #time.sleep(3)
            if self.check_element(By.XPATH,'//table[@class="table_g"]//td[@width="120"]/a', 'located'):
                link = self.browser.find_element_by_xpath('//table[@class="table_g"]//td[@width="120"]/a')
                link.click()
                time.sleep(3)
                html = self.browser.page_source
                print('===============================================>跳转到相应链接！')
            else:
                print('===============================================>找不到链接！')
        else:
            print('搜索未知')
        
        #html = self.browser.page_source
        return HtmlResponse(url=request.url, body=html, encoding='utf-8', request=request)
    
    def check_element(self, by_method, element_key, element_type):
        '''
        检查是否存在某个元素
        '''
        flag = True
        try:
            if element_type == 'located':
                self.wait.until(EC.presence_of_element_located((by_method, element_key)))
            else:
                self.wait.until(EC.element_to_be_clickable((by_method, element_key)))
            return flag
        except:
            flag = False
            return flag

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)
