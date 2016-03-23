
# coding: utf-8

# ## Clickable Histogram of Atmospheric Data (CHAD)
# ### *(Clickable Histogram (ClickHist) + Atmospheric Data Input)*
# 
# Author: [Matthew Niznik](http://matthewniznik.com) ([matt@matthewniznik.com](mailto:matt@matthewniznik.com))<br>
# Post-Doctoral Associate,
# [RSMAS](http://rsmas.miami.edu/),
# [University of Miami](http://welcome.miami.edu/)
# 
# For more information, see:<br>
# https://github.com/matthewniznik/ClickHist/wiki<br>
# http://matthewniznik.com/research-projects/clickhist<br>

# # Let's get started.
# ## (1) Setting Input/Output Files
# ## First, you need to chose the *template* bundle.
# ### This is an IDV bundle with your desired data and displays that ClickHist will alter to focus on the time and location relevant to scatter points you select.
# **Note:** The first bundle in both lists here will be the one referenced in the later script that generates images, movies, and a .zidv file. It should probably be the "full" bundle with the variables you want to study.

# In[ ]:

bundleInFilenames = ['G5NR_template_full', 'G5NR_template_simple_cloudsir']
bundleOutTags = ['full', 'simple']


# ## Now, pick a Tag for this session's *Case Notebooks*.
# #### This is a notebook that will be generated separately from this one containing snapshots of ClickHists and other images related to each case you select.
# This way, without much extra effort you can remember what you were working on!

# In[ ]:

caseNotebookFilename = 'Mar23'


# ## (2) Set the variables, data sources, and other necessary information.
# ### What geographic subset are you interested in exploring?
# 
# Longitude: 0 through 360 (Degrees East)<br>
# Latitude: -90 through 90 (Degrees North)<br>

# In[ ]:

lonLow = 360.-160.
lonHigh = 360.-120.
latLow = -25.0
latHigh = 15.0


# ### Three URLs of CHAD preprocessed data are below. Select the time interval you prefer.
# **Every Hour:**

# In[ ]:

urlToLoad = ('https://weather.rsmas.miami.edu/repository/'+
             'opendap/synth:eab82de2-d682-4dc0-ba8b-2fac7746d269:'+
             'L2FsbFZhcnNfcjkweDQ1XzEubmM0/entry.das')


# **Every Three Hours:**

# In[ ]:

urlToLoad = ('https://weather.rsmas.miami.edu/repository/'+
             'opendap/synth:eab82de2-d682-4dc0-ba8b-2fac7746d269:'+
             'L2FsbFZhcnNfcjkweDQ1XzMubmM0/entry.das')


# **Every Six Hours:**

# In[ ]:

urlToLoad = ('https://weather.rsmas.miami.edu/repository/'+
             'opendap/synth:eab82de2-d682-4dc0-ba8b-2fac7746d269:'+
             'L2FsbFZhcnNfcjkweDQ1XzYubmM0/entry.das')


# ### Now let's get some information on the variables you want
# 
# **For this data, we've preprogrammed all of the units and data into a module so you just have to pick from a list of options (case sensitive):**<br>
# Precip, W500, wPuP, TEEF, ZSKEDot, HMV

# In[ ]:

var1Name = 'Precip'
var2Name = 'W500'


# ### What kind of snapshot from the [online G5NR repository](http://g5nr.nccs.nasa.gov/images/) of pre-made images would you like?
# 
# **Options:** 'cloudsir', 'cloudsvis', 'cyclones', 'storms', 'temperature', 'tropical', 'water', 'winds'
# <br>*N.B. Must be a list. If image saving time is prohibitively long, shorten the list of variables.*

# In[ ]:

imageVar = ['cloudsir']


# ### Set how large you want the IDV bundle to be in space and time
# #### Each of these is calculated as distance from center, so `lonOffset = 1.0` means 2.0° of longitude.
# #### `dtFromCenter` needs to be in seconds

# In[ ]:

lonOffset = 1.0
latOffset = 1.0
dtFromCenter = 3*3600


# ### Would you like specific quantiles indicated in X and Y?
# **If so, specify them here.**

# In[ ]:

quantiles = [0.01,0.1,1,5,95,99,99.9,99.99]


# ### Import the necessary modules needed for CHAD to work

# *Currently supported graphics backends are Qt4Agg ('qt4') and TK ('tk')*

# In[ ]:

#%matplotlib tk
get_ipython().magic(u'matplotlib qt4')
import matplotlib
#matplotlib.use('TkAgg')
#matplotlib.use('Qt4Agg')

from IPython.display import clear_output
import netCDF4
import sys

import ClickHist_G5NR as ClickHist
import ClickHistDo_G5NR as ClickHistDo
import loadmod_G5NR


