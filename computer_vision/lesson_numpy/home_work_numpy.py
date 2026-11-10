import numpy as np
import matplotlib.pyplot as plt
def pattern_1(ones_array):
  res=np.ones(ones_array)
  print(res)
  return res

def fill_ones(n,m):
  res=np.ones((n,m),dtype=np.uint8)
  print( res) 
  return res

def  pattern_2(ones_arr):
  res=np.ones(ones_arr)
  res[4:,4:]=2
  # [boshi:oxiri, boshi:oxiri] ones_arr[4:, 4:] = 2
  print(res)
  return res
def pattern_3(arrays):
  res=np.ones(arrays)
  res[1:3,1:3]=2
  print(res)
  return res


def pattern_4(arrays):
  res=np.ones(arrays)
# [boshi:oxiri, boshi:oxiri] ones_arr[4:, 4:] = 2
  res[0:3,0:3]=2
  res[3:,0:3]=3
  print(res)
  return res

def pattern_5(ones_array):
   res=np.ones(ones_array)
  # [boshi:oxiri, boshi:oxiri] ones_arr[4:, 4:] = 2
   res[0:2,2:]=2
   res[2:,2:]=3
   print(res)
   return res
 
def pattern_6(ones_array):
  res=np.ones(ones_array)
  # [boshi:oxiri, boshi:oxiri] ones_arr[4:, 4:] = 2
  res[0:5,5:,]=2
  res[5:,0:5]=3
  res[5:,5:,]=4
  print(res)
  return res


def pattern_7(ones_array):
 res=np.ones(ones_array)
 res[1:6,1:7]=2
 res[6:7,1:7]=2

 res[2:6,2:6]=4

 print(res)
 return res

def chess(ones_array):
 res=np.ones(ones_array)
 res[::2, ::2] = 2
 res[1::2, 1::2] = 2
 return res

'''

12 12
[[2 1 2 1 2 1 2 1 2 1 2 1]
 [1 2 1 2 1 2 1 2 1 2 1 2]
 [2 1 2 1 2 1 2 1 2 1 2 1]
 [1 2 1 2 1 2 1 2 1 2 1 2]
 [2 1 2 1 2 1 2 1 2 1 2 1]
 [1 2 1 2 1 2 1 2 1 2 1 2]
 [2 1 2 1 2 1 2 1 2 1 2 1]
 [1 2 1 2 1 2 1 2 1 2 1 2]
 [2 1 2 1 2 1 2 1 2 1 2 1]
 [1 2 1 2 1 2 1 2 1 2 1 2]
 [2 1 2 1 2 1 2 1 2 1 2 1]
 [1 2 1 2 1 2 1 2 1 2 1 2]]
'''