# Option Pricing Models ##

## 1. Overview ##

This repository contains a collection of Python implementations for pricing different types of financial options using both analytical models and Monte Carlo simulation techniques. The project demonstrates how various option pricing frameworks can be applied to standard and exotic derivatives.

The models implemented include:

- **European Options** priced using the Black–Scholes analytical solution and Monte Carlo simulation.
- **American Options** priced using the Least Squares Monte Carlo (LSMC) method to capture the possibility of early exercise.
- **Asian Options** priced using Monte Carlo simulation with arithmetic averaging of the underlying asset price.
- **Barrier Options** priced using Monte Carlo simulation with path-dependent barrier conditions.

The underlying asset in all simulations is assumed to follow a **Geometric Brownian Motion (GBM)** under the risk-neutral measure. The project also includes visualizations of simulated stock price paths, payoff distributions, and exercise boundaries to help illustrate the behavior of each option type.

Overall, the goal of this repository is to provide an intuitive and practical implementation of key option pricing techniques commonly used in quantitative finance.

## 2. European Options: Call and Put

**Black–Scholes Model**

The Black–Scholes (BS) model is a mathematical framework used to price **European call and put options** under the risk-neutral pricing measure. The model assumes that the underlying asset price follows a **Geometric Brownian Motion (GBM)** with constant volatility and frictionless market conditions.

Key assumptions of the Black–Scholes model include:

- no arbitrage opportunities  
- constant risk-free interest rate  
- constant volatility of the underlying asset  
- log-normal distribution of asset prices  

---

**Black–Scholes Partial Differential Equation**

The value of an option \(V(S,t)\) satisfies the Black–Scholes partial differential equation:

$$
\frac{\partial V}{\partial t} + \frac{1}{2}\sigma^2 S^2 \frac{\partial^2 V}{\partial S^2} + r S \frac{\partial V}{\partial S} - rV = 0
$$

---

**Closed-Form Black–Scholes Solution**

The closed-form solution for European options uses the following terms:

$$
d_1 = \frac{\ln\left(\frac{S_0}{K}\right) + (r - q + \frac{1}{2}\sigma^2)T}{\sigma \sqrt{T}}
$$

$$
d_2 = d_1 - \sigma \sqrt{T}
$$

European **Call Option**:

$$
C = S_0 e^{-qT} N(d_1) - K e^{-rT} N(d_2)
$$

European **Put Option**:

$$
P = K e^{-rT} N(-d_2) - S_0 e^{-qT} N(-d_1)
$$

---

**Put–Call Parity**

The relationship between European call and put prices is given by:

$$
C - P = S_0 e^{-qT} - K e^{-rT}
$$

---

**Underlying Asset Dynamics**

Under the risk-neutral measure, the stock price follows a **Geometric Brownian Motion**:

$$
dS_t = (r - q)S_tdt + \sigma S_t dW_t
$$

where:

- \(r\) = risk-free interest rate  
- \(q\) = dividend yield  
- \(\sigma\) = volatility  
- \(W_t\) = standard Brownian motion  

The discrete-time representation used for simulations is:

$$
S_{t+\Delta t} = S_t e^{(r - q - \frac{1}{2}\sigma^2)\Delta t + \sigma\sqrt{\Delta t}Z_t}
$$

where \(Z_t \sim N(0,1)\).

---

**Script european_options.py**

The European option pricing script combines the **analytical Black–Scholes formula** with **Monte Carlo simulation** to illustrate and verify the pricing results.

The script follows these main steps:

1. Parameter Setup
The model parameters are defined, including the initial stock price, strike price, volatility, risk-free rate, dividend yield, maturity, number of time steps, and number of simulation paths. Change the parameters according to the your contract and set the datetime.date() as the maturity of the contract. 

2. GBM Stock Price Simulation
The script simulates many possible stock price paths using the Geometric Brownian Motion model.

3. Monte Carlo Payoff Calculation
For each simulated path, the terminal stock price \(S_T\) is used to compute the option payoff:

- Call: \(\max(S_T - K,0)\)  
- Put: \(\max(K - S_T,0)\)

The option price is then estimated as the **discounted average payoff across all simulated paths**.

4. Black–Scholes Analytical Price
The script also calculates the **closed-form Black–Scholes price**, allowing the Monte Carlo estimate to be compared with the theoretical result.

5. Visualization
The script generates visualizations of:

- simulated GBM stock price paths  
- the distribution of terminal stock prices  

These graphs help illustrate the stochastic behavior of the underlying asset and how the option payoff depends on the simulated outcomes.

## 3. American Options: Put and Call

**American Options**

American options are financial derivatives that allow the holder to exercise the option **at any time up to and including the maturity date**. This early-exercise flexibility distinguishes American options from European options, which can only be exercised at maturity.

Under the standard financial assumption that the underlying asset follows a **Geometric Brownian Motion (GBM)** under the risk-neutral measure, the stock dynamics are given by:

$$
dS_t = (r - q) S_t dt + \sigma S_t dW_t
$$

where:

- \(r\) = risk-free interest rate  
- \(q\) = dividend yield  
- \(\sigma\) = volatility of the underlying asset  
- \(W_t\) = standard Brownian motion  

At each potential exercise time, the investor compares:

- the **immediate exercise value**, and  
- the **continuation value** (expected value of holding the option longer).

The option should be exercised early if the immediate payoff exceeds the continuation value.

An important theoretical result is that an **American call option on a non-dividend paying stock should never be exercised early**, meaning its value is equal to the corresponding European call option.

---

**Least Squares Monte Carlo (LSMC) Approach**

