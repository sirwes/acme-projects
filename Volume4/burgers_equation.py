import numpy as np
from scipy.sparse import spdiags
from scipy.sparse import linalg as la
from matplotlib import pyplot as plt
from inspect import signature
import NewtonSolver

def burgers_equation(a,b,T,N_x,N_t,u_0,c_a,d_a,h_a,c_b,d_b,h_b):
    """
    Parameters:
        a - float
        b - float, a < b
        T - positive float
        N_x - positive integer, N_x > 2, N_x = number of mesh nodes in x
        N_t - positive integer, N_t > 1, N_t = number of mesh nodes in t
        u_0 - function handle for the initial function auxiliary condition
        c_a - function handle
        d_a - function handle
        h_a - function handle
        c_b - function handle
        d_b - function handle
        h_b - function handle
    Returns:
        U - a two dimensional numpy array containing floats. Rows correspond to time and columns to x.
    """
    # Check for bad inputs
    if type(a) != float or type(b) != float or b <= a: 
        raise ValueError("The spacial boundary points (a,b) must be floats where a < b")
    elif type(T) != float or T <= 0:
        raise ValueError("The final time (T) must be a float where T > 0")
    elif type(N_x) != int or N_x <=2 or type(N_t) != int or N_t <=1:
        raise ValueError("N_x and N_t must be positive integers with N_x > 2 and N_t > 1")
    elif not callable(u_0):
        raise ValueError("u_0 must be a function handle for the initial function auxilary condition")
    elif not callable(c_a) or not callable(d_a) or not callable(h_a) or not callable(c_b) or not callable(d_b) or not callable(h_b):
        raise ValueError("The last 6 inputs must all be function handles")
    u0sig = signature(u_0)
    if len(u0sig.parameters) != 1:
        raise ValueError("u_0 must be a function of 1 input variable")
    casig = signature(c_a)
    if len(casig.parameters) != 1:
        raise ValueError("c_a must be a function of 1 input variable")
    dasig = signature(d_a)
    if len(dasig.parameters) != 1:
        raise ValueError("d_a must be a function of 1 input variable")
    hasig = signature(h_a)
    if len(hasig.parameters) != 1:
        raise ValueError("h_a must be a function of 1 input variable")
    cbsig = signature(c_b)
    if len(cbsig.parameters) != 1:
        raise ValueError("c_b must be a function of 1 input variable")
    dbsig = signature(d_b)
    if len(dbsig.parameters) != 1:
        raise ValueError("d_b must be a function of 1 input variable")
    hbsig = signature(h_b)
    if len(hbsig.parameters) != 1:
        raise ValueError("h_b must be a function of 1 input variable")
    #Looks like they put in valid stuff, so let's solve it!
    #initialize spacial and time domains
    domain = np.linspace(a,b,N_x)
    rang = np.linspace(0,T,N_t)
    U = np.ones((N_t,N_x))
    #initialize constants
    dx = domain[1]-domain[0]
    dt = rang[1]-rang[0]
    K1,K2 = dt/(4*dx),dt/(2*dx**2)
    s = 3
    
    #initialize the crank-nicholson equation function for 2nd-order Burger's equation
    def f(U1,U0,args):
        """The nonlinear implicit Crank-Nicholson equations for 
        the transformed Burgers' equation.

        Parameters
        ----------
            U1 (ndarray): The values of U^(n+1)
            U0 (ndarray): The values of U^n
            s (float): wave speed
            K1 (float): first constant in the equations
            K2 (float): second constant in the equations

        Returns
        ----------
            out (ndarray): The residuals (differences between right- and 
                        left-hand sides) of the equation, accounting 
                        for boundary conditions
        """
        s,K1,K2 = args # constants needed for Crank-Nicholson Equation
        result = np.zeros_like(U0)
        # equation for implicit Crank-Nicholson Method (everything set equal to 0)
        result[1:-1] = U1[1:-1]-U0[1:-1]-K1*((s-U1[1:-1])*(U1[2:]-U1[:-2])+(s-U0[1:-1])*(U0[2:]-U0[:-2]))-K2*((U1[2:]-2*U1[1:-1]+U1[:-2])+(U0[2:]-2*U0[1:-1]+U0[:-2]))
        # set initial boundary conditions
        result[0] = U1[0]-U0[0]
        # set end boundary conditions
        result[-1] = U1[-1]-U0[-1]
        return result
    
    #build the interior of our solution using the newton solver
    U[0] = u_0(domain)
    for i in range(1,N_t):
        U[i] = NewtonSolver(f,U[i-1],args=(s,K1,K2))
        
    #initialize boundary condition parts
    ux_a = np.array([(U[i,2] - U[i,1])/(2*dx) for i in range(1,N_t)])
    ux_b = np.array([(U[i,-3] - U[i,-2])/(2*dx) for i in range(1,N_t)])
    ca = c_a(rang[1:])*np.eye(N_t-1)
    ha = h_a(rang[1:])*np.eye(N_t-1)
    da = d_a(rang[1:])*np.eye(N_t-1)
    cb = c_b(rang[1:])*np.eye(N_t-1)
    hb = h_b(rang[1:])*np.eye(N_t-1)
    db = d_b(rang[1:])*np.eye(N_t-1)
    
    #Pad the solution with the boundary conditions
    U[1:,0] = np.diag(np.linalg.solve(ca,ha - da*ux_a))
    U[1:,-1] = np.diag(np.linalg.solve(cb,hb - db*ux_b))
    return U


