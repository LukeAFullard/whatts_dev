import os

cases = [
    ('V-06a_Target_Start', 'start'),
    ('V-06b_Target_Middle', 'middle'),
    ('V-06c_Target_End', 'end')
]

sample_sizes = [30, 60, 100, 200]
methods = [
    ('projection', 'WH', 200, 1000)
    # V-06 is specifically for Projection method sensitivity. QR sensitivity could be tested but Projection is the focus here.
    # We can add QR if needed, but 'project_to_current_state' is the feature under test mostly.
    # But calculate_tolerance_limit supports target_date for QR too. Let's stick to Projection for now as per objective.
]

for folder, target in cases:
    for n in sample_sizes:
        for method_name, suffix, iterations, n_boot in methods:
            filename = f"validation/cases/{folder}/run_test_N{n}_{suffix}.py"
            content = f"""from experiment_runner import run_experiment

if __name__ == "__main__":
    # {folder} (Target={target})
    # {method_name} Method
    run_experiment(
        n_samples={n},
        method_name='{method_name}',
        target_date_alias='{target}',
        iterations={iterations}
    )
"""
            with open(filename, "w") as f:
                f.write(content)
            print(f"Created {filename}")
