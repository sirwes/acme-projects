# PageRankAlgorithm.py
import numpy as np
from matplotlib import pyplot as plt
from scipy import sparse as sp
from scipy import linalg as la

def to_matrix(filename, n):
    """Return the nxn adjacency matrix described by datafile.

    Parameters:
        datafile (str): The name of a .txt file describing a directed graph.
        Lines describing edges should have the form '<from node>\t<to node>\n'.
        The file may also include comments.
    n (int): The number of nodes in the graph described by datafile

    Returns:
        A SciPy sparse dok_matrix.
    """
    S = sp.dok_matrix((n,n))                #initialize the dok matrix
    with open(filename, 'r') as myfile:     #open the file
        for line in myfile:                 #loop through each line
            try:
                x = line.strip().split()    #grab the keys
                S[int(x[0]),int(x[1])] = 1  #note that there is a connection
            except:
                continue                    #if there's a problem, skip it
    return S
        

def calculateK(A,N):
    """Compute the matrix K as described in the lab.

    Parameters:
        A (ndarray): adjacency matrix of an array
        N (int): the datasize of the array

    Returns:
        K (ndarray)
    """
    d=[]
    for x in range(N):                     #loop through A
        k=sum(A[x])                        #sum the rows
        if k == 0:                         #if it's a sink
            d.append(N)                    #connect it to everything
            A[x] = [1 for y in range(N)]
        else:
            d.append(k)                    #otherwise, append how many connections it has to the diagonal matrix
    return np.array([[A[x,a]/d[x] for a in range(N)] for x in range(N)]).T    #build K = (D^-1@A).T

def iter_solve(adj, N=None, d=.85, tol=1E-5):
    """Return the page ranks of the network described by 'adj'.
    Iterate through the PageRank algorithm until the error is less than 'tol'.

    Parameters:
        adj (ndarray): The adjacency matrix of a directed graph.
        N (int): Restrict the computation to the first 'N' nodes of the graph.
            If N is None (default), use the entire matrix.
        d (float): The damping factor, a float between 0 and 1.
        tol (float): Stop iterating when the change in approximations to the
            solution is less than 'tol'.

    Returns:
        The approximation to the steady state.
    """
    if N == None or N > len(adj):                      #if N is none, use the whole matrix
        N = len(adj)
    pk = np.random.rand(N)                             #pick a random starting vector
    K=calculateK(adj,N)                                #calculate K
    while True:
        pk1 = d*np.dot(K,pk)+np.ones_like(pk)*(1-d)/N  #update the steady state solution
        if la.norm(pk1 - pk) < tol:                    #if we're close enough, quit
            break
        pk = pk1                                       #otherwise, update and continue
    return pk1
    

def eig_solve(adj, N=None, d=.85):
    """Return the page ranks of the network described by 'adj'. Use SciPy's
    eigenvalue solver to calculate the steady state of the PageRank algorithm

    Parameters:
        adj (ndarray): The adjacency matrix of a directed graph.
        N (int): Restrict the computation to the first 'N' nodes of the graph.
            If N is None (default), use the entire matrix.
        d (float): The damping factor, a float between 0 and 1.

    Returns:
        The approximation to the steady state.
    """
    if N == None or N > len(adj):                #if N is none, use the whole matrix
        N = len(adj)
    E = np.ones_like(adj[:N,:N])                 #create the matrix of 1's: E
    B=d*calculateK(adj,N)+(1-d)/N*E              #Calculate the updating matrix
    evals,evects = la.eig(B)                     #get the eigen-info
    j = np.where(evals == max(evals))[0][0]      #get the index of the largest eigenvalue
    return evects[:,j]/sum(evects[:,j])          #return the corresponding normalized eigenvector


def team_rank(filename='ncaa2013.csv'):
    """Use iter_solve() to predict the rankings of the teams in the given
    dataset of games. The dataset should have two columns, representing
    winning and losing teams. Each row represents a game, with the winner on
    the left, loser on the right. Parse this data to create the adjacency
    matrix, and feed this into the solver to predict the team ranks.

    Parameters:
        filename (str): The name of the data file.
    Returns:
        ranks (list): The ranks of the teams from best to worst.
        teams (list): The names of the teams, also from best to worst.
    """
    teamset = set()
    games = list()
    teamIndex = dict()
    with open(filename, 'r') as ncaafile:
        ncaafile.readline()                   #reads and ignores the header line
        for line in ncaafile:
            teams = line.strip().split(',')   #split on commas
            teamset.add(teams[0])             #add the teams to a set
            teamset.add(teams[1])
            games.append((teams[1],teams[0])) #keep track of who lost to whom (team 1 lost to team 0)

    n = len(teamset)
    S = sp.dok_matrix((n,n))                  #initialize the dok matrix
    i = 0
    
    teamlist = list(teamset)
    for team in teamlist:                     #save the index of each team in our set   
        teamIndex[team] = i
        i+=1
        
    for game in games:                        #go through the track record and build the adjacency matrix
        winner = game[1]
        loser = game[0]
        #if a team beat multiple teams, put a 1 in the row of the losing team, and in the column of the winning one
        S[teamIndex[loser],teamIndex[winner]] = 1
        
    guess = iter_solve(S.toarray(),d=0.7)
    sortedGuess = np.argsort(guess)[::-1]
    return [guess[x] for x in sortedGuess],[teamlist[x] for x in sortedGuess]