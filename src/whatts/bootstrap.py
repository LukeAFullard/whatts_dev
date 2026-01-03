import numpy as np

def generate_block_bootstraps(values, dates, n_boot=2000, block_size=None):
    """
    Generates synthetic datasets using Moving Block Bootstrap (MBB).

    Args:
        values (np.array): The time series values.
        dates (np.array): The ordinal dates (X-axis).
        n_boot (int): Number of bootstrap iterations.
        block_size (int): Length of blocks. If None, uses n^(1/3) heuristic.

    Yields:
        tuple: (resampled_values, resampled_dates)
    """
    n = len(values)

    # Heuristic for block size if not provided: cube root of N
    # (Common rule of thumb for preserving stationarity within blocks)
    if block_size is None:
        block_size = int(np.cbrt(n))
        block_size = max(2, block_size) # At least pairs

    # We use Circular Block Bootstrap logic for simplicity (wrapping around)
    # or just standard Moving Block. Let's use Standard Moving Block.

    # Indices of all possible blocks
    # If N=60, block=4, we have 57 starting positions.
    num_blocks = n - block_size + 1

    for _ in range(n_boot):
        # We need to construct a new series of length N
        # We need ceil(N / block_size) blocks
        indices = []

        while len(indices) < n:
            # Pick a random start index
            start_idx = np.random.randint(0, num_blocks)
            # Add the block
            indices.extend(range(start_idx, start_idx + block_size))

        # Trim to exact length N
        indices = indices[:n]

        # Return the data pairs (Y, X)
        # Note: We must keep Y and X paired together!
        # We are bootstrapping the *residuals* usually, but for QR
        # paired bootstrapping (resampling rows) is robust.
        yield values[indices], dates[indices]
