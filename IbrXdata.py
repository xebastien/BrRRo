# %% Input data
nb_days = '7d'    # time window before now to calculate the performance [84 (CHC) -126 days (me)]
nAssets = 10        # how many assets in your portfolio ? 10 is good
perfI = "CHC"       # ISR = Israelsen ajusted Sharpe Ratio or "CHC" = Carlos Heitor Campani, see his website
mymoney = 3012     # your wealth

#Import packages
import pandas as pd
import numpy as np
import yfinance as yf
import py_financas
import requests


# Let's find out the list of tickers of the IBrX100
#url = 'https://www.infomoney.com.br/cotacoes/ibrx100/'
url = 'https://br.advfn.com/indice/ibrx'
#url = 'https://sistemaswebb3-listados.b3.com.br/indexPage/day/IBXX?language=pt-br'
header = {
  "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36",
  "X-Requested-With": "XMLHttpRequest"
}
r = requests.get(url, headers=header)
data = pd.read_html(r.text)[3]["Ativo"]# valid for second link

#Convert to list of assets
sp = data.to_list()
# filter missing tickers from list
for k in reversed(range(len(sp))):
    if (' ' in sp[k]) == True or ('4' in sp[k]) == True :
        sp.pop(k)
    else:
        sp[k] = sp[k]+'.SA'

# missing from website 
sp.append("LINX3.SA")
sp.append("BRDT3.SA")
sp.append("BTOW3.SA")
sp.append("CNTO3.SA")
sp.append("DTEX3.SA")
sp.append("HGTX3.SA")
sp.append("VVAR3.SA")



# Fetch data for the last period
df = yf.download(sp,period = nb_days,interval="1m")
dv = df["Volume"]
df = df["Adj Close"]
dfc = df.pct_change().fillna(0)

## get daily cdi until today 
cdi = py_financas.indices.recupera_indice('cdi',df.index[0].date(),df.index[-1].date())
if cdi.index[-1] != dfc.index[-1]: # pad the last day (today if missing) with the last value
    cditoday = pd.DataFrame([cdi['cdi'].iloc[-1]],columns=['cdi'],index=[dfc.index[-1]])
    cdi = cdi.append(cditoday)

## cdi is in percent - convert to digits
cdi['cdi'] = cdi['cdi']/100 # put in percent
 # truth is with daily data, it does not change anything especially nowadays with low rates

# #%% Calculate ISR 
dfce = dfc # for future export
dfce = dfce.sub(cdi["cdi"],axis=0)
dfce = dfce.drop(dfce.index[0],axis=0)+1 # drop first line which is bad because of the differential operation
cum_dfce = dfce.cumprod(axis=0).iloc[-1]-1
std_dfce = dfce.std(axis=0)

abs_pow_dfce = cum_dfce.abs()
pow_dfce = cum_dfce.div(abs_pow_dfce,axis=0)
std_pow_dfce = std_dfce.pow(pow_dfce)
ISR = cum_dfce.div(std_pow_dfce)
ISR = ISR.sort_values(ascending=False)

# index Campani
dfce = dfc
max0_dfce =  dfce[dfce > 0].fillna(0) 
max1_dfce = -dfce[dfce < 0].fillna(0) 
max0_mean = max0_dfce.mean()
max1_mean = max1_dfce.mean()
max_div = max0_mean.div(max1_mean)
IC = max_div.sort_values(axis=0,ascending=False)


IC = IC.rename("IC")
ISR  = ISR.rename("ISR")
IC2  =IC.to_frame()
ISR2 = ISR.to_frame()
Price = df.iloc[-2].rename("Price")

ID = pd.concat([IC2, ISR2,Price,dv.mean().rename("Av. Daily. Volume")], axis=1).reindex(IC2.index)
ID = ID[ID["Price"]<10E3]# je paye pas plus de 1000 reais par actions 
ID = ID[ID["IC"]>0]      # better no asset than a loosing one
ID = ID[ID["Av. Daily. Volume"]>1E3]# minimum of liquidity

if perfI == "ISR": 
    ID = ID.sort_values(by=['ISR'],ascending=False)
else:
    ID = ID.sort_values(by=['IC'],ascending=False)

weights0 = np.ones([nAssets]) / (np.arange(0,nAssets) +3)
weights1 = weights0/np.sum(weights0)
ID.insert(4,"Weights %",0)
ID.insert(5,"Shares",0)
ID["Weights %"].iloc[0:nAssets]=weights1[0:nAssets]*100   
ID["Shares"].iloc[0:nAssets]=np.floor(mymoney/ID["Price"].iloc[0:nAssets]*weights1[0:nAssets])
ID = ID.drop("Av. Daily. Volume",axis=1)

pd.options.display.max_rows = 90

print("Porfolio assets and weights")
print(ID[0:11])




# in case yu want to export the fetched data
#dfc.to_csv("""C:\\Users\\sberu\\Documents\\Scripts\\PythonFinance\\Data_indices\\IBrX100_5ans.csv""")
#dv.to_csv("""C:\\Users\\sberu\\Documents\\Scripts\\PythonFinance\\Data_indices\\IBrX100_5ans_vol.csv""")
dfc.to_csv("""C:\\Users\\sberu\\Documents\\Scripts\\PythonFinance\\Data_indices\\IBrX100_7days.csv""")
