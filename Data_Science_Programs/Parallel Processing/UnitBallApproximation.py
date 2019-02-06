# UnitBallApproximation
"""The n-dimensional open unit ball is the set U_n = {x in R^n : ||x|| < 1}.
Estimate the volume of U_n by making N draws on each available process except
for the root process. Have the root process print the volume estimate.

Command line arguments:
    n (int): the dimension of the unit ball.
    N (int): the number of random draws to make on each process but the root.

Usage:
    # Estimate the volume of U_2 (the unit circle) with 2000 draws per process.
    $ mpiexec -n 4 python problem4.py 2 2000
    Volume of 2-D unit ball: 3.13266666667      # Results will vary slightly.
"""
from sys import argv
import numpy as np
from mpi4py import MPI
from numpy import linalg as la

n,N = int(argv[1]),int(argv[2])    #get the inputs
comm = MPI.COMM_WORLD
rank = comm.Get_rank()

if rank != 0:
    points = np.random.uniform(-1,1,(n,N))    #get the sample from the n-d space
    lengths = la.norm(points,axis=0,ord=2)    #get only the ones within the unit ball
    num_within = np.array([np.count_nonzero(lengths < 1)])
    comm.Send(num_within,dest=0)    #send the results to the first process
else:
    num_within = np.zeros(1,dtype=int)
    num_in_total = 0
    size = comm.Get_size()
    for i in range(1,size):    #iterate through and receive stuff from every process
        comm.Recv(num_within,source=i)
        num_in_total += num_within[0]    #add it to my count
    print(2**n * num_in_total/(N*(size-1)))   #calculate pi
    
