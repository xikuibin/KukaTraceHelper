
from common import *



GENERAL_DATA_BEGIN = '#BEGINGLOBALHEADER'
GENERAL_DATA_END = '#ENDGLOBALHEADER'

General_Header_KEY = [
    ("1","OS","Key word for the data set source"),
    ("2","DIAdemVers","Revision number"),
    ("101","Name","Data set title"),
    ("102","Comments","Comments on the Data Set (Array [1...100])"),
    ("103","Author","Author"),
    ("104","DateStr","Date"),
    ("105","TimeStr","Time"),
    ("106","CommentDesc","Comment description"),
    ("110","AsciiTime","Time format for time channels in ASCII files"),
    ("111","NoValValue","Value for NoValues in the data file"),
    ("112","ByteOrder","Exchange high byte and low byte"),
    ("120","ChanFont","Font for viewing the channel contents"),
    ("121","ChanFontSize","Font size for viewing the channel contents"),
    ("122","PropFont","Font for viewing the channel properties."),
    ("123","PropFontSize","Font size for viewing the channel properties."),
    ("130","Reserve1","Reserve 1"),
    ("131","Reserve2","Reserve 2"),
    ("132","Reserve3","Reserve 3"),
    ("133","Reserve4","Reserve 4"),
]


class GeneralHeader():
    def __init__(self, ghdLines) -> None:
        for hl in ghdLines:
            parts = hl.split(',', 1)
            # print(parts)
            for k in General_Header_KEY:
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
        for k in General_Header_KEY:
            # print(k[1])
            if hasattr(self, k[1]):
                dumplines.append(HEADER_LINE_FORMAT.format(k[0], getattr(self, k[1]), k[1], k[2]))
        return '\n'.join(dumplines)

        
    @staticmethod
    def readGeneralHeader(lns):
        return readHeaderSection(lns, GENERAL_DATA_BEGIN, GENERAL_DATA_END)

    
    @staticmethod
    def parseGeneralHeader(lns):
        ghd = None
        bOK, indexbegin, indexend = GeneralHeader.readGeneralHeader(lns)
        if bOK :
            ghdlns = lns[indexbegin+1:indexend] 
            # print("header lines", ghdlns)

            ghd = GeneralHeader(ghdlns)
            lns = lns[indexend+1:]
            # print("lines without globalHeader", lns)

        return lns, ghd
