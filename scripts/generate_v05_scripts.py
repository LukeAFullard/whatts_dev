import os

cases = [
    ('V-05a_AutoCorr_Low', 0.3),
    ('V-05b_AutoCorr_Mod', 0.6),
    ('V-05c_AutoCorr_High', 0.8)
]

sample_sizes = [30, 60, 100, 200]
methods = [
    ('projection', 'WH', 200, 1000),
    ('quantile_regression', 'QR', 20, 200) # Low iterations for QR
]

for folder, rho in cases:
    for n in sample_sizes:
        for method_name, suffix, iterations, n_boot in methods:
            filename = f"validation/cases/{folder}/run_test_N{n}_{suffix}.py"
            content = f"""from experiment_runner import run_experiment

if __name__ == "__main__":
    # {folder} (rho={rho})
    # {method_name} Method
    run_experiment(
        n_samples={n},
        method_name='{method_name}',
        rho={rho},
        iterations={iterations},
        n_boot={n_boot}
    )
"""
            with open(filename, "w") as f:
                f.write(content)
            print(f"Created {filename}")
