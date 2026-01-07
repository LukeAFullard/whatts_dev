from experiment_runner import run_experiment

if __name__ == "__main__":
    # V-05c_AutoCorr_High (rho=0.8)
    # projection Method
    run_experiment(
        n_samples=30,
        method_name='projection',
        rho=0.8,
        iterations=200,
        n_boot=1000
    )
