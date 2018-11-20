#!/usr/bin/python
# -*- coding: UTF-8 -*-

#For create simulate files auto
#For parameter dm, flux, period

#Width is always too big. Input will be smaller than 3-5 times
#use a database to record the progress
#module take care of the module that ubc_AI needed

import time
import yaml
<<<<<<< HEAD
=======
import rfifind
>>>>>>> b39705870bd1a20f8272d82ac10abe71a3b727e7
import numpy as np
import rfifind as prestoRFIfind
import math, sqlite3, optimus
import cPickle, glob, ubc_AI, os, sys
from commands import getoutput
from ubc_AI.data import pfdreader


#----------------------------------------------
#operate database
def writedatabase(database, name, dm, period, width, flux, detection, taskid):
    c = database.cursor()
    #name = "'"+name+"'"
    sql = " insert into simFiles (name, dm, period, width, flux, detection, taskid) values ('%s', '%s', '%s', '%s', '%s', '%s', %s)" %(name, dm, period, width, flux, detection, taskid)
    print sql
    c.execute(sql)
    database.commit()


#----------------------------------------------
#func to simulate files
def simulate(DM,Flux,Period, fastFileName, randomNum, fitsFilePath, simBinarydataPath, simdataPath):
    #set the and write the parameter files
    os.chdir(simBinarydataPath)
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
    SimulatePsrData = str('simulateSimplePsr_mcc -p FAST.params -p %s -o %s' %(psrparamName, psrdatName))
    print SimulatePsrData
    output=getoutput(SimulatePsrData)
    
    #combine files 
    #python ~/psrsoft/OPTIMUS/python/fitsio_combinePolBinary.py fitsfile binaryfile outputfile
    SimulatePsrData = str('python ~/psrsoft/OPTIMUS/python/fitsio_combinePolBinary.py %s/%s %s/%s %s/%s' %(fitsFilePath, fastFileName, simBinarydataPath, psrdatName, simdataPath, psrfitsName))
    print SimulatePsrData
    output = getoutput(SimulatePsrData)

    return psrfitsName, width


#----------------------------------------------
##return the result of AI select
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


#def confirmCandidate(pfdFile,foldResult):
#    os.chdir(foldResult)
#    filename = "ubc_AIScore.txt" 
#    f = open(filename, 'r')
#    result = f.readlines()
#    result = result.split()


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
    os.chdir(foldpath)
    cutfilename = filename[:-5]+'_cut'+filename[-5:]
    #cut file 
    #----------------------------------------------
    if dm <500:
        cutfile = str('python ~/psrsoft/OPTIMUS/python/fitsio_cutfreq.py %s/%s %s %s %s/%s' %(simdataPath, filename, 270, 270+256*2, foldpath, cutfilename))
        print cutfile
        output = getoutput(cutfile)
    elif dm <1000:
        cutfile = str('python ~/psrsoft/OPTIMUS/python/fitsio_cutfreq.py %s/%s %s %s %s/%s' %(simdataPath, filename, 416, 416+256, foldpath, cutfilename))
        print cutfile
        output = getoutput(cutfile)
    else :
        cutfile = str('python ~/psrsoft/OPTIMUS/python/fitsio_cutfreq.py %s/%s %s %s %s/%s' %(simdataPath, filename, 500, 500+256, foldpath, cutfilename))
        print cutfile
        output = getoutput(cutfile)

    #rfifind
    maskfilename = filename[:-5]
    rfifind = str('rfifind %s/%s -o %s -time 1' %(foldpath, cutfilename, maskfilename))
    print rfifind
    output = getoutput(rfifind)

<<<<<<< HEAD
    maskFile = prestoRFIfind.rfifind(maskfilename+'.mask')
    Intervals = maskFile.nchan * maskFile.nint * 1.
    badIntervals = 0.
    for i in maskFile.mask_zap_chans_per_int:
        badIntervals = len(i) + badIntervals

    #fold file
    #if badIntervals more than 50% of Intervals: fold without maskFile
    #if badIntervals less than 50% of Intervals: fold with maskFile
    #foldfile = str('prepfold -noxwin -nosearch -p %s -dm %s -mask %s/%s %s/%s' %(period, dm, foldpath, maskfilename+'_rfifind.mask', foldpath, cutfilename))
    if ((badIntervals / Intervals) > 0.5):
        foldfile = str('prepfold -noxwin -nosearch -p %s -dm %s -o %s  %s/%s' %(period, dm, cutfilename[:-5], foldpath, cutfilename))
    else:
        foldfile = str('prepfold -noxwin -nosearch -p %s -dm %s -o %s -mask %s/%s %s/%s' %(period, dm, cutfilename[:-5], foldpath, maskfilename+'_rfifind.mask', foldpath, cutfilename))
    print foldfile
    output = getoutput(foldfile)
