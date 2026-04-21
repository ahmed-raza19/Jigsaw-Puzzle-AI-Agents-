"""
Jigsaw Puzzle AI Agent -- Assignment 1, Q1
==========================================
Usage:  python jigsaw.py <grid_size> <max_moves>
Example: python jigsaw.py 5 100

This file reuses the abstract classes from agents.py:
  - Thing   -> subclassed as JigsawPiece  (a single puzzle tile)
  - Agent   -> subclassed as our two agent types
  - Environment -> subclassed as JigsawEnvironment (the puzzle board)

Two agents are compared on the SAME randomized puzzle:
  1) Reflex Agent          -- no memory, reacts only to current percept
  2) Model-Based Agent     -- maintains an internal map of the full grid
"""

import sys
import copy
import random

# ------------------------------------------------------------------------------
# Import base classes from the provided agents.py (AIMA textbook code)
# ------------------------------------------------------------------------------
from agents import Thing, Agent, Environment


# ==============================================================================
#  PUZZLE PIECE  (subclass of Thing from agents.py)
# ==============================================================================

class JigsawPiece(Thing):
    """
    Represents one puzzle tile.
      - piece_id : int   -- the unique ID (0 .. n*n-1)
      - rotation : int   -- 0, 1, 2, or 3  (number of 90 deg CW turns from correct)

    A piece with id=k belongs at row k//n, col k%n with rotation 0.
    """

    def __init__(self, piece_id, rotation=0):
        self.piece_id = piece_id
        self.rotation = rotation          # 0 = correct, 1 = 90 CW, etc.

    def rotate_right(self):
        self.rotation = (self.rotation + 1) % 4

    def __repr__(self):
        return "({},r{})".format(self.piece_id, self.rotation)


# ==============================================================================
#  JIGSAW ENVIRONMENT  (subclass of Environment from agents.py)
# ==============================================================================

