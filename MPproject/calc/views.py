from django.shortcuts import render
from scipy.optimize import linprog
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO
import base64
from django.http import HttpResponse


# Home Page
def home(request):
    return render(request, 'home.html', {'name': 'Sree Harshini'})


# Solve LP using Simplex and Graphical Methods
def solve_lp(request):
    if request.method == "POST":
        try:
            method = request.POST.get("method")

            if method == "transportation":
                return solve_transportation(request)

            optimization = request.POST.get("optimization") 

            # Collecting objective function coefficients
            c_values = []
            i = 1
            while True:
                c_val = request.POST.get(f"c{i}")
                if c_val is None:
                    break
                c_values.append(float(c_val))
                i += 1

            # Adjust signs based on Maximize/Minimize
            c = [-val for val in c_values] if optimization == "maximize" else c_values

            # Collecting constraints
            constraints = []
            num_variables = len(c_values)
            constraint_index = 1

            while True:
                constraint_row = []
                for j in range(1, num_variables + 1):
                    coef = request.POST.get(f"a{constraint_index}{j}")
                    if coef is None:
                        break
                    constraint_row.append(float(coef))

                if not constraint_row:
                    break

                b_val = request.POST.get(f"b{constraint_index}")
                if b_val is None:
                    break
                constraints.append((constraint_row, float(b_val)))
                constraint_index += 1

            # Prepare A matrix and b vector
            A = [constraint[0] for constraint in constraints]
            b = [constraint[1] for constraint in constraints]

            # Solve using Simplex Method
            result = linprog(c, A_ub=A, b_ub=b, method="highs")

            decision_variables = {}
            if result.success:
                for i in range(len(result.x)):
                    decision_variables[f"x{i+1}"] = round(result.x[i], 2)

            # Prepare Graphical Solution (only for 2 variables)
            is_graphical = False
            graph_url = None
            if num_variables == 2:
                is_graphical = True
                graph_url = generate_graph(A, b, c_values)
            elif num_variables > 2:
                is_graphical = False  # Cannot solve graphically for more than 2 variables

            context = {
                "optimal_value": round(-result.fun, 2) if result.success and optimization == "maximize" else round(result.fun, 2) if result.success else None,
                "decision_variables": decision_variables if result.success else None,
                "is_graphical": is_graphical,
                "graph_url": graph_url,
                
            }

            return render(request, "result.html", context)
        except ValueError:
            return render(request, "result.html", {"error": "Invalid input. Please check your values."})
        except Exception as e:
            return render(request, "result.html", {"error": f"An error occurred: {str(e)}"})

    return render(request, "home.html")


# Function to generate a graph for the Graphical Method
def generate_graph(A, b, c):
    fig, ax = plt.subplots(figsize=(5, 5))
    x = np.linspace(0, 10, 400)

    y_constraints = []
    for i in range(len(A)):
        if A[i][1] != 0:  # Avoid division by zero
            y = (b[i] - A[i][0] * x) / A[i][1]
            y_constraints.append(y)
            ax.plot(x, y, label=f'{A[i][0]}x1 + {A[i][1]}x2 ≤ {b[i]}')

    # Fill feasible region
    if len(y_constraints) > 1:
        plt.fill_between(x, np.maximum(0, np.minimum.reduce(y_constraints)), alpha=0.3, color='purple')

    ax.set_xlabel('x1')
    ax.set_ylabel('x2')
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axhline(0, color='black', lw=1)
    ax.axvline(0, color='black', lw=1)
    ax.legend()

    # Convert graph to image
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    graph_base64 = base64.b64encode(buffer.getvalue()).decode()
    plt.close()

    return f"data:image/png;base64,{graph_base64}"


# Solve Transportation Problem
def solve_transportation(request):
    try:
        num_sources = int(request.POST.get("num_sources"))
        num_destinations = int(request.POST.get("num_destinations"))

        # Read cost matrix
        cost_matrix = []
        for i in range(1, num_sources + 1):
            row = []
            for j in range(1, num_destinations + 1):
                row.append(float(request.POST.get(f"c_{i}_{j}")))
            cost_matrix.append(row)

        cost_matrix = np.array(cost_matrix)

        # Read supply values
        supply = []
        for i in range(1, num_sources + 1):
            supply.append(float(request.POST.get(f"s{i}")))

        # Read demand values
        demand = []
        for j in range(1, num_destinations + 1):
            demand.append(float(request.POST.get(f"d{j}")))

        supply = np.array(supply)
        demand = np.array(demand)

        # Solve using a transportation algorithm (Northwest Corner Method)
        result, allocation = solve_transportation_problem(cost_matrix, supply, demand)

        return render(request, "result.html", {
            "transportation_cost": result,
            "allocation": allocation,
            "num_sources": num_sources,
            "num_destinations": num_destinations,  # Add this line
            "is_transportation": True,
        })

    except ValueError:
        return render(request, "result.html", {"error": "Invalid input. Please check your values."})
    except Exception as e:
        return render(request, "result.html", {"error": f"An error occurred: {str(e)}"})


# Transportation Solver (Using Northwest Corner Method)
def solve_transportation_problem(cost_matrix, supply, demand):
    # Ensure problem is balanced
    if supply.sum() != demand.sum():
        raise ValueError("Unbalanced problem: Total supply must equal total demand.")

    # Initialize allocation matrix
    allocation = np.zeros_like(cost_matrix)

    # Start with Northwest Corner Method
    i, j = 0, 0
    while i < len(supply) and j < len(demand):
        if supply[i] < demand[j]:
            allocation[i, j] = supply[i]
            demand[j] -= supply[i]
            i += 1
        else:
            allocation[i, j] = demand[j]
            supply[i] -= demand[j]
            j += 1

    total_cost = np.sum(allocation * cost_matrix)
    return total_cost, allocation
