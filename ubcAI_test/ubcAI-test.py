import cPickle, glob, ubc_AI
import numpy as np
from ubc_AI.data import pfdreader
AI_PATH = '/'.join(ubc_AI.__file__.split('/')[:-1])
#pfd_path = '/data/public/AI_data/pzc_pfds/'
pfd_path = './'
#classifier = cPickle.load(open(AI_PATH+'/trained_AI/clfl2_HTRU.pkl','rb'))
#classifier = cPickle.load(open('../clfl2_PALFA_1.pkl','rb'))
classifier = cPickle.load(open(AI_PATH+'/trained_AI/clfl2_PALFA.pkl','rb'))
#classifier = cPickle.load(open(AI_PATH+'/trained_AI/clfl2_BD.pkl','rb'))
#classifier = cPickle.load(open(AI_PATH+'/trained_AI/clfl2_ResNet.pkl','rb'))

pfdfile = glob.glob(pfd_path + '*.pfd')
print pfdfile
AI_scores = classifier.report_score([pfdreader(f) for f in pfdfile])

text = '\n'.join(['%s %s' % (pfdfile[i], AI_scores[i]) for i in range(len(pfdfile))])
fout = open('testResult.txt', 'w')
fout.write(text)
fout.close()

