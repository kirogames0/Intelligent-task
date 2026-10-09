import time
import heapq                      # priority queue (pops the smallest item first)
from collections import deque     # FIFO queue for BFS

MAP_A = ["S..#....", "##.#.##.", "....~~..", ".####.#.", "...~..#G"]
MAP_B = ["S~~~~~~~G", ".#######.", ".........", ".#.#.#.#.", "........."]
MAP_C = ["S..#....", ".#.#.##.", "...#..#.", ".###.##.", "....#..G"]

# Set to None to run all maps, or specify a map name like "A"  <--Change map varable to run a specific map
GRID = MAP_A

MAPS = {"MAP_A": MAP_A, "MAP_B": MAP_B, "MAP_C": MAP_C}

COST = {".": 1, "S": 0, "G": 1, "~": 3}


def check(grid):
    """Validate a map: exactly one S, exactly one G, only known symbols."""
    text = "".join(grid)
    assert text.count("S") == 1 and text.count("G") == 1, "need exactly one S and one G"
    assert set(text) <= set("SG.~#"), "unknown symbol in map"


def build_cells(grid):
    """Convert a list of strings into a dictionary {(row, col): symbol}.

    A position that is off the map is simply not a key, so "does this
    neighbour exist?" is just `nb in cells`. Works for any map size.
    """
    return {(r, c): ch
            for r, row in enumerate(grid)
            for c, ch in enumerate(row)}


def heuristic(a, b):
    """Manhattan distance between two cells.

    Admissible here: every move into a cell costs at least 1, so the true
    remaining cost can never be smaller than the number of moves needed
    when walls are ignored.
    """
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def bfs(cells):
    """Breadth-First Search (uninformed).

    Expands cells in order of number of moves, ignoring terrain cost.
    It finds the path with the FEWEST MOVES, which is not always the cheapest.
    """
    start = next(p for p, ch in cells.items() if ch == "S")
    goal = next(p for p, ch in cells.items() if ch == "G")

    frontier = deque([start])   
    visited = {start}            
    parent = {start: None}     
    expanded = 0
    max_frontier = 1

    while frontier:
        cur = frontier.popleft()
        expanded += 1

        if cur == goal:
            path = []
            while cur:
                path.append(cur)
                cur = parent[cur]
            # Calculate total path cost based on actual terrain costs for fair comparison
            final_path = path[::-1]
            path_cost = sum(COST[cells[node]] for node in final_path[1:])
            return final_path, path_cost, expanded, max_frontier

        r, c = cur
        for nb in [(r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)]:
            if nb in cells and cells[nb] in COST and nb not in visited:
                visited.add(nb)
                parent[nb] = cur
                frontier.append(nb)
                max_frontier = max(max_frontier, len(frontier))

    return None, None, expanded, max_frontier


def ucs(cells):
    """Uniform Cost Search (uninformed).

    Always expands the cell with the lowest cost-so-far g, so the first time
    the goal is popped its path is the CHEAPEST one.
    """
    start = next(p for p, ch in cells.items() if ch == "S")
    goal = next(p for p, ch in cells.items() if ch == "G")

    frontier = [(0, start)]     
    best_cost = {start: 0}      
    parent = {start: None}
    expanded = 0
    max_frontier = 1

    while frontier:
        g, cur = heapq.heappop(frontier)

        # Stale entry: a cheaper route to cur was found after this was pushed
        if g > best_cost[cur]:
            continue

        expanded += 1

        if cur == goal:
            path = []
            while cur:
                path.append(cur)
                cur = parent[cur]
            return path[::-1], g, expanded, max_frontier

        r, c = cur
        for nb in [(r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)]:
            if nb in cells and cells[nb] in COST:
                ng = g + COST[cells[nb]]
                if ng < best_cost.get(nb, float("inf")):
                    best_cost[nb] = ng
                    parent[nb] = cur
                    heapq.heappush(frontier, (ng, nb))
                    max_frontier = max(max_frontier, len(frontier))

    return None, None, expanded, max_frontier


