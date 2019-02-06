# montecarlo_integration.py
import numpy as np
from scipy import linalg as la
from scipy import stats
from tqdm import tqdm
from matplotlib import pyplot as plt

def ball_volume(n, N=10000):
    """Estimate the volume of the n-dimensional unit ball.

    Parameters:
        n (int): The dimension of the ball. n=2 corresponds to the unit circle,
            n=3 corresponds to the unit sphere, and so on.
        N (int): The number of random points to sample.

    Returns:
        (float): An estimate for the volume of the n-dimensional unit ball.
    """
    points = np.random.uniform(-1,1,(n,N))      #get the randomly chosen points
    lengths = la.norm(points,2,axis=0)          #norm them
    num_within = np.count_nonzero(lengths < 1)  #only keep the ones inside
    return 2**n*(num_within/N)                  #estimate pi


def mc_integrate1d(f, a, b, N=10000):
    """Approximate the integral of f on the interval [a,b].

    Parameters:
        f (function): the function to integrate. Accepts and returns scalars.
        a (float): the lower bound of interval of integration.
        b (float): the lower bound of interval of integration.
        N (int): The number of random points to sample.

    Returns:
        (float): An approximation of the integral of f over [a,b].

    Example:
        >>> f = lambda x: x**2
        >>> mc_integrate1d(f, -4, 2)    # Integrate from -4 to 2.
        23.734810301138324              # The true value is 24.
    """
    points = np.random.uniform(a,b,N)       #sample N points from a to b
    return (b-a)*sum(f(points))/len(points) #use 11.1 to get the integral value


def mc_integrate(f, mins, maxs, N=10000):
    """Approximate the integral of f over the box defined by mins and maxs.

    Parameters:
        f (function): The function to integrate. Accepts and returns
            1-D NumPy arrays of length n.
        mins (list): the lower bounds of integration.
        maxs (list): the upper bounds of integration.
        N (int): The number of random points to sample.

    Returns:
        (float): An approximation of the integral of f over the domain.

    Example:
        # Define f(x,y) = 3x - 4y + y^2. Inputs are grouped into an array.
        >>> f = lambda x: 3*x[0] - 4*x[1] + x[1]**2

        # Integrate over the box [1,3]x[-2,1].
        >>> mc_integrate(f, [1, -2], [3, 1])
        53.562651072181225              # The true value is 54.
    """
    n=len(mins)                                   #get the number of dimensions
    points = np.random.uniform(0,1,(n,N))         #pull from a uniform distribution on [0,1]x...x[0,1]
                                                  #alter the points so that they fit inside their respective domains
    points = np.array([points[x]*(maxs[x]-mins[x])+mins[x] for x in range(n)]) 
        
    V=np.prod([maxs[i]-mins[i] for i in range(n)])#product the differences in each max and min
    return V*np.mean([f(x) for x in points.T])

def EstimateFunction():
    """Let n=4 and Omega = [-3/2,3/4]x[0,1]x[0,1/2]x[0,1].
    - Define the joint distribution f of n standard normal random variables.
    - Use SciPy to integrate f over Omega.
    - Get 20 integer values of N that are roughly logarithmically spaced from
        10**1 to 10**5. For each value of N, use mc_integrate() to compute 25
        estimates of the integral of f over Omega with N samples, and average
        the estimates together. Compute the relative error of each average.
    - Plot the relative error against the sample size N on a log-log scale.
        Also plot the line 1 / sqrt(N) for comparison.
    """
    n=4
    mins,maxs = np.asarray([-3/2,0,0,0]),np.asarray([3/4,1,1/2,1])      #define our mins and max's
    f = lambda x: 1/(2*np.pi)**(n/2)*np.exp(-x.T @ x / 2)               #define the pdf
    exactValue = stats.mvn.mvnun(mins,maxs,np.zeros(n),np.eye(n))[0]    #get the exact Value

    relerr = [] #initialize stuff
    domain = np.logspace(1,5,num=20,dtype=int)
    for N in domain:                                                    #for each N, find my approximation and the relative error
        approxIntegral = [mc_integrate(f,mins,maxs,N) for x in range(25)]
        relerr.append(abs(exactValue-np.mean(approxIntegral))/abs(exactValue))
        
    plt.loglog(domain,relerr,'-o',label = 'Relative Error')             #plot the relative error in relation to each N
    plt.loglog(domain,1/np.sqrt(domain),label = 'Root N inverse')
    plt.ylabel('Relative Error')
    plt.xlabel('N')        
    plt.legend(loc = 'upper right')
    plt.show()