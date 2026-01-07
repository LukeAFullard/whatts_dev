from experiment_runner import run_experiment

if __name__ == "__main__":
    # V-06a_Target_Start (Target=start)
    # projection Method
    run_experiment(
        n_samples=100,
        method_name='projection',
        target_date_alias='start',
        iterations=200
    )
