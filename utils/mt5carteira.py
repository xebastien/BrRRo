
# %% Imports

import MetaTrader5 as mt5
import pandas as pd
import time
import datetime as dt
import numpy as np
import py_financas
from os import path
from utils.CalcFiltProbAtT import CalcRegimeProbAtT
import matplotlib.pyplot as plt


from collections import OrderedDict
from pypfopt import discrete_allocation

import MultiRegimesPy # must be called before import matlab for loading the correct matlab running correct engire
import matlab

import sys
import os
print(os.environ['PATH'])
print(sys.version)


# %% Connect to MT5 server
def connect_myServer():
    if not mt5.initialize(server="ClearInvestimentos-Demo",login=1092111551,password="E5R2f4pG"):
        print("initialize() failed")
        mt5.shutdown()

    # request connection status and parameters
    print(mt5.terminal_info())
    # get data on MetaTrader 5 version
    print(mt5.version())

# %% Get my positions with tickers
def get_my_position():
    positions_total = mt5.positions_total()
    if positions_total>0:
        print("Total positions=",positions_total)
    else:
        print("Positions not found")

    # get the list of positions on symbols
    positionsBR2 = mt5.positions_get()
    if positionsBR2==None:
        print("No positions with assets of carteira BR3, error code={}".format(mt5.last_error()))
        return()
    elif len(positionsBR2)>0:
        print("positions_get()={}".format(len(positionsBR2)))
        # display these positions as a table using pandas.DataFrame
        df = pd.DataFrame(list(positionsBR2),columns=positionsBR2[0]._asdict().keys())
        df['time'] = pd.to_datetime(df['time'], unit='s')
        df.drop(['time_update', 'time_msc', 'time_update_msc', 'external_id'], axis=1, inplace=True)
        return(df)

# %% Fetch the ticker candles
initialDate1 = dt.datetime.now() - dt.timedelta(days=2*365)
#end=dt.datetime.now(dt.timezone.utc)
def preprocess_mt5(symbol,mt5, init= initialDate1,end=dt.datetime.now(dt.timezone.utc), time_frame=mt5.TIMEFRAME_D1):
    t = dt.time(16, 55) ## WORKING RIGHT BEFORE MARKET CLOSURE !!
    combined = dt.datetime.combine(initialDate1.date(), t)
    df_rates = pd.DataFrame(mt5.copy_rates_range(symbol, time_frame ,combined, end))
    df_rates['time'] = pd.to_datetime(df_rates['time'], unit='s',utc=True).dt.date

    df_rates["symbol"]=symbol
    #df_rates = df_rates.set_index('time')  # we let time as a column and not the index, to build the larger dataframe
    return(df_rates)


def get_hist_mysymbols(mySymbols):
    DF_list= list()

    initialDate1 = dt.datetime.now() - dt.timedelta(days=2*365)

    for k in list(mySymbols):
        df = preprocess_mt5(symbol=k, mt5=mt5, init=initialDate1)
        df.rename(columns={'close':k}, inplace=True)
        df1 = df[[k,'time']]
        df1.loc[:,'time'] = pd.to_datetime(df1['time'])
        DF_list.append(df1)
        # set_index('time')
        #print(df)

    dfs = [df.set_index('time') for df in DF_list]
    br2_df = pd.concat(dfs, axis=1)
    br2_df = br2_df.fillna(value=0)[::-1]
    #br2_df.fillna(value=0)
    return(br2_df)


# %% Fetch CDI and convert to return dataframe


def get_exessReturns(br2_df):
    cdi = py_financas.indices.recupera_indice('cdi',initialDate1.date(),dt.date.today())
    cdi = cdi[::-1]
    cditoday = pd.DataFrame([cdi['cdi'].iloc[0]],columns=['cdi'],index=[br2_df.index[0]])
    # CDI has not changed today so much
    cdi = cditoday.append(cdi)
    br2_returns = br2_df.pct_change(periods=-1)  
    br2_returns.replace([np.inf, -np.inf], np.nan, inplace=True) 
    br2_returns.fillna(0, inplace=True) 
    br2 = pd.concat([br2_returns, cdi], axis=1).reindex(br2_returns.index)

    # #%% Convert to execss returns
    for j in range(len(br2.index)):
        br2['cdi'].iloc[j] = (br2['cdi'].iloc[j]+1)**(1/252)-1
        #excessReturn['USDBRL'].iloc[j] = 1/(1+excessReturn['USDBRL'].iloc[j])-1

    clmn  = list(br2)
    for i in clmn[:-1]:
        for j in range(len(br2.index)):
            #print(excessReturn[i].iloc[j])
            br2[i].iloc[j] = (1+br2[i].iloc[j])/(1+br2['cdi'].iloc[j])-1

    br2.replace([np.inf, -np.inf], np.nan, inplace=True) 
    br2.fillna(0, inplace=True)
    # br2.pop("cdi") # can be dropped eventually

    return(br2)


