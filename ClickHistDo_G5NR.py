import calendar
import datetime
from PIL import Image
import os
import StringIO
from subprocess import call
import sys
import time
import urllib
import webbrowser

__author__ = 'niznik'

# ClickHistDo is very much specific to the implementation of ClickHist

# In this implementation, input data and relevant axis data are used
# to create multiple .xidv files usable with IDV 
# based on a clicked scatterplot point from a ClickHist


class ClickHistDo:
    def __init__(self, lons, lats, times,
                 startDatetime, bundles, bundleTags,
                 caseNotebookFilenameTag, **kwargs):

        """
        Initializes the ClickHistDo.
        :param lons: input longitude array matching the original dimensions
        of the input x and y data along that axis
        :param lats: input latitude array matching the original dimensions
        of the input x and y data along that axis
        :param times: input time array matching the original dimensions
        of the input x and y data along that axis
        :param startDatetime: a datetime object containing the date and time
        needed to calculate the time of the event based on values within the
        times array. This is needed because netCDF files usually store time
        as some interval (seconds, minutes, hours, days) after a reference
        time. In the case of ClickHist, the user is expected to convert
        the times array to seconds for input.
        :param bundle: The name of the template bundle to be altered
        :param caseNotebookFilename: The name of the file (without .ipynb
        extension) that the user's progress will be saved to
        :param kwargs: many options - see wiki for now
        :return:
        """

        # Check if we are in Linux, OS X, or something unsupported
        self.os = sys.platform

        # Initialize the three relevant dimensions based on input from
        # ClickHist as well as the reference start time
        self.lons = lons
        self.lats = lats
        self.times = times
        self.lonLen = len(self.lons)
        self.latLen = len(self.lats)
        self.timeLen = len(self.times)
        self.startDatetime = startDatetime

        # Set default values for variable names, metadata, and
        # percentiles
        # (xVarName and yVarName can be changed by kwargs below,
        # the rest changed on an individual 'do')
        self.xVarName = 'xVar'
        self.yVarName = 'yVar'
        self.metadata = ''
        self.xPer = 99.9
        self.yPer = 99.9

        # Set default offsets for IDV bundle
        self.lonOffset = 5.0
        self.latOffset = 5.0
        self.dtFromCenter = (2*3600)*1000

        # Set name of bundle templates to alter
        # Also give tags so that the outFiles will be distinguishable
        self.bundleInFilenames = bundles
        self.bundleOutTags = bundleTags

        # Set name of the case notebook file
        self.caseNotebookFilenameTag = caseNotebookFilenameTag

        self.openTab = False
        if 'openTab' in kwargs:
            self.openTab = kwargs['openTab']

        # Set message to give after one click in ClickHist
        self.doObjectHint = 'save IDV bundle...'

        # Handle kwargs for output
        if 'xVarName' in kwargs:
            self.xVarName = kwargs['xVarName']
        if 'yVarName' in kwargs:
            self.yVarName = kwargs['yVarName']
        if 'lonOffset' in kwargs:
            self.lonOffset = kwargs['lonOffset']
        if 'latOffset' in kwargs:
            self.latOffset = kwargs['latOffset']
        if 'dtFromCenter' in kwargs:
            self.dtFromCenter = kwargs['dtFromCenter']*1000

        self.imageVar = ['storms']
        if 'imageVar' in kwargs:
            self.imageVar = kwargs['imageVar']
        if not isinstance(self.imageVar, list):
            raise TypeError('imageVar should be a list')

