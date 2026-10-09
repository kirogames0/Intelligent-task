"""
Warehouse Delivery Robot - Uniform Cost Search (UCS)

General idea:
  The map is turned into a dictionary {(row, col): symbol}. UCS then explores
  the map starting from S, always expanding the cell with the LOWEST total
  cost so far, until it pulls G out of the queue. Because it always expands
  the cheapest cell first, the first time it reaches G is the cheapest path.

How to run:   python warehouse_ucs_commented.py
How to change the map: edit SELECTED below (e.g. "A", "B", "C", "tiny", "big"),
  or set SELECTED = None to run every map in MAPS.
"""

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
    # Find S and G by scanning the dictionary (no hard-coded positions).
    start = next(p for p, ch in cells.items() if ch == "S")
    goal = next(p for p, ch in cells.items() if ch == "G")

    # The frontier is the priority queue of cells waiting to be expanded.
    # Each entry is (cost so far, cell); heapq orders by the first item,
    # so the cheapest cell always comes out first. This is what makes it UCS
    # (BFS would use a plain queue and ignore costs).
    frontier = [(0, start)]

    # Cheapest cost found so far to reach each cell (S costs 0 to "reach").
    best_cost = {start: 0}

    # parent[cell] = the cell we came from on the cheapest known route.
    # Used at the end to walk backwards from G to S and rebuild the path.
    parent = {start: None}

    expanded = 0  # counter for "nodes expanded" in the results table

    while frontier:  # keep going until there is nothing left to explore
        # Take the cheapest cell from the queue.
        g, cur = heapq.heappop(frontier)

        # The same cell can be pushed several times if we later find a
        # cheaper route to it. If this entry is more expensive than the best
        # known cost, it is outdated, so skip it.
        if g > best_cost[cur]:
            continue

        expanded += 1  # this cell is really being expanded now

        # Goal test: done when G is popped (not when first seen), because
        # only at pop time is its cost guaranteed to be the cheapest.
        if cur == goal:
            path = []
            while cur:                # walk back through parents until S
                path.append(cur)      # (S's parent is None, which stops the loop)
                cur = parent[cur]
            return path[::-1], g, expanded  # reverse so it reads S -> G

        # Generate the four neighbours: Up, Down, Left, Right.
        r, c = cur
        for nb in [(r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)]:
            # Valid move = the cell exists on the map AND is not a wall
            # (walls are not in COST).
            if nb in cells and cells[nb] in COST:
                ng = g + COST[cells[nb]]  # cost so far + cost of entering nb

                # Only record it if it is the first time we see nb, or we
                # found a cheaper way to reach it than before.
                if ng < best_cost.get(nb, float("inf")):
                    best_cost[nb] = ng           # remember the cheaper cost
                    parent[nb] = cur             # remember how we got here
                    heapq.heappush(frontier, (ng, nb))  # queue it for expansion

    # Frontier is empty and G was never reached: no solution exists.
    return None, None, expanded


# ---------------------------------------------------------------------------
# Maps (given in the assignment)
# S = start, G = goal, . = cost 1, ~ = cost 3, # = wall
# ---------------------------------------------------------------------------
MAP_A = ["S..#....", "##.#.##.", "....~~..", ".####.#.", "...~..#G"]
MAP_B = ["S~~~~~%^~~G", ".#######.", ".........", ".#.#.#.#.", "........."]
MAP_C = ["S..#....", ".#.#.##.", "...#..#.", ".###.##.", "....#..G"]

# All maps live in one dictionary, so adding a new map is a single line.
MAPS = {"A": MAP_A, "B": MAP_B, "C": MAP_C}

# Custom maps of any size/shape:
MAPS["tiny"] = ["S.G"]
MAPS["big"] = ["S" + "." * 40 + "~" * 5, "#" * 40 + "..", "G" + "." * 41 + "#"]

# Which map to run. Use None to run all maps (useful for the results table).
SELECTED = "B"


def load_map(path):
    """Optional helper: read a map from a text file, one row per line,
    so teammates can test new maps without editing the code."""
    with open(path) as f:
        return [line.rstrip("\n") for line in f if line.strip()]


def check(grid):
    """Validate a map before searching so mistakes fail loudly and early."""
    text = "".join(grid)  # flatten all rows into one string to count symbols
    assert text.count("S") == 1 and text.count("G") == 1, "need exactly one S and one G"
    assert set(text) <= set("SG.~#"), "unknown symbol in map"


def run_all():
    """Run UCS on the selected map (or on every map if SELECTED is None)."""
    for name, grid in MAPS.items():
        if SELECTED and name != SELECTED:  # skip maps we did not select
            continue
        check(grid)
        # IMPORTANT: build the cells from the CURRENT grid in the loop.
        path, cost, expanded = ucs(build_cells(grid))
        print(f"MAP {name}: ", end="")
        if path is None:
            print("No path found")
        else:
            # length = number of moves = number of cells in path minus S
            print(f"cost={cost}, length={len(path) - 1}, expanded={expanded}")


run_all()