from django.shortcuts import render
from scipy.optimize import linprog

# Home Page
def home(request):
    return render(request, 'home.html', {'name': 'Sree Harshini'})

# Solve LP
def solve_lp(request):
    if request.method == "POST":
        try:
            # Retrieve input values
            optimization = request.POST.get("optimization")  # Maximize or Minimize

            # Collect all 'c' values dynamically (objective function coefficients)
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

            # Collect constraints dynamically
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
                    break  # Stop if no more constraints are present

                b_val = request.POST.get(f"b{constraint_index}")
                if b_val is None:
                    break
                constraints.append((constraint_row, float(b_val)))
                constraint_index += 1

            # Prepare A matrix and b vector
            A = [constraint[0] for constraint in constraints]
            b = [constraint[1] for constraint in constraints]

            # Solve the Linear Program using linprog
            result = linprog(c, A_ub=A, b_ub=b, method="highs")

            # Prepare decision variables dynamically
            decision_variables = {}
            if result.success:
                for i in range(len(result.x)):
                    decision_variables[f"x{i+1}"] = result.x[i]

            # Prepare data to send to the template
            context = {
                "status": result.message,
                "optimal_value": -result.fun if result.success and optimization == "maximize" else result.fun if result.success else None,
                "decision_variables": decision_variables if result.success else None
            }
            return render(request, "result.html", context)

        except ValueError:
            return render(request, "result.html", {"error": "Invalid input. Please check your values."})
        except Exception as e:
            return render(request, "result.html", {"error": str(e)})

    return render(request, "home.html")
