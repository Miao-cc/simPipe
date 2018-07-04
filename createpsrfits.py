import numpy as np
import math
import os, sys, glob, re
from commands import getoutput
import time
import datetime

class defaultparams():
    def __init__(self, name = ""):
        self.name = name
        self.data_dic = {}
        self.index = -1
    
    class telescope():
        #'name: FAST system\n', 'f1: 0.125\n', 'f2: 1024.125\n', 'nchan: 4096\n', 't0: 0\n', 't1: 52.4288\n', 'gain: 1\n', 'tsys: 30\n', 'raj: 0\n', 'decj: 0\n', 'useAngle: 0\n', 'tsamp: 0.0002\n'
        def __init__(self, name = 'FAST system', f1 = 0.125, f2 = 1024.125, nchan = 4096, t0 = 0, t1 = 52.4288, gain = 1, tsys = 30, raj = 0, decj = 0, useAngel = 0, tsamp = 0.0002, digitiser = 8):
            self.name = name
            self.f1 = f1
            self.f2 = f2 
            self.nchan = nchan
            self.t0 = t0
            self.t1 = t1
            self.gain = gain 
            self.tsys = tsys
            self.raj =  raj
            self.decj =  decj
            self.useAngel = useAngel
            self.tsamp = tsamp
            self.digitiser = digitiser

        def __str__(self):
#            params=['name','f1', 'f2', 'nchan', 't0','t1', 'gain', 'tsys', 'raj', 'decj', 'useAngel', 'tsamp', 'digitiser']
            return 'name: %s\nf1: %.3f \nf2: %.3f\nnchan: %.0f\nt0: %.5f\nt1: %.5f\ngain: %.2f\ntsys: %.2f\nraj: %.9f\ndecj: %.9f\nuseAngle: %.0f\ntsamp: %.6f\ndigitiser: %.0f\n' %(self.name, self.f1, self.f2, self.nchan, self.t0, self.t1, self.gain, self.tsys, self.raj, self.decj, self.useAngel, self.tsamp, self.digitiser)
        __repr__ = __str__

    class pulsar():
        #'name: J1950+30\n', 'p0: 0.2\n', 'dm: 50.0\n', 'raj: 4.510914803\n', 'decj: 0.13602659 \n', 'width: 0.01\n', 'flux: 0.000008\n', 'useAngle: 0\n'
        def __init__(self, name = 'J1950+30', period = '0.2', dm = '50', raj = 4.510914803, decj = 0.13602659, width = 0.01, flux = '0.001', useAngel = 0):
            self.name = name
            self.dm = dm
            self.period = period
            self.raj = raj
            self.decj = decj
            self.width = width
            self.flux = flux
            self.useAngel = useAngel
        def __str__(self):
            #PSRparams=['name: J1950+30\n', 'p0: 0.2\n', 'dm: 50.0\n', 'raj: 4.510914803\n', 'decj: 0.13602659 \n', 'width: 0.01\n', 'flux: 0.000008\n', 'useAngle: 0\n']
            #return 'name: %s\np0: %.9f \ndm: %.2f\nraj: %.9f\ndecj: %.9f\nflux: %.9f\nwidth: %.4f\nuseAngle: %.0f' %(self.name, self.period, self.dm, self.raj, self.decj, self.flux, self.width,self.useAngel)
            return 'name: %s\np0: %s \ndm: %s\nraj: %.9f\ndecj: %.9f\nflux: %s\nwidth: %.4f\nuseAngle: %.0f\n' %(self.name, self.period, self.dm, self.raj, self.decj, self.flux, self.width,self.useAngel)
        __repr__ = __str__

    #write paramfiles
    class writeParamFile() :
        def __init__(self,filename,paramStruct):
            # write params
            f=open(filename,'w')
            f.writelines(str(paramStruct))
            f.close()

#calculate the width of the pulsar.
#input period (s) meanFref (MHz) randomNum (-1~1)
def pulseWidth(period,meanFref,randomNum):
    meanFref = meanFref/1000.
    B=1.*1E12
    R_LightCylinder = 4.77*10000.*period
    periodDot = ((B/(3.2*1E19))**2)/period
    R_EmisionBeam = 400.*pow(meanFref,-0.26)*pow((periodDot*(1E15)),0.07)*pow(period,0.3)
    rho = 86.*pow(R_EmisionBeam/R_LightCylinder,0.5)
    rho = rho/360.
    w = 2*rho*pow((1.-randomNum**2),0.5)
    return w



