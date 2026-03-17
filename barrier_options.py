# ==========================================================
# Packages
# ==========================================================

import numpy as np
import matplotlib.pyplot as plt
import datetime

# ==========================================================
# Model Parameters
# ==========================================================

def get_model_parameters():
    params = {"S0": 100, "K": 50, "r": 0.5, "q": 0.5, "vol": 0.9, "barrier": 120,
              "option_type": "put", # "call", "put"
              "barrier_type": "up-and-out", # "up-and-out", "down-and-out", "up-and-in", "down-and-in"
              "N": 100, "M": 50000, "seed": 5000,
              "T": (datetime.date(2026, 6, 10) - datetime.date.today()).days / 365}

    params["dt"] = params["T"] / params["N"]

    return params

# ==========================================================
# GBM Simulation
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
# GBM Paths with Barrier
# ==========================================================

def plot_paths_with_barrier(paths, params, max_paths_to_plot=300):

    barrier = params["barrier"]

    n_total = paths.shape[0]
    n_plot = min(max_paths_to_plot, n_total)

    rng = np.random.default_rng(params["seed"])
    idx = rng.choice(n_total, size=n_plot, replace=False)
    sampled_paths = paths[idx]

    time_grid = np.linspace(0, params["T"], paths.shape[1])

    plt.figure(figsize=(12, 7), dpi=140)

    for path in sampled_paths:
        plt.plot(time_grid, path, lw=1.0, alpha=0.5)

    # Shade the barrier region
    if params["barrier_type"].startswith("up"):
        plt.axhspan(barrier, paths.max(), color="red", alpha=0.08)
    elif params["barrier_type"].startswith("down"):
        plt.axhspan(paths.min(), barrier, color="red", alpha=0.08)


    plt.axhline(
        y=barrier,
        color="black",
        linestyle="--",
        linewidth=2,
        label=f"Barrier = {barrier}"
    )

    plt.title(f"Monte Carlo GBM Paths with {params['barrier_type']} Barrier")
    plt.xlabel("Time (Years)")
    plt.ylabel("Stock Price")
    plt.grid(True, linestyle="--", alpha=0.4)
    plt.legend()

    plt.tight_layout()
    plt.show()

# ==========================================================
# Barrier Option Logic
# ==========================================================

def get_barrier_hit_mask(paths, barrier, barrier_type):
    if barrier_type.startswith("up"):
        return np.any(paths >= barrier, axis=1)
    elif barrier_type.startswith("down"):
        return np.any(paths <= barrier, axis=1)
    else:
        raise ValueError("Invalid barrier_type.")

def get_payoff(S_T, K, option_type):
    if option_type == "call":
        return np.maximum(S_T - K, 0.0)
    elif option_type == "put":
        return np.maximum(K - S_T, 0.0)
    else:
        raise ValueError("Invalid option_type.")


def apply_barrier_condition(vanilla_payoff, hit_mask, barrier_type):
    if barrier_type.endswith("out"):
        return np.where(hit_mask, 0.0, vanilla_payoff)
    elif barrier_type.endswith("in"):
        return np.where(hit_mask, vanilla_payoff, 0.0)
    else:
        raise ValueError("Invalid barrier_type.")

# ==========================================================
# Barrier Option Pricing (Monte Carlo)
# ==========================================================

def price_barrier_option_mc(params, paths):
    K = params["K"]
    r = params["r"]
    T = params["T"]
    barrier = params["barrier"]
    option_type = params["option_type"]
    barrier_type = params["barrier_type"]

    S_T = paths[:, -1]

    vanilla_payoff = get_payoff(S_T, K, option_type)
    hit_mask = get_barrier_hit_mask(paths, barrier, barrier_type)
    payoff = apply_barrier_condition(vanilla_payoff, hit_mask, barrier_type)

    price = np.exp(-r * T) * np.mean(payoff)

    return price

# ==========================================================
# Results Summary
# ==========================================================

def print_results(params, price):
    print("Barrier Option Summary")
    print("----------------------")
    print(f"Option Type  : {params['option_type']}")
    print(f"Barrier Type : {params['barrier_type']}")
    print(f"Option Price : {price:.6f}")

# ==========================================================
# Main Controller
# ==========================================================

def main():
    params = get_model_parameters()

    paths = simulate_gbm_paths(params)

    price = price_barrier_option_mc(params, paths)

    print_results(params, price)

    plot_paths_with_barrier(paths, params)

# ==========================================================
# Run Script
# ==========================================================

if __name__ == "__main__":
    main()