class JigsawEnvironment(Environment):
    """
    An n x n jigsaw puzzle environment.

    Key design decisions:
    ---------------------
    - Pieces are placed at their CORRECT positions (piece k at row k//n, col k%n).
    - Only ROTATIONS are randomised (0, 1, 2, or 3).
    - The agent moves freely across the grid (no swapping of pieces).
    - At each cell, the agent can rotate the piece at that cell.
    - A piece is CORRECT when its rotation is 0.

    Movement model:
    ---------------
    The agent moves to an adjacent cell (Up/Down/Left/Right).
    This does NOT move or swap any pieces -- the agent simply walks
    over the grid and can rotate the piece at its current cell.

    Key attributes
    --------------
    n          : grid size (n rows x n columns)
    max_moves  : maximum number of moves allowed per agent
    grid       : 2-D list of JigsawPiece objects  (grid[row][col])
    agent_pos  : dict  {agent: (row, col)}
    steps_used : dict  {agent: int}
    terminated : dict  {agent: bool}
    """

    def __init__(self, n, max_moves):
        super().__init__()                # initialises self.things, self.agents
        self.n = n
        self.max_moves = max_moves

        # -- Build the grid: pieces at correct positions --
        self.grid = [
            [JigsawPiece(r * n + c, 0) for c in range(n)]
            for r in range(n)
        ]

        # -- Randomise rotations only --
        for r in range(n):
            for c in range(n):
                self.grid[r][c].rotation = random.randint(0, 3)

        # -- Per-agent bookkeeping --
        self.agent_pos = {}
        self.steps_used = {}
        self.terminated = {}

    def add_thing(self, thing, location=None):
        """Override: when an Agent is added, assign random start and init counters."""
        super().add_thing(thing, location)
        if isinstance(thing, Agent):
            start = (random.randint(0, self.n - 1),
                     random.randint(0, self.n - 1))
            self.agent_pos[thing] = start
            self.steps_used[thing] = 0
            self.terminated[thing] = False

    def percept(self, agent):
        """
        Returns what the agent can see at its current cell.

        From the problem statement:
          - Agent knows grid size and cell content
          - Environment tells the agent its coordinates and if piece is correct
        """
        r, c = self.agent_pos[agent]
        piece = self.grid[r][c]
        is_correct = (piece.rotation == 0)
        return {
            "cell": (r, c),
            "piece_id": piece.piece_id,
            "rotation": piece.rotation,
            "is_correct": is_correct,
            "grid_size": self.n
        }

    def execute_action(self, agent, action):
        """
        Carry out one of the actions.
        Movement repositions the agent (no piece swapping).
        Rotation changes the current piece's orientation.
        Every action (including NoOp and invalid moves) costs one step.
        """
        if self.terminated.get(agent, True):
            return

        r, c = self.agent_pos[agent]
        n = self.n

        if action == 'Left' and c > 0:
            self.agent_pos[agent] = (r, c - 1)
        elif action == 'Right' and c < n - 1:
            self.agent_pos[agent] = (r, c + 1)
        elif action == 'Up' and r > 0:
            self.agent_pos[agent] = (r - 1, c)
        elif action == 'Down' and r < n - 1:
            self.agent_pos[agent] = (r + 1, c)
        elif action == 'Rotate_right':
            self.grid[r][c].rotate_right()
        elif action == 'Rotate_left':
            self.grid[r][c].rotation = (self.grid[r][c].rotation - 1) % 4
        # NoOp or out-of-bounds moves: do nothing but still count

        self.steps_used[agent] += 1

        if self.steps_used[agent] >= self.max_moves or self.is_puzzle_solved():
            self.terminated[agent] = True

    def is_done(self):
        """Stop when all agents have terminated."""
        if not self.agents:
            return True
        return all(self.terminated.get(ag, True) for ag in self.agents)

    def step(self):
        """Run one percept-action cycle for each active agent."""
        if self.is_done():
            return
        for agent in self.agents:
            if not self.terminated.get(agent, True) and agent.alive:
                p = self.percept(agent)
                action = agent.program(p)
                self.execute_action(agent, action)

    def is_puzzle_solved(self):
        """True if every piece has rotation 0 (pieces are already at correct positions)."""
        n = self.n
        for r in range(n):
            for c in range(n):
                if self.grid[r][c].rotation != 0:
                    return False
        return True

    def count_correct(self):
        """Count pieces with correct rotation (= 0)."""
        n = self.n
        count = 0
        for r in range(n):
            for c in range(n):
                if self.grid[r][c].rotation == 0:
                    count += 1
        return count

    def print_grid(self, label="Puzzle State"):
        """Print the puzzle grid as rotation arrays (matching required format)."""
        n = self.n
        print("")
        print("=" * 60)
        print("  {}  (grid {}x{})".format(label, n, n))
        print("=" * 60)
        show = min(n, 10)
        for r in range(show):
            row_vals = [self.grid[r][c].rotation for c in range(show)]
            if n > show:
                print(str(row_vals) + "  ...")
            else:
                print(row_vals)
        if n > show:
            print("  ... (remaining rows hidden for large grids)")
        print("  Correctly placed: {} / {}".format(self.count_correct(), n * n))


# ==============================================================================
#  REFLEX AGENT  (subclass of Agent from agents.py)
# ==============================================================================
#
#  How it works (simple condition-action rules, like ReflexVacuumAgent):
#
#  The reflex agent has NO MEMORY.  Each step it looks at the current percept
#  and applies these rules in order:
#
#  Rule 1:  If the piece has wrong rotation -> Rotate_right
#           (applying Rotate_right repeatedly will eventually fix any rotation)
#
#  Rule 2:  If the piece is already correct -> move randomly to find work
#           (hope to land on a misplaced piece)
#
#  Weakness: the reflex agent doesn't know which cells still need fixing.
#  It wastes moves revisiting already-fixed cells and moving randomly.
#  Without memory it can't plan an efficient path.
# ==============================================================================

def reflex_program(percept):
    """Simple reflex program -- no state, just condition-action rules."""
    cell = percept["cell"]
    rotation = percept["rotation"]
    is_correct = percept["is_correct"]
    n = percept["grid_size"]

    cur_r, cur_c = cell

    # Rule 1: fix rotation first (rotation must be 0 for piece to be correct)
    if rotation != 0:
        return 'Rotate_right'

    # Rule 2: piece is correct -> move randomly to find work
    directions = []
    if cur_r > 0:     directions.append('Up')
    if cur_r < n - 1: directions.append('Down')
    if cur_c > 0:     directions.append('Left')
    if cur_c < n - 1: directions.append('Right')
    return random.choice(directions) if directions else 'NoOp'


