# ProcessCommunication
"""Pass a random NumPy array of shape (n,) from the root process to process 1,
where n is a command-line argument. Print the array and process number from
each process.

Usage:
    # This script must be run with 2 processes.
    $ mpiexec -n 2 python problem2.py 4
    Process 1: Before checking mailbox: vec=[ 0.  0.  0.  0.]
    Process 0: Sent: vec=[ 0.03162613  0.38340242  0.27480538  0.56390755]
    Process 1: Recieved: vec=[ 0.03162613  0.38340242  0.27480538  0.56390755]
"""
from mpi4py import MPI
from sys import argv
import numpy as np

COMM = MPI.COMM_WORLD    #initialize the communicatins
rank = COMM.Get_rank()
n = int(argv[1])    #get the input integer
arr = np.zeros((n))
if rank == 0:
    arr = np.random.random(n)    #initialize the array
    print("Process 0: Sending the array. vec={}".format(arr))
    COMM.Send(arr,dest=1)   #send it
elif rank == 1:
    print("Process 1: Before checking mailbox: vec={}".format(arr))
    COMM.Recv(arr,source=0)   #pick up the array
    print("Process 1: Received the array. vec={}".format(arr))