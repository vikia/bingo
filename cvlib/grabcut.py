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

def TimeTracer(func):
    """
        简单的计时器，记录处理时间
    """
    def timer(self, *args, **kwargs):
        """
            简单的计时器实现
        """
        def _wrapper():
            beg = datetime.datetime.now().microsecond
            result = func(self, *args, **kwargs)
            end = datetime.datetime.now().microsecond
            logging.debug("func[%s] cost %s ms", func.__name__, (end - beg)/1000)
            return result
        return _wrapper()
    return timer

class GrabCutter(object):

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

    def _cut(self, img):
        if img is None:
            logging.warn('img none!')

        hsv_img = cv.cvtColor(img, cv.COLOR_BGR2HSV)
        print hsv_img.shape

        hsv_map = {}
        for i in range(hsv_img.shape[1]):
            for j in range(hsv_img.shape[0]):
                h, s, v = hsv_img[j][i]
                key = "%d_%d_%d" % (h, s, v)
                if key == "0_0_255":
                    hsv_img[j][i] = np.array([82, 128, 128])

                # hsv_map[key] = hsv_map.setdefault(key, 0) + 1

                # 临时文件
        tmp = tempfile.NamedTemporaryFile(suffix='.jpeg')
        cv.imwrite(tmp.name, hsv_img)

        return tmp.read()

        # for k, v in hsv_map.iteritems():
            # print k, v

        """
        lower_white = np.array([0, 0, 245])
        upper_white = np.array([2, 2, 255])
        mask = cv.inRange(hsv_img, lower_white, upper_white)

        cv.imshow('Mask', mask)
        k = cv.waitKey(0)
        if k == 27:
            cv.destroyAllWindows()

        #腐蚀膨胀
        erode=cv.erode(mask,None,iterations=1)
        dilate=cv.dilate(erode,None,iterations=1)

        return dilate

        cv.imshow('dilate',dilate)
        k = cv.waitKey(0)
        if k == 27:
            cv.destroyAllWindows()
        """

    @TimeTracer
    def process(self, url):
        img = self._read_remote_img(url)
        return self._cut(img)

if __name__ == "__main__":
    logging.basicConfig(level = logging.DEBUG, \
                    format = '%(asctime)s - %(levelname)s - %(message)s', \
                    datefmt = '%Y/%m/%d %H:%M:%S')

    cutter = GrabCutter() 
    cutter.process("http://su.bcebos.com/huitu/demo_url_1535627062392.png")