class ReflexJigsawAgent(Agent):
    """Simple reflex agent -- inherits Agent, uses reflex_program."""

    def __init__(self):
        super().__init__(program=reflex_program)


# ==============================================================================
#  MODEL-BASED REFLEX AGENT  (subclass of Agent from agents.py)
# ==============================================================================
#
#  How it works (like ModelBasedVacuumAgent, but with a full grid model):
#
#  The model-based agent maintains an INTERNAL MAP of the entire puzzle.
#  Every time it visits a cell it records the rotation state.
#  This converts the partially observable environment into effectively
#  fully observable -- the agent knows which cells still need fixing.
#
#  Strategy (systematic traversal with solved-cell protection):
#
#  STEP 1 - INTERNAL STATE: maintain model[r][c] = rotation or None (unknown).
#           Update on every percept received.
#
#  STEP 2 - ORIENTATION FIX: if current piece has wrong rotation, rotate it.
#           Mark the cell as SOLVED (rotation = 0) in the model.
#
#  STEP 3 - FIND NEXT TARGET: scan the model for the nearest cell that is
#           either unknown (not yet visited) or known to have wrong rotation.
#           Use Manhattan distance to find the closest one.
#
#  STEP 4 - NAVIGATE: move toward the target cell using Manhattan reduction.
#           The agent walks directly to the target without wasting moves.
#
#  STEP 5 - EARLY TERMINATION: if the model shows ALL cells are solved
#           (rotation = 0), the agent does NoOp (puzzle is complete).
#
#  Why this is better than the reflex agent:
#  - The model agent REMEMBERS which cells are already fixed -> never revisits
#  - It navigates DIRECTLY to the nearest unfixed cell -> no random wandering
#  - It knows when ALL cells are fixed -> can stop early
#  - The reflex agent wastes moves revisiting fixed cells and moving randomly
# ==============================================================================

class ModelBasedProgram:
    """
    Callable class used as the agent program for the model-based agent.
    Maintains internal state (the 'model') across calls.

    Internal state:
      model[r][c] = rotation value (0-3) or None (unknown/unvisited cell)
      position    = (r, c)  -- agent's current position
      target      = (r, c) or None  -- next cell to navigate to

    Strategy:
      1. Fix rotation at current cell (rotate until 0).
      2. After fixing, update model to mark cell as solved.
      3. Find nearest unsolved cell (unknown or rotation != 0).
      4. Navigate directly to that cell.
      5. If all cells are solved, NoOp.
    """

    def __init__(self):
        self.n = None
        self.model = None       # model[r][c] = rotation (int) or None
        self.position = None    # agent's current position
        self.target = None      # (r, c) to navigate toward

    def __call__(self, percept):
        """Called by the Environment each step -- this IS the agent program."""
        cell = percept["cell"]
        piece_id = percept["piece_id"]
        rotation = percept["rotation"]
        is_correct = percept["is_correct"]
        n = percept["grid_size"]
        r, c = cell

        # -- One-time initialisation --
        if self.model is None:
            self.n = n
            self.model = [[None] * n for _ in range(n)]

        # -- Update internal model with current percept --
        self.position = (r, c)
        self.model[r][c] = rotation

        # -- STEP 1: Fix rotation at current cell --
        if rotation != 0:
            # After rotating, update model to reflect new rotation
            new_rot = (rotation + 1) % 4
            self.model[r][c] = new_rot
            return 'Rotate_right'

        # -- Current cell is now correct (rotation = 0) --
        # Mark it as solved in model
        self.model[r][c] = 0

        # -- STEP 2: Check if all cells are solved --
        if self._all_solved():
            return 'NoOp'   # Puzzle complete! Early termination.

        # -- STEP 3: Find and navigate to next target --
        # Invalidate target if we've arrived at it
        if self.target is not None and self.target == (r, c):
            self.target = None

        # Find new target if needed
        if self.target is None:
            self.target = self._find_nearest_unsolved(r, c)

        # Navigate toward target
        if self.target is not None:
            tr, tc = self.target
            return self._move_toward(r, c, tr, tc)

        # Fallback (shouldn't happen if _all_solved is correct)
        return 'NoOp'

    def _all_solved(self):
        """Check if all cells in the model are known and have rotation 0."""
        n = self.n
        for r in range(n):
            for c in range(n):
                if self.model[r][c] is None or self.model[r][c] != 0:
                    return False
        return True

    def _find_nearest_unsolved(self, r, c):
        """
        Find the nearest cell that needs fixing.
        Priority:
          1. Known cells with rotation != 0 (we know they need fixing)
          2. Unknown cells (we haven't visited them yet)
        Returns (row, col) of the nearest unsolved cell, or None.
        Uses Manhattan distance for nearest.
        """
        n = self.n
        best_dist = float('inf')
        best_cell = None

        # First pass: look for known cells with wrong rotation
        for mr in range(n):
            for mc in range(n):
                val = self.model[mr][mc]
                if val is not None and val != 0:
                    dist = abs(r - mr) + abs(c - mc)
                    if dist < best_dist:
                        best_dist = dist
                        best_cell = (mr, mc)

        # If found a known-wrong cell, go there
        if best_cell is not None:
            return best_cell

        # Second pass: look for unknown cells
        best_dist = float('inf')
        for mr in range(n):
            for mc in range(n):
                if self.model[mr][mc] is None:
                    dist = abs(r - mr) + abs(c - mc)
                    if dist < best_dist:
                        best_dist = dist
                        best_cell = (mr, mc)

        return best_cell

    def _move_toward(self, r, c, tr, tc):
        """Move one step toward target (tr, tc)."""
        if r > tr:
            return 'Up'
        elif r < tr:
            return 'Down'
        elif c > tc:
            return 'Left'
        elif c < tc:
            return 'Right'
        return 'NoOp'


