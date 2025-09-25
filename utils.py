from models import Store
from typing import List
import csv
import os

def one_day_minimum_travel(stores: List[Store]):
    n = len(stores)
    if n <= 1:
        return 0, []
    
    min_distance = float('inf')
    best_path = []
    
    # Try starting from each city
    for start_city in range(n):
        # dp[mask][i] = minimum distance to visit all cities in mask and end at city i
        dp = [[float('inf')] * n for _ in range(1 << n)]
        # parent[mask][i] = previous city in optimal path
        parent = [[-1] * n for _ in range(1 << n)]
        
        # Start from current city
        dp[1 << start_city][start_city] = 0
        
        # Fill dp table
        for mask in range(1 << n):
            for u in range(n):
                if not (mask & (1 << u)):
                    continue
                
                for v in range(n):
                    if u == v or (mask & (1 << v)):
                        continue
                    
                    new_mask = mask | (1 << v)
                    new_dist = dp[mask][u] + stores[u].distance(stores[v])
                    if new_dist < dp[new_mask][v]:
                        dp[new_mask][v] = new_dist
                        parent[new_mask][v] = u
        
        # Find minimum cost to visit all cities
        full_mask = (1 << n) - 1
        end_city = -1
        current_min = float('inf')
        
        for i in range(n):
            if dp[full_mask][i] < current_min:
                current_min = dp[full_mask][i]
                end_city = i
        
        # If this is better than previous attempts, reconstruct path
        if current_min < min_distance:
            min_distance = current_min
            
            # Reconstruct path
            path = []
            mask = full_mask
            curr = end_city
            
            while curr != -1:
                path.append(curr)
                next_curr = parent[mask][curr]
                if next_curr != -1:
                    mask ^= (1 << curr)
                curr = next_curr
            
            best_path = [x + 1 for x in path[::-1]]  # Reverse to get correct order and add 1 to all elements
    
    return min_distance, best_path

def get_stores_from_csv(store_number=10, instance_number=1):
    
    if instance_number < 1 or instance_number > 50 or store_number not in [10, 20, 50, 100]:
        print("Error: instance_number must be between 1 and 50, and store_number must be one of [10, 20, 50, 100].")
        return []
    
    csv_file_path = os.path.join("instances", f"{store_number}_stores", f"instance_{instance_number:03d}", "stores.csv")
    
    # Check if instances directory exists
    if not os.path.exists("instances"):
        print("Error: 'instances' directory not found.")
        print("Please download the data and place it in the 'instances' directory.")
        print("See README.md for setup instructions.")
        return []

    stores = []
    
    try:
        with open(csv_file_path, 'r', newline='') as csvfile:
            reader = csv.reader(csvfile)
            
            # Skip header if it exists
            next(reader, None)  # Skip header row
            
            for row in reader:
                if len(row) >= 12:  # Ensure we have all required columns
                    # Parse the row data according to your Store model
                    store = Store(
                        id=row[0],  # id as string
                        type=row[1],  # type as string
                        coordinates=(float(row[2]), float(row[3])),  # x, y coordinates
                        visit_duration=int(row[4]),  # visit_duration as int
                        initial_frequency=int(row[5]),  # visit_frequency as int
                        baseline_profitability=float(row[6]),  # baseline_profitability
                        profitability_freq_1=float(row[7]),
                        profitability_freq_2=float(row[8]),
                        profitability_freq_3=float(row[9]),
                        profitability_freq_4=float(row[10]),
                        profitability_freq_5=float(row[11]),
                        profitability_freq_6=float(row[12]) if len(row) > 12 else 0.0
                    )
                    stores.append(store)
        
        print(f"Loaded {len(stores)} stores from {csv_file_path}")
        
        if stores:
            return stores
        else:
            print("No stores found in the CSV file.")
            
    except FileNotFoundError:
        print(f"Error: Could not find the CSV file at {csv_file_path}")
        print("Please make sure the file exists and the path is correct.")
    except Exception as e:
        print(f"Error reading CSV file: {e}")

