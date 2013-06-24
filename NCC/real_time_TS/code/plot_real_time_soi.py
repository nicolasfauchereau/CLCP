#!/usr/bin/python
# -*- coding: latin-1 -*-
### ==============================================================================================================
# SOI is calculated using the Troup method, where the climatological period is taken (for historical reasons) to be 1941-1980
# Thus, if T and D are the monthly pressures at Tahiti and Darwin, respectively, and Tc and Dc the climatological monthly pressures, then
#  
#              SOI    =   [ (T – Tc) – (D – Dc) ]  /  [ StDev (T – D)  ]
#   
# So the numerator is the anomalous Tahiti-Darwin difference for the month in question, and the denominator is the standard deviation of the Tahiti-Darwin differences for that month over the 1941-1980 climatological period. I then round the answer to the nearest tenth (ie, 1 decimal place).
# 
# The period 1941-1980 was that used by Neil Gordon at Meteorological Service for his seminal paper in MWR. 

### ==============================================================================================================
### imports 
import os
import sys
import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from numpy import ma
import urllib2
import requests
from matplotlib.dates import YearLocator, MonthLocator, DateFormatter
from dateutil import parser
from datetime import datetime, timedelta

### ==============================================================================================================
### paths 
### ==============================================================================================================
fpath = os.path.join(os.environ['HOME'], 'operational/NCC/real_time_TS/figures')
droppath = os.path.join(os.environ['HOME'], 'Dropbox/operational/NCC/real_time_TS/figures')
opath = os.path.join(os.environ['HOME'], 'operational/NCC/real_time_TS/data')
spath = '/mnt/S/fauchereaun/NCC/INDICES'
wspath = '/mnt/WS/ncc/indices'

### ==============================================================================================================
### define here where the figures need to be saved
figures_paths = [os.path.join(os.environ['HOME'], 'operational/NCC/real_time_TS/figures'), \
        os.path.join(os.environ['HOME'], 'Dropbox/operational/NCC/real_time_TS/figures'), \
        '/mnt/WS/ncc/indices/figures', \
        '/mnt/WS/ncc/global_ppt/inputs']
### ==============================================================================================================

### ==============================================================================================================
### plotting parameters 
years   = YearLocator()
#months  = MonthLocator(bymonth=[1,3,5,7,9,11])
months  = MonthLocator()
mFMT = DateFormatter('%b')
yFMT = DateFormatter('\n\n%Y')
mpl.rcParams['xtick.labelsize'] = 12 
mpl.rcParams['ytick.labelsize'] = 12 
mpl.rcParams['axes.titlesize'] = 14 
mpl.rcParams['xtick.direction'] = 'out'
mpl.rcParams['ytick.direction'] = 'out'
mpl.rcParams['xtick.major.size'] = 5
mpl.rcParams['ytick.major.size'] = 5
mpl.rcParams['xtick.minor.size'] = 2
### ==============================================================================================================

### ==============================================================================================================
### proxies
proxies = {}
proxies['http'] = 'http://www-proxy.niwa.co.nz:80'
proxies['https'] = 'http://www-proxy.niwa.co.nz:80'
proxies['ftp'] = 'http://www-proxy.niwa.co.nz:80'
### use urllib2 to open remote http files
urllib2proxy = urllib2.ProxyHandler(proxies)
opener = urllib2.build_opener(urllib2proxy)
urllib2.install_opener(opener)

### ==============================================================================================================
### define a function to do running mean 
def running_mean(a, window):
    """
    perform a running mean on a, with window "window"
    the window / 2 values at the beginning and end are masked
    """
    shape = a.shape[:-1] + (a.shape[-1] - window + 1, window)
    strides = a.strides + (a.strides[-1],)
    xx = np.lib.stride_tricks.as_strided(a, shape=shape, strides=strides)

    xa = ma.masked_values(ma.ones(a.shape),1.)

    xx = np.mean(xx, -1) 

    xa[(window/2):(len(xx)+(window/2)),...] = xx

    return xa
