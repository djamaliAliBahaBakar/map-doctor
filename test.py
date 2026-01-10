import matplotlib
matplotlib.use('TkAgg') 

import numpy as np
import matplotlib.pyplot as plt


def f(x,y):
    return x**2 - y**2

n = 40
VX = np.linspace(-2,2,n)
print("VX:", VX)
VY = np.linspace(-2,2,n)

X, Y = np.meshgrid(VX, VY)
  

Z = f(X,Y)
fig = plt.figure()
ax = plt.axes(projection='3d')

ax.view_init(40, -30)
ax.contour(X, Y, Z)

plt.show()

