import pandas as pd
from numpy import *
class encoder:
    """
    The encoder/decoder class is the base class for all encoder/decoder pairs.
    Subclasses encode different types of encoding.
    EncoderLearner is a factory class for fitting encoders to data
    """
    def __init__(self,raw):
        """
        given a Pandas DataFrame or Series (raw), find the best model of a given type
        """
    
    def compress(self):
        """
        given a raw sequence and a model, return a compressed representation.
        """
        self.compressed=None
        return self.compressed
    
    def recon(self,compressed):
        """
        Recreate the original DataFrame or Series, possibly with errors.
        """
        Recon=None
        return Recon
    
    def get_size(self):
        return len(self.compressed)
    
    def compute_error(self,S,compressed=None):
        if type(compressed)==type(None):
            compressed=self.compressed
        R=self.recon(compressed=compressed,index=S.index)
        V=R-S
        V.dropna()
        return sqrt(sum([v*v for v in V.values]))/len(V)
    
class piecewise_constant(encoder):
    """ 
    Represent the signal using a sequence of piecewise constant functions 
    """
    def __init__(self,raw):
        if type(raw) != pd.Series:
            raise 'encode expects pandas Series as input'
        self.index=raw.index
        self.Sol=self.fit(raw)
    
    def fit(self,S,max_gap=96):
        S[isnan(S)]=0
        _range=max(S)-min(S)
        print 'range=',_range
        #Dynamic programming
        Sol=[[]]*len(S)  # an array that holds the best partition ending at each point of the sequence.
                # Each element contains a best current value, a pointer to the last change in best 
                # solution so far and the total error of best solution so far.
        for i in range(len(S)):
            if i==0:
                Sol[i]={'prev':None, 'value':S[0], 'error':0.0, 'switch_no':0}
            else:
                err0 = Sol[i-1]['error']+(Sol[i-1]['value']-S[i])**2
                best=None
                best_err=1e20
                best_val=S[i]
                for j in range(max(0,i-max_gap),i):
                    _mean=mean(S[j:i])
                    _std=std(S[j:i])
                    err=_std*(i-j)+Sol[j]['error']+_range
                    if err<best_err:
                        best=j
                        best_val=_mean
                        best_err=err
                Sol[i]={'prev':best, 'value':best_val, 'error':best_err,\
                        'switch_no': Sol[best]['switch_no']+1}
            #print '\r',i,Sol[i],
        return Sol
    
    def compress(self):
        Switch_points=[]
        i=len(self.Sol)-1                # start from the end 
        while i>0:
            prev=self.Sol[i]['prev']
            value=self.Sol[i]['value']
            if self.Sol[prev]['value'] != value:
                Switch_points.append({'time':S.index[prev],'value':value})
            i=prev
        self.compressed=Switch_points
        return Switch_points

    def recon(self,compressed=None, index=None):
        #print '\nindex=',index==None,'\n'
        #print '\ncompressed=',compressed==None,'\n'
        if(type(index)==type(None)):
            index=self.index
        Recon=pd.Series(index=index)
        
        if(type(compressed)==type(None)):
            compressed=self.compressed
        for e in compressed:
            time=e['time']
            value=e['value']
            Recon[time]=value
            
        return Recon.fillna(method='ffill')

import pickle
import pandas as pd 

out=open('Compressed.pkl','w')
A=pickle.load(open('New150Days.pkl','r'))
A=A.dropna(subset=['Rooms'])
rooms=sorted(list(set(A.Room.values)))

cols = list(A.columns)
cols.remove('Room')
cols.remove('Temperature')

for room in rooms[:10]:
    print '-'*20,room,'-'*20
    DF = A[A['Room']==room]
    DF = DF.drop('Room', 1)  # remove the entry "Room"
    for name in cols:
        S=DF[name]
        #S=S[100:200]
        _std=std(S)
        print 'room=',room,'signal=',name, 'std=',_std,
        
        encoder=piecewise_constant(S)
        C=encoder.compress()
        print 'size=',encoder.get_size(),
        error=encoder.compute_error(S,compressed=C)
        print 'error=',error, 'error/_std=',error/_std
        pickle.dump({'name':name,
                     'room':room,
                     'code':C
                     }, out)
out.close()
