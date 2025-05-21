import tkinter as tk
import random
import math

VARIANT = 4408
N = 10
N1, N2, N3, N4 = 4, 4, 0, 8
SEED = VARIANT

def generate_adjacency_matrix(n, k, seed):
    random.seed(seed)
    matrix = []
    for _ in range(n):
        row = []
        for _ in range(n):
            value = random.uniform(0, 2.0) * k
            row.append(1 if value >= 1.0 else 0)
        matrix.append(row)
    for i in range(n):
        matrix[i][i] = 0
    return matrix

def transpose_matrix(matrix):
    return [[matrix[j][i] for j in range(len(matrix))] for i in range(len(matrix))]

def to_undirected(matrix):
    n = len(matrix)
    undirected = [[0]*n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if matrix[i][j] or matrix[j][i]:
                undirected[i][j] = undirected[j][i] = 1
    return undirected

def vertex_degrees(matrix):
    degrees = [sum(row) for row in matrix]
    return degrees

def semi_degrees(matrix):
    out_degrees = [sum(row) for row in matrix]
    in_degrees = [sum(col) for col in zip(*matrix)]
    return in_degrees, out_degrees

def is_regular(degrees):
    return all(deg == degrees[0] for deg in degrees), degrees[0] if degrees else 0

def find_hanging_and_isolated(degrees):
    isolated = [i for i, deg in enumerate(degrees) if deg == 0]
    hanging = [i for i, deg in enumerate(degrees) if deg == 1]
    return isolated, hanging

def matrix_power(matrix, power):
    n = len(matrix)
    result = [[0]*n for _ in range(n)]
    if power == 1:
        return [row[:] for row in matrix]
    if power == 2:
        for i in range(n):
            for j in range(n):
                result[i][j] = sum(matrix[i][k] * matrix[k][j] for k in range(n))
    if power == 3:
        for i in range(n):
            for j in range(n):
                result[i][j] = sum(
                    sum(matrix[i][k] * matrix[k][m] * matrix[m][j] for m in range(n)) for k in range(n))
    return result

def reachability_matrix(matrix):
    n = len(matrix)
    reach = [row[:] for row in matrix]
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if reach[i][j] or (reach[i][k] and reach[k][j]):
                    reach[i][j] = 1
    return reach

def strong_connectivity_matrix(reach):
    n = len(reach)
    return [[1 if reach[i][j] and reach[j][i] else 0 for j in range(n)] for i in range(n)]

def find_strong_components(matrix):
    n = len(matrix)
    visited = [False]*n
    components = []

    def dfs(v, comp):
        visited[v] = True
        comp.append(v)
        for u in range(n):
            if matrix[v][u] and not visited[u]:
                dfs(u, comp)

    for i in range(n):
        if not visited[i]:
            comp = []
            dfs(i, comp)
            components.append(sorted(comp))

    return components

def condensation_graph(components, matrix):
    comp_count = len(components)
    cond = [[0]*comp_count for _ in range(comp_count)]
    comp_index = {}
    for idx, comp in enumerate(components):
        for v in comp:
            comp_index[v] = idx
    for i in range(len(matrix)):
        for j in range(len(matrix)):
            if matrix[i][j]:
                ci = comp_index[i]
                cj = comp_index[j]
                if ci != cj:
                    cond[ci][cj] = 1
    return cond

def calculate_positions(n, width, height):
    margin = 100
    center_x, center_y = width // 2, height // 2
    
    rect_width = width - 2 * margin
    rect_height = height - 2 * margin
    
    top_left = (margin, margin)
    top_right = (width - margin, margin)
    bottom_right = (width - margin, height - margin)
    bottom_left = (margin, height - margin)
    
    positions = [(center_x, center_y)] 
    
    if n == 1:
        return positions
    
    sides = [
        (top_left, top_right),
        (top_right, bottom_right),
        (bottom_right, bottom_left), 
        (bottom_left, top_left)  
    ]
    
    vertices_per_side = (n - 5) // 4  
    remainder = (n - 5) % 4
    
    positions.extend([top_left, top_right, bottom_right, bottom_left])
    
    for side_idx, (start, end) in enumerate(sides):
        count = vertices_per_side + (1 if side_idx < remainder else 0)
        
        for i in range(count):
            t = (i + 1) / (count + 1)
            x = start[0] + t * (end[0] - start[0])
            y = start[1] + t * (end[1] - start[1])
            positions.append((x, y))
    
    return positions[:n]

def draw_graph(matrix, title):
    n = len(matrix)
    width, height = 800, 600
    root = tk.Tk()
    root.title(title)
    canvas = tk.Canvas(root, width=width, height=height, bg='white')
    canvas.pack()
    pos = calculate_positions(n, width, height)
    radius = 20

    for i in range(n):
        x, y = pos[i]
        is_center = (x == width//2 and y == height//2)
        is_corner = (x in [100, width-100] and y in [100, height-100])
        color = 'lightgreen' if is_corner else ('lightblue' if is_center else 'white')
        canvas.create_oval(x-radius, y-radius, x+radius, y+radius, 
                         fill=color, outline='black', width=2)
        canvas.create_text(x, y, text=str(i), font=('Arial', 12))

    for i in range(n):
        for j in range(n):
            if matrix[i][j]:
                x1, y1 = pos[i]
                x2, y2 = pos[j]
                
                if i == j:
                    loop_radius = 25
                    canvas.create_oval(x1+radius, y1-radius-loop_radius, 
                                     x1+radius+loop_radius, y1-radius, 
                                     outline='blue', width=2, arrow=tk.LAST)
                else:
                    dx, dy = x2 - x1, y2 - y1
                    dist = math.hypot(dx, dy)
                    
                    if dist > 0:
                        dx, dy = dx/dist, dy/dist
                    
                    curvature = 0.3
                    
                    if matrix[j][i] and j > i:
                        curvature = 0.6 * (-1 if (i + j) % 2 else 1)
                    
                    cx = (x1 + x2) / 2 + curvature * dy * dist * 0.5
                    cy = (y1 + y2) / 2 - curvature * dx * dist * 0.5
                    
                    sx = x1 + dx * radius
                    sy = y1 + dy * radius
                    ex = x2 - dx * radius
                    ey = y2 - dy * radius
                    
                    canvas.create_line(sx, sy, cx, cy, ex, ey,
                                     smooth=True,
                                     arrow=tk.LAST,
                                     fill='blue',
                                     width=2,
                                     splinesteps=20)

    root.mainloop()

def main():
    k1 = 1.0 - N3 * 0.01 - N4 * 0.01 - 0.3
    k2 = 1.0 - N3 * 0.005 - N4 * 0.005 - 0.27

    adj1 = generate_adjacency_matrix(N, k1, SEED)
    adj1u = to_undirected(adj1)

    print("Directed graph:")
    for row in adj1:
        print(row)
    print("\nUndirected graph:")
    for row in adj1u:
        print(row)

    print("\nDirected degrees:", vertex_degrees(adj1))
    print("Undirected degrees:", vertex_degrees(adj1u))
    indeg, outdeg = semi_degrees(adj1)
    print("In-degrees:", indeg)
    print("Out-degrees:", outdeg)

    reg, deg = is_regular(vertex_degrees(adj1))
    print(f"Regular: {reg}, degree: {deg if reg else '-'}")

    iso, hang = find_hanging_and_isolated(vertex_degrees(adj1u))
    print("Isolated vertices:", iso)
    print("Hanging vertices:", hang)

    draw_graph(adj1, "Directed Graph")
    draw_graph(adj1u, "Undirected Graph")

    print("\n\n=== NEW GRAPH WITH UPDATED K ===")
    adj2 = generate_adjacency_matrix(N, k2, SEED)
    indeg2, outdeg2 = semi_degrees(adj2)
    print("In-degrees:", indeg2)
    print("Out-degrees:", outdeg2)

    A2 = matrix_power(adj2, 2)
    A3 = matrix_power(adj2, 3)

    print("Paths of length 2:")
    for i in range(N):
        for j in range(N):
            if A2[i][j]:
                print(f"{i} -> ... -> {j}")

    print("Paths of length 3:")
    for i in range(N):
        for j in range(N):
            if A3[i][j]:
                print(f"{i} -> ... -> {j}")

    reach = reachability_matrix(adj2)
    print("Reachability matrix:")
    for row in reach:
        print(row)

    strong = strong_connectivity_matrix(reach)
    print("Strong connectivity matrix:")
    for row in strong:
        print(row)

    comps = find_strong_components(strong)
    print("Strongly connected components:")
    for idx, comp in enumerate(comps):
        print(f"Component {idx+1}: {comp}")

    cond = condensation_graph(comps, adj2)
    print("Condensation graph:")
    for row in cond:
        print(row)

    draw_graph(adj2, "Updated Directed Graph")
    draw_graph(cond, "Condensation Graph")

    print("\n=== Висновки ===")
    print(f"Кількість сильно зв'язаних компонент: {len(comps)}")
    if reg:
        print(f"Граф регулярний зі ступенем {deg}")
    else:
        print("Граф не є регулярним")
    if all(all(row) for row in strong):
        print("Граф сильно зв'язний")
    else:
        print("Граф не є сильно зв'язним")
    print(f"Ізольовані вершини: {iso}")
    print(f"Висячі вершини: {hang}")

if __name__ == "__main__":
    main()
