from experiment_runner import run_experiment

if __name__ == "__main__":
    # V-06c_Target_End (Target=end)
    # projection Method
    run_experiment(
        n_samples=100,
        method_name='projection',
        target_date_alias='end',
        iterations=200
    )
