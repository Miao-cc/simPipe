import numpy as np 
import math
import datetime
import sys
import matplotlib as mpl
import matplotlib.pyplot as plt
from pylab import *
from commands import getoutput
import optimus 
import gc
from sys import getrefcount


switch_backend('ps')

def gaussian(sigma, x, u):
    y = np.exp(-(x - u) ** 2 / (2 * sigma ** 2))
    return y
        #x = np.linspace(220, 230, 10000)

def simulate(DM, Flux, Period, randomNum):
    #set the and write the parameter files
    fastparamName = 'FAST.params'
    psrparamName = str('test_DM_%s_Flux_%s_P0_%s.params' %(DM, Flux, Period))
    psrdatName = str('test_DM_%s_Flux_%s_P0_%s.dat' %(DM, Flux, Period))
    
    #get width, had been checked to the right value of width
    meanFreq = 500
    width = optimus.pulseWidth(Period,meanFreq,randomNum)
    
    #write telescope pulsar params
    optimus.writeParamFile(fastparamName,optimus.telescope(f1 = 512.125, f2 = 1024.125, nchan = 2048))
    optimus.writeParamFile(psrparamName, optimus.pulsar(dm = str(DM), flux = str(Flux), period = str(Period), width = width))
    
    #simulate pulsar signal
    SimulatePsrData = str('simulateSimplePsr_mcc -p FAST.params -p %s -o %s' %(psrparamName, psrdatName))
    print SimulatePsrData
    output=getoutput(SimulatePsrData)

    del output
    gc.collect()

    return psrdatName, width


maxPeriod = 10
minPeriod = 0.001
#logPeriod =  np.random.uniform(np.log10(minPeriod), np.log10(maxPeriod), 10)
#p0 = np.arange(0.001,0.01,0.001)

#p0 = np.arange(0.005,0.01,0.001)
#p0 = np.append(p0,np.arange(0.011,0.2,0.01))

#p0 = np.arange(0.001,0.05,0.002)


#p0 = np.append(p0,np.arange(0.011,0.1,0.005))
#p0 = np.arange(0.18,1,0.05)
#p0 = np.arange(0.73,1,0.05)
p0_msp = np.arange(0.1,1,0.2)
p0 = p0_msp
#p0_short = np.arange(0.01,0.5,0.05)
#p0 = np.append(p0,p0_short)
#p0_long = np.arange(0.5,11,0.5)
#p0 = np.append(p0,p0_long)


#logPeriod = [np.log10(i) for i in [0.001,0.003,0.006,0.01,0.03,0.05,0.1,0.2,0.5,0.8,1,1.2,3,3.5,6,6.8,9,10]]
logPeriod = [np.log10(i) for i in p0]

#flux = np.arange(0.0001,0.05,0.005)
#flux = [0.0001, 0.0005,0.001,0.0025,0.005,0.0075,0.01,0.025,0.05,0.075,0.1,0.5,1]
flux = [0.05,0.075]


nchan = 2048
tsamp = 0.0002
print logPeriod
print flux

for period in logPeriod:
    period = 10**period
    for fl in flux:
        
        binaryfile, width  =  simulate(100, round(fl,4), round(period,3), 0)
        print 'width, period, fl: ',width, period, fl
    
        print "start reshape file",datetime.datetime.now()
        nsamp = int(period/tsamp)
        print nsamp, period/tsamp
        print int(0.05/0.0002)
        f = open(binaryfile, 'rb')
        #rowdata = np.fromfile(binaryfile,dtype=np.float32,count=-1)
        rowdata = np.fromfile(f,dtype=np.float32,count=-1)
        f.close()
        nline = int(np.size(rowdata)/nchan)
        simdata = rowdata.reshape((nline,nchan),order='C')
        print "nline",nline,"nchan:",nchan,"rowdata:",np.size(rowdata)
        print 'simdata.dtype',simdata.dtype,'simadata.max',np.max(simdata),'simdata.min',np.min(simdata),"simdata:",np.size(simdata)
        
        fig = figure(figsize=(16,4.5*2), dpi=80)
        # set plot labels
        #reshape downsample the data
        #data = simdata[0:100,:]
        data = simdata[0:2*nsamp,:]
        l, m = data.shape
        print "shape of output data",data.shape
        ax1=fig.add_subplot(211)
        im = ax1.imshow(data.T, aspect='auto',cmap=get_cmap("hot"),origin="lower" )
        position=fig.add_axes([0.15, 0.05, 0.7, 0.03])
        fig.colorbar(im, ax = ax1, cax=position, orientation='horizontal')
        
        ax2=fig.add_subplot(212)
        xlim(0, 2)
        ylim(-0.0001, np.max(simdata)*1.2)
        y = np.max(simdata)*gaussian(width, np.arange(0, 1,1./nsamp), 0.5)
        #y = np.tile(y,2)
        print "simdata,y",len(simdata[0:2*nsamp,50]),len(y),len(np.arange(0, 2,1./nsamp))
    
        ax2.plot(np.arange(len(y))/(1.*len(y)), y, "k", linewidth=10)
        
        tmp = simdata[0:2*nsamp,50]
        ax2.plot(np.arange(len(tmp))/(.5*len(tmp)), tmp, "yellow", linewidth=6)
        
        tmp = np.sum(data,axis=1)/nchan
        ax2.plot(np.arange(len(tmp))/(.5*len(tmp)), tmp, "r", linewidth=2)
    
    #    ax2.plot(np.arange(0, 1,1./nsamp), simdata[0:nsamp,50]-y, "r", linewidth=2)
    
        valueDiff = str(np.sum(simdata[0:len(y),50]-y))
        fig.text(0.1,0.92,'width: '+str(width)+'\n'+r'$\frac{1}{width^2}$: '+str(1./width/width)+'\n sum diff: '+valueDiff)
        sumFlux = np.sum(simdata[0:nsamp,50])*2*math.pi*tsamp/period
        print 'sumFlux: ', sumFlux
        fig.text(0.5,0.92,'period: '+str(period)+'\nDM: 100'+'\nFlux: '+str(fl)+'\nsum area: '+str(sumFlux))
    
        #show()
        savefig(binaryfile[:-4]+'.png',dpi=80)
        plt.cla()
        plt.close(fig)
        
        print "-------------------------------------------"

        del rowdata, simdata, data, tmp, y
        gc.collect()



