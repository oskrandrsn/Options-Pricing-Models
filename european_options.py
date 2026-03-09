# ==========================================================
# Packages
# ==========================================================

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from matplotlib.gridspec import GridSpec
from matplotlib.cm import ScalarMappable
from scipy.stats import gaussian_kde
from scipy.stats import norm as scipy_norm
import math

# ==========================================================
# Model Parameters
# ==========================================================

def get_model_parameters():
    params = {
        "S0": 40,
        "K": 80,
        "r": 0.05,
        "q": 0.0,
        "sigma": 0.30,
        "T": 120/365,
        "Number_Time_Steps": 256,
        "Number_Paths": 5000,
        "seed": 5000
    }
    
    params["dt"] = params["T"] / params["Number_Time_Steps"]
    
    return params

# ==========================================================
# GBM Simulation
# ==========================================================

def simulate_gbm_paths(params):

    S0 = params["S0"]
    r = params["r"]
    q = params["q"]
    sigma = params["sigma"]
    dt = params["dt"]
    steps = params["Number_Time_Steps"]
    paths_n = params["Number_Paths"]

    rng = np.random.default_rng(params["seed"])

    paths = np.zeros((paths_n, steps + 1))
    paths[:, 0] = S0

    for i in range(1, steps + 1):
        Z = rng.standard_normal(paths_n)

        paths[:, i] = paths[:, i-1] * np.exp(
            (r - q - 0.5 * sigma**2) * dt +
            sigma * np.sqrt(dt) * Z
        )

    return paths

# ==========================================================
# Visualization
# ==========================================================

def plot_paths_and_distribution(paths):

    Number_Paths = paths.shape[0]
    Final_Prices = paths[:, -1]

    norm = Normalize(vmin=min(Final_Prices), vmax=max(Final_Prices))
    cmap = plt.get_cmap("magma")
    colors = cmap(norm(Final_Prices))

    fig = plt.figure(figsize=(12,7), dpi=150)
    gs = GridSpec(1,2,width_ratios=[4,1],wspace=0.05)

    ax0 = fig.add_subplot(gs[0])

    for i in range(Number_Paths):
        ax0.plot(paths[i],color=colors[i],lw=1.2,alpha=0.6)

    ax0.set_xlabel("Time Step")
    ax0.set_ylabel("Stock Price")
    ax0.set_title("Risk-Neutral GBM Simulation")
    ax0.grid(True,linestyle="--",alpha=0.4)

    ax1 = fig.add_subplot(gs[1],sharey=ax0)

    bins = np.linspace(min(Final_Prices),max(Final_Prices),20)

    sorted_idx = np.argsort(Final_Prices)
    sorted_prices = Final_Prices[sorted_idx]
    sorted_colors = colors[sorted_idx]

    for i in range(len(bins)-1):

        mask = (sorted_prices>=bins[i]) & (sorted_prices<bins[i+1])
        count = np.sum(mask)

        if count>0:
            color = np.mean(sorted_colors[mask],axis=0)

            ax1.barh(
                (bins[i]+bins[i+1])/2,
                count,
                height=bins[i+1]-bins[i],
                color=color,
                edgecolor="k",
                alpha=0.8
            )

    kde = gaussian_kde(Final_Prices)

    y_vals = np.linspace(min(Final_Prices),max(Final_Prices),300)
    density = kde(y_vals) * Number_Paths * (bins[1]-bins[0])

    ax1.plot(density,y_vals,color="black",lw=2)

    ax1.set_xlabel("Frequency")
    ax1.grid(True,linestyle="--",alpha=0.4)

    sm = ScalarMappable(cmap=cmap,norm=norm)
    sm.set_array([])

    fig.colorbar(sm,ax=[ax0,ax1],orientation="vertical",fraction=0.03,pad=0.02)

    plt.show()

    return Final_Prices

# ==========================================================
# Black-Scholes Option Pricing 
# ==========================================================

_norm_cdf = scipy_norm.cdf
_norm_pdf = scipy_norm.pdf


def d1_d2(S0,K,r,q,sigma,T):

    sqrtT = math.sqrt(T)

    d1 = (math.log(S0/K) + (r-q+0.5*sigma**2)*T) / (sigma*sqrtT)
    d2 = d1 - sigma*sqrtT

    return d1,d2


def bs_call_price(S0,K,r,q,sigma,T):

    d1,d2 = d1_d2(S0,K,r,q,sigma,T)

    return S0*math.exp(-q*T)*_norm_cdf(d1) - K*math.exp(-r*T)*_norm_cdf(d2)


def bs_put_price(S0,K,r,q,sigma,T):

    d1,d2 = d1_d2(S0,K,r,q,sigma,T)

    return K*math.exp(-r*T)*_norm_cdf(-d2) - S0*math.exp(-q*T)*_norm_cdf(-d1)

# ==========================================================
# Monte Carlo Option Pricing
# ==========================================================

def monte_carlo_option_prices(final_prices,params):

    K = params["K"]
    r = params["r"]
    T = params["T"]
    N = len(final_prices)

    payoff_call = np.maximum(final_prices-K,0)
    payoff_put = np.maximum(K-final_prices,0)

    call_price = math.exp(-r*T) * payoff_call.mean()
    put_price = math.exp(-r*T) * payoff_put.mean()

    se_call = math.exp(-r*T) * payoff_call.std(ddof=1)/math.sqrt(N)
    se_put = math.exp(-r*T) * payoff_put.std(ddof=1)/math.sqrt(N)

    return call_price,put_price,se_call,se_put

# ==========================================================
# Results
# ==========================================================

def print_results(params,final_prices,mc_results):

    S0 = params["S0"]
    K = params["K"]
    r = params["r"]
    q = params["q"]
    sigma = params["sigma"]
    T = params["T"]

    mc_call,mc_put,se_call,se_put = mc_results

    print("Monte Carlo Final Price:",np.mean(final_prices))
    print("Theoretical Risk-Neutral Mean:",S0*np.exp((r-q)*T))

    print()

    print("Black-Scholes Call:",bs_call_price(S0,K,r,q,sigma,T))
    print("Monte Carlo Call:",mc_call,"SE:",se_call)

    print()

    print("Black-Scholes Put:",bs_put_price(S0,K,r,q,sigma,T))
    print("Monte Carlo Put:",mc_put,"SE:",se_put)

# ==========================================================
# Main Controller
# ==========================================================

def main():
    
    params = get_model_parameters()

    paths = simulate_gbm_paths(params)

    final_prices = plot_paths_and_distribution(paths)

    mc_results = monte_carlo_option_prices(final_prices,params)

    print_results(params,final_prices,mc_results)

# ==========================================================
# Run Script
# ==========================================================

if __name__ == "__main__":
    main()
