from experiment_runner import run_experiment

if __name__ == "__main__":
    # V-05a_AutoCorr_Low (rho=0.3)
    # quantile_regression Method
    run_experiment(
        n_samples=30,
        method_name='quantile_regression',
        rho=0.3,
        iterations=20,
        n_boot=200
    )
