# ==========================================================
# Packages
# ==========================================================

import datetime
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.cm import ScalarMappable
from matplotlib.colors import Normalize
from matplotlib.gridspec import GridSpec
from scipy.stats import gaussian_kde

# ==========================================================
# Parameters
# ==========================================================

def get_model_parameters():
    params = {"S0": 60, "K": 120, "r": 0.05, "q": 0.15, "vol": 0.80, "N": 256, "M": 50000, "seed": 50000,
              "option_type": "put", "maturity": datetime.date(2026, 4, 12), "today": datetime.date.today()}

    params["T"] = (params["maturity"] - params["today"]).days / 365

    params["dt"] = params["T"] / params["N"]

    params["beta"] = np.exp(-params["r"] * params["dt"])

    return params

# ==========================================================
# GBM Stock Path Simulation
# ==========================================================

def simulate_gbm_paths(params):
    S0 = params["S0"]
    r = params["r"]
    q = params["q"]
    vol = params["vol"]
    dt = params["dt"]
    steps = params["N"]
    paths_n = params["M"]

    rng = np.random.default_rng(params["seed"])

    paths = np.zeros((paths_n, steps + 1))
    paths[:, 0] = S0

    for i in range(1, steps + 1):
        Z = rng.standard_normal(paths_n)

        paths[:, i] = paths[:, i - 1] * np.exp(
            (r - q - 0.5 * vol ** 2) * dt + vol * np.sqrt(dt) * Z
        )

    return paths

# ==========================================================
# Visualisation - GBM Stock Path
# ==========================================================

def plot_paths_and_distribution(paths):
    Number_Paths = paths.shape[0]
    Final_Prices = paths[:, -1]

    norm = Normalize(vmin=min(Final_Prices), vmax=max(Final_Prices))
    cmap = plt.get_cmap("magma")
    colors = cmap(norm(Final_Prices))

    fig = plt.figure(figsize=(12, 7), dpi=150)
    gs = GridSpec(1, 2, width_ratios=[4, 1], wspace=0.05)

    ax0 = fig.add_subplot(gs[0])

    for i in range(Number_Paths):
        ax0.plot(paths[i], color=colors[i], lw=1.2, alpha=0.6)

    ax0.set_xlabel("Time Step")
    ax0.set_ylabel("Stock Price")
    ax0.set_title("Risk-Neutral GBM Simulation")
    ax0.grid(True, linestyle="--", alpha=0.4)

    ax1 = fig.add_subplot(gs[1], sharey=ax0)

    bins = np.linspace(min(Final_Prices), max(Final_Prices), 20)

    sorted_idx = np.argsort(Final_Prices)
    sorted_prices = Final_Prices[sorted_idx]
    sorted_colors = colors[sorted_idx]

    for i in range(len(bins) - 1):

        mask = (sorted_prices >= bins[i]) & (sorted_prices < bins[i + 1])
        count = np.sum(mask)

        if count > 0:
            color = np.mean(sorted_colors[mask], axis=0)

            ax1.barh(
                (bins[i] + bins[i + 1]) / 2,
                count,
                height=bins[i + 1] - bins[i],
                color=color,
                edgecolor="k",
                alpha=0.8
            )

    kde = gaussian_kde(Final_Prices)

    y_vals = np.linspace(min(Final_Prices), max(Final_Prices), 300)
    density = kde(y_vals) * Number_Paths * (bins[1] - bins[0])

    ax1.plot(density, y_vals, color="black", lw=2)

    ax1.set_xlabel("Frequency")
    ax1.grid(True, linestyle="--", alpha=0.4)

    sm = ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])

    fig.colorbar(sm, ax=[ax0, ax1], orientation="vertical", fraction=0.03, pad=0.02)

    plt.show()

    return Final_Prices

# ==========================================================
# Least Square Monte Carlo (LSMC)
# ==========================================================

def lsmc_with_exercise(params, paths):
    option_type = params.get("option_type", "put")

    K = params["K"]
    beta = params["beta"]
    steps = params["N"]
    M = paths.shape[0]

    if option_type == "put":
        payoff = np.maximum(K - paths, 0.0)
    else:
        payoff = np.maximum(paths - K, 0.0)

    V = payoff[:, -1].copy()
    exercise_time = np.full(M, steps, dtype=int)
    exercise_price = paths[:, -1].copy()

    for t in range(steps - 1, -1, -1):
        in_money = payoff[:, t] > 0.0
        if not np.any(in_money):
            continue

        X = paths[in_money, t]
        Y = V[in_money] * beta

        A = np.vstack([np.ones_like(X), X, X ** 2]).T

        coeffs, _, _, _ = np.linalg.lstsq(A, Y, rcond=None)
        continuation = A.dot(coeffs)

        immediate = payoff[in_money, t]
        exercise_now = immediate > continuation

        if np.any(exercise_now):
            in_money_idx = np.where(in_money)[0]
            exercise_idx = in_money_idx[exercise_now]

            V[exercise_idx] = immediate[exercise_now]
            exercise_time[exercise_idx] = t
            exercise_price[exercise_idx] = paths[exercise_idx, t]

    discounted = V * (beta ** exercise_time)
    price = np.mean(discounted)

    return price, exercise_time, exercise_price

# ==========================================================
# Visualisation - Optimal Early Exercise Boundary
# ==========================================================

def visualize_early_exercise(params, paths, show_summary_n=10):
    option_type = params.get("option_type", "put")

    price, exercise_time, exercise_price = lsmc_with_exercise(params, paths)

    s = pd.Series(exercise_time)
    summary = s.value_counts(normalize=True).sort_index()

    print("Normalized exercise time distribution (first rows):")
    print(summary.head(show_summary_n))

    fig, axs = plt.subplots(1, 2, figsize=(14, 5), gridspec_kw={"width_ratios": [4, 1], "wspace": 0.12})
    ax_scatter, ax_bar = axs

    ax_scatter.scatter(exercise_time, exercise_price, s=1, alpha=0.25)
    ax_scatter.set_xlabel("Exercise time step")
    ax_scatter.set_ylabel("Underlying price at exercise")
    ax_scatter.set_title("Simulated Early Exercise Boundary (scatter)")
    ax_scatter.grid(True, linestyle="--", alpha=0.4)

    times = summary.index.values
    freqs = summary.values
    ax_bar.barh(times, freqs, height=0.8, edgecolor="k", alpha=0.8)
    ax_bar.set_xlabel("Normalized frequency")
    ax_bar.set_ylabel("Time step")
    ax_bar.set_title("Exercise time frequency")
    ax_bar.grid(True, linestyle="--", alpha=0.4)

    plt.suptitle("Simulated Early Exercise Boundary and Exercise-Time Distribution")
    plt.show()

    return {
        "price": price,
        "exercise_time": exercise_time,
        "exercise_price": exercise_price,
        "exercise_time_distribution": summary
    }
# ==========================================================
# Print Results
# ==========================================================

def print_results(params, price):
    print("American Option Summary")
    print("----------------------")
    print(f"Option Type  : {params['option_type']}")
    print(f"Option Price : {price:.6f}")

# ==========================================================
# Main Controller
# ==========================================================

def main():

    params = get_model_parameters()

    paths = simulate_gbm_paths(params)

    plot_paths_and_distribution(paths)

    price, _, _ = lsmc_with_exercise(params, paths)

    print_results(params, price)

    visualize_early_exercise(params, paths)

# ==========================================================
# Run Script
# ==========================================================

if __name__ == "__main__":
    main()