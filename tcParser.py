# -*- coding: utf-8 -*-

from pywlibs.xhtml import Xhtml
import os
import sys

class XhtmlParser:

    caseList = []

    def __init__(self, inputFile, outputFolder=r"./testCases/"):
        # check if folder exists, otherwise, create one
        if outputFolder[0] != '/':
            outputFolder = '/'.join([os.getcwd(), outputFolder])
        if not os.path.isdir(outputFolder):
            os.makedirs(outputFolder)

        if inputFile[0] != '/':
            inputFile = '/'.join([os.getcwd(), inputFile])
        fp = FileParser(inputFile)

        # settings for pywlib parser
        doc_type = 'XHTML 1.0 Strict'
        minimize = False

        # generate basic test suite
        X = Xhtml(doc_type, minimize)

        self.caseGenerator(X, fp.testcases, outputFolder)
        self.suiteGenerator(X, self.caseList, outputFolder)

    def suiteGenerator(self, X, cases, outputFolder):
        # generate header
        head = self.headGenerator(X, "Test Suite")

        table = X.table(attrs=(('id', 'suiteTable'), ('cellpadding', '1'), ('cellspacing', '1'), ('border', '1'), ('class', 'selenium')))
        tbodyData = table.tbody()
        tbodyData.tr().td(X.b("Test Suite"))
        for caseLink in cases:
            tbodyData.tr().td(X.a(caseLink, href=caseLink))

        body = X.body(table.render())

        html = X.html(head+body, {'xmlns': 'http://www.w3.org/1999/xhtml', 'xml:lang': 'en', 'lang': 'en'})

        # drop Test Suite file
        print("DROP: " + '/'.join([outputFolder, 'testSuite']))
        f = open('/'.join([outputFolder, 'testSuite']), 'w')
        f.writelines('<?xml version="1.0" encoding="UTF-8"?>')
        f.writelines(X.doctype())

        f.writelines(html)
        f.close()

    def caseGenerator(self, X, cases, outputFolder):
        for case in cases:
            print ("CASE: " + case.__str__())
            fn = str(cases.index(case)).zfill(6)
            # drop Test Suite file
            print("DROP: " + '/'.join([outputFolder, fn]))
            f = open('/'.join([outputFolder, fn]), 'w')
            f.writelines('<?xml version="1.0" encoding="UTF-8"?>')
            f.writelines(X.doctype())

            head = self.headGenerator(X, fn)
            body = self.bodyGenerator(X, fn, case)

            html = X.html(head+body, {'xmlns': 'http://www.w3.org/1999/xhtml', 'xml:lang': 'en', 'lang': 'en'})

            f.writelines(html)
            f.close()
            self.caseList.append(fn)

    def headGenerator(self, X, t):
        meta = X.meta('', {'http-equiv': 'Content-Type', 'content': 'text/html', 'charset': 'UTF-8'})
        link = X.link('', {'rel': 'selenium.base', 'href': 'https//moztrap.mozilla.org/'})
        title = X.title(t)
        head = X.head(meta+link+title, {'profile': 'http://selenium-ide.openqa.org/profiles/test-case'})
        return head

    def bodyGenerator(self, X, fn, case):
        table = X.table(attrs=(('cellpadding', '1'), ('cellspacing', '1'), ('border', '1')))

        table.thead().tr().td(fn, attrs=(('rowspan', '1'), ('colspan', 3)))
        tableData = table.tbody()
        #go to the base page
        self.stepRender(tableData.tr(), 'open', '/manage/cases/', '')
        # click add test case
        self.stepRender(tableData.tr(), 'clickAndWait', 'link=create a test case', '')
        # select product
        self.stepRender(tableData.tr(), 'select', 'id=id_product', 'label='+case.product)
        # select product version
        self.stepRender(tableData.tr(), 'select', 'id=id_productversion', 'label='+case.productversion)
        # select suite
        self.stepRender(tableData.tr(), 'select', 'id=id_suite', 'label='+case.suite)
        # enter title
        self.stepRender(tableData.tr(), 'sendKeys', 'id=id_name', case.title)
        # add description
        self.stepRender(tableData.tr(), 'sendKeys', 'id=id_description', case.description)
        # select tags
        for tag in case.tags:
            self.stepRender(tableData.tr(), 'sendKeys', 'id=id_add_tags', tag)
            self.stepRender(tableData.tr(), 'waitForElementPresent', 'link='+tag+' [tag]')
            self.stepRender(tableData.tr(), 'click', 'link='+tag+' [tag]')
        # add steps
        for step in case.steps:
            index = str(case.steps.index(step))
            instruction, expected = step
            self.stepRender(tableData.tr(), 'click', 'id=id_steps-'+index+'-instruction', '')
            self.stepRender(tableData.tr(), 'sendKeys', 'id=id_steps-'+index+'-instruction', instruction)
            if expected != "":
                self.stepRender(tableData.tr(), 'click', 'id=id_steps-'+index+'-expected', '')
                self.stepRender(tableData.tr(), 'sendKeys', 'id=id_steps-'+index+'-expected', expected)
        # set as draft
        self.stepRender(tableData.tr(), 'select', 'id=id_status', 'label=draft')
        # save
        self.stepRender(tableData.tr(), 'clickAndWait', 'name=save', '')

        return X.body(table)

    def stepRender(self, step, action="", target="", info=""):
        step.td(action)
        step.td(target)
        step.td(info)


