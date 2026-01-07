from experiment_runner import run_experiment

if __name__ == "__main__":
    # V-03a: Linear Up Trend (Slope = 0.05)
    # Quantile Regression Method
    run_experiment(
        n_samples=200,
        method_name='quantile_regression',
        trend_type='linear_up',
        slope_sigma_per_t=0.05,
        iterations=50,
        n_boot=200
    )
