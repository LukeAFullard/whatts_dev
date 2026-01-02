import matplotlib.pyplot as plt
import numpy as np

def plot_compliance_explainer(dates, values, projected_values, result_dict):
    """
    Visualizes the 'Current State Projection'.

    Args:
        dates (pd.Series or np.array): Dates of observations.
        values (np.array): Historical values.
        projected_values (np.array): Projected values to current state.
        result_dict (dict): Result dictionary from calculate_tolerance_limit.

    Returns:
        matplotlib.figure.Figure: The generated figure.
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5), gridspec_kw={'width_ratios': [3, 1]})

    # --- Panel 1: Time Series & Projection ---
    # Plot Raw Data
    ax1.scatter(dates, values, color='gray', alpha=0.5, label='Historical Data')

    # Plot Projected "Current State" (clustered at the final date)
    current_date = dates.max()
    ax1.scatter([current_date]*len(values), projected_values,
                color='blue', alpha=0.6, label='Projected Current State')

    # Draw arrows connecting History to Projection
    for d, v, p in zip(dates, values, projected_values):
        ax1.plot([d, current_date], [v, p], color='blue', alpha=0.1)

    ax1.set_title("Step 1: Projecting History to Current State")
    ax1.legend()

    # --- Panel 2: The Assessment ---
    # Histogram of Projected Data
    # Use density=True so the area sums to 1, comparable to probability
    ax2.hist(projected_values, orientation='horizontal', color='blue', alpha=0.3, density=True)

    # The Statistic
    # Note: result_dict structure depends on implementation (e.g. 'upper_tolerance_limit')
    stat_val = result_dict['point_estimate']
    utl = result_dict['upper_tolerance_limit']

    ax2.axhline(stat_val, color='red', linewidth=2, label='95th %ile')
    ax2.axhline(utl, color='red', linestyle='--', label='UTL (95% Conf)')

    ax2.set_title("Step 2: Assessing Compliance")

    # Match y-axis limits to the time series plot for visual consistency
    ylim = ax1.get_ylim()
    ax2.set_ylim(ylim)

    # Hide x-axis density labels as they are abstract
    ax2.axes.get_xaxis().set_visible(False)

    plt.tight_layout()
    return fig
