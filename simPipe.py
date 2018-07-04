#!/usr/bin/python
# -*- coding: UTF-8 -*-
#For create simulate files auto
#For parameter dm, flux, period
#Width is always too big. Input will be smaller than 3-5 times
#use a database to record the progress
#module take care of the module that ubc_AI needed

import math, sqlite3, optimus
import time
import cPickle, glob, ubc_AI, os
import numpy as np
from commands import getoutput
from ubc_AI.data import pfdreader


#----------------------------------------------
#operate database
def writedatabase(database, name, dm, period, width, flux, detection, taskid):
    name = "'"+name+"'"
    sql = " insert into simFiles (name, dm, period, width, flux, detection, taskid) values (%s, %s, %s, %s, %s, %s, %s)" %(name, dm, period, width, flux, detection, taskid)
    database.cursor().execute(sql)
    database.commit()


#----------------------------------------------
#func to simulate files
def simulate(DM,Flux,Period, fastFileName, randomNum, fitsFilePath, simBinarydataPath, simdataPath):
    #set the and write the parameter files
    fastparamName = 'FAST.params'
    psrparamName = str('test_DM_%s_Flux_%s_P0_%s.params' %(DM, Flux, Period))
    psrdatName = str('test_DM_%s_Flux_%s_P0_%s.dat' %(DM, Flux, Period))
    psrfitsName = str('test_DM_%s_Flux_%s_P0_%s.fits' %(DM, Flux, Period))
    
    #get width, had been checked to the right value of width
    width = optimus.pulseWidth(Period,meanFreq,randomNum)
    
    #write telescope pulsar params
    optimus.writeParamFile(fastparamName,optimus.telescope())
    optimus.writeParamFile(psrparamName, optimus.pulsar(dm = str(DM), flux = str(Flux), period = str(Period), width = width))
    
    #simulate pulsar signal
    SimulatePsrData = str('simulateSimplePsr_mcc -p FAST.params -p %s -o %s' %(psrparamName,psrdatName))
    print SimulatePsrData
    output=getoutput(SimulatePsrData)
    
    #combine files 
    #python ~/psrsoft/OPTIMUS/python/fitsio_combinePolBinary.py fitsfile binaryfile outputfile
    SimulatePsrData = str('python ~/psrsoft/OPTIMUS/python/fitsio_combinePolBinary.py %s/%s %s/%s %s/%s' %(fitsFilePath, fastFileName, simBinarydataPath, psrdatName, simdataPath, psrfitsName))
    print SimulatePsrData
    output = getoutput(SimulatePsrData)

    return psrfitsName


#----------------------------------------------
#return the result of AI select
def confirmCandidate(pfdFile):
    AI_PATH = '/'.join(ubc_AI.__file__.split('/')[:-1])
    #classifier = cPickle.load(open(AI_PATH+'/trained_AI/clfl2_HTRU.pkl','rb'))
    #classifier = cPickle.load(open('../clfl2_PALFA_1.pkl','rb'))
    classifier = cPickle.load(open(AI_PATH+'/trained_AI/clfl2_PALFA.pkl','rb'))
    #classifier = cPickle.load(open(AI_PATH+'/trained_AI/clfl2_BD.pkl','rb'))
    #classifier = cPickle.load(open(AI_PATH+'/trained_AI/clfl2_ResNet.pkl','rb'))
    tmp = []; 
    tmp.append(pfdFile) 
    AI_scores = classifier.report_score([pfdreader(f) for f in tmp])
    
    text = '\n'.join(['%s %s' % (tmp[i], AI_scores[i]) for i in range(len(tmp))])
    return text


#----------------------------------------------
#set work dir
def setworkpath(simpath):
    simBinarydataPath = simpath+'/simBinarydata'
    fitsFilePath = simpath+'/fastdata'
    simdataPath = simpath+'/simdata'
    foldResult = simpath+'/result'
    os.chdir(fitsFilePath)
    fastFile=glob.glob("*.fits")
    os.chdir(simpath)
    return fastFile, fitsFilePath, simBinarydataPath, simdataPath, foldResult