if __name__ == "__main__":
    paramFile = 'paramNode16.txt'
    dms = []
    flux = []
    period = []
    f = open(paramFile, 'r')
    for line in f:
        dm,p,fl = line.split()
        dms.append(dm)
        flux.append(fl)
        period.append(p)
    
    # make dir for each different p0 and dm
    simCodePath=os.getcwd()
    print "path now: ", simCodePath
    #change path to the code path.
    #data dir and code dir should in a same dir
    simparam = open('simparam.txt','w')
    simlog = open('simlog.txt','w')
    simpath = '/public/home/mcc/work/test-1000file2/node16'
    simBinarydataPath = simpath+'/simBinarydata'
    fitsFilePath = simpath+'/fastdata'
    simdataPath = simpath+'/simdata'

    os.chdir(fitsFilePath)
    fastFile=glob.glob("*.fits")
    fitsfileNum=0
    randomNum=np.random.uniform(-1,1,len(dms))
    for count in range(len(dms)):
        dm = dms[count]
        fu = flux[count]
        p = period[count]
        #change dir path
        os.chdir(simBinarydataPath)
        fastparamName = 'FAST.params'            #FAST obs params, FAST.params
        psrparamName = str('test_DM_%s_Flux_%s_P0_%ss.params' %(dm, fu, p))
        psrdatName = str('test_DM_%s_Flux_%s_P0_%ss.dat' %(dm, fu, p))    #psr dat, *.dat
        psrfitsName = str('test10_DM_%s_Flux_%s_P0_%ss.fits' %(dm, fu, p))    #psr fits file, *.sf
        #digitName='digitiser_8bit.params'      #digitise_2bit.params
        #fastdatName='snoise.dat'               #sys noise dat, snoise.dat
        
        #write param files
        #calculate the width with func pulseWidth
        width = pulseWidth(float(p),500,randomNum[fitsfileNum])
        print width
        defaultparams.writeParamFile(fastparamName,defaultparams.telescope())
        defaultparams.writeParamFile(psrparamName,defaultparams.pulsar(dm = dm, flux = fu, period = p, width = width))

        
        #record time 
        startSimBinaryTime = datetime.datetime.now()
        
        #simulate pulsar signal
        SimulatePsrData = str('simulateSimplePsr_mcc -p FAST.params -p %s -o %s' %(psrparamName,psrdatName))
        print SimulatePsrData
        output=getoutput(SimulatePsrData)

        #record time 
        endSimBinaryTime = datetime.datetime.now()
        startCombineTime = datetime.datetime.now()

        #combine files 
        #python ~/psrsoft/OPTIMUS/python/fitsio_combinePolBinary.py fitsfile binaryfile outputfile
        SimulatePsrData = str('python ~/psrsoft/OPTIMUS/python/fitsio_combinePolBinary.py %s/%s %s/%s %s/%s' %(fitsFilePath, fastFile[fitsfileNum], simBinarydataPath, psrdatName, simdataPath, psrfitsName))
        print SimulatePsrData
        output = getoutput(SimulatePsrData)

        #record time 
        endCombineTime = datetime.datetime.now()

        #print time
        simBinaryTime= endSimBinaryTime - startSimBinaryTime
        combineFileTime= endCombineTime - startCombineTime
        print "psrparamName: %s psrdatName: %s psrfitsName:%s" %(psrparamName, psrdatName, fastFile[fitsfileNum])
        print "start simulate pulsar signal %s " %(startSimBinaryTime)
        print "end simulate pulsar signal %s " %(endSimBinaryTime)
        print "start combine file %s " %(startCombineTime)
        print "end combine file %s " %(endCombineTime)
        print 'sim binary file used: %s sec' %(simBinaryTime.seconds)
        print 'combine file used: %s sec' %(combineFileTime.seconds)

        print '-------------Finished!----------------------'
        
        #write logs to files
        simlog.write(str("psrparamName: %s psrdatName: %s psrfitsName:%s\n" %(psrparamName, psrdatName, fastFile[fitsfileNum])))
        simlog.write(str("start simulate pulsar signal %s\n" %(startSimBinaryTime)))
        simlog.write(str("end simulate pulsar signal %s\n" %(endSimBinaryTime)))
        simlog.write(str("start combine file %s\n" %(startCombineTime)))
        simlog.write(str("end combine file %s\n" %(endCombineTime)))
        simlog.write(str('sim binary file used: %s sec\n' %(simBinaryTime.seconds)))
        simlog.write(str('combine file used: %s sec\n' %(combineFileTime.seconds)))
        simlog.write(str('-------------Finished!----------------------\n'))
        #filename dm period width flux
        simparam.write(str('%s  %s  %s  %s  %s\n' %(psrfitsName, dm, p, width, fu)))

        fitsfileNum += 1
    simparam.close()
    simlog.close()
    
