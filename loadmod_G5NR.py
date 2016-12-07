import datetime
import numpy as np

# These values are editable but hidden here to make the notebooks cleaner

# Figure dimensions in pixels
figureXSize = 800
figureYSize = 800
figDPI = 150
# Maximum number of points plotted in each bin
# Keep this low for faster performance
maxPlottedInBin_UD = 1000

# Easy default values for each variable

# Formatting for Output
# Basic Help: The number after the decimal point sets the number of
# decimal points shown in output
# For more on Python string formatting, see:
# (https://mkaz.github.io/2012/10/10/python-string-format/)
# These are OPTIONAL inputs to ClickHist: xFmtStr=?,yFmtStr=?)
fmtStrOptions = {'Precip': "{:3.0f}", 'W500': "{:0.3f}", 'wPuP': "{:0.2f}",
                 'TEEF': "{:3.0f}", 'HMV': "{:2.0f}", 'SKEDot': "{:0.3f}"}

# These are the variable names in the loaded data files
valueNameOptions = {'Precip': 'PREC', 'W500': 'W', 'wPuP': 'WPUP',
                    'TEEF': 'TEEF', 'HMV': 'HMV', 'SKEDot': 'SKEDOT'}

binOptions = {'Precip': np.array([0., 1., 11., 21., 31., 41., 51.,
                                  61., 71., 81., 91., 101., 250.]),
              'W500': np.array([-0.5, -0.135, -0.105, -0.075, -0.045,
                                -0.015, 0.015, 0.045, 0.075, 0.105,
                                0.135, 0.165, 0.5]),
              'wPuP': np.array([-0.5, -0.18, -0.14, -0.10, -0.06, -0.02,
                                 0.02, 0.06, 0.10, 0.14, 0.18, 0.22, 0.5]),
              'TEEF': np.array([-20., 20., 60., 100., 140., 180., 220.,
                                 260., 300., 340., 380., 420., 1000.]),
              'HMV': np.array([0., 4., 8., 12., 16., 20., 24.,
                               28., 32., 36., 40., 44., 100.]),
              'SKEDot': np.array([-5., -1.10, -0.90, -0.70, -0.50,
                                   -0.30, -0.10, 0.10, 0.30, 0.50,
                                   0.70, 0.90, 5.])*1.5}

varUnitOptions = {'Precip': 'mm day-1', 'W500': 'm s-1', 'wPuP': 'm2 s-2',
                  'TEEF': 'J m kg-1 s-1', 'HMV': 'm2 s-2',
                  'SKEDot': 'W m-2'}

# If you are converting to units different from those in the input files,
# you can set a conversion factor here
varMultOptions = {'Precip': 86400., 'W500': 1., 'wPuP': 1.,
                  'TEEF': 1., 'HMV': 1., 'SKEDot': 1.}

# These values are tied to the current data files in the loaders. If you change
# the data files, you will likely have to change many of these values

lonValueName = 'lon'
latValueName = 'lat'
timeValueName = 'time'

# Note: In future versions, this may be implemented manually
# (i.e. CHAD queries the data for what units 'time' is in)
timeValueMult = 60
timeValueOffset = 0

startYear = 2005
startMonth = 5
startDay = 16
startHour = 0
startMinute = 30
startSecond = 0

startDatetime = datetime.datetime(startYear, startMonth, startDay,
                                  startHour, startMinute, startSecond)

# Functions and classes that are useful in the notebook


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


def getIntEdges(dim, low, high):
    lowInt = np.argmin(abs(dim-low))
    highInt = np.argmin(abs(dim-high))
    return lowInt, highInt

