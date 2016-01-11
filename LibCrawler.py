#!/usr/bin/env python
# -*- coding: utf-8 -*-


from PIL import Image
import pytesseract
from StringIO import StringIO
import json

from config import Config
from NUPTCrawlerBase import NUPTCrawlerBase
from lib.http import req
from lib.PageParser import LibParser


class LibCrawler(NUPTCrawlerBase):

    def __init__(self, debug=False):
        super(LibCrawler, self).__init__(debug=debug)
        self.debug = debug
        self.URLS = Config.LIB_URLS
        self.cookies = None

    def _get_captcha(self, crack=True):
        resp = req(self.URLS['CAPTCHA'], 'get')
        self.cookies = resp.cookies
        i = Image.open(StringIO(resp.content))
        if self.debug:
            i.save('lib_captcha.png')
        if crack:
            guess = pytesseract.image_to_string(i)
            # i.close()
            return guess
        else:
            return resp.content

    def _login(self, login_data=None):
        login_data = {
            'number': login_data['student_id'],
            'passwd': login_data['password'],
            'captcha': self._get_captcha(),
            'select': 'cert_no',
            'returnUrl': ''
        }
        resp = req(self.URLS['LOGIN'], 'post', data=login_data, cookies=self.cookies)
        if resp.url == self.URLS['LOGIN_SUCCESS']:
            return Config.SERVER_MSG['LOGIN_SUCCESS']
        elif self.URLS['WRONG_PASS_FINGER'].encode('utf8') in resp.content:
            return Config.SERVER_MSG['WRONG_PASSWORD']
        elif self.URLS['WRONG_CAPTCHA_FINGER'] in resp.content:
            # 验证码错误，重试
            return Config.SERVER_MSG['WRONG_CAPTCHA']
        else:
            return Config.SERVER_MSG['SERVER_ERROR']

    def login(self, login_data=None):
        return self._login(login_data=login_data)

    def _get_info(self):
        resp = req(self.URLS['INFO'], 'get', cookies=self.cookies)
        if resp is None:
            return "[]"
        content = resp.content
        res = LibParser.parse_lib_info(content)
        return json.dumps(res, ensure_ascii=False)

    def _get_current_list(self):
        resp = req(self.URLS['CURRENT'], 'get', cookies=self.cookies)
        if resp is None:
            return "[]"
        content = resp.content
        res = LibParser.parse_lib_curlst(content)
        return json.dumps(res, ensure_ascii=False)

    def _get_history(self):
        data = {
            'para_string': 'all',
            'topage': 1
        }
        resp = req(self.URLS['HISTORY'], 'post', data=data, cookies=self.cookies)
        if resp is None:
            return "[]"
        content = resp.content
        res = LibParser.parse_lib_common(content, tr_start=1, td_start=1)
        return json.dumps(res, ensure_ascii=False)

    def _get_recommend(self):
        resp = req(self.URLS['RECOMMEND'], 'get', cookies=self.cookies)
        if resp is None:
            return "[]"
        content = resp.content
        res = LibParser.parse_lib_common(content, tr_start=1)
        return json.dumps(res, ensure_ascii=False)

    def _get_reserve(self):
        resp = req(self.URLS['RESERVE'], 'get', cookies=self.cookies)
        if resp is None:
            return "[]"
        content = resp.content
        res = LibParser.parse_lib_common(content, tr_start=1)
        return json.dumps(res, ensure_ascii=False)

    def _get_book_shelf(self):
        resp = req(self.URLS['BOOKSHELF'], 'get', cookies=self.cookies)
        if resp is None:
            return "[]"
        content = resp.content
        res = LibParser.parse_lib_shelf(content)
        return json.dumps(res, ensure_ascii=False)

    def _get_payment(self):
        resp = req(self.URLS['FINE'], 'get', cookies=self.cookies)
        if resp is None:
            return "[]"
        content = resp.content
        res = LibParser.parse_lib_common(content, tr_start=1, tr_end=-1)
        return json.dumps(res, ensure_ascii=False)

    def _get_payment_detail(self):
        resp = req(self.URLS['FINE_DETAIL'], 'get', cookies=self.cookies)
        if resp is None:
            return "[]"
        content = resp.content
        res = LibParser.parse_lib_common(content, tr_start=1, tr_end=-1)
        return json.dumps(res, ensure_ascii=False)

    def _get_comment(self):
        resp = req(self.URLS['COMMENT'], 'get', cookies=self.cookies)
        if resp is None:
            return "[]"
        content = resp.content
        res = LibParser.parse_lib_comment(content)
        return json.dumps(res, ensure_ascii=False)

    def _get_search(self):
        resp = req(self.URLS['SEARCH'], 'get', cookies=self.cookies)
        if resp is None:
            return "[]"
        content = resp.content
        res = LibParser.parse_lib_search(content)
        return json.dumps(res, ensure_ascii=False)

    def get_data(self):
        pass

if __name__ == '__main__':
    lc = LibCrawler(debug=True)
    login_data = {
        'student_id': Config.TEST_STUDENT_ID,
        'password': Config.TEST_EHOME_PASSWORD
    }
    print lc.login(login_data)
    print lc._get_payment_detail()