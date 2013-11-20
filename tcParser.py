# -*- coding: utf-8 -*-

from pywlibs.xhtml import Xhtml
import os

class XhtmlParser():

    def __init__():
    
        # settings for pywlib parser
        doc_type = 'XHTML 1.0 Strict'
        minimize = False

        # generate basic test suite
        X = Xhtml(doc_type, minimize)

        # check if folder exists, otherwise, create one
        testCaseFolder = r"./testCase"
        if not os.exists(testCaseFolder):
            os.makedirs(testCaseFolder)

    ## File Parser

class FileParser(f):

    def __init__():
        break

class TestCase:
    product = ""
    productversion = ""
    suite = ""
    title = ""
    tags = []
    steps = []

    def __init__(self, product, productversion, suite, title, tags, steps):
        self.product = product
        self.productversion = productversion
        self.suite = suite
        self.title = title
        self.tags = tags
        self.steps = steps
