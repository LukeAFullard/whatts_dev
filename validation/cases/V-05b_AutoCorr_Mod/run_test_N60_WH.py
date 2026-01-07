from experiment_runner import run_experiment

if __name__ == "__main__":
    # V-05b_AutoCorr_Mod (rho=0.6)
    # projection Method
    run_experiment(
        n_samples=60,
        method_name='projection',
        rho=0.6,
        iterations=200,
        n_boot=1000
    )
