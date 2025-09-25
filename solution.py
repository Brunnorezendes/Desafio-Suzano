import numpy as np
from pulp import LpProblem, LpMinimize, LpVariable, lpSum, LpBinary, PULP_CBC_CMD, LpStatus
from main import get_stores_from_csv, one_day_minimum_travel

def solve_vrp_multi_promotor(n_promotores):
    """
    Solve the Vehicle Routing Problem for multiple promoters.
    
    Args:
        n_promotores (int): Number of promoters/salespeople
        
    Returns:
        dict: Results containing status, objective value, assignments, and routes
    """
    
    # Get store data from CSV
    stores = get_stores_from_csv(10, 1)
    
    if not stores:
        return {"error": "Could not load store data"}
    
    num_lojas = len(stores)
    
    # Calculate seconds per unit based on number of stores
    s_por_un = 0
    if num_lojas >= 100:
        s_por_un = 18
    elif num_lojas >= 50:
        s_por_un = 15
    elif num_lojas >= 20:
        s_por_un = 12
    elif num_lojas >= 10:
        s_por_un = 10
    else:
        print("Atenção: Número de lojas fora dos padrões. Usando 10s/un.")
        s_por_un = 10

    # Calculate distance matrix in minutes using Store model
    matriz_deslocamento_minutos = np.zeros((num_lojas, num_lojas))
    for i in range(num_lojas):
        for j in range(num_lojas):
            if i != j:
                euclidean_dist = stores[i].distance(stores[j])
                matriz_deslocamento_minutos[i][j] = (euclidean_dist * s_por_un) / 60
                

    # Fixed parameters
    n_dias = 6
    I = range(n_promotores)
    Z = range(n_dias)

    # Extract data from Store objects
    J = [store.id for store in stores]  # Store IDs
    n_lojas_real = len(J)

    # Visit duration in minutes (Cj)
    C = np.array([store.visit_duration for store in stores])

    # Weekly frequency required per store (Fj)
    F = np.array([store.initial_frequency for store in stores])

    # Travel time matrix (Dkl)
    D = matriz_deslocamento_minutos

    # Available time per day (Az) in hours
    A = np.array([8, 8, 8, 8, 8, 4])

    # --- Model construction and solving ---
    model = LpProblem("VRP_multi_promotor", LpMinimize)

    # Variables
    X = LpVariable.dicts("X", (I, J, Z), cat=LpBinary)
    y = LpVariable.dicts("y", (I, J), cat=LpBinary)
    U = LpVariable.dicts("U", (I, J, J, Z), cat=LpBinary)

    # Objective function
    model += lpSum(D[k_idx, l_idx] * U[i][k][l][z]
                  for i in I for z in Z
                  for k_idx, k in enumerate(J)
                  for l_idx, l in enumerate(J))

    # Constraints
    # Each store must be assigned to exactly one promoter
    for j in J:
        model += lpSum(y[i][j] for i in I) == 1

    # Visit frequency constraint
    for i in I:
        for j_idx, j in enumerate(J):
            model += lpSum(X[i][j][z] for z in Z) == F[j_idx] * y[i][j]

    # Maximum stores per promoter
    for i in I:
        model += lpSum(y[i][j] for j in J) <= 8

    # Time capacity constraint per day
    for i in I:
        for z in Z:
            model += (
                lpSum(C[j_idx] * X[i][j][z] for j_idx, j in enumerate(J)) +
                lpSum(D[k_idx, l_idx] * U[i][k][l][z]
                      for k_idx, k in enumerate(J) for l_idx, l in enumerate(J))
            ) <= A[z] * 60

    # Each promoter must visit at least one store per day
    for i in I:
        for z in Z:
            model += lpSum(X[i][j][z] for j in J) >= 1

    # Flow conservation constraints
    for i in I:
        for j in J:
            for z in Z:
                model += lpSum(U[i][k][j][z] for k in J) == X[i][j][z]
                model += lpSum(U[i][j][l][z] for l in J) == X[i][j][z]

    # No self-loops constraint
    for i in I:
        for k in J:
            for z in Z:
                model += lpSum(U[i][k][k][z] for k in J) <= 1

    # Solve the model
    solver = PULP_CBC_CMD(msg=False, timeLimit=60)  # 60 seconds limit
    model.solve(solver)

    # Collect results
    results = {
        "status": LpStatus[model.status],
        "objective_value": model.objective.value() if model.objective.value() else 0,
        "assignments": {},
        "daily_visits": {},
        "routes": {}
    }

    if model.status == 1:  # Optimal solution found
        # Store assignments
        for i in I:
            results["assignments"][f"promotor_{i+1}"] = []
            for j in J:
                if y[i][j].value() and y[i][j].value() > 0.5:
                    results["assignments"][f"promotor_{i+1}"].append(j)

        # Daily visits
        dias = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado"]
        for z in Z:
            results["daily_visits"][dias[z]] = {}
            for i in I:
                results["daily_visits"][dias[z]][f"promotor_{i+1}"] = []
                for j in J:
                    if X[i][j][z].value() and X[i][j][z].value() > 0.5:
                        results["daily_visits"][dias[z]][f"promotor_{i+1}"].append(j)

        # Calculate optimal routes for each promoter each day using TSP solver
        for z in Z:
            day_name = dias[z]
            results["routes"][day_name] = {}
            for i in I:
                promoter_name = f"promotor_{i+1}"
                visited_stores = results["daily_visits"][day_name][promoter_name]
                
                if len(visited_stores) > 1:
                    # Get Store objects for visited stores
                    day_stores = [store for store in stores if store.id in visited_stores]
                    
                    # Calculate optimal route using TSP
                    min_distance, route_indices = one_day_minimum_travel(day_stores)
                    
                    # Convert route indices back to store IDs
                    route_store_ids = [day_stores[idx-1].id for idx in route_indices]
                    
                    results["routes"][day_name][promoter_name] = {
                        "stores": route_store_ids,
                        "total_distance": (min_distance * s_por_un) / 60,  # Convert back to minutes
                        "route_order": route_indices
                    }
                elif len(visited_stores) == 1:
                    results["routes"][day_name][promoter_name] = {
                        "stores": visited_stores,
                        "total_distance": 0,
                        "route_order": [1]
                    }
                else:
                    results["routes"][day_name][promoter_name] = {
                        "stores": [],
                        "total_distance": 0,
                        "route_order": []
                    }

    return results

