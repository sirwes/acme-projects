#  ProcessCommLoop
"""In each process, generate a random number, then send that number to the
process with the next highest rank (the last process should send to the root).
Print what each process starts with and what each process receives.

Usage:
    $ mpiexec -n 2 python problem3.py
    Process 1 started with [ 0.79711384]        # Values and order will vary.
    Process 1 received [ 0.54029085]
    Process 0 started with [ 0.54029085]
    Process 0 received [ 0.79711384]

    $ mpiexec -n 3 python problem3.py
    Process 2 started with [ 0.99893055]
    Process 0 started with [ 0.6304739]
    Process 1 started with [ 0.28834079]
    Process 1 received [ 0.6304739]
    Process 2 received [ 0.28834079]
    Process 0 received [ 0.99893055]
"""
from mpi4py import MPI
import numpy as np

COMM = MPI.COMM_WORLD
largest = COMM.Get_size() - 1    #Get the highest rank
rank = COMM.Get_rank()
i = np.random.random(1)    #initialize the global var
if rank == 0:
    print("Process 0 started with {}".format(i))
    COMM.Send(i,dest=rank+1)    #if it's process 0, receive from the last process.
    COMM.Recv(i,source=largest)
    print("Process {} received {}".format(rank,i))
elif rank == largest:
    print("Process {} started with {}".format(rank,i))
    COMM.Send(i,dest=0)   #if it's the last process, send to the first
    COMM.Recv(i,source=rank-1)
    print("Process {} received {}".format(rank,i))
else:
    print("Process {} started with {}".format(rank,i))
    COMM.Send(i,dest=rank+1)    #if it's anything else, send to i+1 and receive from i-1
    COMM.Recv(i,source=rank-1)
    print("Process {} received {}".format(rank,i))
    