#!/usr/bin/python
import urllib2
import xml.etree.ElementTree
import sys, getopt
import os

schemaUrls = []
schemaFilenames = []
dirName = ''

def urlGet(url):
    try:
        urlContent = urllib2.urlopen(url)
    except:
        print 'Error opening URL:' + url
        sys.exit(2)

    return urlContent

def urlGetString(url):
    try:
        urlContent = urllib2.urlopen(url)
    except:
        print 'Error opening URL:' + url
        sys.exit(2)

    return urlContent.read()

def getSubSchemaUrl(url):
    subSchemaContent = urlGet(url)

    try:
        subSchemaTree = xml.etree.ElementTree.parse(subSchemaContent)
    except:
        print 'Failed to parse response from:' + url + ' as XML'
        sys.exit(2)

    subSchemaRoot = subSchemaTree.getroot()
    importElements = subSchemaRoot.findall(".//*[@schemaLocation]")

    for child in importElements:
        subSchemaUrl = child.attrib['schemaLocation']
        print 'Found schema reference to: ' + subSchemaUrl + ' in url: ' + url
        schemaUrls.append(subSchemaUrl)
        getSubSchemaUrl(subSchemaUrl)

def downloadSchemas():
    global schemaFilenames
    global dirName

    for url,filename in schemaFilenames:
        fileContent = urlGetString(url)

        print 'Transforming and saving ' + url + ' to local file: ' + filename

        for in_url,in_filename in schemaFilenames:
            print 'replacing ' + in_url + ' with ' + in_filename
            fileContent = fileContent.replace(in_url,in_filename)
            print fileContent.find(in_url)

        schemaFile = open(dirName + '/' + filename, 'w')
        schemaFile.write(fileContent)
        schemaFile.close

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
    schemaUrls = list(set(schemaUrls))
    schemaUrls.sort()

    for index,schemaUrl in enumerate(schemaUrls):
        schemaName = wsdlName + '_' + str(index) + '.xsd'
        schemaFilenames.append([schemaUrl,schemaName])

    schemaFilenames.append([wsdlUrl, wsdlName + '.wsdl'])

    downloadSchemas()

    print 'Done!'
if __name__ == "__main__":
    main(sys.argv[1:])