def print_results(results):
    """Print the results in a formatted way"""
    if "error" in results:
        print(f"Error: {results['error']}")
        return
    
    print("=" * 50)
    print("RESULTADOS DA OTIMIZAÇÃO")
    print("=" * 50)
    print(f"Status: {results['status']}")
    print(f"Valor da função objetivo: {results['objective_value']:.2f}")
    
    print("\n" + "=" * 30)
    print("ATRIBUIÇÃO DE LOJAS")
    print("=" * 30)
    for promoter, stores in results["assignments"].items():
        print(f"{promoter.replace('_', ' ').title()}: {stores}")
    
    print("\n" + "=" * 30)
    print("VISITAS DIÁRIAS E ROTAS")
    print("=" * 30)
    for day, promoters in results["daily_visits"].items():
        print(f"\n{day.upper()}:")
        for promoter, stores in promoters.items():
            if stores:
                route_info = results["routes"][day][promoter]
                print(f"  {promoter.replace('_', ' ').title()}:")
                print(f"    Lojas visitadas: {stores}")
                if route_info["stores"]:
                    print(f"    Rota otimizada: {route_info['stores']}")
                    print(f"    Distância total: {route_info['total_distance']:.2f}")
            else:
                print(f"  {promoter.replace('_', ' ').title()}: Nenhuma visita")

if __name__ == "__main__":
    # Example usage with 2 promoters
    results = solve_vrp_multi_promotor(n_promotores=2)
    print_results(results)