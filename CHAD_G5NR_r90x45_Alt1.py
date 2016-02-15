
# coding: utf-8

# # Clickable Histogram of Atmospheric Data (CHAD)
# ## for GEOS-5 Nature Run, 4-degree coarse grained stats

# ## Operating procedure: 
# >1. Select region and variables, and name your Journals accordingly
# >2. Select template bundle size and complexity
# >2. Set up scatterplot size 
# >3. Click on scatterplot. Details of the nearest point is shown in console. 
# >4. Second click on that point will create a Journal page with browse imagery, and also an IDV bundle centered on the region of your datapoint. 
# >5. Journal page (in Outputs/...) is itself a PyIDV notebook to capture views and commentary from the IDV bundle, whose name matches and is pre-entered in the Journal page's openBundle command. Select it from your Jupyter "Home" browser tab and you are rolling. 
# >6. If the .xidv loading time is too long for your taste, a .isl file with the same name has also been created. Launching it will create an IDV process offline (without a GUI) to fetch and render the data and create a .zidv bundle, image, and movie. 

# ### 1. Select region and variables, and name your Case Notebook accordingly

# In[ ]:

caseNotebookFilename = 'G5NR_Florida_W500_ZSKEDot_4deg_hourly'

# Regions to be loaded from the file, All must be defined
# lon in degE (0 to 360), lat in degN (-90 to 90)

lonLow = 360.-88.
lonHigh = 360.-80.
latLow = 24.0
latHigh = 32.0

# Coarse grid variables characterizing 4deg regions of the Nature Run
# Options: Precip, W500, wPuP, TEEF = Total Eddy Enthalpy Flux, 
# ZSKEDot = Zonal shear kinetic energy tendency due to eddy momentum flux, 
# HMV = 

var1Name = 'W500'
var2Name = 'ZSKEDot'

# Read the file
# This is the pathname for the coarse-grid data to scatterplot. 
# --- 1 hourly data ---
# urlToLoad = ('https://weather.rsmas.miami.edu/repository/'+
#            'opendap/synth:eab82de2-d682-4dc0-ba8b-2fac7746d269:'+
#            'L2FsbFZhcnNfcjkweDQ1XzEubmM0/entry.das')
# ---  3 hourly data ---
#urlToLoad = ('https://weather.rsmas.miami.edu/repository/'+
#             'opendap/synth:eab82de2-d682-4dc0-ba8b-2fac7746d269:'+
#             'L2FsbFZhcnNfcjkweDQ1XzMubmM0/entry.das')
# --- 6 hourly data ---
urlToLoad = ('https://weather.rsmas.miami.edu/repository/'+
             'opendap/synth:eab82de2-d682-4dc0-ba8b-2fac7746d269:'+
             'L2FsbFZhcnNfcjkweDQ1XzYubmM0/entry.das')

# datetime for setting the first data point's time
# More accurately, the starting point for counting
# for the time variable later on. This might be different
# from the time of the first data if timeValues[0] is not 0.
import datetime
startYear = 2005
startMonth = 5
startDay = 16
startHour = 0
startMinute = 30
startSecond = 0
startDatetime = datetime.datetime(startYear,startMonth,startDay,
                                  startHour,startMinute,startSecond)


# ### 3. Choose template bundle: simple, or more complex? How large, how long? 

# In[ ]:

# Name of bundle template - assumed to be in Outputs/templates
bundleInFilename = 'ClickHist_NewAggG5NRtemplate_smallarea.xidv'
#bundleInFilename = 'testSimple.xidv'

# Setting parameters for window size and time span of IDV bundle
lonOffset=1.0
latOffset=1.0
dtFromCenter=3*3600


# ### 3. Setup scatterplot window of desired size

# In[ ]:

# Scatterplot Size and Resolution
# Set the figure x by y resolution, DPI, and the max number of points
# to appear in a given bin
# (Plotting time as well as finding an individual event prohibitive
# for very large maxPlottedInBin values)
# (These are OPTIONAL inputs to ClickHist: figX=?, figY=?,
# figDPI=?, maxPlottedInBin=?)
figureXSize = 800
figureYSize = 800
figDPI = 150
maxPlottedInBin_UD = 1000

fmtStrOptions = {'Precip':"{:3.0f}", 'W500':"{:0.3f}", 'wPuP':"{:0.2f}",
                 'TEEF':"{:3.0f}", 'HMV':"{:2.0f}", 'ZSKEDot':"{:0.3f}"}

