from solution import solve_vrp_multi_promotor, print_results

def get_minimum_promoters(n_stores=10, instance=1):
    n = 2
    results = solve_vrp_multi_promotor(n_promotores=n, n_stores=n_stores, instance=instance)
    while results.get("status") != "Optimal":
        n = n+1
        results = solve_vrp_multi_promotor(n_promotores=n, n_stores=n_stores, instance=instance)
    print(f"Número mínimo de promotores necessário: {n}")
    print_results(results)

if __name__ == "__main__":
    get_minimum_promoters(n_stores=20, instance=1)
    