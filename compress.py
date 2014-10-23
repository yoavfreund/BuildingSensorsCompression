def compress(self):
    Switch_points=[]
    i=len(self.Sol)-1                # start from the end 
    while i>0:
        prev=self.Sol[i]['prev']
        value=self.Sol[i]['value']
        i=prev
        Switch_points.append({'time':S.index[prev],'value':value})
    self.switch_points=Switch_points
    return Switch_points

def recon(self,index):
    Recon=np.zeros(len(self.Sol))
    
    Recon[prev:i]=value
    
    DF1=pd.DataFrame({'raw':S,'reconstructed':Recon})
    len(DF[abs(DF['raw'] - DF['reconstructed'])>0.1])
