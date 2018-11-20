# For simPipeline

version 2 by mcc 2018/11

## 1. Introduction

This code is use used to get the minxmal flux search line can detected.
Using the ubc_AI from Weiwei Zhu.

## 2. Order to use

 1. set up the parameter ranges and search grid need to test
 2. set up the directory
 3. set up the limit of AI select
 4. simulate the data in given paramters
 5. process created data
 6. choose the correct range and up to 4

### usage

 1. add ubc_AI module to the pythonpath (test the ubc_AI module )
 2. set up the directory: simdata, result, fastdata, simBinarydata
    </br>simdata: simulate data
    </br>result: cut file and fold result
    </br>fastdata: obs data
    </br>simBinarydata: binarydata and parameters
 3. link the obs data to directory `fastdata`
 4. edit the config.yaml file
 5. run the code with python2.7
 6. `python simPipe.py config.yaml config1.yaml` (you can split the parameters to different yaml file)

## 3. Log files

It will write the detect result to the database.

## 4. Code struct

- simulateSimplePsr_mcc.c

  - Read paramter files

  - Calculate time delay in each channel
  - Make simple profile
       1. Get random numble to reshape the flux in each profile (rand1 random numble)
       2. For long files, loop for 1 minute. Use omp parallel for a faster calculate.
       3. **Note:** For a FAST version, we set the profile lower than 244 MHz will be set to 0. And you can set it by yourself.
       4. For different width input, it will use different profile equation to calculate the profile.
       5. The profile will normolized by the sum in each channel.

- simPipe.py
  - simulate code

## 5. usage

- C </br>
  simulateSimplePsr_mcc:
  - input: FAST.params, pulsar.params
  - output: profile.dat
  - output file format: binary file

- python </br>
  fitsio_combinePolBinary.py:
  - input: profile.dat, obs.fits
  - output: combine.fits
  - output file format: PSRFITS

- python module</br>
  optimus:
  - usage: import optimus

FILE: ./simPipe/optimus.py


CLASSES
- pulsar
- telescope
- writeParamFile

```python
#!/usr/bin/python
class pulsar
 |  #set pulsar params
 |  #return string list
 |  
 |  Methods defined here:
 |  
 |  __init__(self, name='J1950+30', period='0.2', dm='50', raj=4.510914803, decj=0.13602659, width=0.01, flux='0.001', useAngel=0)
 |      #'name: J1950+30\n', 'p0: 0.2\n', 'dm: 50.0\n', 'raj: 4.510914803\n', 'decj: 0.13602659 \n', 'width: 0.01\n', 'flux: 0.000008\n', 'useAngle: 0\n'
 |  
 |  __repr__ = __str__(self)
 |  
 |  __str__(self)

class telescope
 |  #return string list
 |  
 |  Methods defined here:
 |  
 |  __init__(self, name='FAST system', f1=0.125, f2=1024.125, nchan=4096, t0=0, t1=52.4288, gain=1, tsys=30, raj=0, decj=0, useAngel=0, tsamp=0.0002, digitiser=8)
 |  
 |  __repr__ = __str__(self)
 |  
 |  __str__(self)

class writeParamFile
 |  #write paramfiles
 |  
 |  Methods defined here:
 |  
 |  __init__(self, filename, paramStruct)
 ```

FUNCTIONS
   - pulseWidth(period, meanFref, randomNum)
     </br>#calculate the width of the pulsar.
     </br>#input period (s) meanFref (MHz) randomNum (-1~1)
