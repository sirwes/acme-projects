# image_segmentation.py
import numpy as np
from scipy import linalg as la
from scipy.misc import imread as ir
from scipy import sparse as sp
from matplotlib import pyplot as plt

def laplacian(A):
    """Compute the Laplacian matrix of the graph G that has adjacency matrix A.

    Parameters:
        A ((N,N) ndarray): The adjacency matrix of an undirected graph G.

    Returns:
        L ((N,N) ndarray): The Laplacian matrix of G.
    """
    D=np.zeros_like(A)
    for i in range(len(D[0])):
        D[i,i]=sum(A[:,i])
    return D-A

def connectivity(A, tol=1e-8):
    """Compute the number of connected components in the graph G and its
    algebraic connectivity, given the adjacency matrix A of G.

    Parameters:
        A ((N,N) ndarray): The adjacency matrix of an undirected graph G.
        tol (float): Eigenvalues that are less than this tolerance are
            considered zero.

    Returns:
        (int): The number of connected components in G.
        (float): the algebraic connectivity of G.
    """
    eigs = np.sort(np.real(la.eigvals(laplacian(A))))
    numEigs = 0
    for i in range(len(eigs)):
        if abs(eigs[i]) < tol:
            eigs[i]=0
        numEigs+=1
    return numEigs, eigs[1]


# Helper function
def get_neighbors(index, radius, height, width):
    """Calculate the flattened indices of the pixels that are within the given
    distance of a central pixel, and their distances from the central pixel.

    Parameters:
        index (int): The index of a central pixel in a flattened image array
            with original shape (radius, height).
        radius (float): Radius of the neighborhood around the central pixel.
        height (int): The height of the original image in pixels.
        width (int): The width of the original image in pixels.

    Returns:
        (1-D ndarray): the indices of the pixels that are within the specified
            radius of the central pixel, with respect to the flattened image.
        (1-D ndarray): the euclidean distances from the neighborhood pixels to
            the central pixel.
    """
    # Calculate the original 2-D coordinates of the central pixel.
    row, col = index // width, index % width

    # Get a grid of possible candidates that are close to the central pixel.
    r = int(radius)
    x = np.arange(max(col - r, 0), min(col + r + 1, width))
    y = np.arange(max(row - r, 0), min(row + r + 1, height))
    X, Y = np.meshgrid(x, y)

    # Determine which candidates are within the given radius of the pixel.
    R = np.sqrt(((X - col)**2 + (Y - row)**2))
    mask = R < radius
    return (X[mask] + Y[mask]*width).astype(np.int), R[mask]


class ImageSegmenter:
    """Class for storing and segmenting images.
    
        Attributes:
            original (M,N): original image matrix
            flatImage (MN array): flattened array of the original matrix   
            isColor (boolean): Tells us if the original image was in color 
            m,n (int): Size of the original matrix
    """

    def __init__(self, filename):
        """Read the image file. Store its brightness values as a flat array."""
        image = ir(filename)/255        
        self.original = image
        self.m,self.n = image.shape[:2]
        self.isColor = (len(image.shape)==3)
        if self.isColor:
            self.flatImage = np.ravel(image.mean(axis=2))
        else:
            self.flatImage = image
                

    def show_original(self):
        """Display the original image."""
        if self.isColor:
            plt.imshow(self.original,cmap="gray")
        else:
            plt.imshow(self.original)
        plt.axis("off")
        plt.show()

    def adjacency(self, r=5., sigma_B2=.02, sigma_X2=3.):
        """Compute the Adjacency and Degree matrices for the image graph."""
        A=sp.lil_matrix((self.m*self.n,self.m*self.n))
        D=np.zeros(self.m*self.n)
        for vertex in range(self.m*self.n):
            neighbors,distances = get_neighbors(vertex,r,self.m,self.n)
            for x,j in enumerate(neighbors):
                weights = np.exp(-1*np.abs(self.flatImage[vertex]-self.flatImage[j])/sigma_B2-distances[x]/sigma_X2)
                A[vertex,j] = weights
            A=sp.csc_matrix(A)
        return A,np.ravel(A.sum(0))

    def cut(self, A, D):
        """Compute the boolean mask that segments the image."""
        L=sp.csgraph.laplacian(A)
        b=sp.diags(1/np.sqrt(D))
        eigval, eigvec = sp.linalg.eigsh(b@L@b, which = "SM",k=2)
        return np.reshape(eigvec[:,1],(self.m,self.n)) >0
        
        

    def segment(self, r=5., sigma_B=.02, sigma_X=3.):
        """Display the original image and its segments."""
        A,D=self.adjacency(r,sigma_B,sigma_X)
        mask=self.cut(A,D)
        plt.subplot(131)
        plt.imshow(self.original,cmap=("gray" if self.isColor else None),label="original")
        plt.subplot(132)
        plt.imshow(self.original*np.dstack((mask,mask,mask)),label='positive')
        plt.subplot(133)
        maskc=(mask==False)
        plt.imshow(self.original*np.dstack((maskc,maskc,maskc)),label="negative")
        plt.show()