valueNameOptions = {'Precip': 'PREC','W500': 'W','wPuP': 'WPUP',
                    'TEEF': 'TEEF','HMV': 'HMV','ZSKEDot': 'ZSKEDOT'}

varUnitOptions = {'Precip': 'mm day-1','W500': 'm s-1','wPuP': 'm2 s-2',
                  'TEEF': 'J m kg-1 s-1','HMV': 'm2 s-2',
                  'ZSKEDot': 'm2 s-3 (x 10^-3)'}

varMultOptions = {'Precip': 86400.,'W500': 1.,'wPuP': 1.,
                  'TEEF': 1.,'HMV': 1.,'ZSKEDot': 1000.}

import numpy as np
binOptions = {'Precip': np.array([0.,1.,11.,21.,31.,41.,51.,
                                  61.,71.,81.,91.,101.,250.]),
              'W500': np.array([-0.5,-0.135,-0.105,-0.075,-0.045,-0.015,
                                 0.015,0.045,0.075,0.105,0.135,0.165,0.5]),
              'wPuP': np.array([-0.5,-0.18,-0.14,-0.10,-0.06,-0.02,
                                 0.02,0.06,0.10,0.14,0.18,0.22,0.5]),
              'TEEF': np.array([-20.,20.,60.,100.,140.,180.,220.,
                                 260.,300.,340.,380.,420.,1000.]),
              'HMV': np.array([0.,4.,8.,12.,16.,20.,24.,
                               28.,32.,36.,40.,44.,100.]),
              'ZSKEDot': np.array([-5.,-1.10,-0.90,-0.70,-0.50,-0.30,-0.10,
                                  0.10,0.30,0.50,0.70,0.90,5.])*1.5}

# Set Bin Edges
var1Edges = binOptions[var1Name]
var2Edges = binOptions[var2Name]

# Formatting for Output
# Basic Help: The number after the decimal point sets the number of
# decimal points shown in output
# For more on Python string formatting, see:
# (https://mkaz.github.io/2012/10/10/python-string-format/)
# These are OPTIONAL inputs to ClickHist: xFmtStr=?,yFmtStr=?)
var1FmtStr = fmtStrOptions[var1Name]
var2FmtStr = fmtStrOptions[var2Name]

# Variable names in input file(s) for values
var1ValueName = valueNameOptions[var1Name]
var2ValueName = valueNameOptions[var2Name]

var1Units = varUnitOptions[var1Name]
var2Units = varUnitOptions[var2Name]
metadata_UD = (var1Name+' vs '+var2Name+': '+
               str(lonLow)+' to '+str(lonHigh)+' E, '+
               str(latLow)+' to '+str(latHigh)+' N')

# Unit correction options
# If the units in the input file are not what is desired,
# they can be corrected during the load with these multipliers.
var1ValueMult = varMultOptions[var1Name]
var2ValueMult = varMultOptions[var2Name]


# #### A bunch of magics and imports necessary for the plot to come up

# In[ ]:

# Setting the GUI 
# ClickHist is currently optimized for tk
# For more options see section "%matplotlib" at
# https://ipython.org/ipython-doc/3/interactive/magics.html

# matplotlib for graphics, set tk too
# %matplotlib osx is experimental
get_ipython().magic(u'matplotlib tk')
#%matplotlib osx
import matplotlib

# (Note: for debugging, replace '%' command with
# matplotlib.use)
#matplotlib.use('TkAgg')

# Modules for fixing the buffer in cell 3 
from IPython.display import clear_output
import sys

# numpy to create the sample input arrays
import numpy as np

# And obviously import ClickHist and ClickHistDo!
import ClickHist_G5NR as ClickHist
import ClickHistDo_G5NR as ClickHistDo

# User-specified imports
# netCDF4 to load the netCDF input file
import netCDF4


# gory details

# In[ ]:

# Fixing the output so it isn't buffered
# See: http://stackoverflow.com/questions/29772158/make-ipython-notebook-print-in-real-time

oldsysstdout = sys.stdout
class flushfile():
    def __init__(self, f):
        self.f = f
    def __getattr__(self,name): 
        return object.__getattribute__(self.f, name)
    def write(self, x):
        self.f.write(x)
        self.f.flush()
    def flush(self):
        self.f.flush()
sys.stdout = flushfile(sys.stdout)

