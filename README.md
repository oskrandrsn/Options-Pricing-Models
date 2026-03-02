# Option Pricing and 3D Volatility Visualizer (In Progress) 
**By:** Oskar Andersen 


## Content ##

**1. Overview** 

**2. European Options: Call and Put**

**3. American Options: Call and Put**

**4. Asian Options**

**5. Barrier Options**

**6. Volatility Surface Visualizor 3D** 


## 1. Overview ## 

This is a very first project implemented in Python by me with focus on option pricing, as I am interested in derivative and asset pricing. I wanted to challenge myself and implement something interesting within my field of study which is quantitative finance and asset pricing. 

This project explores option pricing with core objective to move beyond classical closed-form pricing methods and investigate more realistic models that better reflect the financial market and behavior. I began my implementing the famous Black-Scholes model for European pricing, using its analytical solution. The model is computationally efficient, but relies on perfect market conditions, consequently misaligning with how the real financial market behaves. Most notable incosistant assumptions are the constant volatility or log-normal asset dynamics, which may casue empirical problems like the volatility smile. 

To adress these limitation to Black-Scholes model I extended the project to using stochastic volatility modelling for Exotic options - including asian and barrier options - that do not have a analytical solutions, as they are rather more unique than European options in terms of payoffs and pricing. For this section I wanted to focus on Heston model, allowing volatility to evolve as a stochastic process and enabling a better fit. 

As a final step I implemented a 3D volatility visualizer. 

Current implementations: 
- Black-Scholes model for European calls and puts
- GBM simulation for stock paths

Currntly working on: 
- American options 

Planned: 
- Barrier
- Asian options
- 3D volatility visualizer


## 2. European Options: Call and Put ##

**Parameters**

- $S_0$ - Initial Stock Price at Time $t=0$  

- $K$ - Strike Price

- $r$ — Risk Free Rate (countinous compounding)

- $q$ - Dividend Yield 

- $\sigma$ — Volatility (standard deviation of returns)  

- $N_{\text{Time}}$ — Number of time steps  

- $N_{\text{Paths}}$ — Number of simulated paths  

- $T$ — Option's Maturity


**Black-Scholes Model**

The Black-Scholes model (BS) is a mathematical framework for pricing European call and put options under the risk-netrual pricing measure. It assumes the underlying stock follows the Geometric Brownian Motion (GBM) dynamics with constant volatility and frictionless market condition.

Assumption of the BS model includes: 
- no arbitrage condition
- constant risk free rate
- constant volatility
- log-normal asset price dynamics

Black–Scholes PDE for the option value $V(S,t)$:

$\frac{\partial V}{\partial t} + \frac{1}{2}\sigma^2 S^2 \frac{\partial^2 V}{\partial S^2} + r S \frac{\partial V}{\partial S} - r V = 0$

Closed form solution of the BS model is given by: 

$d_1 = \frac{\ln\left(\frac{S_0}{K}\right) + (r - q + \frac{1}{2}\sigma^2)T}{\sigma \sqrt{T}}$

$d_2 = d_1 - \sigma \sqrt{T}$

Let $\( N(\cdot) \)$ denote the cumulative distribution function (CDF) of the standard normal distribution.

European Call: 
$C = S_0 e^{-qT} N(d_1) - K e^{-rT} N(d_2)$

European Put: 
$P = K e^{-rT} N(-d_2) - S_0 e^{-qT} N(-d_1)$

Put-Call Parity: 
$C - P = S_0 e^{-qT} - K e^{-rT}$

**Geometric Brownian Motion**

Under the BS model a stock price $S_T$ follows the GBM dynamics - a countinous time stochastic process with a drift and random component. A stock $S_t$ follows a GBM process given under the risk-netrual measure by:  

$$dS_t = (r - q) S_t dt + \sigma S_t d W_t$$ 

where: 

$(r - q) S_t$ = drift 

$W_t$ = standard brownian motion 



The future possible prices of a stock that follows the GBM model can be modelled by the GBM stochastic differential process:  

$$
S_{t+\Delta t} = S_t \cdot \exp\Big((r - q - \frac{1}{2}\sigma^2)\Delta t + \sigma \sqrt{\Delta t} Z_t \Big)
$$

The formula above is used to simulate possible stochastic paths of stock prices under the risk neutral measure to ensure that discounted prices follow a martingale approach. 

Changing the parameters will generate all the possible paths of the stock starting from an initial stock price at time t=0. The right-hand side of the graph shows the empirical distribution of simulated terminal stock prices $S_T$. 

**Notes**

Note:

(1) Keeping 252 time steps so that it is more aligned with trading days. 

(2) Having a larger number of paths simulated will more closly align with the theoritical expected stock price as well as put and call prices (typically > 50,000 simulations is good enough)

(3) Option maturity is measured in $T$ years. If an option matures in 120 days from now then write code 120/365, which let's Python calculate the option maturing in 120 days with 256 time steps. 

Example graph of simulated stock paths: 

<img width="1148" height="670" alt="Simulation of Stock Paths by GBM Dynamics " src="https://github.com/user-attachments/assets/636b7575-41f9-4a12-9727-3352d7c3def6" />


## 3. American Options: Put and Call  ## 

**Parameters** 

**American Options** 

American options are standard options similar to European contracts with the only difference where the contract holder can exercise the option at anytime prior to maturity of the contract. This allows for more flexibility and hedging strategies for investors, but in contrary come in higher price for the contract. 

With 