#----------------------------------------------
#cut and fold the file

def foldfile(filename, simdataPath, foldpath, dm, period):
    cutfilename = filename[:-5]+'_cut'+filename[-5:]
    #cut file 
    if dm <1000:
        cutfile = str('python ~/psrsoft/OPTIMUS/python/fitsio_cutfreq.py %s/%s %s %s %s/%s' %(simdataPath, filename, 300, 800, foldpath, cutfilename))
        print cutfile
        output = getoutput(cutfile)
    elif dm <3000:
        cutfile = str('python ~/psrsoft/OPTIMUS/python/fitsio_cutfreq.py %s/%s %s %s %s/%s' %(simdataPath, filename, 500, 800, foldpath, cutfilename))
        print cutfile
        output = getoutput(cutfile)

    #rfifind
    maskfilename = filename[:-5]
    rfifind = str('rfifind %s/%s -o %s -time 1' %(foldpath, cutfilename, maskfilename))
    print rfifind
    output = getoutput(rfifind)

    #fold file
    foldfile = str('prepfold -noxwin -nosearch -p %s -dm %s -mask %s/%s %s/%s' %(period, dm, foldpath, maskfilename+'_rfifind.mask', foldpath, cutfilename))
    print foldfile
    output = getoutput(foldfile)

    #find pfdfile
    pfdfilename = glob.glob('%s/%s*.pfd' %(foldpath, maskfilename))

    return pfdfilename








#----------------------------------------------
if __name__ == "__main__":


    #----------------------------------------------
    #set parameters
    #DM range: 10 - 3000 cm-3/pc
    #Period range: 0.001 - 10 sec
    #Flux range: 0.1 -0.0001 Jy
    #db file: simPipe.db
    maxDM = 3000; minDM = 10; maxPeriod = 10; minPeriod = 0.001; maxFlux = 0.1; minFlux = 0.0001
    logDM = np.random.uniform(np.log10(minDM), np.log10(maxDM), 2) 
    logPeriod =  np.random.uniform(np.log10(minPeriod), np.log10(maxPeriod), 2)
    
    #----------------------------------------------
    #setworkpath
    simpath = os.getcwd()
    fastFile, fitsFilePath, simBinarydataPath, simdataPath, foldResult = setworkpath(simpath)
    print foldResult

    #----------------------------------------------
    #record random params
    f = open('randomParams.txt','a')
    f.writelines(time.asctime( time.localtime(time.time()) ))
    f.writelines("\n")
    f.writelines("DM\n")
    f.writelines(str(logDM))
    f.writelines("\n")
    f.writelines("Period\n")
    f.writelines(str(logPeriod))
    f.writelines("\n")
    f.close()

    #----------------------------------------------
    # other paramters
    meanFreq = 500
    randomNum=np.random.uniform(-1,1,len(logDM)*len(logPeriod))
    detection = 0
    taskid = 11
    count = 0

    for dm in logDM:
        for period in logPeriod:
            Flux = 2
            print fastFile[count]
            psrfitsName =  simulate(10**dm, Flux, 10**period, fastFile[count], randomNum[count], fitsFilePath, simBinarydataPath, simdataPath)
            print psrfitsName
            #fold file
            pfdfile = foldfile(psrfitsName, simdataPath, foldpath, dm, period):
            #AI select
            AItext =  confirmCandidate(pfdFile)                    
            if 
            count += 1

            
    #
    #
    ##----------------------------------------------
    ##record the test details
    #recordFile = "simlog.log"
    #f = open(recordFile,'a')
    #f.writelines()
    #f.close()
    #
    #
    #----------------------------------------------
    #record the result of test into the database
    #conn = sqlite3.connect('simPipe.db')
    #writedatabase(conn, psrparamName, DM, Period, width, Flux, detection, taskid)
    #cursor = conn.execute("SELECT * from simFiles")
    #for row in cursor:
    #    print row
    #conn.close()
