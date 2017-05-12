#!/usr/bin/python
import urllib2
import xml.etree.ElementTree
import sys, getopt
import os

schemaUrls = []
schemaFilenames = []

def getSubSchemaUrl(url):
    global schemaUrls
    try:
        subSchemaContent = urllib2.urlopen(url)
    except:
        print 'Error opening URL:' + url
        sys.exit(2)

    subSchemaTree = xml.etree.ElementTree.parse(subSchemaContent)
    subSchemaRoot = subSchemaTree.getroot()

    importElements = subSchemaRoot.findall(".//*[@schemaLocation]")

    for child in importElements:
        subSchemaUrl = child.attrib['schemaLocation']
        print 'Found schema reference to: ' + subSchemaUrl + ' in url: ' + url
        schemaUrls.append(subSchemaUrl)
        getSubSchemaUrl(subSchemaUrl)

def downloadSchemas():
    global schemaFilenames
    for url,filename in schemaFilenames:
        try:
            fileContent = urllib2.urlopen(url)
        except:
            print 'Error opening URL:' + url
            sys.exit(2)

        print 'Transforming and saving ' + url + ' to local file: ' + filename

        fileTree = xml.etree.ElementTree.parse(fileContent)
        fileRoot = fileTree.getroot()

        for in_url,in_filename in schemaFilenames:
            xpathValue = ".//*[@schemaLocation=\"" + in_url + "\"]"
            importElement = fileTree.find(xpathValue)
            if importElement is not None:
                importElement.set('schemaLocation',in_filename)

        fileTree.write(open(filename, 'wb'))

def main(argv):
    wsdlUrl = ''
    global schemaUrls
    global schemaFilenames

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
    print 'Exporting schema definitions from: ' + wsdlUrl
    if not os.path.exists(wsdlName):
        print 'Creating new project directory: ' + wsdlName
        os.makedirs(wsdlName)

    getSubSchemaUrl(wsdlUrl)
    schemaUrls = list(set(schemaUrls))
    schemaUrls.sort()

    for index,schemaUrl in enumerate(schemaUrls):
        schemaName = wsdlName + '/' + wsdlName + '_' + str(index) + '.xsd'
        schemaFilenames.append([schemaUrl,schemaName])

    schemaFilenames.append([wsdlUrl, wsdlName + '/' + wsdlName + '.wsdl'])

    downloadSchemas()

    print 'Done!'
if __name__ == "__main__":
    main(sys.argv[1:])