def getIntEdges(dim,low,high):
    lowInt = np.argmin(abs(dim-low))
    highInt = np.argmin(abs(dim-high))
    return lowInt,highInt


# ### Grabs the coarse data and subsets it. No edits needed, just execute. 

# In[ ]:

# Load the datafile
cdfIn = netCDF4.Dataset(urlToLoad,'r')

# Get the lat, lon, time data. 

lonValues = cdfIn.variables['lon'][:]
latValues = cdfIn.variables['lat'][:]
timeValues = cdfIn.variables['time'][:]

# Set time offset & multiplier if time variable is not in desired units
timeValueMult = 60
timeValueOffset = 0
timeValues = timeValues*timeValueMult + timeValueOffset

# Based on the lat-lon range selected, subset the values 
lowLonInt,highLonInt = getIntEdges(lonValues,lonLow,lonHigh)
lowLatInt,highLatInt = getIntEdges(latValues,latLow,latHigh)

# Bin Edge and Value Data
# Later call to create ClickHist uses the below variable names
# You should probably leave the names alone
#
# N.B. that CHAD expects the data to be in the Python format
# variable[times,latitudes,longitudes]. If this is not the default,
# you will have to permute the data here (or ideally process it to)
# match before loading - permutation could potentially take some
# time.
#
#var1Edges = cdfIn.variables[var1EdgeName][:]
#var2Edges = cdfIn.variables[var2EdgeName][:]
var1Values = cdfIn.variables[var1ValueName][:,
                                            lowLatInt:highLatInt+1,
                                            lowLonInt:highLonInt+1]*\
                                            var1ValueMult
var2Values = cdfIn.variables[var2ValueName][:,
                                            lowLatInt:highLatInt+1,
                                            lowLonInt:highLonInt+1]*\
                                            var2ValueMult

lonValues = lonValues[lowLonInt:highLonInt+1]
latValues = latValues[lowLatInt:highLatInt+1]

cdfIn.close()


# ### This one actually launches the scatter plot.

# In[ ]:

# Create ClickHist using a proper call

# This call is necessary to create the output console for ClickHist
# (Note: for debugging, comment out '%' command)
get_ipython().magic(u'qtconsole')

# Create a ClickHistDo instance
ClickHistDo1 = ClickHistDo.ClickHistDo(lonValues,latValues,
                                       timeValues,startDatetime,
                                       bundleInFilename,
                                       caseNotebookFilename,
                                       xVarName=var1Name,
                                       yVarName=var2Name,
                                       lonOffset=lonOffset,
                                       latOffset=latOffset,
                                       dtFromCenter=dtFromCenter,
                                       openTab=True)
# Create a ClickHist instance
ClickHist1 = ClickHist.ClickHist(var1Edges,var2Edges,
                                 var1Values,var2Values,
                                 xVarName=var1Name,yVarName=var2Name,
                                 xUnits=var1Units,yUnits=var2Units,
                                 xFmtStr=var1FmtStr,
                                 yFmtStr=var2FmtStr,
                                 maxPlottedInBin=maxPlottedInBin_UD,
                                 metadata=metadata_UD)

# Set ClickHistDo1 to be the official "action" for ClickHist
ClickHist1.setDo(ClickHistDo1)

# Show the ClickHist
ClickHist1.showPlot()


# # User: now click away!
# >3. Click on scatterplot. Details of the nearest point is shown in console. 
# >4. Second click on that point will create a Journal page with browse imagery, and also an IDV bundle centered on the region of your datapoint. 
# >5. Case Notebook page (in Outputs/CaseNotebooks/) is itself a PyIDV notebook to capture views and commentary from the IDV bundle, whose name matches and is pre-entered in the Journal page's openBundle command. Select it from your Jupyter "Home" browser tab and you are rolling. 
# >6. If the .xidv loading time is too long for your taste, a .isl file with the same name has also been created. Launching it will create an IDV process offline (without a GUI) to fetch and render the data and create a .zidv bundle, image, and movie. 

# Author: [Matthew Niznik](http://matthewniznik.com) ([matt@matthewniznik.com](mailto:matt@matthewniznik.com))<br>
# Post-Doctoral Associate, RSMAS, University of Miami
# 
# For more information, see:<br>
# https://github.com/matthewniznik/ClickHist/wiki<br>
# http://matthewniznik.com/research-projects/clickhist<br>

# In[ ]:



