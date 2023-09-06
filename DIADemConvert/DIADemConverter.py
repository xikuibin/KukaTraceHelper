'''

DIADem converter for KUKA trace
V 1.0 2022/11/26


'''

# DIAdem data file format speciction
# https://www.ni.com/docs/zh-CN/bundle/diadem/page/header/header/header_overview.htm

import os, argparse
import csv
import numpy as np

# dict Channel Header
from common import *
from GeneralHeader import *
from ChannelHeader import *


def readDIAdemHeaders(lns):
    print("passing header lines ...")
    lns = stripLines(lns)
    # print("stripped lines", lns)

    fileheader = lns[0]
    if not fileheader.startswith(HEADERFILE_KEYWORD):
        print("Invalid DIAdem header file")
        return
    
    del lns[0]

    ghd = None
    chs = []
    lns, ghd = GeneralHeader.parseGeneralHeader(lns)
    if ghd:
        chs = []
        while len(lns) > 0:
            lns, channel = ChannelHeader.parseChannelHeader(lns)
            if channel:
                chs.append(channel)
            else:
                break
   
    return ghd, chs



def dumpHeader(ghd, chs, filenamebase):
    dumpname = filenamebase + ".header.txt"
    print("dump header to", dumpname)
    with open(dumpname, 'wt', encoding='utf-8') as f:
        f.write("DIAdem HEADER dump\n\n")
        f.write("# General Data Set Header\n")
        f.write(ghd.DumpText())
        f.write("\n\n")

        for i in range(len(chs)):
            f.write("# Channel Header - {}\n".format(i+1))
            f.write(chs[i].DumpText())
            f.write("\n\n")



def processHeaderFile(headerFilePath):
    print("read", headerFilePath)

    filenamebase = os.path.splitext(headerFilePath)[0]
    # print(filenamebase)

    encodingTest = detectEncoding(headerFilePath)
    # print (encodingTest)
    # {'encoding': 'ISO-8859-1', 'confidence': 0.73, 'language': ''}

    with open(headerFilePath, 'rt', encoding= encodingTest['encoding']) as f:
        lns = f.readlines()

    ghd, chs = readDIAdemHeaders(lns)

    dumpHeader(ghd, chs, filenamebase)

    return ghd, chs


def processTraceFile(tracefile):
    ghd, chs = processHeaderFile(tracefile)

    print("Read channel data ..., channel count=", len(chs))
    alldata, lstchdesc = readChannelData(chs)
    print("result channel count:", len(lstchdesc))

    pathbase = os.path.splitext(tracefile)[0]
    csvpath = pathbase + ".channel.csv"
    print("write data to", csvpath)

    colheaders = ','.join([d['colHeader'] for d in lstchdesc])
    np.savetxt(csvpath, alldata, fmt='%g', delimiter=',', 
               header=colheaders, comments='', encoding='utf-8')


def processTraceDir(traceDir):
    import glob
    headerfiles = glob.glob(os.path.join(traceDir, '*.dat'))
    print("found header files count", len(headerfiles))
    for p in headerfiles:
        print("\n")
        processTraceFile(p)

    
def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument('-f',
                        '--file',
                        help='trace dat file to be processed.')
    group.add_argument('-d',
                        '--dir',
                        help='trace data directory to be processed')

    args = parser.parse_args()
    print(args)
    #print(args.file, args.dir)
    if args.file:
        processTraceFile(args.file)
    elif args.dir:
        processTraceDir(args.dir)
    
if __name__ == '__main__':
    main()
    pass

# headerFileName = '.\\20230831-18-18-44_NextGenDrive#6.dat'
# processTraceFile(headerFileName)

# headerDir = ".\\"
# processTraceDir(headerDir)