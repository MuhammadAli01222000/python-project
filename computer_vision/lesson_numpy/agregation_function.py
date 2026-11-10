import numpy as np
import matplotlib.pyplot as plt
arr=np.array([1,2,3,4,5])
#f=open('computer_vision/california_housing_train.csv').read()
data =np.loadtxt('/Users/fds/python project/computer_vision/assets/salary_data.csv',delimiter=',',skiprows=1)
print(data)
exp=data[:,0]
salary=data[:,1]
print(data)
print(salary)
plt.title("Salary va Experiense")
plt.xlabel('Years of experinse')
plt.ylabel("Salary")
plt.scatter(exp,salary)
plt.show()