### ==============================================================================================================

### ==============================================================================================================
### prelim, we get the date for which the next update is likely to be made available: 
url = "http://www.bom.gov.au/climate/current/soihtm1.shtml"
r = requests.get(url, proxies=proxies)
urlcontent = r.content
date_update = urlcontent[urlcontent.find("Next SOI update expected:"):urlcontent.find("Next SOI update expected:")+60]
date_update = date_update.split("\n")[0]
print date_update
### ==============================================================================================================

### ==============================================================================================================
# step 1: get the data for TAHITI

url = urllib2.urlopen("ftp://ftp.bom.gov.au/anon/home/ncc/www/sco/soi/tahitimslp.html")

data = url.readlines()
soidata = []
for i in xrange(16, len(data) - 3):
    soidata.append(data[i].strip("\r\n"))

tahiti = [] 
for i in xrange(soidata.__len__() - 1):
    tahiti.append(soidata[i].split("  "))

tahitic = []
for i in xrange(tahiti.__len__()):
    tahitic.append(np.array(map(np.float, tahiti[i][0:13])))

tahitic = np.array(tahitic)

### deal with the messy last line of the data 
lastl = soidata[-1]
lastl = lastl.replace("*\t","-999.9").replace("*", "-999.9")
lastl = lastl.split(" ")
clastl = []
[clastl.append(x) for x in lastl if x is not ""]
tahitic = np.r_[tahitic, np.array(map(np.float, clastl))[np.newaxis,]]