def a_star(cells):
    """A* Search (informed).

    Like UCS, but orders the frontier by f = g + h, where h is the Manhattan
    distance to the goal. The heuristic never overestimates, so A* is still
    optimal, but it expands fewer cells because it is pulled toward G.
    """
    start = next(p for p, ch in cells.items() if ch == "S")
    goal = next(p for p, ch in cells.items() if ch == "G")

    frontier = [(heuristic(start, goal), 0, start)]   # (f, g, cell)
    best_cost = {start: 0}
    parent = {start: None}
    expanded = 0
    max_frontier = 1

    while frontier:
        f, g, cur = heapq.heappop(frontier)

        if g > best_cost[cur]:        # stale entry
            continue

        expanded += 1

        if cur == goal:
            path = []
            while cur:
                path.append(cur)
                cur = parent[cur]
            return path[::-1], g, expanded, max_frontier

        r, c = cur
        for nb in [(r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)]:
            if nb in cells and cells[nb] in COST:
                ng = g + COST[cells[nb]]
                if ng < best_cost.get(nb, float("inf")):
                    best_cost[nb] = ng
                    parent[nb] = cur
                    heapq.heappush(frontier, (ng + heuristic(nb, goal), ng, nb))
                    max_frontier = max(max_frontier, len(frontier))

    return None, None, expanded, max_frontier


ALGORITHMS = {"BFS": bfs, "UCS": ucs, "A*": a_star}


def draw_path(grid, path):
    """Return the map as text with path cells replaced by '*' (S and G are kept)."""
    rows = [list(row) for row in grid]
    for r, c in path:
        if rows[r][c] not in "SG":
            rows[r][c] = "*"
    return "\n".join("".join(row) for row in rows)


def run_algorithm(name, grid):
    """Run one algorithm on a grid and return a dict of results, including run time."""
    cells = build_cells(grid)
    start = time.perf_counter()
    path, cost, expanded, max_frontier = ALGORITHMS[name](cells)
    elapsed_ms = (time.perf_counter() - start) * 1000
    return {"name": name, "path": path, "cost": cost, "expanded": expanded,
            "max_frontier": max_frontier, "time_ms": elapsed_ms}


def show_result(res, grid):
    print(f"Algorithm : {res['name']}")
    if res["path"] is None:
        print("No path found")
        print(f"Nodes expanded: {res['expanded']}")
    else:
        print(f"Path      : {res['path']}")
        print(f"Length    : {len(res['path']) - 1} moves")
        print(f"Cost      : {res['cost']}")
        print(f"Expanded  : {res['expanded']}")
        print(f"Max frontier: {res['max_frontier']}")
        print(f"Time      : {res['time_ms']:.4f} ms")
        print("Map with path:")
        print(draw_path(grid, res["path"]))
    print("-" * 60)


check(GRID)
print("=== Running on the selected GRID ===")
print("\n".join(GRID))
print("=" * 60)
for algo_name in ALGORITHMS:
    show_result(run_algorithm(algo_name, GRID), GRID)

print() 
print("\/" * 80) 
print()   

rows = []
for map_name, grid in MAPS.items():
    check(grid)
    for algo_name in ALGORITHMS:
        res = run_algorithm(algo_name, grid)
        found = res["path"] is not None
        rows.append({
            "Map": map_name,
            "Algorithm": algo_name,
            "Path length": len(res["path"]) - 1 if found else "-",
            "Path cost": res["cost"] if found else "-",
            "Nodes expanded": res["expanded"],
            "Max frontier": res["max_frontier"],
            "Time (ms)": f"{res['time_ms']:.4f}",
            "Result": "found" if found else "No path found",
        })

print("\n=== Results table: MAP_A, MAP_B, MAP_C ===")
headers = list(rows[0].keys())
widths = [max(len(h), *(len(str(r[h])) for r in rows)) for h in headers]
line = "+-" + "-+-".join("-" * w for w in widths) + "-+"
print(line)
print("| " + " | ".join(h.ljust(w) for h, w in zip(headers, widths)) + " |")
print(line)
for i, r in enumerate(rows):
    print("| " + " | ".join(str(r[h]).ljust(w) for h, w in zip(headers, widths)) + " |")
    if i % len(ALGORITHMS) == len(ALGORITHMS) - 1:
        print(line)    

print() 
print("\/" * 80)  
print() 

print("\n=== Paths on every map ===")
for map_name, grid in MAPS.items():
    print("#" * 60)
    print(f"# {map_name}")
    print("#" * 60)
    for algo_name in ALGORITHMS:
        show_result(run_algorithm(algo_name, grid), grid)
