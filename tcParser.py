# -*- coding: utf-8 -*-

from pywlibs.xhtml import Xhtml
import os

class XhtmlParser:

    caseList = []

    def __init__(self, inputFile, outputFolder=r"./testCases/"):
        caseList = []
        # check if folder exists, otherwise, create one
        if not os.exists(outputFolder):
            os.makedirs(outputFolder)

        fp = FileParser(inputFile)

        # settings for pywlib parser
        doc_type = 'XHTML 1.0 Strict'
        minimize = False

        # generate basic test suite
        X = Xhtml(doc_type, minimize)

        caseGenerator(X, fp.testcases, outputFolder)

    def caseGenerator(self, X, fp.testcases, outputFolder):
        for case in fp.testcases:
            fn = str(fp.testcases.index(case)).zfill(6)
            f = open(fn, 'w')
            f.writelines('<?xml version="1.0" encoding="UTF-8"?>')
            f.writelines(X.doctype())

            head = headGenerator(fn)
            body = bodyGenerator(case)

            f.close()

    def headGenerator(self, fn):
        meta = X.meta('', {'http-equiv': 'Content-Type', 'content': 'text/html', 'charset': 'UTF-8'})
        link = X.link('', {'rel': 'selenium.base', 'href': 'https//moztrap.mozilla.org/'})
        title = X.title(fn)
        head = X.head(meta+link+title, {'profile': 'http://selenium-ide.openqa.org/profiles/test-case'})
        return head

    def bodyGenerator(self, case):
        


### File Parser
class FileParser:

    testcases = []

    def __init__(self, filename):
        self.testcases = []
        f = open(filename, 'r')
        self.parsing(f.readlines())
        f.close()

    def parsing(self, f):
        product = ""
        productversion = ""
        suite = ""
        title = ""
        description = []
        tags = []
        steps = []
        step = []
        expect =[]

        state = ""
        for line in f.readlines:
            for case in switch(line):
                if case("PRODUCT"):
                    state = "PRODUCT"
                    break
                if case("PRODUCTVERSION"):
                    state = "PRODUCTVERSION"
                    break
                if case("SUITE"):
                    state = "suite"
                    break
                if case("TITLE"):
                    state = "TITLE"
                    break
                if case("DESCRIPTION"):
                    state = "DESCRIPTION"
                    description = []
                    break
                if case("TAGS"):
                    state = "TAGS"
                    tags = []
                    break
                if case("STEP"):
                    if len(step) != 0:
                        steps.append((''.join(step), ''.join(expect)))
                    state = "STEP"
                    step = ""
                    expect = ""
                    break
                if case("EXPECT"):
                    state = "EXPECT"
                    break
                if case("DONE"):
                    steps.append((''.join(step), ''.join(expect)))
                    self.testcases.append(TestCase(product, productversion,
                        suite, title, ''.join(description), tags, steps))
                    break
                if case():
                    if state == "PRODUCT":
                        product = line
                    elif state == "PRODUCTVERSION":
                        productversion = line
                    elif state == "SUITE":
                        suite = line
                    elif state == "TITLE":
                        title = line
                    elif state == "DESCRIPTON":
                        description.append(line)
                    elif state == "TAGS":
                        tags.append(line[:-1]) # drop the new line
                    elif state == "STEP":
                        step.append(line)
                    elif state == "EXPECT":
                        expect.append(line)
                    break





### Test Case Model
class TestCase:
    product = ""
    productversion = ""
    suite = ""
    title = ""
    description = ""
    tags = []
    steps = []

    def __init__(self, product, productversion, suite, title, description, tags, steps):
        self.product = product
        self.productversion = productversion
        self.suite = suite
        self.title = title
        self.description = description
        self.tags = tags
        self.steps = steps

### Implement switch like function for state machine :)
class switch(object):
    def __init__(self, value):
        self.value = value
        self.fall = False

    def __iter__(self):
        yield self.match
        raise StopIteration

    def match(self, *args):
        if self.fall or not args:
            return True
        elif self.value in args:
            self.fall = True
            return True
        else:
            return False

