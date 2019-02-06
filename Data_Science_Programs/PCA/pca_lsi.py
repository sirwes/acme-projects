import os
import string
from collections import Counter
from scipy import sparse
import numpy as np
from scipy import linalg as la
from sklearn import datasets
from scipy.sparse import linalg as sla
import matplotlib.pyplot as plt
from math import log


def Iris():
    iris = datasets.load_iris()
    X = iris.data
    Y = X-X.mean(axis=0)
    U,S,VT = la.svd(Y, full_matrices=False)
    S**2/(S**2).sum() # variance percentages
    Yh = Y@VT.T[:,:2]
    setosa = Yh[iris.target==0]
    vers = Yh[iris.target==1]
    virg = Yh[iris.target==2]
    plt.plot(setosa[:,0],setosa[:,1],'b.',ms=3,label='Setosa')
    plt.plot(vers[:,0],vers[:,1],'r.',ms=3,label='Versicolor')
    plt.plot(virg[:,0],virg[:,1],'g.',ms=3,label='Virginica')
    plt.legend(loc=0)
    plt.xlim([-4,4])
    plt.ylim([-4,4])
    plt.xlabel("First Principal Component")
    plt.ylabel("Second Principal Component")
    plt.title("PCA of the Iris dataset")
    plt.show()
    
def BestWorstSimilarSpeechesPCA(speech):
    folder = "./Addresses/"
    paths = [folder+p for p in os.listdir(folder) if p.endswith(".txt")]
    # Helper function to get list of words in a string
    def extractWords(text):
        ignore = string.punctuation + string.digits
        cleaned = "".join([t for t in text.strip() if t not in ignore])
        return cleaned.lower().split()
    # Initialize vocab set, then read each file and add to the vocab set.
    vocab = set()
    for p in paths:
        with open(p, 'r') as infile:
            for line in infile:
                vocab.update(extractWords(line))
    # Load stopwords.
    with open("stopwords.txt", 'r') as f:
        stops = set([w.strip().lower() for w in f.readlines()])
    # Remove stopwords from vocabulary, create ordering.
    vocab = {w:i for i, w in enumerate(vocab.difference(stops))}        

    counts = [] # holds the entries of X
    doc_index = [] # holds the row index of X
    word_index = [] # holds the column index of X
    # Iterate through the documents.
    for doc, p in enumerate(paths):
        with open(p, 'r') as f:
        # create the word counter
            ctr = Counter()
            for line in f:
                ctr.update(extractWords(line))
        # Iterate through the word counter, storing counts
            for word, count in ctr.items():
                if word in vocab:
                    word_index.append(vocab[word])
                    counts.append(count)
                    doc_index.append(doc)
    # Create sparse matrix holding these word counts.
    X = sparse.csr_matrix((counts, [doc_index, word_index]),
                          shape=(len(paths), len(vocab)), dtype=np.float)
    
    i=paths.index(speech)
    U,S,V = sla.svds(X)
    Xh = (X@(V.T))[:,:7]
    Xh = Xh/(la.norm(Xh,axis=1).reshape((-1,1)))
    indexes = np.arange(0,len(Xh))
    order = indexes[np.argsort(Xh.dot(Xh[i]))]
    best,worst = order[-2],order[0]
    return paths[best],paths[worst]


def BestWorstSimilarSpeechesLSI(speech):
    """
    Uses LSI, applied to the globally weighted word count matrix A, with the
    first 7 principal components to find the most similar and least similar speeches

    Parameters:
        speech str: Path to speech eg: "./Addresses/1984-Reagan.txt"

    Returns:
        tuple of str: (Most similar speech, least similar speech)
    """

    # Get list of filepaths to each text file in the folder.
    folder = "./Addresses/"
    paths = [folder+p for p in os.listdir(folder) if p.endswith(".txt")]

    # Helper function to get list of words in a string.
    def extractWords(text):
        ignore = string.punctuation + string.digits
        cleaned = "".join([t for t in text.strip() if t not in ignore])
        return cleaned.lower().split()

    # Initialize vocab set, then read each file and add to the vocab set.
    vocab = set()
    for p in paths:
        with open(p, 'r') as infile:
            for line in infile:
                vocab.update(extractWords(line))


    # load stopwords
    with open("stopwords.txt", 'r') as f:
        stops = set([w.strip().lower() for w in f.readlines()])

    # remove stopwords from vocabulary, create ordering
    vocab = {w:i for i, w in enumerate(vocab.difference(stops))}

    t = np.zeros(len(vocab))
    counts = []
    doc_index = []
    word_index = []

    # get doc-term counts and global term counts
    for doc, path in enumerate(paths):
        with open(path, 'r') as f:
            # create the word counter
            ctr = Counter()
            for line in f:
                words = extractWords(line)
                ctr.update(words)
            # iterate through the word counter, store counts
            for word, count in ctr.items():
                if word in vocab:
                    word_ind = vocab[word]
                    word_index.append(word_ind)
                    counts.append(count)
                    doc_index.append(doc)
                    t[word_ind] += count

    # Get global weights.
    g = np.ones(len(vocab))
    logM = log(len(paths))
    for count, word in zip(counts, word_index):
        p = count/float(t[word])
        g[word] += p*log(p+1)/logM

    # Get globally weighted counts.
    gwcounts = []
    for count, word in zip(counts, word_index):
        gwcounts.append(g[word]*log(count+1))

    # Create sparse matrix holding these globally weighted word counts
    X = sparse.csr_matrix((gwcounts, [doc_index,word_index]),
                          shape=(len(paths), len(vocab)), dtype=np.float)

    i=paths.index(speech)
    U,S,V = sla.svds(X)
    Xh = (X@(V.T))[:,:7]
    Xh = Xh/(la.norm(Xh,axis=1).reshape((-1,1)))
    indexes = np.arange(0,len(Xh))
    order = indexes[np.argsort(Xh.dot(Xh[i]))]
    best,worst = order[-2],order[0]
    #print("Looks reasonable to me!")
    return paths[best],paths[worst]