tahitidf = pd.DataFrame(data=tahitic[:,1:], index=tahitic[:,0], columns=["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])

### uncomment that to have the annual cycles of averages and std
# subplot(121); tahiti_mean.plot(); title('mean');
# subplot(122); tahiti_std.plot(); title('std');

### handles missing values
tahitidf[tahitidf == -999.9] = np.NaN

### ==============================================================================================================
# step 2: get the data for DARWIN

url = urllib2.urlopen("ftp://ftp.bom.gov.au/anon/home/ncc/www/sco/soi/darwinmslp.html")

data = url.readlines()
soidata = []
for i in xrange(16, len(data) - 3):
    soidata.append(data[i].strip("\r\n"))

darwin = [] 
for i in xrange(soidata.__len__() - 1):
    darwin.append(soidata[i].split("  "))

darwinc = []
for i in xrange(darwin.__len__()):
    darwinc.append(np.array(map(np.float, darwin[i][0:13])))

darwinc = np.array(darwinc)

### deal with the messy last line of the data 
lastl = soidata[-1]
lastl = lastl.replace("*\t","-999.9").replace("*", "-999.9")
lastl = lastl.split(" ")
clastl = []
[clastl.append(x) for x in lastl if x is not ""]
darwinc = np.r_[darwinc, np.array(map(np.float, clastl))[np.newaxis,]]

darwindf = pd.DataFrame(data=darwinc[:,1:], index=darwinc[:,0], columns=["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])

# handles missing values
darwindf[darwindf == -999.9] = np.NaN

### ==============================================================================================================
# calculate the climatology over 1941 to 1980
tahiti_cli = tahitidf.ix[1941.0:1980.0]
darwin_cli = darwindf.ix[1941.0:1980.0]
tahiti_mean = tahiti_cli.mean(0)
darwin_mean = darwin_cli.mean(0)
### ==============================================================================================================

### ==============================================================================================================
### Step 3: calculate the SOI
soi = ((tahitidf - tahiti_mean) - (darwindf - darwin_mean)) / ((tahiti_cli -  darwin_cli).std(0))
# write ... 
soi.to_csv(os.path.join(wspath, "NICO_NIWA_SOI.csv"))
soi.to_csv(os.path.join(spath, "NICO_NIWA_SOI.csv"))
soi.to_csv(os.path.join(opath, "NICO_NIWA_SOI.csv"))

### stack everything vertically 
ts_soi = soi.stack()

# create a index of dates to transform the soi into a well defined pandas Timeseries
dates = [parser.parse("/".join([str(np.int(ts_soi.index[i][0])),ts_soi.index[i][1],"1"])) for i in range(ts_soi.index.__len__())]

# create a time series in pandas
pdS_soi = pd.Series(ts_soi.values, index=dates)

### ==============================================================================================================
### HERE WE CHOOSE THE PERIOD ! 
pdS_soi = pdS_soi.truncate(before="2010/1/1")
#pdS_soi = pdS_soi.truncate(before="2009/7/1", after="2012/12/1")
### ==============================================================================================================

dates = np.array(pdS_soi.index.to_pydatetime())
soi = pdS_soi.values
#soi = np.round(soi,1)
soim = running_mean(soi,3)

widths=np.array([(dates[j+1]-dates[j]).days for j in range(len(dates)-1)] + [30])

### middle of the month for the 3 month running mean plot
datesrm = np.array([x + timedelta(days=15) for x in dates])

### ==============================================================================================================
### now plot the figure
fig = plt.figure(figsize=(20,9))
ax = fig.add_subplot(111)
#ax.bar(dates,values, width=25, align='edge', facecolor='b', alpha=0.8)
# ax.bar(dates[soi>=0],soi[soi>=0], width=widths[soi>=0], align='center', facecolor='steelblue', alpha=.9)
# ax.bar(dates[soi<0],soi[soi<0], width=widths[soi<0], align='center', facecolor='coral', alpha=.9)
ax.bar(dates[soi>=0],soi[soi>=0], width=widths[soi>=0], facecolor='b', alpha=.8)
ax.bar(dates[soi<0],soi[soi<0], width=widths[soi<0], facecolor='r', alpha=.8)
ax.plot(datesrm,soim, lw=3, color='k', label='3-mth mean')
#ax.bar(pdS_soi.index, pdS_soi.values, width=[(dates[j+1]-dates[j]).days for j in range(len(dates)-1)] + [30], align='edge',facecolor='b', alpha=0.8 )
ax.xaxis.set_minor_locator(months)
ax.xaxis.set_major_locator(years)
ax.xaxis.set_minor_formatter(mFMT)
ax.xaxis.set_major_formatter(yFMT)
#ax.set_frame_on(False)
labels = ax.get_xminorticklabels()
for label in labels:
    label.set_fontsize(14)
    label.set_rotation(90)
labels = ax.get_xmajorticklabels()
for label in labels:
    label.set_fontsize(18)
labels = ax.get_yticklabels()
for label in labels:
    label.set_fontsize(18)
ax.grid(linestyle='--')
ax.xaxis.grid(True, which='both')
ax.legend(loc=3, fancybox=True)
ax.set_ylim(-3., 3.)
ax.set_ylabel('Monthly SOI (NIWA)', fontsize=14, backgroundcolor="w")
ax.text(dates[0],3.2,"NIWA SOI", fontsize=24, fontweight='bold')
ax.text(dates[-5], 2.8, "%s NIWA Ltd." % (u'\N{Copyright Sign}'))

textBm = "%s = %+4.1f" % (dates[-1].strftime("%B %Y"), soi[-1])
textBs = "%s to %s = %+4.1f" % (dates[-3].strftime("%b %Y"), dates[-1].strftime("%b %Y"), soi[-3:].mean())
 
ax.text(datesrm[8],3.2,"Latest values: %s, %s" % (textBm, textBs), fontsize=16)
ax.text(datesrm[0],2.8,date_update, fontsize=14)
for fpath in figures_paths: 
    plt.savefig(os.path.join(fpath, "real_time_monthly_NIWA_SOI.png"), dpi=400)
    plt.savefig(os.path.join(fpath, "real_time_monthly_NIWA_SOI.pdf"), dpi=400)
