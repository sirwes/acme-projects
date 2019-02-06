#I'll make a newton solver from scratch Similar to scipy's odeint function
def NewtonSolver(fun,x0,args,tol=1e-8,maxIters=500):
    """
    Find the roots of a function using newton-secant iteration
    Parameters:
        fun (function): The function whose root is wanted.
        x0 (ndarray) : initial guess
        args (list): extra arguments to 'fun'
    Returns:
        Estimated location where function is zero
    """

    def secant(xn,x1,x0,f,args):
        """Estimates the derivative using the secant method"""
        bottom = f(xn,x0,args)-f(x1,x0,args) 
        # set all values of 0 to our tolerance level, to avoid 'divideByZero' and NaN errors
        bottom[bottom == 0] = tol**2
        return (xn-x1)/(bottom) # equation for first derivative estimation

    #initialize 2 guesses to estimate the derivative
    xn_1 = x0
    xn_2 = np.ones_like(x0)*tol**3
    it = 0        
    while True:
        df = secant(xn_2,xn_1,x0,f,args) #estimate the derivative
        xn = xn_1 - f(xn_1,x0,args)*df   #Update our guess of U[i+1] using secant method
                                         #for Newton iteration
        if np.linalg.norm(xn-xn_1) < tol:#If our iterations converge
            break                        #we're finished
        if it > maxIters:                #We don't want to run forever
            break                        #break after 500 iterations
        it+=1
        xn_2 = xn_1                      #otherwise, update our guesses
        xn_1 = xn
    return xn