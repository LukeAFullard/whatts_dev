import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import experiment_runner

if __name__ == "__main__":
    experiment_runner.run_experiment(
        n_samples=60,
        method_name='quantile_regression',
        dist_name='gamma',
        dist_params={'shape': 2.0, 'scale': 2.0},
        iterations=200,
        n_boot=1000
    )
