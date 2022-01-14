# BrRRo
Brazilian Regime Robot for MT5

++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
The little IBrXata.py script

Simple strategy for long only portfolio.

The code should be run once per month (21 days) and the portfolio rebalanced accordingly.

The code directly implements the strategy represented by the Indice-Valor COPPEAD of CH Campani and R Leal (https://www.carlosheitorcampani.com/saiba-mais). The idea is simply to exploit the momentum of the stocks that is present on the Brazilian market.
Upon some tuning by back testing, I use contrary to the original authors, only 10 assets (instead of 20 -> less work) and 126 days=0.5y for the calculation of the performance. But you can change these parameters easily if you like. Note that for the selection of these two parameters, I did not consider the turnover factor, which may have led to this discrepancy. Also, the script is so simple that is does not consider the dividends and might as well introduced a bias from the original method.
