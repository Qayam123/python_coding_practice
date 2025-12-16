from miscellaneous import *
import matplotlib.pyplot as plt
import numpy as np
from functools import cache
import random
    
class pattern3:
    def __init__(self,mstring):
        self.mstring=mstring
    @string_pattern
    def count_vowels(self):
        vowels='aeiouAEIOU'
        count=sum(1 for char in self.mstring if char in vowels)
        return count
    @cache
    def reverse_string(self):
        return self.mstring[::-1]
    def count_words(self):
        words=self.mstring.split()
        return len(words)
    def count_consonants(self):
        vowels='aeiouAEIOU'
        count=sum(1 for char in self.mstring if char.isalpha() and char not in vowels)
        return count
    @time_cal
    def count_special_characters(self):
        special_chars='!@#$%^&*()-_=+[]{}|;:\'",.<>?/`~'
        count=sum(1 for char in self.mstring if char in special_chars)
        return count
class pattern4(pattern2,pattern3):
    def __init__(self,mlist,mstring):
        pattern1.__init__(self,mlist)
        pattern3.__init__(self,mstring)
    def identify(self):
        in_list1=self.flatten()
        in_string=self.reverse_string()
        in_list2=in_string.split()
        in_list3=[]
        for i in in_list2:
            for j in in_list1:
                in_list3.append(i+str(j))
        return random.choices(in_list3)
        
      
if __name__=="__main__":
    my_list=[1,[11,[7,(5,8,{3,9})]]]
    obj=pattern2(my_list)
    obj1=pattern3("Hello, World! This is a test string with 123 numbers and special characters #@$%.")
    obj2=pattern4(my_list,"Hello, World! This is a test string with 123 numbers and special characters #@$%.")
    print(obj2.identify())
    #print(obj.sigmoid())
    print(obj.flatten())
    #print(obj.rot_list())
    #print(obj.softmax())
    #print(obj1.count_vowels())
    #print(obj1.reverse_string())    
    #print(obj1.count_words())
    #print(obj1.count_consonants())
    #print(obj1.count_special_characters())
    #print(obj.gelu())
    #print(obj.relu())