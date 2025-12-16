import time
import numpy as np
from functools import cache
def time_cal(func):
    def inner(*args,**kwargs):
        st=time.time()
        result=func(*args,**kwargs)
        et=time.time()
        print(f"The Time taken is:{1000000*(et-st):.2f} micro seconds")
        return result
    return inner
def string_pattern(func):
    def inner(*args,**kwargs):
        result=func(*args,**kwargs)
        return str(result).lower()
    return inner

class pattern1:
    def __init__(self,my_list):
        self.lst=my_list
    @time_cal
    def flatten(self):
        return self._flatten(self.lst)
    #@cache
    def _flatten(self,mlist):
        flat_list=[]
        for i in mlist:
            if isinstance(i,(list,tuple,set)):
                flat_list.extend(self._flatten(i))
            else:
                flat_list.append(i)
        return sorted(flat_list)
    def chk_eo(self):
        in_list=self.flatten()
        return ["even" if i%2==0 else "odd" for i in in_list]
    def club_list(self):
        in_list=self.flatten()
        return [in_list[i:i+2] for i in range(len(in_list)-1)]
    def rat(self):
        in_list=self.flatten()
        for i in range(len(in_list)):
            print(i*"*")
        print("")
        for i in range(len(in_list)):
            print((len(in_list)-i)*"*")
        print("")
    def rot_list(self):
        in_list=self.flatten()
        return in_list[-2:]+in_list[:-2]
    
class pattern2(pattern1):
    def __init__(self,mlist):
        super().__init__(mlist)
    def sigmoid(self):
        mlist=self.flatten()
        arr=np.array(mlist,dtype=float)
        return 1/(1+np.exp(-arr))
    def tanh(self):
        mlist=self.flatten()
        arr=np.array(mlist,dtype=float)
        return np.tanh(arr)
    def relu(self):
        mlist=self.flatten()
        arr=np.array(mlist,dtype=float)
        return np.maximum(0,arr)
    def softmax(self):
        mlist=self.flatten()
        arr=np.array(mlist,dtype=float)
        e_x = np.exp(arr - np.max(arr, axis=-1, keepdims=True))
        return e_x / np.sum(e_x, axis=-1, keepdims=True)

    def gelu(self):
        mlist=self.flatten()
        arr=np.array(mlist,dtype=float)
        return 0.5 * arr * (1 + np.tanh(np.sqrt(2 / np.pi) * (arr + 0.044715 * np.power(arr, 3))))