# %% Read parameter file
def load_param_file(fileRegimeParam):

    regime_datas = pd.read_csv(fileRegimeParam,usecols=np.arange(0,7),skiprows=7,nrows=44)
    Adf = regime_datas.iloc[0:4, 2:7]
    Pdf = regime_datas.iloc[29:33, 2:6]
    var_covdf = regime_datas.iloc[5:28, 2:7]
    pi_infdf = regime_datas.iloc[42, 2:6]
    volmatdf = regime_datas.iloc[35:39, 2:7]

    var_covdf = var_covdf.dropna()  # drop the lines with the Nan
    var_covdf = var_covdf.to_numpy(dtype='float64')
    #print(var_covdf)


    # format data to np matrix
    RegParams={}
    RegParams["A"] = Adf.to_numpy(dtype='float64')
    RegParams["P"] = Pdf.to_numpy(dtype='float64')
    RegParams["pi_inf"] = pi_infdf.to_numpy(dtype='float64')

    volmat = volmatdf.to_numpy(dtype='float64')
    RegParams["volmat"] = volmat
    
    var_cov = np.zeros([5,5,4])
    for k in range(4):
        var_cov[:,:,k] = var_covdf[5*k:5*k+5,:]
    
    #var_cov = var_cov.reshape((5,5,4))
    pd.options.display.float_format = "{:,.3f}".format
    print("Parameter estimates correctly loaded from file")

    RegParams["var_cov"] =var_cov

    return(RegParams)

# %% Calculate filtered probabilities
#   Calculate prob  with my function transcriptedT to python
def calc_filt_prob(br2,RegParams):
    print("Calculating filtered probabilities")


    A = RegParams["A"]
    P = RegParams["P"]
    var_cov = RegParams["var_cov"]
    pi_inf = RegParams["pi_inf"]

    lnReturns = br2.iloc[:,0:5]
    reg_ret = np.log(1+lnReturns.to_numpy(dtype='float64'))

    Y_t_t, Y_t_1_t, smoothed_prob = CalcRegimeProbAtT(reg_ret,A,P,var_cov,pi_inf)
    # COnvert to DataFra,e
    Y1 = pd.DataFrame(Y_t_1_t[:,:,0].T,index=lnReturns.index,columns = ['Crash','Bear','Bull','Boom'])
    
    print("Calculations OK")
    return Y1,Y_t_1_t# reg_ret, 
    # keeping both for now because of shape size

# %% print the smoothed probabilities
def plot_FiltProb(Y1):
    # Last year probabilities
    Ymonth = Y1.iloc[1:22]

    plt.stackplot(Ymonth.index,
                [Ymonth['Crash'], Ymonth['Bear'],
                Ymonth['Bull'], Ymonth['Boom']],
                labels=['Crash', 'Bear', 'Bull', 'Boom'],
                alpha=0.8)
    plt.tick_params(labelsize=12,rotation=75)
    plt.xlabel('Date', size=12)
    plt.ylabel('Prob (percentage)', size=12)
    plt.ylim(bottom=0)
    plt.legend(loc=2, fontsize='large')              
    plt.title('Last month probabilities')
    plt.show()


    Ytrim = Y1.iloc[1:65]

    plt.stackplot(Ytrim.index,
                [Ytrim['Crash'], Ytrim['Bear'],
                Ytrim['Bull'], Ytrim['Boom']],
                labels=['Crash', 'Bear', 'Bull', 'Boom'],
                alpha=0.8)
    plt.tick_params(labelsize=12,rotation=75)
    plt.xlabel('Month', size=12)
    plt.ylabel('Prob (percentage)', size=12)
    plt.ylim(bottom=0)
    plt.legend(loc=2, fontsize='large')              
    plt.title('Last trimestre probabilities')
    plt.show()


    Yyear = Y1.iloc[1:252]
    plt.stackplot(Yyear.index,
                [Yyear['Crash'], Yyear['Bear'],
                Yyear['Bull'], Yyear['Boom']],
                labels=['Crash', 'Bear', 'Bull', 'Boom'],
                alpha=0.8)
    plt.tick_params(labelsize=12,rotation=75)
    plt.xlabel('Month', size=12)
    plt.ylabel('Prob (percentage)', size=12)
    plt.ylim(bottom=0)
    plt.legend(loc=2, fontsize='large')              
    plt.title('Last year probabilities')
    plt.show()

    Ydec = Y1.iloc[1:1000]
    plt.stackplot(Ydec.index,
                [Ydec['Crash'], Ydec['Bear'],
                Ydec['Bull'], Ydec['Boom']],
                labels=['Crash', 'Bear', 'Bull', 'Boom'],
                alpha=0.8)
    plt.tick_params(labelsize=12,rotation=75)
    plt.xlabel('Month', size=12)
    plt.ylabel('Prob (percentage)', size=12)
    plt.ylim(bottom=0)
    plt.legend(loc=2, fontsize='large')              
    plt.title('Last decade probabilities')
    plt.show()


    # Print the first 10 lines (most recent)
    print(Y1.iloc[1:22])
    #plt.plot(smoothed_prob[:,:,0].T)
    #plt.show()

