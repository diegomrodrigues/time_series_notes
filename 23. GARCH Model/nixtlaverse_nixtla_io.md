[Nixtla home page![light logo](https://mintlify.s3.us-west-1.amazonaws.com/nixtla/light.png)![dark logo](https://mintlify.s3.us-west-1.amazonaws.com/nixtla/dark.png)](https://nixtlaverse.nixtla.io/)

Search or ask...

Search...

Navigation

Model References

GARCH Model

## [​](https://nixtlaverse.nixtla.io/statsforecast/docs/models/garch.html\#table-of-contents)  Table of Contents

- [Introduction](https://nixtlaverse.nixtla.io/statsforecast/docs/models/garch.html#introduction)
- [GARCH Models](https://nixtlaverse.nixtla.io/statsforecast/docs/models/garch.html#model)
- [Loading libraries and data](https://nixtlaverse.nixtla.io/statsforecast/docs/models/garch.html#loading)
- [Explore data with the plot method](https://nixtlaverse.nixtla.io/statsforecast/docs/models/garch.html#plotting)
- [Split the data into training and testing](https://nixtlaverse.nixtla.io/statsforecast/docs/models/garch.html#splitting)
- [Implementation of GARCH with StatsForecast](https://nixtlaverse.nixtla.io/statsforecast/docs/models/garch.html#implementation)
- [Cross-validation](https://nixtlaverse.nixtla.io/statsforecast/docs/models/garch.html#cross_validate)
- [Model evaluation](https://nixtlaverse.nixtla.io/statsforecast/docs/models/garch.html#evaluate)
- [References](https://nixtlaverse.nixtla.io/statsforecast/docs/models/garch.html#references)

## [​](https://nixtlaverse.nixtla.io/statsforecast/docs/models/garch.html\#introduction)  Introduction

The Generalized Autoregressive Conditional Heteroskedasticity (GARCH)
model is a statistical technique used to model and predict volatility in
financial and economic time series. It was developed by Robert Engle in
1982 as an extension of the Autoregressive Conditional
Heteroskedasticity (ARCH) model proposed by Andrew Lo and Craig
MacKinlay in 1988.

The GARCH model allows capturing the presence of conditional
heteroscedasticity in time series data, that is, the presence of
fluctuations in the variance of a time series as a function of time.
This is especially useful in financial data analysis, where volatility
can be an important measure of risk.

The GARCH model has become a fundamental tool in the analysis of
financial time series and has been used in a wide variety of
applications, from risk management to forecasting prices of shares and
other financial values.

## [​](https://nixtlaverse.nixtla.io/statsforecast/docs/models/garch.html\#definition-of-garch-models)  Definition of GARCH Models

**Definition 1.** A GARCH(p,q)\\text{GARCH}(p,q)GARCH(p,q) model with order (p≥1,q≥0)(p≥1,q≥0)(p≥1,q≥0) is
of the form

{Xt=σtεtσt2=ω+∑i=1pαiXt−i2+∑j=1qβjσt−j2
\\begin{equation}
\\begin{cases}
X\_t = \\sigma\_t \\varepsilon\_t\\\
\\sigma\_{t}^2 = \\omega + \\sum\_{i=1}^{p} \\alpha\_i X\_{t-i}^2 + \\sum\_{j=1}^{q} \\beta\_j \\sigma\_{t-j}^2
\\end{cases}
\\end{equation}
{Xt​=σt​εt​σt2​=ω+∑i=1p​αi​Xt−i2​+∑j=1q​βj​σt−j2​​​​

where ω≥0,αi≥0,βj≥0,αp>0\\omega ≥0,\\alpha\_i ≥0,\\beta\_j ≥0,\\alpha\_p >0ω≥0,αi​≥0,βj​≥0,αp​>0 ,and βq>0\\beta\_q >0βq​>0
are constants,εt∼iid(0,1)\\varepsilon\_t \\sim iid(0,1)εt​∼iid(0,1), and εt\\varepsilon\_tεt​ is
independent of {Xk;k≤t−1}\\{X\_k;k ≤ t − 1 \\}{Xk​;k≤t−1}. A stochastic process XtX\_tXt​ is
called a GARCH(p,q)\\text{GARCH}(p, q )GARCH(p,q) process if it satisfies Eq. (1).

In practice, it has been found that for some time series, the
ARCH(p)\\text{ARCH}(p)ARCH(p) model defined by (1) will provide an adequate fit only
if the order ppp is large. By allowing past volatilities to affect the
present volatility in (1), a more parsimonious model may result. That is
why we need
[`GARCH`](https://nixtla.github.io/statsforecast/src/core/models.html#garch)
models. Besides, note the condition that the order p≥1p ≥ 1p≥1. The **GARCH**
**model** in Definition 1 has the properties as follows.

Proposition 1. If XtX\_tXt​ is a GARCH(p,q)\\text{GARCH}(p, q)GARCH(p,q) process defined in (1)
and ∑i=1pαi+∑j=1qβj<1\\sum\_{i=1}^{p} \\alpha\_{i} + \\sum\_{j=1}^{q} \\beta\_j <1∑i=1p​αi​+∑j=1q​βj​<1,then the
following propositions hold.

- Xt2X\_{t}^2Xt2​ follows the ARMA(m,q)\\text{ARMA}(m, q )ARMA(m,q) model

Xt2=ω+∑i=1m(αi+βi)Xt−i2+ηt−∑j=1qβjηt−jX\_{t}^2=\\omega +\\sum\_{i=1}^{m} (\\alpha\_i + \\beta\_i )X\_{t-i}^2 + \\eta\_t − \\sum\_{j=1}^q \\beta\_j \\eta\_{t-j}Xt2​=ω+∑i=1m​(αi​+βi​)Xt−i2​+ηt​−∑j=1q​βj​ηt−j​

where αi=0\\alpha\_i =0αi​=0 for i>p,βj=0i >p,βj =0i>p,βj=0 for j>q,m=max(p,q)j >q,m=max(p,q)j>q,m=max(p,q), and
ηt=σt2(εt2−1)\\eta\_t =\\sigma\_{t}^2 (\\varepsilon\_{t}^2 −1)ηt​=σt2​(εt2​−1).

- XtX\_tXt​ is a white noise with

E(X)=0,E(Xt+hXt)=0  for anyh≠0,Var(Xt)=ω1−∑i=1m(αi+βi)E(X)=0, E(X\_{t+h} X\_t )=0 \ \ \\text{for} \ any \ \ h \\neq 0, Var(X\_t)= \\frac{\\omega}{1-\\sum\_{i=1}^{m} (\\alpha\_i + \\beta\_i )}E(X)=0,E(Xt+h​Xt​)=0foranyh=0,Var(Xt​)=1−∑i=1m​(αi​+βi​)ω​

- σt2\\sigma\_{t}^2σt2​ is the conditional variance of XtX\_tXt​ , that is, we
have

E(Xt∣Ft−1)=0,σt2=Var(Xt2∣Ft−1).E(X\_t\|\\mathscr{F}\_{t−1}) = 0, \\sigma\_{t}^2 = Var(X\_{t}^2\|\\mathscr{F}\_{t−1}).E(Xt​∣Ft−1​)=0,σt2​=Var(Xt2​∣Ft−1​).

- Model (1) reflects the fat tails and volatility clustering.

Although an asset return series can usually be seen as a white noise,
there exists such a return series so that it may be autocorrelated. What
is more, a given original time series is not necessarily a return
series, and at the same time, its values may be negative. If a time
series is autocorrelated, we must first build an adequate model (e.g.,
an ARMA model) for the series in order to remove any autocorrelation in
it. Then check whether the residual series has an ARCH effect, and if
yes then we further model the residuals. In other words, if a time
series YtY\_tYt​ is autocorrelated and has ARCH effect, then a GARCH model
that can capture the features of YtY\_tYt​t should be of the form

where Eq. (2) is referred to as the mean equation (model) and Eq. (3) is
known as the volatility (variance) equation (model), and ZtZ\_tZt​ is a
representative of exogenous regressors. If YtY\_tYt​ is a return series,
then typically Yt=r+XtY\_t = r + X\_tYt​=r+Xt​ where rrr is a constant that means the
expected returns is fixed.

### [​](https://nixtlaverse.nixtla.io/statsforecast/docs/models/garch.html\#advantages-and-disadvantages-of-the-generalized-autoregressive-conditional-heteroskedasticity-garch-model)  Advantages and disadvantages of the Generalized Autoregressive Conditional Heteroskedasticity (GARCH) Model

| Advantages | Disadvantages |
| --- | --- |
| 1\. 1. Flexible model: The GARCH model is flexible and can fit different types of time series data with different volatility patterns. | 1\. Requires a large amount of data: The GARCH model requires a large amount of data to accurately estimate the model parameters. |
| 2\. Ability to model volatility: The GARCH model is capable of modeling the volatility and heteroscedasticity of a time series, which can improve the accuracy of forecasts. | 2\. Sensitive to the model specification: The GARCH model is sensitive to the model specification and can be difficult to estimate if incorrectly specified. |
| 3\. It incorporates past information: The GARCH model incorporates past information on the volatility of the time series, which makes it useful for predicting future volatility. | 3\. It can be computationally expensive: The GARCH model can be computationally expensive, especially if more complex models are used. |
| 4\. Allows the inclusion of exogenous variables: The GARCH model can be extended to include exogenous variables, which can improve the accuracy of the predictions. | 4\. It does not consider extreme events: The GARCH model does not consider extreme or unexpected events in the time series, which can affect the accuracy of the predictions in situations of high volatility. |
| 5\. The GARCH model makes it possible to model conditional heteroscedasticity, that is, the variation of the variance of a time series as a function of time and of the previous values of the time series itself. | 5\. The GARCH model assumes that the time series errors are normally distributed, which may not be true in practice. If the errors are not normally distributed, the model may produce inaccurate estimates of volatility. |
| 6\. The GARCH model can be used to estimate the value at risk (VaR) and the conditional value at risk (CVaR) of an investment portfolio. |  |

### [​](https://nixtlaverse.nixtla.io/statsforecast/docs/models/garch.html\#the-generalized-autoregressive-conditional-heteroskedasticity-garch-model-can-be-applied-in-several-fields)  The Generalized Autoregressive Conditional Heteroskedasticity (GARCH) model can be applied in several fields

The Generalized Autoregressive Conditional Heteroskedasticity (GARCH)
model can be applied in a wide variety of areas where time series
volatility is required to be modeled and predicted. Some of the areas in
which the GARCH model can be applied are:

01. **Financial markets:** the GARCH model is widely used to model the
    volatility (risk) of returns on financial assets such as stocks,
    bonds, currencies, etc. It allows you to capture the changing nature
    of volatility.

02. **Commodity prices:** the prices of raw materials such as oil, gold,
    grains, etc. they exhibit conditional volatility that can be modeled
    with GARCH.

03. **Credit risk:** the risk of non-payment of loans and bonds also
    presents volatility over time that suits GARCH well.

04. **Economic time series:** macroeconomic indicators such as
    inflation, GDP, unemployment, etc. they have conditional volatility
    modelable with GARCH.

05. **Implicit volatility:** the GARCH model allows estimating the
    implicit volatility in financial options.

06. **Forecasts:** GARCH allows conditional volatility forecasts to be
    made in any time series.

07. **Risk analysis:** GARCH is useful for measuring and managing the
    risk of investment portfolios and assets.

08. **Finance:** The GARCH model is widely used in finance to model the
    price volatility of financial assets, such as stocks, bonds, and
    currencies.

09. **Economics:** The GARCH model is used in economics to model the
    volatility of the prices of goods and services, inflation, and other
    economic indicators.

10. **Environmental sciences:** The GARCH model is applied in
    environmental sciences to model the volatility of variables such as
    temperature, precipitation, and air quality.

11. **Social sciences:** The GARCH model is used in the social sciences
    to model the volatility of variables such as crime, migration, and
    employment.

12. **Engineering:** The GARCH model is applied in engineering to model
    the volatility of variables such as the demand for electrical
    energy, industrial production, and vehicular traffic.

13. **Health sciences:** The GARCH model is used in health sciences to
    model the volatility of variables such as the number of cases of
    infectious diseases and the prices of medicines.


The GARCH Model is applicable in any context where it is required to
model and forecast heterogeneous conditional volatility in time series,
especially in finance and economics.

## [​](https://nixtlaverse.nixtla.io/statsforecast/docs/models/garch.html\#loading-libraries-and-data)  Loading libraries and data

> **Tip**
>
> Statsforecast will be needed. To install, see
> [instructions](https://nixtlaverse.nixtla.io/statsforecast/docs/getting-started/installation.html).

Next, we import plotting libraries and configure the plotting style.

Copy

```python
import matplotlib.pyplot as plt
from statsmodels.graphics.tsaplots import plot_acf
from statsmodels.graphics.tsaplots import plot_pacf
plt.style.use('fivethirtyeight')
plt.rcParams['lines.linewidth'] = 1.5
dark_style = {
    'figure.facecolor': '#212946',
    'axes.facecolor': '#212946',
    'savefig.facecolor':'#212946',
    'axes.grid': True,
    'axes.grid.which': 'both',
    'axes.spines.left': False,
    'axes.spines.right': False,
    'axes.spines.top': False,
    'axes.spines.bottom': False,
    'grid.color': '#2A3459',
    'grid.linewidth': '1',
    'text.color': '0.9',
    'axes.labelcolor': '0.9',
    'xtick.color': '0.9',
    'ytick.color': '0.9',
    'font.size': 12 }
plt.rcParams.update(dark_style)

from pylab import rcParams
rcParams['figure.figsize'] = (18,7)

```

### [​](https://nixtlaverse.nixtla.io/statsforecast/docs/models/garch.html\#read-data)  Read Data

Let’s pull the S&P500 stock data from the Yahoo Finance site.

Copy

```python
import datetime

import pandas as pd
import time
import yfinance as yf

ticker = '^GSPC'
period1 = datetime.datetime(2015, 1, 1)
period2 = datetime.datetime(2023, 9, 22)
interval = '1d' # 1d, 1m

SP_500 = yf.download(ticker, start=period1, end=period2, interval=interval, progress=False)
SP_500 = SP_500.reset_index()

SP_500.head()

```

| Price | Date | Adj Close | Close | High | Low | Open | Volume |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Ticker |  | ^GSPC | ^GSPC | ^GSPC | ^GSPC | ^GSPC | ^GSPC |
| 0 | 2015-01-02 00:00:00+00:00 | 2058.199951 | 2058.199951 | 2072.360107 | 2046.040039 | 2058.899902 | 2708700000 |
| 1 | 2015-01-05 00:00:00+00:00 | 2020.579956 | 2020.579956 | 2054.439941 | 2017.339966 | 2054.439941 | 3799120000 |
| 2 | 2015-01-06 00:00:00+00:00 | 2002.609985 | 2002.609985 | 2030.250000 | 1992.439941 | 2022.150024 | 4460110000 |
| 3 | 2015-01-07 00:00:00+00:00 | 2025.900024 | 2025.900024 | 2029.609985 | 2005.550049 | 2005.550049 | 3805480000 |
| 4 | 2015-01-08 00:00:00+00:00 | 2062.139893 | 2062.139893 | 2064.080078 | 2030.609985 | 2030.609985 | 3934010000 |

Copy

```python
df=SP_500[["Date","Close"]]

```

The input to StatsForecast is always a data frame in long format with
three columns: unique\_id, ds and y:

- The `unique_id` (string, int or category) represents an identifier
for the series.

- The `ds` (datestamp) column should be of a format expected by
Pandas, ideally YYYY-MM-DD for a date or YYYY-MM-DD HH:MM:SS for a
timestamp.

- The `y` (numeric) represents the measurement we wish to forecast.


Copy

```python
df["unique_id"]="1"
df.columns=["ds", "y", "unique_id"]
df.head()

```

|  | ds | y | unique\_id |
| --- | --- | --- | --- |
| 0 | 2015-01-02 00:00:00+00:00 | 2058.199951 | 1 |
| 1 | 2015-01-05 00:00:00+00:00 | 2020.579956 | 1 |
| 2 | 2015-01-06 00:00:00+00:00 | 2002.609985 | 1 |
| 3 | 2015-01-07 00:00:00+00:00 | 2025.900024 | 1 |
| 4 | 2015-01-08 00:00:00+00:00 | 2062.139893 | 1 |

Copy

```python
print(df.dtypes)

```

Copy

```text
ds           datetime64[ns, UTC]
y                        float64
unique_id                 object
dtype: object

```

## [​](https://nixtlaverse.nixtla.io/statsforecast/docs/models/garch.html\#explore-data-with-the-plot-method)  Explore data with the plot method

Plot a series using the plot method from the StatsForecast class. This
method prints a random series from the dataset and is useful for basic
EDA.

Copy

```python
from statsforecast import StatsForecast

StatsForecast.plot(df)

```

![](https://mintlify.s3.us-west-1.amazonaws.com/nixtla/statsforecast/docs/models/GARCH_files/figure-markdown_strict/cell-7-output-1.png)

### [​](https://nixtlaverse.nixtla.io/statsforecast/docs/models/garch.html\#the-augmented-dickey-fuller-test)  The Augmented Dickey-Fuller Test

An Augmented Dickey-Fuller (ADF) test is a type of statistical test that
determines whether a unit root is present in time series data. Unit
roots can cause unpredictable results in time series analysis. A null
hypothesis is formed in the unit root test to determine how strongly
time series data is affected by a trend. By accepting the null
hypothesis, we accept the evidence that the time series data is not
stationary. By rejecting the null hypothesis or accepting the
alternative hypothesis, we accept the evidence that the time series data
is generated by a stationary process. This process is also known as
stationary trend. The values of the ADF test statistic are negative.
Lower ADF values indicate a stronger rejection of the null hypothesis.

Augmented Dickey-Fuller Test is a common statistical test used to test
whether a given time series is stationary or not. We can achieve this by
defining the null and alternate hypothesis.

Null Hypothesis: Time Series is non-stationary. It gives a
time-dependent trend. Alternate Hypothesis: Time Series is stationary.
In another term, the series doesn’t depend on time.

ADF or t Statistic < critical values: Reject the null hypothesis, time
series is stationary. ADF or t Statistic > critical values: Failed to
reject the null hypothesis, time series is non-stationary.

Let’s check if our series that we are analyzing is a stationary series.
Let’s create a function to check, using the `Dickey Fuller` test

Copy

```python
from statsmodels.tsa.stattools import adfuller

def Augmented_Dickey_Fuller_Test_func(series , column_name):
    print (f'Dickey-Fuller test results for columns: {column_name}')
    dftest = adfuller(series, autolag='AIC')
    dfoutput = pd.Series(dftest[0:4], index=['Test Statistic','p-value','No Lags Used','Number of observations used'])
    for key,value in dftest[4].items():
       dfoutput['Critical Value (%s)'%key] = value
    print (dfoutput)
    if dftest[1] <= 0.05:
        print("Conclusion:====>")
        print("Reject the null hypothesis")
        print("The data is stationary")
    else:
        print("Conclusion:====>")
        print("The null hypothesis cannot be rejected")
        print("The data is not stationary")

```

Copy

```python
Augmented_Dickey_Fuller_Test_func(df["y"],'S&P500')

```

Copy

```text
Dickey-Fuller test results for columns: S&P500
Test Statistic          -0.814971
p-value                  0.814685
No Lags Used            10.000000
                          ...
Critical Value (1%)     -3.433341
Critical Value (5%)     -2.862861
Critical Value (10%)    -2.567473
Length: 7, dtype: float64
Conclusion:====>
The null hypothesis cannot be rejected
The data is not stationary

```

In the previous result we can see that the `Augmented_Dickey_Fuller`
test gives us a `p-value` of 0.864700, which tells us that the null
hypothesis cannot be rejected, and on the other hand the data of our
series are not stationary.

We need to differentiate our time series, in order to convert the data
to stationary.

### [​](https://nixtlaverse.nixtla.io/statsforecast/docs/models/garch.html\#return-series)  Return Series

Since the 1970s, the financial industry has been very prosperous with
advancement of computer and Internet technology. Trade of financial
products (including various derivatives) generates a huge amount of data
which form financial time series. For finance, the return on a financial
product is most interesting, and so our attention focuses on the return
series. If PtP\_tPt​ is the closing price at time t for a certain financial
product, then the return on this product is

Xt=(Pt−Pt−1)Pt−1≈log(Pt)−log(Pt−1).X\_t = \\frac{(P\_t − P\_{t−1})}{P\_{t−1}} ≈ log(P\_t ) − log(P\_{t−1}).Xt​=Pt−1​(Pt​−Pt−1​)​≈log(Pt​)−log(Pt−1​).

It is return series {Xt}\\{X\_t \\}{Xt​} that have been much independently
studied. And important stylized features which are common across many
instruments, markets, and time periods have been summarized. Note that
if you purchase the financial product, then it becomes your asset, and
its returns become your asset returns. Now let us look at the following
examples.

We can estimate the series of returns using the
[pandas](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.pct_change.html),
`DataFrame.pct_change()` function. The `pct_change()` function has a
periods parameter whose default value is 1. If you want to calculate a
30-day return, you must change the value to 30.

Copy

```python
df['return'] = 100 * df["y"].pct_change()
df.dropna(inplace=True, how='any')
df.head()

```

|  | ds | y | unique\_id | return |
| --- | --- | --- | --- | --- |
| 1 | 2015-01-05 00:00:00+00:00 | 2020.579956 | 1 | -1.827811 |
| 2 | 2015-01-06 00:00:00+00:00 | 2002.609985 | 1 | -0.889347 |
| 3 | 2015-01-07 00:00:00+00:00 | 2025.900024 | 1 | 1.162984 |
| 4 | 2015-01-08 00:00:00+00:00 | 2062.139893 | 1 | 1.788828 |
| 5 | 2015-01-09 00:00:00+00:00 | 2044.810059 | 1 | -0.840381 |

Copy

```python
import plotly.express as px
fig = px.line(df, x=df["ds"], y="return",title="SP500 Return Chart",template = "plotly_dark")
fig.show()

```

![](https://mintlify.s3.us-west-1.amazonaws.com/nixtla/statsforecast/docs/models/GARCH_files/figure-markdown_strict/cell-11-output-2.png)

### [​](https://nixtlaverse.nixtla.io/statsforecast/docs/models/garch.html\#creating-squared-returns)  Creating Squared Returns

Copy

```python
df['sq_return'] = df["return"].mul(df["return"])
df.head()

```

|  | ds | y | unique\_id | return | sq\_return |
| --- | --- | --- | --- | --- | --- |
| 1 | 2015-01-05 00:00:00+00:00 | 2020.579956 | 1 | -1.827811 | 3.340891 |
| 2 | 2015-01-06 00:00:00+00:00 | 2002.609985 | 1 | -0.889347 | 0.790938 |
| 3 | 2015-01-07 00:00:00+00:00 | 2025.900024 | 1 | 1.162984 | 1.352532 |
| 4 | 2015-01-08 00:00:00+00:00 | 2062.139893 | 1 | 1.788828 | 3.199906 |
| 5 | 2015-01-09 00:00:00+00:00 | 2044.810059 | 1 | -0.840381 | 0.706240 |

### [​](https://nixtlaverse.nixtla.io/statsforecast/docs/models/garch.html\#returns-vs-squared-returns)  Returns vs Squared Returns

Copy

```python
from plotly.subplots import make_subplots
import plotly.graph_objects as go

fig = make_subplots(rows=1, cols=2)

fig.add_trace(go.Scatter(x=df["ds"], y=df["return"],
                         mode='lines',
                         name='return'),
row=1, col=1
)

fig.add_trace(go.Scatter(x=df["ds"], y=df["sq_return"],
                         mode='lines',
                         name='sq_return'),
    row=1, col=2
)

fig.update_layout(height=600, width=800, title_text="Returns vs Squared Returns", template = "plotly_dark")
fig.show()

```

![](https://mintlify.s3.us-west-1.amazonaws.com/nixtla/statsforecast/docs/models/GARCH_files/figure-markdown_strict/cell-13-output-1.png)

Copy

```python
from scipy.stats import probplot, moment
from statsmodels.tsa.stattools import adfuller, q_stat, acf
import numpy as np
import seaborn as sns

def plot_correlogram(x, lags=None, title=None):
    lags = min(10, int(len(x)/5)) if lags is None else lags
    fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(14, 8))
    x.plot(ax=axes[0][0], title='Return')
    x.rolling(21).mean().plot(ax=axes[0][0], c='k', lw=1)
    q_p = np.max(q_stat(acf(x, nlags=lags), len(x))[1])
    stats = f'Q-Stat: {np.max(q_p):>8.2f}\nADF: {adfuller(x)[1]:>11.2f}'
    axes[0][0].text(x=.02, y=.85, s=stats, transform=axes[0][0].transAxes)
    probplot(x, plot=axes[0][1])
    mean, var, skew, kurtosis = moment(x, moment=[1, 2, 3, 4])
    s = f'Mean: {mean:>12.2f}\nSD: {np.sqrt(var):>16.2f}\nSkew: {skew:12.2f}\nKurtosis:{kurtosis:9.2f}'
    axes[0][1].text(x=.02, y=.75, s=s, transform=axes[0][1].transAxes)
    plot_acf(x=x, lags=lags, zero=False, ax=axes[1][0])
    plot_pacf(x, lags=lags, zero=False, ax=axes[1][1])
    axes[1][0].set_xlabel('Lag')
    axes[1][1].set_xlabel('Lag')
    fig.suptitle(title+ f'Dickey-Fuller: {adfuller(x)[1]:>11.2f}', fontsize=14)
    sns.despine()
    fig.tight_layout()
    fig.subplots_adjust(top=.9)

```

Copy

```python
plot_correlogram(df["return"], lags=30, title="Time Series Analysis plot \n")

```

![](https://mintlify.s3.us-west-1.amazonaws.com/nixtla/statsforecast/docs/models/GARCH_files/figure-markdown_strict/cell-15-output-1.png)

### [​](https://nixtlaverse.nixtla.io/statsforecast/docs/models/garch.html\#ljung-box-test)  Ljung-Box Test

Ljung-Box is a test for autocorrelation that we can use in tandem with
our ACF and PACF plots. The Ljung-Box test takes our data, optionally
either lag values to test, or the largest lag value to consider, and
whether to compute the Box-Pierce statistic. Ljung-Box and Box-Pierce
are two similar test statisitcs, Q , that are compared against a
chi-squared distribution to determine if the series is white noise. We
might use the Ljung-Box test on the residuals of our model to look for
autocorrelation, ideally our residuals would be white noise.

- Ho : The data are independently distributed, no autocorrelation.
- Ha : The data are not independently distributed; they exhibit serial
correlation.

The Ljung-Box with the Box-Pierce option will return, for each lag, the
Ljung-Box test statistic, Ljung-Box p-values, Box-Pierce test statistic,
and Box-Pierce p-values.

If p<α(0.05)p<\\alpha (0.05)p<α(0.05) we reject the null hypothesis.

Copy

```python
from statsmodels.stats.diagnostic import acorr_ljungbox

ljung_res = acorr_ljungbox(df["return"], lags= 40, boxpierce=True)

ljung_res.head()

```

|  | lb\_stat | lb\_pvalue | bp\_stat | bp\_pvalue |
| --- | --- | --- | --- | --- |
| 1 | 49.222273 | 2.285409e-12 | 49.155183 | 2.364927e-12 |
| 2 | 62.991348 | 2.097020e-14 | 62.899234 | 2.195861e-14 |
| 3 | 63.944944 | 8.433622e-14 | 63.850663 | 8.834380e-14 |
| 4 | 74.343652 | 2.742989e-15 | 74.221024 | 2.911751e-15 |
| 5 | 80.234862 | 7.494100e-16 | 80.093498 | 8.022242e-16 |

## [​](https://nixtlaverse.nixtla.io/statsforecast/docs/models/garch.html\#split-the-data-into-training-and-testing)  Split the data into training and testing

Let’s divide our data into sets 1. Data to train our
[`GARCH`](https://nixtla.github.io/statsforecast/src/core/models.html#garch)
model 2. Data to test our model

For the test data we will use the last 30 day to test and evaluate the
performance of our model.

Copy

```python
df=df[["ds","unique_id","return"]]
df.columns=["ds", "unique_id", "y"]

```

Copy

```python
train = df[df.ds<='2023-05-31'] # Let's forecast the last 30 days
test = df[df.ds>'2023-05-31']

```

Copy

```python
train.shape, test.shape

```

Copy

```text
((2116, 3), (78, 3))

```

## [​](https://nixtlaverse.nixtla.io/statsforecast/docs/models/garch.html\#implementation-of-garch-with-statsforecast)  Implementation of GARCH with StatsForecast

### [​](https://nixtlaverse.nixtla.io/statsforecast/docs/models/garch.html\#load-libraries)  Load libraries

Copy

```python
from statsforecast import StatsForecast
from statsforecast.models import GARCH

```

### [​](https://nixtlaverse.nixtla.io/statsforecast/docs/models/garch.html\#instantiating-models)  Instantiating Models

Import and instantiate the models. Setting the argument is sometimes
tricky. This article on [Seasonal\\
periods](https://robjhyndman.com/hyndsight/seasonal-periods/) by the
master, Rob Hyndmann, can be useful.season\_length.

Copy

```python
season_length = 7 # Dayly data
horizon = len(test) # number of predictions biasadj=True, include_drift=True,

models = [GARCH(1,1),\
          GARCH(1,2),\
          GARCH(2,2),\
          GARCH(2,1),\
          GARCH(3,1),\
          GARCH(3,2),\
          GARCH(3,3),\
          GARCH(1,3),\
          GARCH(2,3)]

```

We fit the models by instantiating a new StatsForecast object with the
following parameters:

models: a list of models. Select the models you want from models and
import them.

- `freq:` a string indicating the frequency of the data. (See [pandas’\\
available\\
frequencies](https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#offset-aliases).)

- `n_jobs:` n\_jobs: int, number of jobs used in the parallel
processing, use -1 for all cores.

- `fallback_model:` a model to be used if a model fails.


Any settings are passed into the constructor. Then you call its fit
method and pass in the historical data frame.

Copy

```python
sf = StatsForecast(
    models=models,
    freq='C', # custom business day frequency
)

```

## [​](https://nixtlaverse.nixtla.io/statsforecast/docs/models/garch.html\#cross-validation)  Cross-validation

We have built different GARCH models, so we need to determine which is
the best model to then be able to train it and thus be able to make the
predictions. To know which is the best model we go to the Cross
Validation.

With time series data, Cross Validation is done by defining a sliding
window across the historical data and predicting the period following
it. This form of cross-validation allows us to arrive at a better
estimation of our model’s predictive abilities across a wider range of
temporal instances while also keeping the data in the training set
contiguous as is required by our models.

The following graph depicts such a Cross Validation Strategy:

![](https://raw.githubusercontent.com/Nixtla/statsforecast/main/nbs/imgs/ChainedWindows.gif)

### [​](https://nixtlaverse.nixtla.io/statsforecast/docs/models/garch.html\#perform-time-series-cross-validation)  Perform time series cross-validation

Cross-validation of time series models is considered a best practice but
most implementations are very slow. The statsforecast library implements
cross-validation as a distributed operation, making the process less
time-consuming to perform. If you have big datasets you can also perform
Cross Validation in a distributed cluster using Ray, Dask or Spark.

The cross\_validation method from the StatsForecast class takes the
following arguments.

- `df:` training data frame

- `h (int):` represents h steps into the future that are being
forecasted. In this case, 12 months ahead.

- `step_size (int):` step size between each window. In other words:
how often do you want to run the forecasting processes.

- `n_windows(int):` number of windows used for cross validation. In
other words: what number of forecasting processes in the past do you
want to evaluate.


Copy

```python
crossvalidation_df = sf.cross_validation(df=train,
                                         h=horizon,
                                         step_size=6,
                                         n_windows=5)

```

The crossvaldation\_df object is a new data frame that includes the
following columns:

- `unique_id:` series identifier
- `ds:` datestamp or temporal index
- `cutoff:` the last datestamp or temporal index for the n\_windows.
- `y:` true value
- `"model":` columns with the model’s name and fitted value.

Copy

```python
crossvalidation_df

```

|  | unique\_id | ds | cutoff | y | GARCH(1,1) | GARCH(1,2) | GARCH(2,2) | GARCH(2,1) | GARCH(3,1) | GARCH(3,2) | GARCH(3,3) | GARCH(1,3) | GARCH(2,3) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | 1 | 2023-01-04 00:00:00+00:00 | 2023-01-03 00:00:00+00:00 | 0.753897 | 1.678755 | 1.678412 | 1.680475 | 1.686649 | 1.719494 | 2.210902 | 1.702743 | 1.647114 | 1.637795 |
| 1 | 1 | 2023-01-05 00:00:00+00:00 | 2023-01-03 00:00:00+00:00 | -1.164553 | -0.728069 | -0.745487 | -0.730648 | -0.722156 | -0.738119 | -0.824748 | -0.755277 | -0.740976 | -0.744150 |
| 2 | 1 | 2023-01-06 00:00:00+00:00 | 2023-01-03 00:00:00+00:00 | 2.284078 | -0.589733 | -0.582982 | -0.590078 | -0.598076 | -0.587109 | -0.866347 | -0.571160 | -0.587807 | -0.584692 |
| … | … | … | … | … | … | … | … | … | … | … | … | … | … |
| 387 | 1 | 2023-05-26 00:00:00+00:00 | 2023-02-07 00:00:00+00:00 | 1.304909 | -1.697814 | -1.694747 | -1.702537 | -1.735631 | -1.729903 | -1.712997 | -1.663399 | -1.702160 | -1.687723 |
| 388 | 1 | 2023-05-30 00:00:00+00:00 | 2023-02-07 00:00:00+00:00 | 0.001660 | -0.326945 | -0.337504 | -0.329686 | -0.330120 | -0.334717 | -0.327583 | -0.330260 | -0.338245 | -0.332412 |
| 389 | 1 | 2023-05-31 00:00:00+00:00 | 2023-02-07 00:00:00+00:00 | -0.610862 | 0.807625 | 0.787054 | 0.807819 | 0.841536 | 0.811702 | 0.836159 | 0.772193 | 0.801933 | 0.804526 |

Copy

```python
from utilsforecast.evaluation import evaluate
from utilsforecast.losses import rmse

```

Copy

```python
evals = evaluate(crossvalidation_df.drop(columns='cutoff'), metrics=[rmse], agg_fn='mean')
evals

```

|  | metric | GARCH(1,1) | GARCH(1,2) | GARCH(2,2) | GARCH(2,1) | GARCH(3,1) | GARCH(3,2) | GARCH(3,3) | GARCH(1,3) | GARCH(2,3) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | rmse | 1.383143 | 1.526258 | 1.481056 | 1.389969 | 1.453538 | 1.539906 | 1.392352 | 1.515796 | 1.389061 |

Copy

```python
evals.drop(columns='metric').loc[0].idxmin()

```

Copy

```text
'GARCH(1,1)'

```

**Note:** This result can vary depending on the data and period you use
to train and test the model, and the models you want to test. This is an
example, where the objective is to be able to teach a methodology for
the use of
[`StatsForecast`](https://nixtla.github.io/statsforecast/src/core/core.html#statsforecast),
and in particular the GARCH model and the parameters used in Cross
Validation to determine the best model for this example.

In the previous result it can be seen that the best model is the model
GARCH(1,1)\\text{GARCH}(1,1)GARCH(1,1)

With this result found using Cross Validation to determine which is the
best model, we are going to continue training our model, to then make
the predictions.

### [​](https://nixtlaverse.nixtla.io/statsforecast/docs/models/garch.html\#fit-the-model)  Fit the Model

Copy

```python
season_length = 7 # Dayly data
horizon = len(test) # number of predictions biasadj=True, include_drift=True,

models = [GARCH(1,1)]

```

Copy

```python
sf = StatsForecast(models=models,
                   freq='C', # custom business day frequency
                  )

```

Copy

```python
sf.fit(df=train)

```

Copy

```text
StatsForecast(models=[GARCH(1,1)])

```

Let’s see the results of our Theta model. We can observe it with the
following instruction:

Copy

```python
result=sf.fitted_[0,0].model_
result

```

Copy

```text
{'p': 1,
 'q': 1,
 'coeff': array([0.03745049, 0.18399111, 0.7890637 ]),
 'message': 'Optimization terminated successfully',
 'y_vals': array([-0.61086242]),
 'sigma2_vals': array([0.76298402]),
 'fitted': array([        nan,  2.14638896, -0.76426268, ..., -0.19747638,\
         0.76993462,  0.13183178]),
 'actual_residuals': array([        nan, -3.03573613,  1.92724695, ...,  1.50238505,\
        -0.7682743 , -0.7426942 ])}

```

Let us now visualize the residuals of our models.

As we can see, the result obtained above has an output in a dictionary,
to extract each element from the dictionary we are going to use the
`.get()` function to extract the element and then we are going to save
it in a `pd.DataFrame()`.

Copy

```python
residual=pd.DataFrame(result.get("actual_residuals"), columns=["residual Model"])
residual

```

|  | residual Model |
| --- | --- |
| 0 | NaN |
| 1 | -3.035736 |
| 2 | 1.927247 |
| … | … |
| 2113 | 1.502385 |
| 2114 | -0.768274 |
| 2115 | -0.742694 |

Copy

```python
from scipy import stats

fig, axs = plt.subplots(nrows=2, ncols=2)

# plot[1,1]
residual.plot(ax=axs[0,0])
axs[0,0].set_title("Residuals");

# plot
sns.distplot(residual, ax=axs[0,1]);
axs[0,1].set_title("Density plot - Residual");

# plot
stats.probplot(residual["residual Model"], dist="norm", plot=axs[1,0])
axs[1,0].set_title('Plot Q-Q')

# plot
plot_acf(residual,  lags=35, ax=axs[1,1],color="fuchsia")
axs[1,1].set_title("Autocorrelation");

plt.show();

```

![](https://mintlify.s3.us-west-1.amazonaws.com/nixtla/statsforecast/docs/models/GARCH_files/figure-markdown_strict/cell-33-output-1.png)

### [​](https://nixtlaverse.nixtla.io/statsforecast/docs/models/garch.html\#forecast-method)  Forecast Method

If you want to gain speed in productive settings where you have multiple
series or models we recommend using the
[`StatsForecast.forecast`](https://nixtla.github.io/statsforecast/src/core/core.html#statsforecast.forecast)
method instead of `.fit` and `.predict`.

The main difference is that the `.forecast` doest not store the fitted
values and is highly scalable in distributed environments.

The forecast method takes two arguments: forecasts next `h` (horizon)
and `level`.

- `h (int):` represents the forecast h steps into the future. In this
case, 12 months ahead.

- `level (list of floats):` this optional parameter is used for
probabilistic forecasting. Set the level (or confidence percentile)
of your prediction interval. For example, `level=[90]` means that
the model expects the real value to be inside that interval 90% of
the times.


The forecast object here is a new data frame that includes a column with
the name of the model and the y hat values, as well as columns for the
uncertainty intervals. Depending on your computer, this step should take
around 1min. (If you want to speed things up to a couple of seconds,
remove the AutoModels like
[`ARIMA`](https://nixtla.github.io/statsforecast/src/core/models.html#arima)
and
[`Theta`](https://nixtla.github.io/statsforecast/src/core/models.html#theta))

Copy

```python
Y_hat = sf.forecast(df=train, h=horizon, fitted=True)
Y_hat.head()

```

|  | unique\_id | ds | GARCH(1,1) |
| --- | --- | --- | --- |
| 0 | 1 | 2023-06-01 00:00:00+00:00 | 1.366914 |
| 1 | 1 | 2023-06-02 00:00:00+00:00 | -0.593121 |
| 2 | 1 | 2023-06-05 00:00:00+00:00 | -0.485200 |
| 3 | 1 | 2023-06-06 00:00:00+00:00 | -0.927145 |
| 4 | 1 | 2023-06-07 00:00:00+00:00 | 0.766640 |

Copy

```python
Y_hat = sf.forecast(df=train, h=horizon, fitted=True, level=[95])
Y_hat.head()

```

|  | unique\_id | ds | GARCH(1,1) | GARCH(1,1)-lo-95 | GARCH(1,1)-hi-95 |
| --- | --- | --- | --- | --- | --- |
| 0 | 1 | 2023-06-01 00:00:00+00:00 | 1.366914 | -0.021035 | 2.754863 |
| 1 | 1 | 2023-06-02 00:00:00+00:00 | -0.593121 | -2.435497 | 1.249254 |
| 2 | 1 | 2023-06-05 00:00:00+00:00 | -0.485200 | -2.139216 | 1.168815 |
| 3 | 1 | 2023-06-06 00:00:00+00:00 | -0.927145 | -2.390566 | 0.536276 |
| 4 | 1 | 2023-06-07 00:00:00+00:00 | 0.766640 | -0.771479 | 2.304759 |

Copy

```python
values=sf.forecast_fitted_values()
values.head()

```

|  | unique\_id | ds | y | GARCH(1,1) | GARCH(1,1)-lo-95 | GARCH(1,1)-hi-95 |
| --- | --- | --- | --- | --- | --- | --- |
| 0 | 1 | 2015-01-05 00:00:00+00:00 | -1.827811 | NaN | NaN | NaN |
| 1 | 1 | 2015-01-06 00:00:00+00:00 | -0.889347 | 2.146389 | -0.972874 | 5.265652 |
| 2 | 1 | 2015-01-07 00:00:00+00:00 | 1.162984 | -0.764263 | -3.883526 | 2.355000 |
| 3 | 1 | 2015-01-08 00:00:00+00:00 | 1.788828 | -0.650707 | -3.769970 | 2.468556 |
| 4 | 1 | 2015-01-09 00:00:00+00:00 | -0.840381 | -1.449049 | -4.568312 | 1.670214 |

Adding 95% confidence interval with the forecast method

Copy

```python
sf.forecast(df=train, h=horizon, level=[95])

```

|  | unique\_id | ds | GARCH(1,1) | GARCH(1,1)-lo-95 | GARCH(1,1)-hi-95 |
| --- | --- | --- | --- | --- | --- |
| 0 | 1 | 2023-06-01 00:00:00+00:00 | 1.366914 | -0.021035 | 2.754863 |
| 1 | 1 | 2023-06-02 00:00:00+00:00 | -0.593121 | -2.435497 | 1.249254 |
| 2 | 1 | 2023-06-05 00:00:00+00:00 | -0.485200 | -2.139216 | 1.168815 |
| … | … | … | … | … | … |
| 75 | 1 | 2023-09-14 00:00:00+00:00 | -1.686546 | -3.049859 | -0.323233 |
| 76 | 1 | 2023-09-15 00:00:00+00:00 | -0.322556 | -2.497448 | 1.852335 |
| 77 | 1 | 2023-09-18 00:00:00+00:00 | 0.799407 | -1.027642 | 2.626457 |

Copy

```python
sf.plot(train, Y_hat.merge(test), max_insample_length=200)

```

![](https://mintlify.s3.us-west-1.amazonaws.com/nixtla/statsforecast/docs/models/GARCH_files/figure-markdown_strict/cell-38-output-1.png)

### [​](https://nixtlaverse.nixtla.io/statsforecast/docs/models/garch.html\#predict-method-with-confidence-interval)  Predict method with confidence interval

To generate forecasts use the predict method.

The predict method takes two arguments: forecasts the next `h` (for
horizon) and `level`.

- `h (int):` represents the forecast h steps into the future. In this
case, 30 dayly ahead.

- `level (list of floats):` this optional parameter is used for
probabilistic forecasting. Set the level (or confidence percentile)
of your prediction interval. For example, `level=[95]` means that
the model expects the real value to be inside that interval 95% of
the times.


The forecast object here is a new data frame that includes a column with
the name of the model and the y hat values, as well as columns for the
uncertainty intervals.

This step should take less than 1 second.

Copy

```python
sf.predict(h=horizon)

```

|  | unique\_id | ds | GARCH(1,1) |
| --- | --- | --- | --- |
| 0 | 1 | 2023-06-01 00:00:00+00:00 | 1.366914 |
| 1 | 1 | 2023-06-02 00:00:00+00:00 | -0.593121 |
| 2 | 1 | 2023-06-05 00:00:00+00:00 | -0.485200 |
| … | … | … | … |
| 75 | 1 | 2023-09-14 00:00:00+00:00 | -1.686546 |
| 76 | 1 | 2023-09-15 00:00:00+00:00 | -0.322556 |
| 77 | 1 | 2023-09-18 00:00:00+00:00 | 0.799407 |

Copy

```python
forecast_df = sf.predict(h=horizon, level=[80,95])
forecast_df.head(10)

```

|  | unique\_id | ds | GARCH(1,1) | GARCH(1,1)-lo-95 | GARCH(1,1)-lo-80 | GARCH(1,1)-hi-80 | GARCH(1,1)-hi-95 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | 1 | 2023-06-01 00:00:00+00:00 | 1.366914 | -0.021035 | 0.459383 | 2.274445 | 2.754863 |
| 1 | 1 | 2023-06-02 00:00:00+00:00 | -0.593121 | -2.435497 | -1.797786 | 0.611543 | 1.249254 |
| 2 | 1 | 2023-06-05 00:00:00+00:00 | -0.485200 | -2.139216 | -1.566703 | 0.596303 | 1.168815 |
| … | … | … | … | … | … | … | … |
| 7 | 1 | 2023-06-12 00:00:00+00:00 | -1.051435 | -4.790880 | -3.496526 | 1.393657 | 2.688010 |
| 8 | 1 | 2023-06-13 00:00:00+00:00 | 0.421605 | -3.001123 | -1.816396 | 2.659607 | 3.844333 |
| 9 | 1 | 2023-06-14 00:00:00+00:00 | -0.300086 | -3.138338 | -2.155920 | 1.555747 | 2.538166 |

Copy

```python
sf.plot(train, test.merge(forecast_df), level=[80, 95], max_insample_length=200)

```

![](https://mintlify.s3.us-west-1.amazonaws.com/nixtla/statsforecast/docs/models/GARCH_files/figure-markdown_strict/cell-41-output-1.png)

## [​](https://nixtlaverse.nixtla.io/statsforecast/docs/models/garch.html\#model-evaluation)  Model Evaluation

Now we are going to evaluate our model with the results of the
predictions, we will use different types of metrics MAE, MAPE, MASE,
RMSE, SMAPE to evaluate the accuracy.

Copy

```python
from functools import partial

import utilsforecast.losses as ufl
from utilsforecast.evaluation import evaluate

```

Copy

```python
evaluate(
    test.merge(Y_hat),
    metrics=[ufl.mae, ufl.mape, partial(ufl.mase, seasonality=season_length), ufl.rmse, ufl.smape],
    train_df=train,
)

```

|  | unique\_id | metric | GARCH(1,1) |
| --- | --- | --- | --- |
| 0 | 1 | mae | 0.843296 |
| 1 | 1 | mape | 3.703305 |
| 2 | 1 | mase | 0.794905 |
| 3 | 1 | rmse | 1.048076 |
| 4 | 1 | smape | 0.709150 |

## [​](https://nixtlaverse.nixtla.io/statsforecast/docs/models/garch.html\#acknowledgements)  Acknowledgements

We would like to thank [Naren\\
Castellon](https://www.linkedin.com/in/naren-castellon-1541b8101/?originalSubdomain=pa)
for writing this tutorial.

## [​](https://nixtlaverse.nixtla.io/statsforecast/docs/models/garch.html\#references)  References

1. Changquan Huang • Alla Petukhina. Springer series (2022). Applied
Time Series Analysis and Forecasting with Python.
2. [Bollerslev, T. (1986). Generalized autoregressive conditional\\
heteroskedasticity. Journal of econometrics, 31(3),\\
307-327.](https://citeseerx.ist.psu.edu/document?repid=rep1&type=pdf&doi=7da8bfa5295375c1141d797e80065a599153c19d)
3. [Engle, R. F. (1982). Autoregressive conditional heteroscedasticity\\
with estimates of the variance of United Kingdom inflation.\\
Econometrica: Journal of the econometric society,\\
987-1007.](http://www.econ.uiuc.edu/~econ508/Papers/engle82.pdf).
4. [James D. Hamilton. Time Series Analysis Princeton University Press,\\
Princeton, New Jersey, 1st Edition,\\
1994.](https://press.princeton.edu/books/hardcover/9780691042893/time-series-analysis)
5. [Nixtla\\
Parameters](https://nixtla.github.io/statsforecast/src/core/models.html#arch-model).
6. [Pandas available\\
frequencies](https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#offset-aliases).
7. [Rob J. Hyndman and George Athanasopoulos (2018). “Forecasting\\
principles and practice, Time series\\
cross-validation”.](https://otexts.com/fpp3/tscv.html).
8. [Seasonal periods- Rob J\\
Hyndman](https://robjhyndman.com/hyndsight/seasonal-periods/).

[Dynamic Standard Theta Model](https://nixtlaverse.nixtla.io/statsforecast/docs/models/dynamicstandardtheta.html) [Holt Model](https://nixtlaverse.nixtla.io/statsforecast/docs/models/holt.html)

On this page

- [Table of Contents](https://nixtlaverse.nixtla.io/statsforecast/docs/models/garch.html#table-of-contents)
- [Introduction](https://nixtlaverse.nixtla.io/statsforecast/docs/models/garch.html#introduction)
- [Definition of GARCH Models](https://nixtlaverse.nixtla.io/statsforecast/docs/models/garch.html#definition-of-garch-models)
- [Advantages and disadvantages of the Generalized Autoregressive Conditional Heteroskedasticity (GARCH) Model](https://nixtlaverse.nixtla.io/statsforecast/docs/models/garch.html#advantages-and-disadvantages-of-the-generalized-autoregressive-conditional-heteroskedasticity-garch-model)
- [The Generalized Autoregressive Conditional Heteroskedasticity (GARCH) model can be applied in several fields](https://nixtlaverse.nixtla.io/statsforecast/docs/models/garch.html#the-generalized-autoregressive-conditional-heteroskedasticity-garch-model-can-be-applied-in-several-fields)
- [Loading libraries and data](https://nixtlaverse.nixtla.io/statsforecast/docs/models/garch.html#loading-libraries-and-data)
- [Read Data](https://nixtlaverse.nixtla.io/statsforecast/docs/models/garch.html#read-data)
- [Explore data with the plot method](https://nixtlaverse.nixtla.io/statsforecast/docs/models/garch.html#explore-data-with-the-plot-method)
- [The Augmented Dickey-Fuller Test](https://nixtlaverse.nixtla.io/statsforecast/docs/models/garch.html#the-augmented-dickey-fuller-test)
- [Return Series](https://nixtlaverse.nixtla.io/statsforecast/docs/models/garch.html#return-series)
- [Creating Squared Returns](https://nixtlaverse.nixtla.io/statsforecast/docs/models/garch.html#creating-squared-returns)
- [Returns vs Squared Returns](https://nixtlaverse.nixtla.io/statsforecast/docs/models/garch.html#returns-vs-squared-returns)
- [Ljung-Box Test](https://nixtlaverse.nixtla.io/statsforecast/docs/models/garch.html#ljung-box-test)
- [Split the data into training and testing](https://nixtlaverse.nixtla.io/statsforecast/docs/models/garch.html#split-the-data-into-training-and-testing)
- [Implementation of GARCH with StatsForecast](https://nixtlaverse.nixtla.io/statsforecast/docs/models/garch.html#implementation-of-garch-with-statsforecast)
- [Load libraries](https://nixtlaverse.nixtla.io/statsforecast/docs/models/garch.html#load-libraries)
- [Instantiating Models](https://nixtlaverse.nixtla.io/statsforecast/docs/models/garch.html#instantiating-models)
- [Cross-validation](https://nixtlaverse.nixtla.io/statsforecast/docs/models/garch.html#cross-validation)
- [Perform time series cross-validation](https://nixtlaverse.nixtla.io/statsforecast/docs/models/garch.html#perform-time-series-cross-validation)
- [Fit the Model](https://nixtlaverse.nixtla.io/statsforecast/docs/models/garch.html#fit-the-model)
- [Forecast Method](https://nixtlaverse.nixtla.io/statsforecast/docs/models/garch.html#forecast-method)
- [Predict method with confidence interval](https://nixtlaverse.nixtla.io/statsforecast/docs/models/garch.html#predict-method-with-confidence-interval)
- [Model Evaluation](https://nixtlaverse.nixtla.io/statsforecast/docs/models/garch.html#model-evaluation)
- [Acknowledgements](https://nixtlaverse.nixtla.io/statsforecast/docs/models/garch.html#acknowledgements)
- [References](https://nixtlaverse.nixtla.io/statsforecast/docs/models/garch.html#references)

![](https://nixtlaverse.nixtla.io/statsforecast/docs/models/garch.html)

![](https://nixtlaverse.nixtla.io/statsforecast/docs/models/garch.html)

![](https://nixtlaverse.nixtla.io/statsforecast/docs/models/garch.html)

![](https://nixtlaverse.nixtla.io/statsforecast/docs/models/garch.html)

![](https://nixtlaverse.nixtla.io/statsforecast/docs/models/garch.html)

![](https://nixtlaverse.nixtla.io/statsforecast/docs/models/garch.html)

![](https://nixtlaverse.nixtla.io/statsforecast/docs/models/garch.html)