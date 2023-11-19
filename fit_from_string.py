import numpy as np
import symfit as sf
from sympy import symbols, parse_expr
import matplotlib.pyplot as plt

def create_equation_function(equation_string):
    # Parse the equation string into a symbolic expression
    equation_expr = parse_expr(equation_string)
    
    # Extract the parameters from the expression
    parameters = list(equation_expr.free_symbols)
    parameters.remove(symbols('x'))
    
    params = {str(param): sf.Parameter(str(param)) for param in parameters}

    model = {sf.Variable('y'): equation_expr.subs({param: params[str(param)] for param in parameters})}

    return params, model, equation_expr.subs({param: params[str(param)] for param in parameters})

def fit_from_str(equation_string, x_data, y_data):
    if '|' in equation_string:
        return fit_from_str_2functions(equation_string, x_data, y_data)
    params, model, _ = create_equation_function(equation_string)
    fit = sf.Fit(model, x=x_data, y=y_data)
    return(fit)

# accepts equation in format (equation to be used before deviding point)|(equation to be used before deviding point) for example x**2|m*x+b you can add limits for the deviding point like so: eq1|eq2|min;max
def fit_from_str_2functions(equation_string, x_data, y_data):
    if len(equation_string.split('|')) not in [2,3]:
        raise Exception('Invalid equation string')
    x0 = sf.Parameter('x0')
    if len(equation_string.split('|')) == 2:
        eq_str_1, eq_str_2 = equation_string.split('|')
    else:
        eq_str_1, eq_str_2, x0_limits = equation_string.split('|')
        x0.min = x0_limits.split(';')[0]
        x0.max = x0_limits.split(';')[1]
    _, _, eq1 = create_equation_function(eq_str_1)
    _, _, eq2 = create_equation_function(eq_str_2)
    y = sf.Variable('y')
    model = {y: sf.Piecewise((eq1, symbols('x') <= x0), (eq2, symbols('x') > x0))}
    print(model)
    fit = sf.Fit(model, x=x_data, y=y_data)
    return fit

if __name__ == '__main__':
    x_data = np.arange(0.1, 3.9, 0.2)
    y_data = [15.18, 262.94, 337.03, 319.32, 211.86, 100.82, 39.35, 15.52, 7.70, 3.38, 1.83, 0.95, 0.52, 0.23, 0.12, 0.07, 0.04, 0.02, 0.01]
    equation_string = 'a * x**b * exp(-c*x)'

    fit = fit_from_str(equation_string, x_data, y_data)
    fit_result = fit.execute()
    print(fit_result)

    plt.scatter(x_data, y_data)
    plt.plot(x_data, fit.model(x=x_data, **fit_result.params).y)
    plt.yscale('log')
    plt.show()