class ModelBasedJigsawAgent(Agent):
    """Model-based agent -- inherits Agent, uses ModelBasedProgram (with state)."""

    def __init__(self):
        super().__init__(program=ModelBasedProgram())


# ==============================================================================
#  RUNNER: run a single agent on its own COPY of the environment
# ==============================================================================

def run_agent_on_puzzle(agent, env_template, start_pos):
    """
    Deep-copies the environment template, adds the agent at start_pos,
    and runs the simulation until termination.
    Returns (env, steps_used, correct_count).
    """
    env = copy.deepcopy(env_template)
    env.add_thing(agent)
    # Override random start with the fixed one (for fair comparison)
    env.agent_pos[agent] = start_pos
    # Run until done
    env.run(steps=env.max_moves)
    steps = env.steps_used[agent]
    correct = env.count_correct()
    return env, steps, correct


# ==============================================================================
#  MAIN -- CLI entry point
# ==============================================================================

def main():
    if len(sys.argv) != 3:
        print("Usage: python jigsaw.py <grid_size> <max_moves>")
        print("Example: python jigsaw.py 5 70")
        sys.exit(1)

    n = int(sys.argv[1])
    max_moves = int(sys.argv[2])

    # Create ONE randomized environment (template for both agents)
    env_template = JigsawEnvironment(n, max_moves)

    # Pick ONE random start position (same for both agents)
    start_pos = (random.randint(0, n - 1), random.randint(0, n - 1))

    # Print starting state
    env_template.print_grid("Starting Puzzle State")

    # ---- Run Reflex Agent ----
    reflex_agent = ReflexJigsawAgent()
    env_r, steps_r, correct_r = run_agent_on_puzzle(
        reflex_agent, env_template, start_pos)

    env_r.print_grid("Final Puzzle State")

    # ---- Run Model-Based Agent ----
    model_agent = ModelBasedJigsawAgent()
    env_m, steps_m, correct_m = run_agent_on_puzzle(
        model_agent, env_template, start_pos)

    env_m.print_grid("Final Puzzle State")

    # ---- Required output ----
    print("Reflex Agent: No of correct pieces = {}, "
          "no of moves utilized = {}".format(correct_r, steps_r))
    print("Model-based Agent: No of correct pieces = {}, "
          "no of moves utilized = {}".format(correct_m, steps_m))


if __name__ == "__main__":
    main()
