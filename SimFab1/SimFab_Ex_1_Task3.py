import numpy as np
import matplotlib.pyplot as plt
import sys
from SimFab_Ex_1_Task2 import SDFGrid  # to import the previous code and calculations of task 2

# for advancing the surface by simply subtracting velocity value
def simple_advance(grid, V, del_t):
    return grid - V * del_t

# for advancing the surface using the Engquist-Osher scheme
def engquist_osher(grid, velocity_field, spacing, del_t):
    n_x, n_y = grid.shape
    new_grid = np.copy(grid)
    for x in range(n_x):
        for y in range(n_y):
            D_x, D_y = numerical_derivative(grid, x, y, spacing)
            V = velocity_field[x, y]
            if V < 0:
                Dx_neg = max(-D_x, 0)**2 + min(-D_x, 0)**2
                Dy_neg = max(-D_y, 0)**2 + min(-D_y, 0)**2
                gradSDF_magnitude = np.sqrt(Dx_neg + Dy_neg)
            else:
                Dx_pos = max(D_x, 0)**2 + min(D_x, 0)**2
                Dy_pos = max(D_y, 0)**2 + min(D_y, 0)**2
                gradSDF_magnitude = np.sqrt(Dx_pos + Dy_pos)
            new_grid[x, y] -= V * gradSDF_magnitude * del_t
    return new_grid

# computing numerical derivatives
def numerical_derivative(grid, x, y, spacing):
    n_x, n_y = grid.shape
    D_x = (grid[min(x + 1, n_x - 1), y] - grid[max(x - 1, 0), y]) / (2 * spacing)
    D_y = (grid[x, min(y + 1, n_y - 1)] - grid[x, max(y - 1, 0)]) / (2 * spacing)
    return D_x, D_y

# calculating the velocity field based on a given vector
def velocity_field(grid, V_vector):
    n_x, n_y = grid.shape
    velocity = np.zeros_like(grid)
    sdf_grid = SDFGrid(n_x, n_y, 1.0)
    sdf_grid.grid = grid
    for x in range(n_x):
        for y in range(n_y):
            n = sdf_grid.normal(x, y)
            V = np.dot(V_vector, n)
            velocity[x, y] = V
    return velocity

# calculation when the curvature is used as velocity
def curvature_as_velocity(grid):
    n_x, n_y = grid.shape
    velocity = np.zeros_like(grid)
    sdf_grid = SDFGrid(n_x, n_y, 1.0)
    sdf_grid.grid = grid
    for x in range(n_x):
        for y in range(n_y):
            k = sdf_grid.curvature(x, y)   # k = curvature
            velocity[x, y] = -k
    return velocity

# for comparing different surface advancement methods
def compare_advancements(shape, V, time, method, filename, spacing):
    grid = np.loadtxt(filename, delimiter=',')
    sdf_grid = SDFGrid(grid.shape[0], grid.shape[1], spacing)
    sdf_grid.grid = grid
    for t in time:
        if method == "simple advance":
            new_grid = simple_advance(sdf_grid.grid, V, t)
        elif method == "engquist_osher":
            velocity_field = np.full_like(grid, V)
            new_grid = engquist_osher(sdf_grid.grid, velocity_field, sdf_grid.spacing, t)
        output_filename = f'{shape.lower()}_{method}_t_{t}_dx_{spacing}.csv'
        np.savetxt(output_filename, new_grid, delimiter=',')
        print(f'Saved grid to {output_filename}')
        plot_grid(new_grid, f'{shape}    {method}    t={t}    dx={spacing}', output_filename.replace('.csv', '.png'))

# Plotting the grid
def plot_grid(grid, title, filename):
    plt.figure(figsize=(8, 6))
    plt.contourf(grid.T, levels=50, cmap='RdYlBu')
    plt.colorbar(label='Signed Distance')
    plt.contour(grid.T, levels=[0], colors='black')
    plt.title(title)
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.grid(True)
    plt.savefig(filename)
    plt.show()
    plt.close()

# main function for command-line arguments and running the script
def main():
    args = sys.argv[1:]
    if len(args) < 5:   # both circle and rectangle require 5 arguments
        print("Provide the following values: ./Grid[x-size(n_x) y-size(n_y)] [Circle / Rectangle] [parameters]")
        return
    n_x = int(args[0])
    n_y = int(args[1])
    shape = args[2]
    grid = SDFGrid(n_x, n_y, 1.0)
    if shape == "Circle":
        center = (float(args[3]), float(args[4]))
        radius = 10      # Radius is fixed at 10
        grid.distance_circle(center, radius)
        grid.save_to_csv('circle_grid.csv')
    elif shape == "Rectangle":
        min_corner = (float(args[3]), float(args[4]))
        max_corner = (min_corner[0] + 5, min_corner[1] + 20)           # Side lengths are fixed at 5 and 20
        grid.distance_rectangle(min_corner, max_corner)
        grid.save_to_csv('rectangle_grid.csv')
    
    V = 10    # for making the calculations for V = 10
    time = [0.1, 1]
    for method in ["simple advance", "engquist_osher"]:
        for spacing in [1, 0.25]:
            filename = f'{shape.lower()}_grid.csv'
            compare_advancements(shape, V, time, method, filename, spacing)

    # using Engquist-Osher scheme, investigating behaviour of rectangle and when curvature is used as velocity
    V_vector = np.array([1, 0])
    grid = np.loadtxt(f'{shape.lower()}_grid.csv', delimiter=',')
    for spacing in [1, 0.25]:
        velocity = velocity_field(grid, V_vector)
        t = 1
        new_grid = engquist_osher(grid, velocity, spacing, t)
        np.savetxt(f'{shape.lower()}_vector_velocity_t_{t}_dx_{spacing}.csv', new_grid, delimiter=',')
        print(f'Saved grid with vector velocity function to {shape.lower()}_vector_velocity_t_{t}_dx_{spacing}.csv')
        plot_grid(new_grid, f'{shape}    vector velocity    t={t}     dx={spacing}', f'{shape.lower()}_vector_velocity_t_{t}_dx_{spacing}.png')

        curvature_velocity = curvature_as_velocity(grid)
        new_grid = engquist_osher(grid, curvature_velocity, spacing, t)
        np.savetxt(f'{shape.lower()}_curvature_velocity_t_{t}_dx_{spacing}.csv', new_grid, delimiter=',')
        print(f'Saved grid with curvature velocity to {shape.lower()}_curvature_velocity_t_{t}_dx_{spacing}.csv')
        plot_grid(new_grid, f'{shape}    curvature velocity    t={t}    dx={spacing}', f'{shape.lower()}_curvature_velocity_t_{t}_dx_{spacing}.png')

if __name__ == '__main__':
    main()
