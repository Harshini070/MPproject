from django.shortcuts import render
from scipy.optimize import linprog

# Create your views here.
def home(request):
    return render(request, 'home.html', {'name': 'Sree Harshini'})

def solve_lp(request):
    if request.method == "POST":
        try:
            # Retrieve input values from the form
            optimization = request.POST.get("optimization")  # Maximize or Minimize
            c1 = float(request.POST.get("c1"))
            c2 = float(request.POST.get("c2"))

            # Prepare the objective function
            c = [-c1, -c2] if optimization == "maximize" else [c1, c2]

            # Gather all constraints dynamically
            # Get all constraint variables (e.g., a11, a12, b1, ...)
            constraints = []
            for i in range(1, len(request.POST) // 3 + 1):  # Constraints are in sets of 3 inputs
                a1 = float(request.POST.get(f"a{i}1", 0))  # Default to 0 if not provided
                a2 = float(request.POST.get(f"a{i}2", 0))  # Default to 0 if not provided
                b_val = float(request.POST.get(f"b{i}", 0))  # Default to 0 if not provided
                constraints.append(([a1, a2], b_val))  # Add tuple (coefficients, RHS)

            # Prepare the A matrix and b vector
            A = [constraint[0] for constraint in constraints]
            b = [constraint[1] for constraint in constraints]

            # Solve the Linear Program using linprog
            result = linprog(c, A_ub=A, b_ub=b, method="highs")

            # Prepare data to send to the template
            context = {
                "status": result.message,
                "optimal_value": -result.fun if result.success and optimization == "maximize" else result.fun if result.success else None,
                "x1": result.x[0] if result.success else None,
                "x2": result.x[1] if result.success else None,
            }
            return render(request, "result.html", context)

        except ValueError as e:
            return render(request, "result.html", {"error": "Invalid input. Please check your values."})
        except Exception as e:
            return render(request, "result.html", {"error": str(e)})

    return render(request, "home.html")