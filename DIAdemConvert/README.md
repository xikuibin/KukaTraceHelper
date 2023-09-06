
Usage: DIAdemConvert.py [-h] [-f FILE | -d DIR]

DIAdem converter for KUKA trace 
V 1.0 2023/09/06

optional arguments:
  -h, --help            show this help message and exit
  -f FILE, --file FILE  trace .dat file to be processed.
  -d DIR, --dir DIR     trace data directory to be processed


KUKA robots use DIAdem data file to storage the trace data.
This is not a complete DIAdem to CSV converter. Only features used by Kuka Trace will be supported.

The full file format document could be found at [DIAdem data file format speciction](https://www.ni.com/docs/zh-CN/bundle/diadem/page/header/header/header_overview.htm).