# #### This call is necessary to make sure the output displays properly
# 
# (If interested in the details, see: http://bit.ly/1SsishU)

# In[ ]:

oldsysstdout = sys.stdout
sys.stdout = loadmod_G5NR.flushfile(sys.stdout)


# #### The following (less often edited) items are set to default values in the module `loadmod_G5NR`
# 
# (You can change them in the module if desired, but they are left out here to save space. For "advanced" users.)

# In[ ]:

lonValueName = loadmod_G5NR.lonValueName
latValueName = loadmod_G5NR.latValueName
timeValueName = loadmod_G5NR.timeValueName
startDatetime = loadmod_G5NR.startDatetime

var1Edges = loadmod_G5NR.binOptions[var1Name]
var2Edges = loadmod_G5NR.binOptions[var2Name]

var1FmtStr = loadmod_G5NR.fmtStrOptions[var1Name]
var2FmtStr = loadmod_G5NR.fmtStrOptions[var2Name]

var1ValueName = loadmod_G5NR.valueNameOptions[var1Name]
var2ValueName = loadmod_G5NR.valueNameOptions[var2Name]

var1Units = loadmod_G5NR.varUnitOptions[var1Name]
var2Units = loadmod_G5NR.varUnitOptions[var2Name]
metadata_UD = (var1Name+' vs '+var2Name+': '+
               str(lonLow)+' to '+str(lonHigh)+' E, '+
               str(latLow)+' to '+str(latHigh)+' N')

var1ValueMult = loadmod_G5NR.varMultOptions[var1Name]
var2ValueMult = loadmod_G5NR.varMultOptions[var2Name]


# ## (3) Load the Data
# 
# **N.B.** CHAD currently expects the 3-D variables to be in the Python format `variable[times,latitudes,longitudes]`.<br>
# If this is not the default, you will have to either permute the data below or preprocess the data so that it matches this format.

# In[ ]:

cdfIn = netCDF4.Dataset(urlToLoad,'r')


# In[ ]:

lonValues = cdfIn.variables[lonValueName][:]
latValues = cdfIn.variables[latValueName][:]
timeValues = cdfIn.variables[timeValueName][:]*loadmod_G5NR.timeValueMult


# #### By finding the needed index ranges here, we can load a subset of the data over the web instead of loading it all and subsetting later.

# In[ ]:

lowLonInt,highLonInt = loadmod_G5NR.getIntEdges(lonValues,lonLow,lonHigh)
lowLatInt,highLatInt = loadmod_G5NR.getIntEdges(latValues,latLow,latHigh)


# *Based on the data chunk you're accessing, the variable load may take some time.*

# In[ ]:

var1Values = cdfIn.variables[var1ValueName][:,
                                            lowLatInt:highLatInt+1,
                                            lowLonInt:highLonInt+1]*\
                                            var1ValueMult
var2Values = cdfIn.variables[var2ValueName][:,
                                            lowLatInt:highLatInt+1,
                                            lowLonInt:highLonInt+1]*\
                                            var2ValueMult


# *(We now subset the longitudes and latitudes since the previous call to getIntEdges needed the full lon/lat.)*

# In[ ]:

lonValues = lonValues[lowLonInt:highLonInt+1]
latValues = latValues[lowLatInt:highLatInt+1]


# In[ ]:

cdfIn.close()


# ## (4) Create ClickHist and ClickHistDo Instances

# ### Initialize 'ClickHistDo'

# In[ ]:

ClickHistDo1 = ClickHistDo.ClickHistDo(lonValues,latValues,
                                       timeValues,startDatetime,
                                       bundleInFilenames,
                                       bundleOutTags,
                                       caseNotebookFilename,
                                       xVarName=var1Name,
                                       yVarName=var2Name,
                                       lonOffset=lonOffset,
                                       latOffset=latOffset,
                                       dtFromCenter=dtFromCenter,
                                       imageVar=imageVar,
                                       openTab=False)


# ### Initialize 'ClickHist' and launch!

# If you want the output of CHAD to be in a separate window, make sure `%qtconsole` below is not commented. Otherwise, the text output will appear below the last cell.

# In[ ]:

#%qtconsole
ClickHist1 = ClickHist.ClickHist(var1Edges,var2Edges,
                                 var1Values,var2Values,
                                 xVarName=var1Name,yVarName=var2Name,
                                 xUnits=var1Units,yUnits=var2Units,
                                 xFmtStr=var1FmtStr,
                                 yFmtStr=var2FmtStr,
                                 maxPlottedInBin=loadmod_G5NR.maxPlottedInBin_UD,
                                 quantiles=quantiles,
                                 metadata=metadata_UD)
ClickHist1.setDo(ClickHistDo1)
ClickHist1.showPlot()


# In[ ]:



