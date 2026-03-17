# ==========================================================
# Packages
# ==========================================================

import datetime
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.cm import ScalarMappable
from matplotlib.colors import Normalize
from matplotlib.gridspec import GridSpec
from scipy.stats import gaussian_kde

# ==========================================================
# Parameters
# ==========================================================

def get_model_parameters():
    params = {"S0": 100, "K": 125, "r": 0.05, "q": 0.0, "vol": 0.5, "N": 256, "M": 50000, "seed": 50000,
                "maturity": datetime.date(2026, 6, 12), "today": datetime.date.today()}

    params["T"] = (params["maturity"] - params["today"]).days / 365

    params["dt"] = params["T"] / params["N"]

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
    number_paths = paths.shape[0]
    final_prices = paths[:, -1]

    norm = Normalize(vmin=min(final_prices), vmax=max(final_prices))
    cmap = plt.get_cmap("inferno")
    colors = cmap(norm(final_prices))

    fig = plt.figure(figsize=(12, 7), dpi=150)
    gs = GridSpec(1, 2, width_ratios=[4, 1], wspace=0.05)

    ax0 = fig.add_subplot(gs[0])

    for i in range(number_paths):
        ax0.plot(paths[i], color=colors[i], lw=0.8, alpha=0.6)

    ax0.set_xlabel("Time Step")
    ax0.set_ylabel("Stock Price")
    ax0.set_title("Risk-Neutral GBM Simulation")
    ax0.grid(True, linestyle="--", alpha=0.4)

    ax1 = fig.add_subplot(gs[1], sharey=ax0)

    bins = np.linspace(min(final_prices), max(final_prices), 20)

    sorted_idx = np.argsort(final_prices)
    sorted_prices = final_prices[sorted_idx]
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

    kde = gaussian_kde(final_prices)

    y_vals = np.linspace(min(final_prices), max(final_prices), 300)
    density = kde(y_vals) * number_paths * (bins[1] - bins[0])

    ax1.plot(density, y_vals, color="black", lw=2)

    ax1.set_xlabel("Frequency")
    ax1.grid(True, linestyle="--", alpha=0.4)

    sm = ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])

    fig.colorbar(sm, ax=[ax0, ax1], orientation="vertical", fraction=0.03, pad=0.02)

    plt.show()

    return final_prices

# ==========================================================
# Monte Carlo Pricing Function
# ==========================================================

def asian_options(params, paths):

    K = params["K"]
    r = params["r"]
    T = params["T"]

    S_avg = paths.mean(axis=-1)

    call = np.maximum(S_avg - K, 0)
    put = np.maximum(K - S_avg, 0)

    discount = np.exp(-r * T)

    price_call = discount * np.mean(call)
    price_put = discount * np.mean(put)

    return price_call, price_put

# ==========================================================
# Asian Option Price Visualization
# ==========================================================

def asian_option_price_visualization(params, call, put, max_cum=10_000):

    r = params["r"]
    T = params["T"]

    call = np.asarray(call).ravel()
    put = np.asarray(put).ravel()
    n = len(call)
    if len(put) != n:
        raise ValueError("call and put arrays must have same length")

    discount = np.exp(-r * T)
    disc_call = discount * call
    disc_put = discount * put

    cumsum_call = np.cumsum(disc_call)
    cumsum_put = np.cumsum(disc_put)
    idx = np.arange(1, n + 1)
    c_AS = cumsum_call / idx
    p_AS = cumsum_put / idx

    cumsum_call_sq = np.cumsum(disc_call ** 2)
    cumsum_put_sq = np.cumsum(disc_put ** 2)

    var_call = (cumsum_call_sq / idx) - (c_AS ** 2)
    var_put = (cumsum_put_sq / idx) - (p_AS ** 2)

    var_call = np.maximum(var_call, 0.0)
    var_put = np.maximum(var_put, 0.0)

    se_call = np.sqrt(var_call / idx)
    se_put = np.sqrt(var_put / idx)

    ci_multiplier = 1.96

    max_cum_plot = min(max_cum, n)
    x_cum = np.arange(1, max_cum_plot + 1)

    fig, ax = plt.subplots(figsize=(12, 6))

    ax.plot(x_cum, c_AS[:max_cum_plot], label="Discounted cumulative avg (Call)", color="tab:blue", lw=1.2)
    ax.plot(x_cum, p_AS[:max_cum_plot], label="Discounted cumulative avg (Put)", color="tab:orange", lw=1.2)

    upper_call = c_AS[:max_cum_plot] + ci_multiplier * se_call[:max_cum_plot]
    lower_call = c_AS[:max_cum_plot] - ci_multiplier * se_call[:max_cum_plot]
    upper_put = p_AS[:max_cum_plot] + ci_multiplier * se_put[:max_cum_plot]
    lower_put = p_AS[:max_cum_plot] - ci_multiplier * se_put[:max_cum_plot]

    ax.fill_between(x_cum, lower_call, upper_call, color="tab:blue", alpha=0.12, edgecolor=None)
    ax.fill_between(x_cum, lower_put, upper_put, color="tab:orange", alpha=0.12, edgecolor=None)

    ax.axhline(c_AS[-1], color="tab:blue", linestyle="--", lw=0.9,
               label=f'Final MC Call = {c_AS[-1]:.6f}')
    ax.axhline(p_AS[-1], color="tab:orange", linestyle="--", lw=0.9,
               label=f'Final MC Put  = {p_AS[-1]:.6f}')

    ax.set_xlabel("Number of simulated paths (cumulative)")
    ax.set_ylabel("Discounted cumulative average payoff")
    ax.set_title("Asian Option: Discounted Cumulative Running Averages (with 95% CI)")
    ax.legend(loc="upper right")
    ax.grid(True, linestyle="--", alpha=0.4)

    plt.tight_layout()
    plt.show()

    return {
        "discounted_call": disc_call,
        "discounted_put": disc_put,
        "cumulative_call": c_AS,
        "cumulative_put": p_AS,
        "se_call": se_call,
        "se_put": se_put
    }

# ==========================================================
# Print Results
# ==========================================================

def print_results(price_call, price_put):
    print("Asian Option Summary")
    print("----------------------")
    print(f"Asian Call Option Price: {float(price_call):.6f}")
    print(f"Asian Put Options Price: {float(price_put):.6f}")

# ==========================================================
# Main Controller
# ==========================================================

def main():

    params = get_model_parameters()

    paths = simulate_gbm_paths(params)

    plot_paths_and_distribution(paths)

    price_call, price_put = asian_options(params, paths)

    print_results(price_call, price_put)

# ==========================================================
# Run Script
# ==========================================================

if __name__ == "__main__":
    main()
