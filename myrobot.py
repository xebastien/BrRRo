# %%import MetaTrader5 as mt5
import MetaTrader5 as mt5
from datetime import datetime, timedelta
import pandas as pd
import time
import schedule
import pytz
import talib as ta

from utils.mt5carteira import *
#from .mt5carteira import connect_myServer

# %% my parameters of robozinho
account = 1092111551
take_profit_pc  = 800 #pips
stop_loss_pc    = 200

start_date = '2018-04-14'

initialDate1  = datetime.strptime(start_date, '%Y-%m-%d')

mytrackers = 'SmallCaps', 'Nasdaq100', 'SP500', 'IBrX100', 'EurStocks600' 
mySymbols = 'SMAC11', 'NASD11', 'IVVB11', 'BRAX11', 'EURP11' #
mySymBuy = 'SMAC11', 'NASD11', 'IVVB11', 'BRAX11', 'EURP11' # 
fileRegimeParam = """C:\\Users\\sberu\\Documents\\Scripts\\PythonFinance\\Carteira_br3\\Parameters_Br3.csv"""
start_date = '2020-04-14'
initialDate1  = dt.datetime.strptime(start_date, '%Y-%m-%d')
open_time  = "14:55" # does not consider time zone - I am in Europe playing on the B3
close_time = "21:55"
alavancagem = 3

myRiskAversion   = 5    # in gamma
myHorizon        = 15   # in days

mymoney = 0             # how much in bank
# %% conect mt5 
def connect(account):
    account = int(account)
    mt5.initialize()
    authorized=mt5.login(account)

    if authorized:
        print("Connected: Connecting to MT5 Client")
    else:
        print("Failed to connect at account #{}, error code: {}"
              .format(account, mt5.last_error()))

# %%
def get_order_history(date_from, date_to):
    res = mt5.history_deals_get(date_from, date_to)
    
    if(res is not None and res != ()):
        df = pd.DataFrame(list(res),columns=res[0]._asdict().keys())
        df['time'] = pd.to_datetime(df['time'], unit='s')
        return df
    
    return pd.DataFrame()


def open_position(pair, order_type, size, tp_distance=None, stop_distance=None):
    symbol_info = mt5.symbol_info(pair)
    if symbol_info is None:
        print(pair, "not found")
        return

    if not symbol_info.visible:
        print(pair, "is not visible, trying to switch on")
        if not mt5.symbol_select(pair, True):
            print("symbol_select({}}) failed, exit",pair)
            return
    print(pair, "found!")

    point = symbol_info.point
    
    if(order_type == "BUY"):
        order = mt5.ORDER_TYPE_BUY
        price = mt5.symbol_info_tick(pair).ask
        if(stop_distance):
            sl = price - (stop_distance * point)
        if(tp_distance):
            tp = price + (tp_distance * point)
            
    if(order_type == "SELL"):
        order = mt5.ORDER_TYPE_SELL
        price = mt5.symbol_info_tick(pair).bid
        if(stop_distance):
            sl = price + (stop_distance * point)
        if(tp_distance):
            tp = price - (tp_distance * point)

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": pair,
        "volume": float(size),
        "type": order,
        "price": price,
        "sl": sl,
        "tp": tp,
        "magic": 234000,
        "comment": "",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    result = mt5.order_send(request)

    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print("Failed to send order :(")
        print(result)
    else:
        print ("Order successfully placed!")



# %%  get position
def positions_get(symbol=None):
    if(symbol is None):
	    res = mt5.positions_get()
    else:
        res = mt5.positions_get(symbol=symbol)

    if(res is not None and res != ()):
        df = pd.DataFrame(list(res),columns=res[0]._asdict().keys())
        df['time'] = pd.to_datetime(df['time'], unit='s')
        return df
    
    return pd.DataFrame()
# %%  close positions
def close_position(deal_id):
    open_positions = positions_get()
    open_positions = open_positions[open_positions['ticket'] == deal_id]
    order_type  = open_positions["type"].iloc[0]
    symbol = open_positions['symbol'].iloc[0]
    volume = open_positions['volume'].iloc[0]

    if(order_type == mt5.ORDER_TYPE_BUY):
        order_type = mt5.ORDER_TYPE_SELL
        price = mt5.symbol_info_tick(symbol).bid
    else:
        order_type = mt5.ORDER_TYPE_BUY
        price = mt5.symbol_info_tick(symbol).ask
	
    close_request={
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": float(volume),
        "type": order_type,
        "position": deal_id,
        "price": price,
        "magic": 234000,
        "comment": "Close trade",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    result = mt5.order_send(close_request)
    
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print("Failed to close order :(")
    else:
        print ("Order successfully closed!")
# %% close by symbol
def close_positons_by_symbol(symbol):
    open_positions = positions_get(symbol)
    open_positions['ticket'].apply(lambda x: mt5.close_position(x))

    
    
def live_trading():

    schedule.every().day.at(open_time).do(run_trader,  mt5.TIMEFRAME_H1)
    schedule.every().day.at(close_time).do(run_closing, mt5.TIMEFRAME_H1)

    while True:
        schedule.run_pending()
        time.sleep(1)

def run_closing():
    print("Closing all positions")
    for elsymbol in mySymbols:
        elsymPos = positions_get(elsymbol)
        if len(elsymPos) > 0:
            close_positons_by_symbol(elsymbol)
    print("All positions in the symbol list closed")

def run_trader(time_frame):
    print("Running trader at", datetime.now())
    connect(1092111551)

    # get past data of the securities
    br2_df = get_hist_mysymbols(mySymbols)
    # convert to exess returns in regards of the CDI (does not change much thing at this point)
    br2 = get_exessReturns(br2_df)
    # load to memmory the estimated parameters
    RegParams = load_param_file(fileRegimeParam)
    # Calculate Filtered Probabilities
    Y1,Y_t_1_t = calc_filt_prob(br2,RegParams) #  reg_ret
    # plot probabilities
    plot_FiltProb(Y1)
    # calculates the weights with the model, array of weights by date
    PF_weights = calc_weights(RegParams,Y_t_1_t,myRiskAversion,myHorizon)# reg_ret,

    myPos = positions_get()
    print(myPos)

    account_info_dict = mt5.account_info()._asdict()
    global mymoney 
    mymoney = account_info_dict["balance"] * alavancagem
    #for k in range(len(mypos)):
    #    mymoney = mymoney + myPos["price_current"].iloc[k]

    # convert to dataframe and get the last allocation, leveraged and not
    PF, PFpertocome, PF_Weights_noLev = conv_dfWeights(PF_weights,br2_df)
    # convert weights to shares
    allocation_share, rem_minv = convert_weight2shares(br2_df,PFpertocome,mymoney)
    for elsymbol in allocation_share:
        if allocation_share[elsymbol] > 0:
            open_position(elsymbol, "BUY", allocation_share[elsymbol], tp_distance=300, stop_distance=150)
        elif allocation_share[elsymbol] < 0:
            open_position(elsymbol, "SELL", abs(allocation_share[elsymbol]), tp_distance=300, stop_distance=150)



if __name__ == '__main__':

    live_trading()
# %%