#This is a CLASS called a "do"
    def do(self, flatIndex, **kwargs):

        """

        :param flatIndex: Location of data in the flattened, 1D x and y data
        arrays. Combined with the lengths of each dimension (here, lon, lat,
        and time), this can be used to back out the dimensionalized data and
        thus the associated values for each dimension (i.e. the longitude,
        latitude, and time of the data point).
        :param kwargs: metadata - words to display in the output specific
        to the case, xPer,yPer - the percentiles of the x and y data, xyVals -
        a string containing the x and y data values to display to the user
        :return:
        """

        # Check if the metadata tag was included
        # Also check if the x and y percentiles were passed along
        if 'metadata' in kwargs:
            self.metadata = kwargs['metadata']
        if 'xPer' in kwargs:
            self.xPer = kwargs['xPer']
        if 'yPer' in kwargs:
            self.yPer = kwargs['yPer']

        # Make sure output folders exist
        #
        # Tmp is where some files are processed before being moved to their
        # proper locations
        # GeneratedBundles is the folder for .xidv files written by this code
        # GeneratedBundlesZ is the folder for .zidv files generated when
        # the .isl script is run
        # Scripts stores the .isl scripts that generate image, movie, and
        # .zidv output
        # Images is where the image and movies generated by the .isl script
        # are stored
        #
        # Note that GeneratedBundlesZ and Images are not necessary at runtime
        # here, but they will be needed as soon as the user runs the .isl
        # script so it's best to make them ahead of time to avoid errors
        if not os.path.exists('./Output/Tmp/'):
            call('mkdir ./Output/Tmp/', shell=True)
        if not os.path.exists('./Output/GeneratedBundles/'):
            call('mkdir ./Output/GeneratedBundles/', shell=True)
        if not os.path.exists('./Output/GeneratedBundlesZ/'):
            call('mkdir ./Output/GeneratedBundlesZ/', shell=True)
        if not os.path.exists('./Output/Scripts/'):
            call('mkdir ./Output/Scripts/', shell=True)
        if not os.path.exists('./Output/Images/'):
            call('mkdir ./Output/Images/', shell=True)

        # Notify the user that the processing has begun
        print('Saving IDV bundle(s)...')

        # Grab the current Unix/Epoch time as a placeholder tag for the
        # temporary results and create lists that can be iterated in the
        # event of more than one bundle template
        basisBundleFiles = []
        tempBundleFiles = []
        currentUnixTime = str(int(time.time()))
        for ii in range(0, len(self.bundleInFilenames)):
            basisBundleFiles.append('./Templates/' +
                                    self.bundleInFilenames[ii] + '.xidv')
            tempBundleFiles.append('./Output/Tmp/tempBundle_' +
                                   currentUnixTime+str(ii)+'.xidv')

        # Determine the longitude, latitude, and time of the point passed
        # to Do
        inputLonIndex, inputLatIndex, inputTimeIndex = \
            self.find3DIndices(flatIndex)
        inputLon = self.lons[inputLonIndex]
        inputLat = self.lats[inputLatIndex]
        
