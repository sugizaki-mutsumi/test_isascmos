# My fits-file tools for ISAS CMOS event data

## Event fits file converter 
Python proram [`genevtfits.py`](enevtfits.py) convert binary event files in a single directory into an event fits file. 
```
$ ./genevtfits.py (dirname) (output filename)

Example 
$ ./genevtfits.py  (some data dir)/141637  141637.evt
```
## Analysis example
- Example of plotting PHA histogram and image in juypyter-notebook [ql_isascmosevt.ipynb](ql_isascmosevt.ipynb)
