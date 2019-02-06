# iPyParallel.py - Intro to Parallel Programming

from ipyparallel import Client
import numpy as np
import time
from matplotlib import pyplot as plt

def initialize():
    """
    Write a function that initializes a Client object, creates a Direct
    View with all available engines, and imports scipy.sparse as spar on
    all engines.
    """
    client = Client()
    dview = client[:]
    dview.execute("import scipy.sparse as spar")

def variables(dx):
    """
    Write a function that accepts a dictionary of variables. Create a Client
    object, a Direct View, and distribute the variables. Then, pull the
    variables in both a blocking and non-blocking format.
    :param dx: Dictionary of variables
    :return: (list of results, list of ASyncResult objects)
    """
    client = Client()   #initialize the client
    dview = client[:]
    dview.push(dx)  #push the dictionary
    results = []
    results_asyncObj = []    
    for x in dx:    #pull all of the info in non-blocking format
        results.append(dview[x])
        results_asyncObj.append(dview.pull(x))
        
    return (results,results_asyncObj)

def MeanMaxMin(n=1000000):
    """
    Write a function that returns the mean, max, and min for n draws
    from the standard normal distribution where n is default to 1,000,000.
    Use apply_sync() to execute this function across all available engines.
    Print the results as returned by each engine.
    """
    global client
    client = Client()   #initialize the client
    dview = client[:]
    dview.push({'n':n}) #push n to each engine
    dview.execute('draws=np.random.randn(n)')  #make the draws on each engine
    print(dview.apply(np.mean))    #run the functions on each engine & print results
    print(dview.apply(np.max))
    print(dview.apply(np.min))

def ParallelSpeeds():
    """
    Time the function from the previous problem in parallel and serially. Run
    apply_sync() on the function to time in parallel. To time the function
    serially, run the function in a for loop n times, where n is the number
    of engines on your machine. Print the results.
    """
    nVec = [1000000,5000000,10000000,15000000]
    times1,times2 = [],[]
    for n in nVec:
        start1 = time.time()
        MeanMaxMin(n)
        times1.append(time.time()-start1)
        global client
        N = client.ids
        start2 = time.time()
        for i in N:
            print(np.mean(n))
            print(np.max(n))
            print(np.min(n))
        times2.append(time.time()-start2)
    plt.plot(nVec,times1,label='Multiple Engines')
    plt.plot(nVec,times2,label='1 Engine')
    plt.title("Time it takes to run prob3 on multiple vs 1 engine(s)")
    plt.ylabel("Time")
    plt.xlabel("n")
    plt.legend(loc=0)
    plt.show()


def parallel_trapezoidal_rule(f, a, b, n=200):
    """
    Write a function that accepts a function handle, f, bounds of integration,
    a and b, and a number of points to use, n. Split the interval of
    integration evenly among all available processors and use the trapezoidal
    rule to numerically evaluate the integral over the interval [a,b].

    Parameters:
        f (function handle): the function to evaluate
        a (float): the lower bound of integration
        b (float): the upper bound of integration
        n (int): the number of points to use, defaults to 200
    Returns:
        value (float): the approximate integral calculated by the
            trapezoidal rule
    """
    def trapezoid(xk,xk1):
        return h/2*(f(xk)+f(xk1))
        
    client = Client()   #initialize the client
    dview = client[:]
    lsp = np.linspace(a,b,n)
    h = lsp[1]-lsp[0]
    result = dview.map_async(trapezoid,lsp[:-1],lsp[1:])    #get the result from all of the engines

    return np.sum(result.get()) #sum up what we got

















