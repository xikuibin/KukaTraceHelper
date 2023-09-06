
import chardet
from chardet.universaldetector import UniversalDetector

HEADER_LINE_FORMAT = "{:>5} {:48} [{:16}] {}"

HEADERFILE_KEYWORD = 'DIAEXTENDED'


def detectEncoding(filename):
    bigdata = open(filename,'rb')
    detector = UniversalDetector()
    for line in bigdata.readlines():    
        detector.feed(line)    
        if detector.done:            
            break
    detector.close()
    bigdata.close()
    return detector.result

def stripLines(lns):
    clearText = []
    for l in lns:
        newl = l.strip()
        if newl:
            clearText.append(newl)
    return   clearText 

def readHeaderSection(lns, beginKey, endKey):
    bOK = False
    try:
        indexbegin = lns.index(beginKey)
        indexend = lns.index(endKey)
        # print(indexbegin, indexend)
        bOK=True
    except ValueError as e:
        print('ValueError:', e)
    else:
        pass #print('no error!')

    return bOK, indexbegin, indexend



