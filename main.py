import numpy as np
import matplotlib.pyplot as plt

def f(X):
    return X * np.sin(-X**2)

a,b=-3, 3
X = np.linspace(a,b,num=100)
Y = f(X)
plt.title('Amorti')
plt.axis("equal")
plt.grid()
plt.savefig('yest.png')
plt.plot(X,Y, color="red")
plt.show()