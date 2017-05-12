#!/usr/bin/python
import urllib2
import xml.etree.ElementTree
import sys, getopt
import os
import itertools

schemaUrls = []
schemaFilenames = []
dirName = ''

def urlGet(url):
    try:
        urlContent = urllib2.urlopen(url)
    except:
        print 'Error opening URL:' + url
        sys.exit(2)

    return urlContent.read()

def getSubSchemaUrl(url):
    subSchemaContent = urlGet(url)
    subSchemaTree = ''

    try:
        subSchemaTree = xml.etree.ElementTree.fromstring(subSchemaContent)
    except:
        print 'Failed to parse response from:' + url + ' as XML'


    # print subSchemaContentString
    subSchemaRoot = subSchemaTree
    importElements = subSchemaRoot.findall(".//*[@schemaLocation]")

    schemaUrls.append([url,subSchemaContent])

    for child in importElements:
        subSchemaUrl = child.attrib['schemaLocation']
        print 'Found schema reference in: ' + url + ' to: ' + subSchemaUrl
        getSubSchemaUrl(subSchemaUrl)

def saveSchemas():
    global schemaFilenames
    global dirName

    for url,filename,content in schemaFilenames:
        # fileContent = urlGet(url)

        print 'Transforming and saving ' + url + ' to local file: ' + filename
        for in_url,in_filename,_ in schemaFilenames:
            content = content.replace(in_url,in_filename)
        # fileTree = content
        # fileRoot = fileTree.getroot()
        #
        # for in_url,in_filename,_ in schemaFilenames:
        #     xpathValue = ".//*[@schemaLocation=\"" + in_url + "\"]"
        #     importElement = fileTree.find(xpathValue)
        #     if importElement is not None:
        #         importElement.set('schemaLocation',in_filename)

        schemaFile = open(dirName + '/' + filename, 'w')
        schemaFile.write(content)
        schemaFile.close
        # content.write(open(dirName + '/' + filename, 'wb'))

def main(argv):
    wsdlUrl = ''
    global schemaUrls
    global schemaFilenames
    global dirName

    print 'Starting...'

    try:
        opts, args = getopt.getopt(argv,"u:")
    except getopt.GetoptError:
        print 'usage: export-wsdl.py -u <wsdlUrl>'
        sys.exit(2)
    if len(opts) == 0:
        print 'usage: export-wsdl.py -u <wsdlUrl>'
        sys.exit(2)

    wsdlUrl = opts[0][1]
    wsdlName = wsdlUrl.split("/")[-1].split("?")[0]
    dirName = wsdlName
    print 'Exporting schema definitions from: ' + wsdlUrl
    if not os.path.exists(wsdlName):
        print 'Creating new project directory: ' + wsdlName
        os.makedirs(dirName)

    getSubSchemaUrl(wsdlUrl)

    schemaUrls.sort()
    schemaUrls = list(schemaUrls for schemaUrls,_ in itertools.groupby(schemaUrls))

    for index,schemas in enumerate(schemaUrls):
        if '?wsdl' in schemas[0]:
            schemaName = wsdlName + '.wsdl'
        else:
            schemaName = wsdlName + '_' + str(index) + '.xsd'
        schemaFilenames.append([schemas[0],schemaName,schemas[1]])

    # schemaFilenames.append([wsdlUrl, wsdlName + '/' + wsdlName + '.wsdl'])

    saveSchemas()

    print 'Done!'
if __name__ == "__main__":
    main(sys.argv[1:])