=======
    maskfilename = glob.glob('%s/%s*.mark' %(foldpath, cutfilename[:-5]))
    x = rfifind.rfifind(maskfilename)
    # while bad inverband more than 50%, no use mask file; else use mask file
    if (((len(x.mask_zap_chans)+len(x.get_avg_zap_chans())) / (1. * x.nchan)) > 0.5):
        #fold file
        #foldfile = str('prepfold -noxwin -nosearch -p %s -dm %s -mask %s/%s %s/%s' %(period, dm, foldpath, maskfilename+'_rfifind.mask', foldpath, cutfilename))
        foldfile = str('prepfold -noxwin -nosearch -p %s -dm %s -o %s %s/%s' %(period, dm, cutfilename[:-5], foldpath, cutfilename))
        print foldfile
        output = getoutput(foldfile)
    else:
        #fold file
        #foldfile = str('prepfold -noxwin -nosearch -p %s -dm %s -mask %s/%s %s/%s' %(period, dm, foldpath, maskfilename+'_rfifind.mask', foldpath, cutfilename))
        foldfile = str('prepfold -noxwin -nosearch -p %s -dm %s -o %s -mask %s/%s %s/%s' %(period, dm, cutfilename[:-5], foldpath, maskfilename+'_rfifind.mask', foldpath, cutfilename))
        print foldfile
        output = getoutput(foldfile)
>>>>>>> b39705870bd1a20f8272d82ac10abe71a3b727e7

    #find pfdfile
    #pfdfilename = glob.glob('%s/%s*.pfd' %(foldpath, maskfilename))
    pfdfilename = glob.glob('%s/%s*.pfd' %(foldpath, cutfilename[:-5]))

    return pfdfilename