The model uses the **Least Squares Monte Carlo (LSMC)** method proposed by Longstaff and Schwartz (2001). This method combines Monte Carlo simulation with regression techniques to estimate the continuation value of the option at each potential exercise date.

The key idea is to simulate many possible stock price paths and then use **least squares regression** to estimate the expected continuation value conditional on the current stock price.

---

**Script: american_options.py**

The script prices American options using the following steps:

1. Parameter Setup
The model parameters are defined, including the initial stock price, strike price, risk-free interest rate, dividend yield, volatility, maturity, number of time steps, number of simulation paths, and random seed. Change the parameters according to the your contract and set the datetime.date() as the maturity of the contract.

2. GBM Stock Path Simulation
The script generates many possible stock price paths using the **Geometric Brownian Motion model** under the risk-neutral measure.

3. Backward Induction with LSMC
Starting from maturity and moving backward through time, the model:

- identifies paths where the option is **in the money**
- estimates the **continuation value** using a regression on simulated stock prices
- compares the continuation value to the **immediate exercise payoff**

If exercising early is optimal, the option payoff is recorded at that time step.

4. Option Pricing
The American option price is estimated as the **average discounted payoff across all simulated paths**.

5. Visualization
The script produces two visual outputs:

- ** GBM stock path simulations ** showing the possible price trajectories of the underlying asset  
- ** Early exercise boundary visualization **, illustrating where early exercise occurs across the simulated paths


## 4. Asian Options

**Asian Options**

Asian options – often referred to as *average options* – are a type of exotic option whose payoff depends on the **average price of the underlying asset** over a specified time period rather than only the final price at maturity. Because the payoff is based on an average price, Asian options are generally **less sensitive to extreme price movements** than standard European options.

The payoff for a fixed-strike Asian option is given by:

$$
\pi =
\begin{cases}
\max(\bar{S} - K, 0) & \text{Call option} \\
\max(K - \bar{S}, 0) & \text{Put option}
\end{cases}
$$

where:

- \( \bar{S} \) = average price of the underlying asset  
- \( K \) = strike price

---

**Underlying Asset Dynamics**

The underlying asset price follows a **Geometric Brownian Motion (GBM)** under the risk-neutral measure:

$$
S_{t+\Delta t} = S_t e^{(r - q - \frac{1}{2}\sigma^2)\Delta t + \sigma \sqrt{\Delta t} Z_t}
$$

where:

- \( r \) = risk-free interest rate  
- \( q \) = dividend yield  
- \( \sigma \) = volatility  
- \( Z_t \sim N(0,1) \)

---

**Average Price Calculation**

The average stock price used in the payoff can be calculated in two ways.

**Arithmetic Average**

$$
\bar{S} = \frac{1}{n}\sum_{i=1}^{n} S_{t_i}
$$

The arithmetic average is the most commonly used in practice and is typically priced using **Monte Carlo simulation**, since no closed-form solution exists.

**Geometric Average**

$$
\bar{S}_G = \left(\prod_{i=1}^{n} S_{t_i}\right)^{\frac{1}{n}}
$$

Geometric Asian options are mathematically easier to price and closed-form solutions exist, which can be used as benchmarks or control variates in simulations.

---

**Script: asian_options.py**

The Python script prices Asian options using **Monte Carlo simulation** and follows these main steps:

1. Parameter Setup
The script first defines the model parameters, including the initial stock price, strike price, risk-free interest rate, dividend yield, volatility, maturity, number of time steps, and number of simulated paths. Change the parameters according to the your contract and set the datetime.date() as the maturity of the contract.

2. GBM Path Simulation
Stock price paths are simulated using the **Geometric Brownian Motion model**. Each simulation generates a possible future trajectory for the stock price over the life of the option.

3. Average Price Calculation
For each simulated path, the **arithmetic average price** of the underlying asset is computed across all observation times.

4. Payoff Calculation
The payoff for both call and put Asian options is calculated using the average price from each simulated path.

5. Monte Carlo Pricing
The option price is obtained by taking the **discounted average payoff across all simulated paths** using the risk-free interest rate.

6. Visualization
The script also includes visualizations of the simulated stock price paths and the convergence of the Monte Carlo estimate. These plots help illustrate the distribution of terminal prices and the stability of the pricing estimate as the number of simulations increases.


## 5. Barrier Options ##

**Barrier Options**

Barrier options are path-dependent exotic options whose payoff depends not only on the final stock price but also on whether the underlying asset crosses a predefined barrier level during the option’s lifetime. If the barrier is triggered, the option may either become active (knock-in) or cease to exist (knock-out), depending on the contract specifications.

**Script: barrier_options.py**

The script prices barrier options using Monte Carlo simulation under a risk-neutral Geometric Brownian Motion (GBM) framework.

The main steps are:

1. Parameter Setup  
   The model parameters are defined, including the initial stock price, strike price, volatility, risk-free rate, maturity, barrier level, number of simulated paths, and time steps. Change the parameters according to the your contract and set the datetime.date() as the maturity of the contract.

2. Stock Price Simulation  
   The underlying asset price paths are simulated using a GBM process under the risk-neutral measure.

3. Barrier Monitoring  
   For each simulated path, the code checks whether the stock price crosses the barrier level during the option’s life.

4. Payoff Calculation  
   The option payoff at maturity is computed and adjusted depending on whether the barrier condition was triggered.

5. Monte Carlo Pricing  
   The barrier option price is estimated as the discounted average payoff across all simulated paths.

The script also includes visualizations of simulated price paths and the terminal price distribution to illustrate how the barrier condition affects the option payoff.