# debug a time error (it was in the dataset, not the code)
#        print 'self.startDatetime', self.startDatetime 
#        print 'self.times[inputTimeIndex]', self.times[inputTimeIndex]
#        print 'datetime.timedelta(0, (self.times[inputTimeIndex]))', \
#        datetime.timedelta(0, (self.times[inputTimeIndex]))

        inputDatetime = (self.startDatetime +
                         datetime.timedelta(0, (self.times[inputTimeIndex])))
        inputTime = int(calendar.timegm(inputDatetime.timetuple()))

        # Inform the user of the time and location of the point
        # And if passed, the values of X and Y as well
        timeString = str(inputDatetime)
        locationString = ("{:3.0f}".format(inputLon)+' E ' +
                          "{:2.0f}".format(inputLat)+' N')
        xyValString = ''
        if 'xyVals' in kwargs:
            xyValString = kwargs['xyVals']
        perString = ''
        if ('xPer' in kwargs) and ('yPer' in kwargs):
            perString = ('x%: '+"{:2.3f}".format(kwargs['xPer'])+' ' +
                         'y%: '+"{:2.3f}".format(kwargs['yPer']))

        print(inputDatetime)
        print("{:3.0f}".format(inputLon)+' E '+"{:2.0f}".format(inputLat)+' N')
        if 'xyVals' in kwargs:
            print(kwargs['xyVals'])
        if ('xPer' in kwargs) and ('yPer' in kwargs):
            print('x%: '+"{:2.3f}".format(kwargs['xPer'])+' ' +
                  'y%: '+"{:2.3f}".format(kwargs['yPer']))

        urlSave = []
        for ii in range(0, len(self.imageVar)):

            url = ('http://g5nr.nccs.nasa.gov/static/naturerun/fimages/' +
                   self.imageVar[ii].upper() +
                   '/Y'+"{:4d}".format(inputDatetime.year) +
                   '/M'+"{:02d}".format(inputDatetime.month) +
                   '/D'+"{:02d}".format(inputDatetime.day) +
                   '/'+self.imageVar[ii]+'_globe_c1440_NR_BETA9-SNAP_' +
                   "{:4d}".format(inputDatetime.year) +
                   "{:02d}".format(inputDatetime.month) +
                   "{:02d}".format(inputDatetime.day) +
                   '_'+"{:02d}".format(inputDatetime.hour) +
                   "{:02d}".format(inputDatetime.minute) +
                   'z.png')
            urlSave.append(url)

            print('\nLink to '+self.imageVar[ii]+' image: '+url)
            if self.openTab is True:
                webbrowser.open(url, new=1)
        print('')

        # Based on the lon, lat, and time, determine all necessary input
        # to create an .xidv bundle
        # First, the edges of the display window
        westLon = str(inputLon-self.lonOffset)
        eastLon = str(inputLon+self.lonOffset)
        southLat = str(inputLat-self.latOffset)
        northLat = str(inputLat+self.latOffset)

        # Next, the start and end time for the time looping
        adjTime = int(inputTime)*1000
        startTime = str(long(adjTime-self.dtFromCenter))
        endTime = str(long(adjTime+self.dtFromCenter))
        # IDV wants these in minutes (hence dividing by 60*1000 to convert
        # out of milliseconds)
        startOffset = str(0)
        endOffset = str((self.dtFromCenter*2)/(60*1000))

        # Determine the filename based on the quantiles of the scatterplot parameters 
        timeTag = self.convertToYMDT(inputTime)
        
# Old and hard to read: 
# example    Precip_SKEDot_96667_01111_208_-20_20070605_0630
#        commonFilename = (self.xVarName+'_'+self.yVarName+'_' +
#                          "{:005.0f}".format(min(1000*self.xPer, 99999))+'_' +
#                          "{:005.0f}".format(min(1000*self.yPer, 99999))+'_' +
#                          str("%03i"%inputLon)+'_'+str("%02i"%inputLat)+'_' +
#                          timeTag)
#Newer, BEM likes better. Hope sign is allowed for Lat and Lon
        commonFilename = (self.xVarName+'_quantile_'+
                          "{:005.3f}".format(min(self.xPer, 99.999))+'_' +
                          self.yVarName+'_quantile_'+
                          "{:005.3f}".format(min(self.yPer, 99.999))+'_' +
                          'lat_'+str("%02i"%inputLat)+'_' +
                          'lon_'+str("%03i"%inputLon)+'_' +
                          'time_'+timeTag)

        # The flag for dealing with backup in OS X and Linux is different but -i.bckp works for both
        # Set it here based on the OS that was determined upon initialization
        backupTag = '-i.bckp'
        if self.os.startswith('darwin'):
            backupTag = '-i.bckp'
        elif self.os.startswith('linux'):
            backupTag = '-i.bckp'
        else:
            print('Unsupported OS detected')
            print('Functionality might not work as intended...')

        # Preset longitude dummy values in the .xidv template to be
        # replaced by the values calculated above
        centerLonFiller = '-154.123456789'
        lonLenFiller = '2.123456789'
        minLonFiller = '-155.1851851835'
        maxLonFiller = '-153.0617283945'
        incLonFiller = '0.345678912'

        # Same, but latitude
        centerLatFiller = '0.135792468'
        latLenFiller = '1.592592592'
        minLatFiller = '-0.660503828'
        maxLatFiller = '0.932088764'
        incLatFiller = '0.234567891'

        # Same, but time and metadata
        startTimeFiller = '1117594837000'
        endTimeFiller = '1117616461000'
        startOffsetFiller = '-119.87654321'
        endOffsetFiller = '361.23456789'
        metadataFiller = 'replaceme_METADATASTRING_replaceme'