#----------------------------------------------
if __name__ == "__main__":


    #----------------------------------------------
    #set parameters
    #DM range: 10 - 3000 cm-3/pc
    #Period range: 0.001 - 10 sec
    #Flux range: 1 -0.0001 Jy
    #----------------------------------------------
    #db file: simPipe.db
    np.set_printoptions(precision=5)
    inputFilename = sys.argv[1:]

    for filename in inputFilename:
        with open(filename, 'r') as f:
            cont = f.read()
            x = yaml.load(cont)
        print "open file: ",filename,", reading settings."
        for i in x:
            print i
            print x[i]


    maximumFlux = x['maxFlux']
    minimumFlux = x['minFlux']
    logDM = [np.log10(i) for i in x['dm']]
    logPeriod = [np.log10(i) for i in x['period']]
    taskid = x['taskid']
    detectScore = x['detectScore']


    #----------------------------------------------
    #maxDM = 3000; minDM = 10; maxPeriod = 10; minPeriod = 0.001; maximumFlux = 5; minimumFlux = 0.0001
    #logDM = np.random.uniform(np.log10(minDM), np.log10(maxDM), 20) 
    #logPeriod =  np.random.uniform(np.log10(minPeriod), np.log10(maxPeriod), 20)

    #logPeriod = [np.log10(0.7658)]
    #logDM= [np.log10(100)]


    #----------------------------------------------
    # other paramters
    meanFreq = 500
    randomNum=np.random.uniform(-1,1,len(logDM)*len(logPeriod))
    detection = 0
    count = 0
    databasePath = "/public/home/mcc/work/test-simPipe/simPipe.db"

    
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
    #setworkpath
    simpath = os.getcwd()
    fastFile, fitsFilePath, simBinarydataPath, simdataPath, foldResult = setworkpath(simpath)
    print "path now: ", simpath


    for dm in logDM:
        for period in logPeriod:
            maxFlux = maximumFlux
            minFlux = minimumFlux
            meanFlux = (maxFlux+minFlux)/2.
            while (maxFlux/minFlux > 5):
                print "================running(1/4)================"
                print fastFile[count]
                #get filename
                psrfitsName_max, width_max  =  simulate(round(10**dm,5), round(maxFlux,5), round(10**period,5), fastFile[count], randomNum[count], fitsFilePath, simBinarydataPath, simdataPath)
                psrfitsName_min, width_min =  simulate(round(10**dm,5), round(minFlux,5), round(10**period,5), fastFile[count], randomNum[count], fitsFilePath, simBinarydataPath, simdataPath)
                psrfitsName_mean, width_mean  =  simulate(round(10**dm,5), round(meanFlux,5), round(10**period,5), fastFile[count], randomNum[count], fitsFilePath, simBinarydataPath, simdataPath)

                print "================running(2/4)================"
                #fold file
                pfdFile_max  = foldfile(psrfitsName_max , simdataPath, foldResult, round(10**dm,5), round(10**period,5))
                pfdFile_min  = foldfile(psrfitsName_min , simdataPath, foldResult, round(10**dm,5), round(10**period,5))
                pfdFile_mean = foldfile(psrfitsName_mean, simdataPath, foldResult, round(10**dm,5), round(10**period,5))


                print "================running(3/4)================"
                #AI select
                #maxFluxScore  = confirmCandidate(pfdFile_max, foldResult)
                #minFluxScore  = confirmCandidate(pfdFile_min, foldResult)
                #meanFluxScore = confirmCandidate(pfdFile_mean, foldResult)
                maxFluxScore  = float(confirmCandidate(pfdFile_max[0]).split()[1])
                minFluxScore  = float(confirmCandidate(pfdFile_min[0]).split()[1])
                meanFluxScore = float(confirmCandidate(pfdFile_mean[0]).split()[1])
                print maxFluxScore, minFluxScore, meanFluxScore


                print "================running(4/4)================"
                #check source order
                if (minFluxScore < meanFluxScore and meanFluxScore < maxFluxScore):

                    print "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"

                    print psrfitsName_max,round(10**dm,5), round(10**period,5), width_max, maxFlux, maxFluxScore, taskid
                    print psrfitsName_min,round(10**dm,5), round(10**period,5), width_min, minFlux, minFluxScore, taskid
                    print psrfitsName_mean,round(10**dm,5), round(10**period,5), width_mean, meanFlux, meanFluxScore, taskid

                    print "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"


                    #record the result to the database
                    #----------------------------------------------
                    conn = sqlite3.connect(databasePath)
                    writedatabase( conn, psrfitsName_max,round(10**dm,5), round(10**period,5), width_max, maxFlux, maxFluxScore, taskid)
                    writedatabase( conn, psrfitsName_min,round(10**dm,5), round(10**period,5), width_min, minFlux, minFluxScore, taskid)
                    writedatabase(conn, psrfitsName_mean,round(10**dm,5), round(10**period,5), width_mean, meanFlux, meanFluxScore, taskid)
                    #cursor = conn.execute("SELECT * from simFiles")
                    #for row in cursor:
                    #    print row
                    conn.close()
                else : 
                    print "================running================"
                    print "minFluxScore, meanFluxScore, maxFluxScore",minFluxScore, meanFluxScore, maxFluxScore


                #minFluxScore > detectScore
                if (minFluxScore > detectScore) :
                    print "================(1/4)================"
                    maxFlux = minFlux
                    minFlux = minimumFlux
                    meanFlux = (maxFlux+minFlux)/2.
                    print maxFlux, meanFlux, minFlux

                #minFluxScore < detectScore
                else: 
                    #meanFluxScore > detectScore
                    if (meanFluxScore > detectScore):
                        print "================(2/4)================"
                        maxFlux = meanFlux
                        meanFlux = (maxFlux+minFlux)/2.
                        print maxFlux, meanFlux, minFlux
                    #meanFluxScore < detectScore
                    else: 
                        #maxFluxScore > detectScore
                        if (maxFluxScore > detectScore):
                            print "================(3/4)================"
                            minFlux = meanFlux
                            meanFlux = (maxFlux+minFlux)/2.
                            print maxFlux, meanFlux, minFlux
                        #maxFluxScore < detectScore
                        else:
                            print "================(4/4)================"
                            maxFlux = maximumFlux
                            minFlux = maxFlux
                            meanFlux = (maxFlux+minFlux)/2.
                            print maxFlux, meanFlux, minFlux
                        
            #----------------------------------------------
            count += 1

    print "*************************finish***********************************"
