# SentenceGenerator.py
from scipy import linalg as la
import numpy as np


def random_chain(n):
    """Creates and returns a transition matrix for a random Markov chain with
    'n' states. This should be stored as an nxn NumPy array.
    """
    Markov=[np.random.random_sample(n) for i in range(n)]
    return np.asmatrix([i/sum(i) for i in Markov]).T


def forecast(days):
    """Forecast tomorrow's weather given that today is hot."""
    transition = np.array([[0.7, 0.6], [0.3, 0.4]])
    # Sample from a binomial distribution to choose a new state.
    forecast = [np.random.binomial(1, transition[1, 0])]
    for i in range(days-1):
        if forecast[-1] == 0:
            forecast += [np.random.binomial(1, transition[0, 1])]
        else:
            forecast += [np.random.binomial(1, transition[0, 0])]
    return forecast


def four_state_forecast(days):
    """Run a simulation for the weather over the specified number of days,
    with mild as the starting state, using the four-state Markov chain.
    Return a list containing the day-by-day results, not including the
    starting day.

    Examples:
        >>> four_state_forecast(3)
        [0, 1, 3]
        >>> four_state_forecast(5)
        [2, 1, 2, 1, 1]
    """
    transition=np.array([[.5,.3,.1,0],[.3,.3,.3,.3],[.2,.3,.4,.5],[0,.1,.2,.2]])  #transition matrix
    forecast = [1]
    for i in range(days):                                                         #loop through every day
        result = np.random.multinomial(1, transition[:,forecast[-1]])             #grab the prediction from the matrix
        forecast += [result.nonzero()[0][0]]                                      #add to the forecast
    return forecast[1:]


def steady_state(A, tol=1e-12, N=40):
    """Compute the steady state of the transition matrix A.

    Inputs:
        A ((n,n) ndarray): A column-stochastic transition matrix.
        tol (float): The convergence tolerance.
        N (int): The maximum number of iterations to compute.

    Raises:
        ValueError: if the iteration does not converge within N steps.

    Returns:
        x ((n,) ndarray): The steady state distribution vector of A.
    """
    xk=np.random.random(np.shape(A)[0]).T
    xk1=np.dot(A,xk)
    iiterations=0
    while la.norm(xk-xk1)>tol:
        if iiterations > N:
            raise ValueError("A doesn't converge")
        xk=xk1
        xk1=A@xk
        iiterations+=1
    return xk1

class SentenceGenerator(object):
    """Markov chain creator for simulating bad English.

    Attributes:
        TransitionMatrix (n,n) Matrix: Probability matrix to predict the next word
        words (list): words corresponding to the TransitionMatrix

    Example:
        >>> yoda = SentenceGenerator("Yoda.txt")
        >>> print(yoda.babble())
        The dark side of loss is a path as one with you.
    """
    def __init__(self, filename):
        """Read the specified file and build a transition matrix from its
        contents. You may assume that the file has one complete sentence
        written on each line.
        """
        with open(filename,'r') as myFile:
            contents = myFile.read().split()
        with open(filename,'r') as myFile:
            trainingSet = myFile.read().split('\n')
        iuniqueWords = len(set(contents))+2
        self.TransitionMatrix = np.zeros((iuniqueWords,iuniqueWords))
        states = ['$tart']
        for sentence in trainingSet:
            sentence = sentence.split(' ')
            indices,prevWord = [],'$tart'             
            for word in sentence:
                if word not in states:
                    states += [word]
                indices +=[(states.index(word),states.index(prevWord))]#word's row & previous word's column
                prevWord = word
            indices +=[(iuniqueWords-1,states.index(prevWord))]
            for entry in indices:
                self.TransitionMatrix[entry]+=1
        for i in range(iuniqueWords):
            self.TransitionMatrix[:,i]=self.TransitionMatrix[:,i]/sum(self.TransitionMatrix[:,i])
        states+=['$top']
        self.words=states
            
    def babble(self):
        """Begin at the start sate and use the strategy from
        four_state_forecast() to transition through the Markov chain.
        Keep track of the path through the chain and the corresponding words.
        When the stop state is reached, stop transitioning and terminate the
        sentence. Return the resulting sentence as a single string.
        """
        n=np.shape(self.TransitionMatrix)[0]
        forecast = []
        result = np.random.multinomial(1, self.TransitionMatrix[:,0])
        while result.nonzero()[0][0] != n-1:
            forecast += [result.nonzero()[0][0]]
            result = np.random.multinomial(1, self.TransitionMatrix[:,forecast[-1]])
        sentence = ''
        for index in forecast:
            sentence += self.words[index]+' '
        return sentence[:-1]