from experiment_runner import run_experiment

if __name__ == "__main__":
    # V-05c_AutoCorr_High (rho=0.8)
    # quantile_regression Method
    run_experiment(
        n_samples=200,
        method_name='quantile_regression',
        rho=0.8,
        iterations=20,
        n_boot=200
    )
