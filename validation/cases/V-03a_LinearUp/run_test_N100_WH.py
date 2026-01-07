from experiment_runner import run_experiment

if __name__ == "__main__":
    # V-03a: Linear Up Trend (Slope = 0.05)
    # Projection Method
    run_experiment(
        n_samples=100,
        method_name='projection',
        trend_type='linear_up',
        slope_sigma_per_t=0.05,
        iterations=200
    )