### File Parser
class FileParser:

    testcases = []

    def __init__(self, filename):
        self.testcases = []
        print("OPEN: " + filename) ### log
        f = open(filename, 'r')
        self.parsing(f.readlines())
        f.close()

    def parsing(self, lines):
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
        for line in lines:
            for case in switch(line):
                if case("PRODUCT\n"):
                    state = "PRODUCT"
                    break
                if case("PRODUCTVERSION\n"):
                    state = "PRODUCTVERSION"
                    break
                if case("SUITE\n"):
                    state = "SUITE"
                    break
                if case("TITLE\n"):
                    state = "TITLE"
                    break
                if case("DESCRIPTION\n"):
                    state = "DESCRIPTION"
                    description = []
                    break
                if case("TAGS\n"):
                    state = "TAGS"
                    tags = []
                    break
                if case("STEP\n"):
                    if len(step) != 0:
                        steps.append((''.join(step), ''.join(expect)))
                    state = "STEP"
                    step = []
                    expect = []
                    break
                if case("EXPECTED\n"):
                    state = "EXPECTED"
                    break
                if case("DONE\n"):
                    state = ""
                    steps.append((''.join(step), ''.join(expect)))
                    self.testcases.append(TestCase(product, productversion,
                        suite, title, '\n'.join(description), tags, steps))
                    break
                if case():
                    if state == "PRODUCT":
                        product = line[:-1]
                    elif state == "PRODUCTVERSION":
                        productversion = line[:-1]
                    elif state == "SUITE":
                        suite = line[:-1]
                    elif state == "TITLE":
                        title = line[:-1]
                    elif state == "DESCRIPTION":
                        description.append(line[:-1])
                    elif state == "TAGS":
                        tags.append(line[:-1]) # drop the new line
                    elif state == "STEP":
                        step.append(line)
                    elif state == "EXPECTED":
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

    def __str__(self):
        return "Product: " + self.product + "\n" + \
               "Product Version: " + self.productversion + "\n" + \
               "Suite: " + self.suite + "\n" + \
               "Title: " + self.title + "\n" + \
               "Description: " + self.description + "\n" + \
               "tags: " + ' '.join(self.tags) + "\n" + \
               "steps: " + str(self.steps)

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


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("There should have two arguments")
        print("python tcParser.py <input> <output>")
        print(sys.argv)
    else:
        XhtmlParser(sys.argv[1], sys.argv[2])
