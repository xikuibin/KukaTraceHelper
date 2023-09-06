import numpy as np
import os
from common import *

CHANNEL_DATA_BEGIN = '#BEGINCHANNELHEADER'
CHANNEL_DATA_END = '#ENDCHANNELHEADER'

ChannelDataTypes = {
    'REAL64' : {
        'csvfmt':'%f',
        'dtype':'float64'
        },
}


Channel_Header_KEY = [
    ("200","Name","Channel name"),
    ("201","Description","Channel comment"),
    ("202","Unit","Unit"),
    ("210","ChannelType","Channel type"),
    ("211","SourceFile","File from which channel data is read"),
    ("213","StorageMethod","Method of storing the data"),
    ("214","DataType","Data type"),
    ("215","BitMask","Bit masking"),
    ("220","NumberOfValues","No. of values in the channel"),
    ("221","Pointer1stValue","Pointer to the 1st value in the channel"),
    ("222","OffsetPerValue","Offset for ASCII block files / Offset for binary block files with header"),
    ("223","LocalAsciiPtr","Local ASCII-pointer in the case of ASCII block files"),
    ("230","DelimiterChar","Separator character for ASCII-block files"),
    ("231","DecimalChar","Decimal character in ASCII-files"),
    ("232","ExponentChar","Exponential character in ASCII-files"),
    ("240","StartValOffset","Starting value / Offset"),
    ("241","StepWidthCalFac","Step width/Calibration factor"),
    ("250","Min","Minimum value in the channel"),
    ("251","Max","Maximum value of the channel"),
    ("252","NoValues","Keyword for NoValues in the channel"),
    ("253","Monotonous","Keyword for monotony"),
    ("254","ChanNoValValue","Value for NoValues in the channel"),
    ("260","DisplayType","Keyword for the data display at the interface"),
    ("261","Visibility","Specifies whether the channel is visible in the channel contents and channel properties"),
    ("262","DisplayOrder","Order number for viewing the channel contents"),
    ("263","ContentsWidth","Column width within the channel contents"),
    ("264","DisplayFormat","Format for the display of channel values in the channel contents"),
    ("265","PropertiesWidth","Column width in the channel properties"),
    ("270","AdditRealVar1","Register variable RV1 for storing the channel-related additional data"),
    ("271","AdditRealVar2","Register variable RV2 for storing the channel-related additional data"),
    ("272","AdditRealVar3","Register variable RV3 for storing the channel-related additional data"),
    ("273","AdditRealVar4","Register variable RV4 for storing the channel-related additional data"),
    ("274","AdditRealVar5","Register variable RV5 for storing the channel-related additional data"),
    ("275","AdditRealVar6","Register variable RV6 for storing the channel-related additional data"),
    ("280","AdditIntVar1","Register variable Int1 for storing the channel-related additional data in Integer format"),
    ("281","AdditIntVar2","Register variable Int2 for storing the channel-related additional data in Integer format"),
    ("282","AdditIntVar3","Register variable Int3 for storing the channel-related additional data in Integer format"),
    ("283","AdditIntVar4","Register variable Int4 for storing the channel-related additional data in Integer format"),
    ("284","AdditIntVar5","Register variable Int5 for storing the channel-related additional data in Integer format"),
    ("300","AdditTextVar1","Reserve 1 Text string"),
    ("301","AdditTextVar2","Reserve 2 Text String"),
]



class ChannelHeader():
    def __init__(self, ghdLines) -> None:
        for hl in ghdLines:
            parts = hl.split(',', 1)
            # print(parts)
            for k in Channel_Header_KEY:
                if k[0] == parts[0]:
                    # print(parts[0], k[1], parts[1])
                    self.__setattr__(k[1], parts[1])
        pass

    
    def __str__(self):
        L = [(attr, getattr(self, attr)) for attr in dir(self)
             if not attr.startswith("__")]
        return str(L)

    def DumpText(self):
        dumplines = []
        for k in Channel_Header_KEY:
            # print(k[1])
            if hasattr(self, k[1]):
                dumplines.append(HEADER_LINE_FORMAT.format(k[0], getattr(self, k[1]), k[1], k[2]))
        return '\n'.join(dumplines)

        
    @staticmethod
    def readChannelHeader(lns):
        return readHeaderSection(lns, CHANNEL_DATA_BEGIN, CHANNEL_DATA_END)

    
    @staticmethod
    def parseChannelHeader(lns):
        ghd = None
        bOK, indexbegin, indexend = ChannelHeader.readChannelHeader(lns)
        if bOK :
            ghdlns = lns[indexbegin+1:indexend] 
            #  print("header lines", ghdlns)

            ghd = ChannelHeader(ghdlns)
            lns = lns[indexend+1:]
            #  print("lines without vcvvv globalHeader", lns)

        return lns, ghd




def readExplicitBlockData(chheader, datadir):
    '''ONLY support real64 type now'''

    assert chheader.ChannelType == 'EXPLIZIT'
    header = "{}({})".format(chheader.Name, chheader.Unit)
    print("reading channel", header)

    cnt = int(chheader.NumberOfValues)
    pos = int(chheader.Pointer1stValue) - 1 #in DIADem  the file position numbers starts at 1

    chdatafile = os.path.join(datadir, chheader.SourceFile)

    alldata = np.fromfile(chdatafile, dtype=ChannelDataTypes[chheader.DataType]['dtype'])
    # print(alldata.shape)

    offset = float(chheader.StartValOffset)
    factor = float(chheader.StepWidthCalFac)

    chdata = alldata.reshape(cnt, -1)[:,pos:pos+1].reshape(cnt)
    chdata = chdata * factor + offset
    # print(chdata.shape, chdata.dtype)

    chDesc = ChannelDataTypes[chheader.DataType].copy()
    chDesc['colHeader'] = header
    # print(chDesc)
    
    return chdata, chDesc 

def generateImplicitData(chheader):
    '''use real64 as default data type'''
    assert chheader.ChannelType == 'IMPLIZIT' 

    header = "{}({})".format(chheader.Name, chheader.Unit)
    print("reading channel", header)

    cnt = int(chheader.NumberOfValues)

    start = float(chheader.StartValOffset)
    step = float(chheader.StepWidthCalFac)
    base = np.array(range(cnt), dtype='float64')
    chdata = base * step + start

    # print(chdata.shape, chdata.dtype)
    #print(channelDateTypes[chheader.DataType])
    chDesc = ChannelDataTypes['REAL64'].copy()
    chDesc['colHeader'] = header
    
    return chdata, chDesc 

def readChannelData(channels, datadir):
    lstchdata = []
    lstchdesc = []
    for ch in channels:
        if ch.ChannelType == 'EXPLIZIT' and 'BLOCK' == ch.StorageMethod:
            pass
            chdata, chDesc = readExplicitBlockData(ch, datadir)
            lstchdata.append(chdata)
            lstchdesc.append(chDesc)
        elif ch.ChannelType == 'IMPLIZIT':
            chdata, chDesc = generateImplicitData(ch)
            lstchdata.append(chdata)
            lstchdesc.append(chDesc)
        else:
            print("unsuported channel", ch)

    alldata = np.vstack(lstchdata).T
    print("result data shape:", alldata.shape)
    # print(alldata)
    # print(lstchdesc)
    return alldata, lstchdesc