# %% Calculates weights in percents - return np array of weights arranged by dates
# 
# Cast variables to matlab doubles
def calc_weights(RegParams,Y1,myRiskAversion,myHorizon): 
    Amat = matlab.double(RegParams["A"].tolist())
    Pmat = matlab.double(RegParams["P"].tolist())
    # reg_retMat = matlab.double(reg_ret.tolist()) #reg_ret
    var_covmat = matlab.double(RegParams["var_cov"].tolist())
    pi_infmat = matlab.double(RegParams["pi_inf"].tolist())
    volmatmat = matlab.double(RegParams["volmat"].tolist())
    Y_t_1_tM1 = matlab.double(Y1.tolist())
    gamma1 = matlab.double([myRiskAversion])
    horizon = matlab.double([myHorizon])

    MultiRegimesPy.initialize_runtime(['-nojvm', '-nodisplay'])
    myMatlabFunc = MultiRegimesPy.initialize()
    PF_WeightsM = myMatlabFunc.PyGeneral_Solution(Y_t_1_tM1,Amat,Pmat,var_covmat,pi_infmat,volmatmat,gamma1,horizon,nargout=1)#,nargout=1)#,Y_t_1_t,smoothed_prob
    PF_Weights1 = np.asarray(PF_WeightsM)

    # Y_t_tM,Y_t_1_tM2,smoothed_probM = myMatlabFunc.PyCalcRegimeProbAtT(reg_retMat,Amat,Pmat,var_covmat,pi_infmat,nargout=3)#,nargout=1)#,Y_t_1_t,smoothed_prob
    # PF_WeightsM = myMatlabFunc.PyGeneral_Solution(Y_t_1_tM2,Amat,Pmat,var_covmat,pi_infmat,volmatmat,gamma1,horizon,nargout=1)#,nargout=1)#,Y_t_1_t,smoothed_prob
    # PF_Weights2 = np.asarray(PF_WeightsM)

    # PF_Weights2 = np.asarray(PF_Weights2)
    PF_Weights1 = np.asarray(PF_Weights1)


    return PF_Weights1


# %% convert the np weight to a DataFrame and return as well the last ones for allocation
# + last one with no leverage
# % make data frame

def conv_dfWeights(PF_weights,br2_df):
    clmn = list(br2_df.columns)
    assetsList = clmn[0:5]
    assetsList.append('RF')

    PF = pd.DataFrame(PF_weights, columns = assetsList,index=br2_df.index)
    print(PF)

    # this is the weights in percent
    PFpertocome = PF.iloc[0,:].to_numpy(dtype='float64')

    PF_Weights_noLev = PFpertocome/np.sum(((PFpertocome)>0)*PFpertocome/100)
    
    return PF, PFpertocome, PF_Weights_noLev
#CurrPF = CurrPF / 100

# %%  Calculate number of shares
# make an ordered Dict 
#def calc_NbSecurities():

def convert_weight2shares(br2_df,PFpertocome,mymoney):

    currPrice = br2_df.reindex(index=br2_df.index[::-1])

    myweights = OrderedDict()

    clmn = list(br2_df.columns)
    assetsList = clmn[0:5]
    assetsList.append('RF')

    for k,j in zip(assetsList[0:5], range(0,5)):
        myweights[k] =  PFpertocome[j]/100

    latest_prices = discrete_allocation.get_latest_prices(currPrice)
    # Allocate Portfolio Value in $ as required to show number of shares/stocks to buy, also bounds for shorting will affect allocation
    allocation_share, rem_minv = discrete_allocation.DiscreteAllocation(myweights, latest_prices, total_portfolio_value=mymoney).lp_portfolio()
    return allocation_share, rem_minv

# %% Gathering cell

# mytrackers = 'SmallCaps', 'Nasdaq100', 'SP500', 'IBrX100', 'EurStocks600' 
# mySymbols = 'SMAC11', 'NASD11', 'IVVB11', 'BRAX11', 'EURP11' #
# mySymBuy = 'SMAC11', 'NASD11', 'IVVB11', 'BRAX11', 'EURP11' # 
# fileRegimeParam = """C:\\Users\\sberu\\Documents\\Scripts\\PythonFinance\\Carteira_br3\\Parameters_Br3.csv"""
# start_date = '2020-04-14'
# initialDate1  = dt.datetime.strptime(start_date, '%Y-%m-%d')

# myRiskAversion = 5
# myHorizon        = 15   # in days
######################### run functions   ####################################

# if __name__ == '__main__':
    main()