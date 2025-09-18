# PO-207 Project

This project contains algorithms for solving the Traveling Salesman Problem (TSP) for store routing optimization.

## Files

- `main.py` - Main script containing TSP solver algorithm
- `models.py` - Store model definitions
- `instances/` - Directory containing CSV data files with store instances

## Usage

Run the main script to solve TSP for the store routing problem:

```bash
python main.py
```

The algorithm uses dynamic programming with bitmasks to find the optimal route through all stores.

## Data Setup

The instance data is not included in this repository. To run the project:

1. Download the data from [https://drive.google.com/file/d/1M7EQclDZD-3eLizeMhwGeqViCfQ4eyZO/view]
2. Extract to `instances/` directory
3. Ensure the structure matches:

```
instances/
  10_stores/
    instance_001/
      stores.csv
    instance_002/
      stores.csv
    ...
  20_stores/
    instance_001/
      stores.csv
    ...
```

## Data Format

Store data is expected in CSV format with columns:
- store_id
- type
- x_coordinate
- y_coordinate
- visit_duration_minutes
- initial_frequency
- baseline_profitability
- profitability_freq_1 through profitability_freq_6