# Section for modifying .xidv template bundles:         
        # change finalBundleFile to a list of filenames and loop over them
        finalBundles = []
        for ii in range(0, len(basisBundleFiles)):

            finalBundleFile = ('./Output/GeneratedBundles/' +
                               commonFilename+'_' +
                               self.bundleOutTags[ii]+'.xidv')
            finalBundles.append('../GeneratedBundles/' +
                                commonFilename+'_' +
                                self.bundleOutTags[ii]+'.xidv')

            # Each call to sed here replaces one of the dummy lon/lat/time
            # values with the values appropriate to the passed data point
            call('sed \'s/'+minLonFiller+'/'+westLon+'/\' ' +
                 basisBundleFiles[ii] + ' > '+tempBundleFiles[ii],
                 shell=True)
            call('sed '+backupTag+' \'s/'+maxLonFiller+'/'+eastLon+'/\' ' +
                 tempBundleFiles[ii], shell=True)
            call('sed '+backupTag+' \'s/'+minLatFiller+'/'+southLat+'/\' ' +
                 tempBundleFiles[ii], shell=True)
            call('sed '+backupTag+' \'s/'+maxLatFiller+'/'+northLat+'/\' ' +
                 tempBundleFiles[ii], shell=True)
            call('sed '+backupTag+' \'s/'+centerLonFiller+'/'+str(inputLon) +
                 '/\' '+tempBundleFiles[ii], shell=True)
            call('sed '+backupTag+' \'s/'+centerLatFiller+'/'+str(inputLat) +
                 '/\' '+tempBundleFiles[ii], shell=True)
            call('sed '+backupTag+' \'s/'+lonLenFiller+'/' +
                 str(self.lonOffset*2) + '/\' '+tempBundleFiles[ii],
                 shell=True)
            call('sed '+backupTag+' \'s/'+latLenFiller+'/' +
                 str(self.latOffset*2) + '/\' '+tempBundleFiles[ii],
                 shell=True)
            call('sed '+backupTag+' \'s/'+incLonFiller+'/' +
                 str(self.lonOffset/2.) + '/\' '+tempBundleFiles[ii],
                 shell=True)
            call('sed '+backupTag+' \'s/'+incLatFiller+'/' +
                 str(self.latOffset/2.) + '/\' '+tempBundleFiles[ii],
                 shell=True)
            call('sed '+backupTag+' \'s/'+startTimeFiller+'/'+startTime +
                 '/\' ' + tempBundleFiles[ii], shell=True)
            call('sed '+backupTag+' \'s/'+endTimeFiller+'/'+endTime+'/\' ' +
                 tempBundleFiles[ii], shell=True)
            call('sed '+backupTag+' \'s/'+startOffsetFiller+'/'+startOffset +
                 '/\' '+tempBundleFiles[ii], shell=True)
            call('sed '+backupTag+' \'s/'+endOffsetFiller+'/'+endOffset +
                 '/\' ' + tempBundleFiles[ii], shell=True)
            call('sed '+backupTag+' \'s/'+metadataFiller+'/'+self.metadata +
                 '/\' ' + tempBundleFiles[ii], shell=True)
                            
            # Save the bundle with a recognizable filename
            call('mv '+tempBundleFiles[ii]+' '+finalBundleFile, shell=True)
            call('rm '+tempBundleFiles[ii]+'.bckp', shell=True)

            # Inform the user of success
            print('Bundle \''+self.bundleOutTags[ii]+'\' Saved!')

        print('')
        
