# LeastSquares.py
from scipy import linalg as la
import numpy as np
from matplotlib import pyplot as plt
from scipy.stats import linregress


def least_squares(A, b):
    """Calculate the least squares solutions to Ax = b by using the QR
    decomposition.

    Parameters:
        A ((m,n) ndarray): A matrix of rank n <= m.
        b ((m, ) ndarray): A vector of length m.

    Returns:
        x ((n, ) ndarray): The solution to the normal equations.
    """
    Q,R = la.qr(A,mode='economic')
    return la.solve(R,Q.T@b)

def line_fit():
    """Find the least squares line that relates the year to the housing price
    index for the data in housing.npy. Plot both the data points and the least
    squares line.
    """
    data = np.load("housing.npy")
    A=np.column_stack((data[:,0],np.ones(np.shape(data[:,0])[0])))
    b=np.vstack(data[:,1])
    x = least_squares(A,b)
    m,b = x[0][0],x[1][0]
    y=np.linspace(0,20)
    plt.plot(data[:,0],data[:,1],'.')
    plt.plot(y,m*y+b,'-')
    plt.show()
        
def polynomial_fit():
    """Find the least squares polynomials of degree 3, 6, 9, and 12 that relate
    the year to the housing price index for the data in housing.npy. Plot both
    the data points and the least squares polynomials in individual subplots.
    """
    data = np.load("housing.npy")
    b=np.vstack(data[:,1])
    x3 = la.lstsq(np.vander(data[:,0],4),b)[0]
    x6 = la.lstsq(np.vander(data[:,0],7),b)[0]
    x9 = la.lstsq(np.vander(data[:,0],10),b)[0]
    x12 = la.lstsq(np.vander(data[:,0],13)  ,b)[0] 
    
    plt.subplot(221)
    plt.plot(data[:,0],data[:,1],'.')
    plt.plot(np.linspace(0,16,100),np.polyval(x3,np.linspace(0,16,100)),'k-',label="3-Deg poly")
    plt.legend(loc='lower right')
    plt.subplot(222)
    plt.plot(data[:,0],data[:,1],'.')
    plt.plot(np.linspace(0,16,100),np.polyval(x6,np.linspace(0,16,100)),'g-',label="6-Deg poly")
    plt.legend(loc='lower right')
    plt.subplot(223)
    plt.plot(data[:,0],data[:,1],'.')
    plt.plot(np.linspace(0,16,100),np.polyval(x9,np.linspace(0,16,100)),'c-',label="9-Deg poly")
    plt.legend(loc='lower right')
    plt.subplot(224)
    plt.plot(data[:,0],data[:,1],'.')
    plt.plot(np.linspace(0,16,100),np.polyval(x12,np.linspace(0,16,100)),'r-',label="12-Deg poly")
    plt.legend(loc='lower right')
    plt.show()

def plot_ellipse(a, b, c, d, e):
    """Plot an ellipse of the form ax^2 + bx + cxy + dy + ey^2 = 1."""
    theta = np.linspace(0, 2*np.pi, 200)
    cos_t, sin_t = np.cos(theta), np.sin(theta)
    A = a*(cos_t**2) + c*cos_t*sin_t + e*(sin_t**2)
    B = b*cos_t + d*sin_t
    r = (-B + np.sqrt(B**2 + 4*A)) / (2*A)

    plt.plot(r*cos_t, r*sin_t)
    plt.gca().set_aspect("equal", "datalim")

def ellipse_fit():
    """Calculate the parameters for the ellipse that best fits the data in
    ellipse.npy. Plot the original data points and the ellipse together, using
    plot_ellipse() to plot the ellipse.
    """
    xk,yk=np.load("ellipse.npy").T
    A=np.column_stack((xk**2,xk,xk*yk,yk,yk**2))
    b=np.ones_like(xk)
    a,b,c,d,e = la.lstsq(A,b)[0]
    plot_ellipse(a,b,c,d,e)
    plt.plot(xk,yk,'k.')
    plt.show()
    


def power_method(A, N=20, tol=1e-12):
    """Compute the dominant eigenvalue of A and a corresponding eigenvector
    via the power method.

    Parameters:
        A ((n,n) ndarray): A square matrix.
        N (int): The maximum number of iterations.
        tol (float): The stopping tolerance.

    Returns:
        (float): The dominant eigenvalue of A.
        ((n,) ndarray): An eigenvector corresponding to the dominant
            eigenvalue of A.
    """
    n=np.shape(A)[0]
    x=np.zeros((N,n))
    x[0,:]=np.random.random(n)
    x[0,:]=x[0]/np.linalg.norm(x[0])
    for k in range(1,N):
        x[k+1,:]=A@y[k,:]
        x[k+1,:]=x[k+1,:]/np.linalg.norm(x[k+1,:])
        if la.norm(x[k+1,:]-x[k,:])<tol:
        		N=k+2
            break
    return x[N-2,:].T@A@x[N-2,:],x[N-2,:]    

def qr_algorithm(A, N=50, tol=1e-12):
    """Compute the eigenvalues of A via the QR algorithm.

    Parameters:
        A ((n,n) ndarray): A square matrix.
        N (int): The number of iterations to run the QR algorithm.
        tol (float): The threshold value for determining if a diagonal S_i
            block is 1x1 or 2x2.

    Returns:
        ((n,) ndarray): The eigenvalues of A.
    """
    n=np.shape(A)[0]
    S=la.hessenberg(A)
    for k in range(N):
        Q,R=la.qr(S)
        S=R@Q
    eigs=[]
    i=0
    while i<n:
        if S[i,i] == S[-1,-1] or np.abs(S[i+1,i])<tol:
            eigs.append(S[i,i])
        elif np.shape(S[i]) == (2,2):
            sqrt=cmath.sqrt((S[i,i][0,0]+S[i,i][1,1])**2-4*(S[i,i][0,0]*S[i,i][1,1]-(S[i,i][1,0]*S[i,i][0,1])))/(2*S[i,i][0,0])
            eigs.append((S[i,i][0,0]+S[i,i][1,1])/(2*S[i,i][0,0])+sqrt)
            eigs.append((S[i,i][0,0]+S[i,i][1,1])/(2*S[i,i][0,0])-sqrt)
            i=i+1
        i=i+1
    return eigs
