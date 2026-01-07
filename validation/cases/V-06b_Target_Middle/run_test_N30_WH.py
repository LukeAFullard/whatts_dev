from experiment_runner import run_experiment

if __name__ == "__main__":
    # V-06b_Target_Middle (Target=middle)
    # projection Method
    run_experiment(
        n_samples=30,
        method_name='projection',
        target_date_alias='middle',
        iterations=200
    )
