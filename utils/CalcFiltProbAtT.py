import numpy as np

def CalcRegimeProbAtT(returns,A,P,var_cov,pi_inf):
    #[Y_t_t,Y_t_1_t,smoothed_prob] = CalcRegimeProbAtT(returns,A,B,P,predictor,var_cov,pi_inf)
    n = returns.shape[1]    # catch the number of assets from the size of the return matrix
    m = var_cov.shape[2]   # same same with the number of regime
    data_length = returns.shape[0]


    A = A.T # happens the same in the matlab code since the transpose comes from saving loading tricky trick

    LR = np.transpose(returns)
    n_timeseries = n
    
    MLR = np.zeros((n_timeseries, m, data_length))
    
    temp = np.zeros((n,m))
    for reg in range(m):
        temp[:,reg] = 1/2*np.diag(var_cov[:,:,reg],0)
   
   
    for t in range(data_length):
        MLR[:,:,t] = A - temp

    eta = np.zeros((m, data_length))
    
    # for reg in range(0,m):

   #     sigma_i = np.linalg.cholesky(var_cov[:,:,reg] + np.eye(n)*(0.00001))
    for reg in range(0,m):     
        for t in range(data_length):
            eta[reg,t] = 1/((2*np.pi)**(n_timeseries/2))/(np.linalg.det(var_cov[:,:,reg])**0.5)*np.exp(-1/2 * np.transpose(LR[:,t] - MLR[:,reg,t])@(np.linalg.matrix_power(var_cov[:,:,reg],-1)@(LR[:,t] - MLR[:,reg,t])))
                #eta[reg,t] = 1/(2*np.pi)**(n_timeseries/2)/(np.linalg.det(sigma_i@sigma_i.T))**0.5*np.exp(-1/2 * np.transpose(LR[:,t] - MLR[:,reg,t])@(np.linalg.matrix_power(sigma_i@sigma_i.T,-1)@(LR[:,t] - MLR[:,reg,t])))
                
   
    Y_t_1_t = np.zeros((m,data_length,2))
    Y_t_t   = np.zeros((m,data_length,2))
    Y_t_1_t[:,-1,0] = pi_inf              # Initial values for the probabilities (ergodic probabilities)
    Y_t_1_t[:,-1,1] = np.ones((m))/m    # Initial values for the probabilities (equal probabilities)

    for j in  np.arange(data_length-2,-1,-1):
        Y_t_t[:,j+1,0] = (Y_t_1_t[:,j+1,0]* eta[:,j+1])/(np.ones(m)@(Y_t_1_t[:,j+1,0]* eta[:,j+1])+1E-11)
        Y_t_t[:,j+1,1] = (Y_t_1_t[:,j+1,1]* eta[:,j+1])/(np.ones(m)@(Y_t_1_t[:,j+1,1]* eta[:,j+1])+1E-11)
        Y_t_1_t[:,j,0] = np.transpose(P)@Y_t_t[:,j+1,0]
        Y_t_1_t[:,j,1] = np.transpose(P)@Y_t_t[:,j+1,1]
    
    Y_t_t[:,0,0] = (Y_t_1_t[:,0,0]* eta[:,0])/(np.transpose(np.ones((m)))@(Y_t_1_t[:,0,0]* eta[:,0]))
    Y_t_t[:,0,1] = (Y_t_1_t[:,0,1]* eta[:,0])/(np.transpose(np.ones((m)))@(Y_t_1_t[:,0,1]* eta[:,0]))
    
    # Calculating Smoothed Probabilities
    smoothed_prob = np.zeros((m,data_length,2))
    smoothed_prob[:,0,:] = Y_t_t[:,0,:]
    
    for t in range(1,data_length):
        smoothed_prob[:,t,0] = Y_t_t[:,t,0] * (P@(smoothed_prob[:,t-1,0]/Y_t_1_t[:,t-1,0]))
        smoothed_prob[:,t,1] = Y_t_t[:,t,1] * (P@(smoothed_prob[:,t-1,1]/Y_t_1_t[:,t-1,1]))


    return Y_t_t, Y_t_1_t, smoothed_prob
