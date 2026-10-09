from collections import deque
import heapq  # heapq gives us a priority queue (always pops the smallest item first)

# ---------------------------------------------------------------------------
# Cost table: cost of ENTERING a cell of each symbol.
# "#" (wall) is deliberately missing: any symbol not in this table is
# treated as impassable, so walls need no special-case code.
# ---------------------------------------------------------------------------
COST = {".": 1, "S": 0, "G": 1, "~": 3}


def build_cells(grid):
    """Convert a list of strings into a dictionary {(row, col): symbol}.

    Why a dictionary? The search never needs to know the map's width or
    height: a position that is off the map is simply not a key, so we can
    check "does this neighbour exist?" with `nb in cells`.
    Works for any map size, even rows of different lengths.
    """
    return {(r, c): ch                      # key = (row, col), value = symbol
            for r, row in enumerate(grid)   # r = row index, row = the string
            for c, ch in enumerate(row)}    # c = column index, ch = one character


def ucs(cells):
    """Uniform Cost Search.

    Input : the cells dictionary from build_cells.
    Output: (path, total_cost, nodes_expanded)
            path is a list of (row, col) from S to G, or None if unreachable.
    """
    start = next(p for p, ch in cells.items() if ch == "S")
    goal = next(p for p, ch in cells.items() if ch == "G")

    frontier = [(0, start)]
    best_cost = {start: 0}
    parent = {start: None}
    expanded = 0

    while frontier:
        g, cur = heapq.heappop(frontier)

        if g > best_cost[cur]:
            continue

        expanded += 1

        if cur == goal:
            path = []
            while cur:
                path.append(cur)
                cur = parent[cur]
            return path[::-1], g, expanded

        r, c = cur
        for nb in [(r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)]:
            if nb in cells and cells[nb] in COST:
                ng = g + COST[cells[nb]]

                if ng < best_cost.get(nb, float("inf")):
                    best_cost[nb] = ng
                    parent[nb] = cur
                    heapq.heappush(frontier, (ng, nb))

    return None, None, expanded


def bfs(cells):
    
    start = next(p for p, ch in cells.items() if ch == "S")
    goal = next(p for p, ch in cells.items() if ch == "G")

    frontier = deque([start])
    visited = {start}
    parent = {start: None}
    expanded = 0

    while frontier:
        cur = frontier.popleft()
        expanded += 1

        if cur == goal:
            path = []
            while cur:
                path.append(cur)
                cur = parent[cur]
            # Calculate total path cost based on actual terrain costs for fair comparison, 
            # or use (len(path) - 1) if treating all steps as cost 1.
            final_path = path[::-1]
            path_cost = sum(COST[cells[node]] for node in final_path[1:])
            return final_path, path_cost, expanded

        r, c = cur
        for nb in [(r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)]:
            if nb in cells and cells[nb] in COST and nb not in visited:
                visited.add(nb)
                parent[nb] = cur
                frontier.append(nb)

    return None, None, expanded


# ---------------------------------------------------------------------------
# Maps (given in the assignment)
# S = start, G = goal, . = cost 1, ~ = cost 3, # = wall
# ---------------------------------------------------------------------------
MAP_A = ["S..#....", "##.#.##.", "....~~..", ".####.#.", "...~..#G"]
MAP_B = ["S~~~~~~~G", ".#######.", ".........", ".#.#.#.#.", "........."]
MAP_C = ["S..#....", ".#.#.##.", "...#..#.", ".###.##.", "....#..G"]

MAPS = {"A": MAP_A, "B": MAP_B, "C": MAP_C}
MAPS["tiny"] = ["S.G"]
MAPS["big"] = ["S" + "." * 40 + "~" * 5, "#" * 40 + "..", "G" + "." * 41 + "#"]

# Set to None to run all maps, or specify a map name like "A"
SELECTED =  "B"


def load_map(path):
    with open(path) as f:
        return [line.rstrip("\n") for line in f if line.strip()]


def check(grid):
    text = "".join(grid)
    assert text.count("S") == 1 and text.count("G") == 1, "need exactly one S and one G"
    assert set(text) <= set("SG.~#"), "unknown symbol in map"


def run_all():
    """Run both UCS and BFS on the selected map(s) and print comparison results."""
    for name, grid in MAPS.items():
        if SELECTED and name != SELECTED:
            continue
        check(grid)
        cells = build_cells(grid)
        
        # Run UCS
        ucs_path, ucs_cost, ucs_expanded = ucs(cells)
        # Run BFS
        bfs_path, bfs_cost, bfs_expanded = bfs(cells)
        
        print(f"--- MAP {name} ---")
        if ucs_path is None:
            print("UCS: No path found")
        else:
            print(f"UCS -> cost={ucs_cost}, length={len(ucs_path) - 1}, expanded={ucs_expanded}")
            
        if bfs_path is None:
            print("BFS: No path found")
        else:
            print(f"BFS -> cost={bfs_cost}, length={len(bfs_path) - 1}, expanded={bfs_expanded}")
        print()


run_all()