# End section for modifying .xidv bundles, now modify .isl template

        # Now create the ISL file - a bit less involved
        basisISL = './Templates/idvMovieOutput_fillIn.isl'
        tempISL = './Output/Scripts/idvImZIDVOutput_'+commonFilename+'.isl'

        # Process a few replacements via sed

        call('sed \'s/BUNDLENAME/'+commonFilename+'_'+self.bundleOutTags[0] +
             '/\' '+basisISL+' > '+tempISL, shell=True)
        call('sed '+backupTag+' \'s/MOVIENAME/'+commonFilename+'/\' ' +
             tempISL, shell=True)
        call('sed '+backupTag+' \'s/IMAGENAME/'+commonFilename+'/\' ' +
             tempISL, shell=True)
        call('sed '+backupTag+' \'s/\"METADATA\"/\"'+self.metadata+'\"/\' ' +
             tempISL, shell=True)

        # Clean up backup files
        call('rm '+tempISL+'.bckp', shell=True)

# End section for modifying .isl scripts


#The section to actually write the JSON of the .ipynb notebook
        # Create a Case Notebook!
        caseNotebookFilename = (self.caseNotebookFilenameTag + '_' +
                                commonFilename+'.ipynb')
        print('Creating Case Notebook ('+caseNotebookFilename +
              ')')
 
        if not os.path.exists('./Output/CaseNotebooks/'):
            call('mkdir ./Output/CaseNotebooks', shell=True)

        if(os.path.isfile('./Output/CaseNotebooks/' +
                          caseNotebookFilename) == True):
            print('Notebook previously created - returning...')
            return
        
        #Copy the template (it must exist already)
        print('Copy the template')

        call('cp ./Templates/caseNotebookTemplate.ipynb ' +
             './Output/CaseNotebooks/'+caseNotebookFilename, shell=True)

    # Now insert case specific information into the template 
        pathToCaseNB = './Output/CaseNotebooks/'+caseNotebookFilename

        date = str(datetime.datetime.now().replace(second=0,
                                                   microsecond=0))
        # Creation date
        call('sed '+backupTag+' \'s/INSERT_DATE/'+date+'/\' ' +
             pathToCaseNB, shell=True)
        call('rm '+pathToCaseNB+'.bckp', shell=True)

    # Grab a copy of the .ipynb as a string list called lines. 
    # Code will change that, then write it out. 
        inFile = open('./Output/CaseNotebooks/' +
                      caseNotebookFilename, 'r')
        lines = inFile.readlines()
        inFile.close()

        # Add case metadata under the line containing the string called Quick Stats
        insertIndexMeta = -1
        for ll in range(0, len(lines)-1):
            if 'Quick Stats' in lines[ll]:
                insertIndexMeta = ll

        lines[insertIndexMeta] += ','
        lines.insert(insertIndexMeta+1, '    \"'+timeString+'<br>\",\n')
        lines.insert(insertIndexMeta+2, '    \"'+locationString+'<br>\",\n')
        lines.insert(insertIndexMeta+3, '    \"'+xyValString+'<br>\",\n')
        lines.insert(insertIndexMeta+4, '    \"'+perString+'<br>\"\n')
       
        #define where to add new image cells 
        insertImageCells = insertIndexMeta+7 # After the close of metadata cell above
        
        
        # The next thing I want at the top is the quicklook imagery. This involves adding new cells.
        if True:   # BEM is too lazy to reindent this block so make it a if True:
            linesToAdd = []

            
            # First image is the scatterplot with highlighted point that defines the case
            # Copy it into the Images folder so it is not lost after it is overwritten
            call('cp ./Output/Tmp/mostRecentCH.png ./Output/Images/' +
                 commonFilename+'_CH.png', shell=True)

            # Open a new notebook cell of type Markdown and put the name there
            self.appendCellStart(linesToAdd, 'markdown')
            linesToAdd.append('    \"**Common Filename:** `' +
                              commonFilename+'`\",\n')
            # Appending the actual image, instead of a command to fetch it, involves ![]
            linesToAdd.append('    \"![](../Images/' + commonFilename +
                              '_CH.png)\"\n')
            self.appendCellEnd(linesToAdd, False)
            
            
            # Open new notebook cells with the RESULTS of Image() calls in them
            print 'Adding quicklook images to the notebook'        
            print 'Now looping over ', self.imageVar, '...'
            
            for ii in range(0, len(self.imageVar)):
                print ' trying ', self.imageVar[ii], '...'
                # Load an image, or use a broken link image of the same size
                imageLoaded = 1
                try:
                    imgFile = StringIO.StringIO(urllib.urlopen(urlSave[ii]).read())
                    imgIn = Image.open(imgFile)
                except IOError:
                    print('Couldn\'t open the G5NR image...is the server down?')
                    imgIn = Image.open('BrokenLinkImage.png')
                    print('(Using Broken Link Image)')
                    # imageLoaded = 0, I changed this to use a dummy image instead of no image

                imgInWidth = imgIn.size[0]
                imgInHeight = imgIn.size[1]

                #Crop the image, very specific to G5NR images on the web site
                if imageLoaded == 1:
                    outImageWidthHalf = int(imgInWidth*(30./360.))
                    outImageHeightHalf = int(imgInHeight*(15./180.))

                    # NASA images start at 17.5 W, not 0 E so we need to account
                    # for that. Pulled out the numerator to make things clearer.
                    lonOffset = 17.5
                    numForCentX = (inputLon+lonOffset) % 360

                    cropCentX = int((numForCentX/360.)*imgInWidth)
                    cropCentY = int((-1.*(inputLat-90.)/180.)*imgInHeight)
                    centToEdgeX = outImageWidthHalf
                    centToEdgeY = outImageHeightHalf

                    imgToSave = Image.new("RGB", (outImageWidthHalf*2,
                                                  outImageHeightHalf*2))

                    leftEdge = cropCentX-centToEdgeX
                    rightEdge = cropCentX+centToEdgeX
                    upperEdge = cropCentY-centToEdgeY
                    lowerEdge = cropCentY+centToEdgeY

                    boxHeightOffset = 0

                    if lowerEdge >= imgInHeight:
                        boxHeightOffset = lowerEdge - imgInHeight
                        lowerEdge = imgInHeight-1
                        upperEdge = lowerEdge-centToEdgeY*2
                    elif upperEdge < 0:
                        boxHeightOffset = upperEdge
                        upperEdge = 0
                        lowerEdge = upperEdge+centToEdgeY*2

                    imgCrop1, imgCrop2 = None, None

                    if leftEdge < 0:
                        imgCrop1 = imgIn.crop((leftEdge+imgInWidth,
                                               upperEdge,
                                               imgInWidth-1,
                                               lowerEdge))
                        imgCrop2 = imgIn.crop((0,
                                               upperEdge,
                                               rightEdge,
                                               lowerEdge))
                    elif rightEdge >= imgInWidth:
                        imgCrop1 = imgIn.crop((leftEdge,
                                               upperEdge,
                                               imgInWidth-1,
                                               lowerEdge))
                        imgCrop2 = imgIn.crop((0,
                                               upperEdge,
                                               rightEdge-imgInWidth,
                                               lowerEdge))
                    else:
                        imgCrop1 = imgIn.crop((leftEdge,
                                               upperEdge,
                                               rightEdge,
                                               lowerEdge))

                    imgToSave.paste(imgCrop1, (0, 0))
                    if imgCrop2 is not None:
                        imgToSave.paste(imgCrop2, (imgCrop1.size[0], 0))

                    pix = imgToSave.load()

                    saveCenterW = imgToSave.size[0]/2
                    saveCenterH = imgToSave.size[1]/2
                    sqRad = 5

                    for x in range(saveCenterW-sqRad, saveCenterW+sqRad+1, 1):
                        for y in range(saveCenterH+boxHeightOffset-sqRad,
                                       saveCenterH+boxHeightOffset+sqRad+1, 1):
                            pix[x, y] = (255, 0, 0)

                    # output cropped image
                    saveFilename = (commonFilename + '_' + self.imageVar[ii] +
                                    '.png')
                    imgToSave.save('./Output/Images/' + saveFilename)

                    
                    # Now put the cropped image in a markdown cell. If it's not the last, need a comma
                    if ii < len(self.imageVar)-1:
                        print 'appending '+str(ii)
                        self.appendCellStart(linesToAdd, 'markdown')
                        linesToAdd.append('    \"![](../Images/' +
                                      saveFilename+')\",\n')
                    
                    #If this was the last image to add, no comma and close (False <- not final cell)
                    else: 
                        print 'appending '+str(ii)+' and adding URL'
                        linesToAdd.append('    \"![](../Images/' +
                                      saveFilename+')\"\n')
                        self.appendCellEnd(linesToAdd, False)

                #endif ImageLoaded
            #endfor loop over all images wanted
