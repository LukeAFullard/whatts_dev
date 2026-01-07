from experiment_runner import run_experiment

if __name__ == "__main__":
    # V-05a_AutoCorr_Low (rho=0.3)
    # projection Method
    run_experiment(
        n_samples=30,
        method_name='projection',
        rho=0.3,
        iterations=200,
        n_boot=1000
    )
