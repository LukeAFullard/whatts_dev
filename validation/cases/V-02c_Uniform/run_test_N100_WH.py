import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import experiment_runner

if __name__ == "__main__":
    experiment_runner.run_experiment(
        n_samples=100,
        method_name='projection',
        dist_name='uniform',
        dist_params={'low': 0, 'high': 100},
        iterations=200,
        n_boot=1000
    )