#        except: 
#            print 'Problem with the quicklook images!'

            # Now insert this block of linesToAdd[] containing the image cells into lines[]
            for ll in range(0, len(linesToAdd)):
                lines.insert(insertImageCells+ll, linesToAdd[ll])

            
    # Next part of the notebook is the IDV commands with the filename prepopulated
            
        # Add the load calls for all generated bundles, find the right cell 
        insertIndexLoad = -1
        for ll in range(0, len(lines)-1):
            if 'loadBundle()' in lines[ll]:
                insertIndexLoad = ll

        lines[insertIndexLoad] = ('    \"#loadBundle(\''+finalBundles[0] +
                                  '\')\\n\",\n')
        for bb in range(1, len(finalBundles)):
            lines.insert(insertIndexLoad+bb, '    \"#loadBundle(\'' +
                         finalBundles[bb]+'\')\\n\"')
            if bb != len(finalBundles)-1:
                lines[insertIndexLoad+bb] += ','
            lines[insertIndexLoad+bb] += '\n'

        # Stub to add something at the very end of the Case Notebook if desired
        #insertIndexEnd = -1
        #for ll in range(0, len(lines)-1):
        #    if lines[ll] == ' ],\n' and lines[ll+1] == ' \"metadata\": {\n':
        #        insertIndexEnd = ll



    # WRITE THE NOTEBOOK
            outFile = open('./Output/Tmp/'+caseNotebookFilename, 'w')
            outFile.writelines(lines)
            outFile.close()
            call('mv ./Output/Tmp/'+caseNotebookFilename +
                 ' ./Output/CaseNotebooks/'+caseNotebookFilename, shell=True)

        print('Case Notebook created!')

        return

    
    def convertToYMDT(self, unixTime):
        """
        Converts a Unix/Epoch time given in seconds to a YMDT string for
        file outputs
        :param unixTime: A Unix/Epoch time, in units of seconds
        :return: a YMDT string (e.g. Jan 1, 2001 at 12:35 becomes
        20010101_1235)
        """
        ymdt = datetime.datetime.utcfromtimestamp(unixTime)
        return str(ymdt.year)+"{:02.0f}".format(ymdt.month) +\
               "{:02.0f}".format(ymdt.day)+'_' +\
               "{:02.0f}".format(ymdt.hour)+"{:02.0f}".format(ymdt.minute)

    def find3DIndices(self, flatIndex):
        """
        Finds the index of the appropriate latitude, longitude, and time
        based on the 1D index for the flattened data. This is accomplished
        by the input data following the assumed order (when flattened, loop
        through all longitudes, then all longitudes for the next latitude, etc.
        until both all latitudes and longitudes have been seen for a time, then
        next time, etc.)
        :param flatIndex: The 1D index of the x and y data in the flattened
        arrays
        :return: (1) the index of the longitude, (2) the index of the latitude,
        (3) the index of the time
        """
        lonIndex = flatIndex%self.lonLen
        latIndex = (flatIndex/self.lonLen)%self.latLen
        timeIndex = flatIndex/(self.lonLen*self.latLen)
        return lonIndex, latIndex, timeIndex

    def appendCellStart(self, lineList, cellType):

        lineList.append('  {\n',)
        lineList.append('   \"cell_type\": \"'+cellType+'\",\n')
        lineList.append('   \"metadata\": {},\n')
        lineList.append('   \"source\": [\n')

    def appendCellEnd(self, lineList, lastCell):

        lineList.append('   ]\n')

        if lastCell is False:
            lineList.append('  },\n')
        else:
            lineList.append('  }\n')

