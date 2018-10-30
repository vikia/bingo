#coding=utf-8

import os
import time
import copy
import json
import logging
import traceback
import cv2 as cv
import numpy as np
import logging
import datetime
import tempfile

import requests
requests.packages.urllib3.disable_warnings()

from grabcut import TimeTracer

class Filter(object):

    __errno_cut_succ = 0

    __errno_conn_timeout = 100
    __errno_read_timeout = 101

    def __init__(self):
        self.__connectTimeout = 600
        self.__socketTimeout = 600
        self.__client = requests

    @TimeTracer
    def _read_remote_img(self, url, data=None):
        img = None
        try:
            resp = self.__client.get(url, timeout=(self.__connectTimeout, self.__socketTimeout))
            img = np.asarray(bytearray(resp.content), dtype="uint8")
            img = cv.imdecode(img, cv.IMREAD_COLOR)
            logging.info('read img remote succ!')
        except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectTimeout) as e:
            logging.warn('conn or read data timeout!')
        except Exception as e:
            logging.fatal('unhandled exception : %s', e)

        return img

    @TimeTracer
    def _filter(self, img):
        if img is None:
            logging.warn('img none!')

        rgb_img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
        print rgb_img.shape

        for i in range(rgb_img.shape[1]):
            if i % 100 == 0:
                print "now processed %d xs" % i

            for j in range(rgb_img.shape[0]):
                r, g, b = rgb_img[j][i]
                new_r = 0.393 * r + 0.769 * g + 0.189 * b
                new_g = 0.349 * r + 0.686 * g + 0.168 * b
                new_b = 0.272 * r + 0.534 * g + 0.131 * b
                new_rgb = [new_r, new_g, new_b]
                for k in range(len(new_rgb)):
                    if new_rgb[k] < 0:
                        new_rgb[k] = 0
                    elif new_rgb[k] > 255:
                        new_rgb[k] = 255

                rgb_img[j][i] = np.array(new_rgb)

                # hsv_map[key] = hsv_map.setdefault(key, 0) + 1

        return rgb_img

    def _filter3(self, img):
        print "in _filter2"
        if img is None:
            logging.warn('img none!')
            print('img none!')

        rgb_img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
        print rgb_img.shape

        for i in range(rgb_img.shape[1]):
            if i % 100 == 0:
                print "now processed %d xs" % i

            for j in range(rgb_img.shape[0]):
                r, g, b = rgb_img[j][i]
                new_r = int(r) * 255.0 / (int(g) + int(b) + 1.0)
                new_g = int(g) * 255.0 / (int(b) + int(r) + 1.0)
                new_b = int(b) * 255.0 / (int(g) + int(r) + 1.0)
                new_rgb = [new_r, new_g, new_b]
                for k in range(len(new_rgb)):
                    if new_rgb[k] < 0:
                        new_rgb[k] = 0
                    elif new_rgb[k] > 255:
                        new_rgb[k] = 255

                rgb_img[j][i] = np.array(new_rgb, dtype='uint8')

                # hsv_map[key] = hsv_map.setdefault(key, 0) + 1

        return rgb_img

    def _filter2(self, img):
        if img is None:
            logging.warn('img none!')

        rgb_img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
        print rgb_img.shape

        for i in range(rgb_img.shape[1]):
            if i % 100 == 0:
                print "now processed %d xs" % i

            for j in range(rgb_img.shape[0]):
                r, g, b = rgb_img[j][i]
                new_r = int(r) - int(g) - int(b) * 3.0 / 2
                new_g = int(g) - int(b) - int(r) * 3.0 / 2
                new_b = int(b) - int(g) - int(r) * 3.0 / 2
                new_rgb = [new_r, new_g, new_b]
                for k in range(len(new_rgb)):
                    if new_rgb[k] < 0:
                        new_rgb[k] = -new_rgb[k]
                    elif new_rgb[k] > 255:
                        new_rgb[k] = 255

                rgb_img[j][i] = np.array(new_rgb, dtype='uint8')

                # hsv_map[key] = hsv_map.setdefault(key, 0) + 1

        return rgb_img

    def process(self, url, stra=1):
        img = self._read_remote_img(url)
        res_img = None
        if stra == 1:
            res_img = self._filter(img)
        elif stra == 2:
            res_img = self._filter2(img)
        elif stra == 3:
            res_img = self._filter3(img)

        # cv.imshow('filter', res_img)
        # cv.waitKey(0)
        # cv.destroyAllWindows()
        # return
        print "WFJ here"

        # 临时文件,讲ndarray转成字节流
        tmp = tempfile.NamedTemporaryFile(suffix='.jpeg')
        cv.imwrite(tmp.name, res_img)

        return tmp.read()

if __name__ == "__main__":
    logging.basicConfig(level = logging.DEBUG, \
                    format = '%(asctime)s - %(levelname)s - %(message)s', \
                    datefmt = '%Y/%m/%d %H:%M:%S')

    flt = Filter() 
    flt.process("https://ss2.bdstatic.com/70cFvnSh_Q1YnxGkpoWK1HF6hhy/it/u=1161149267,3646555459&fm=26&gp=0.jpg")
