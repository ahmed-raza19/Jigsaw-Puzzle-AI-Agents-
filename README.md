# Jigsaw Puzzle AI Agents 🧩🤖

This project explores foundational Artificial Intelligence concepts by implementing and comparing two types of intelligent agents solving a randomized Jigsaw Puzzle grid. It is built upon the agent-environment architecture defined in the textbook *Artificial Intelligence: A Modern Approach (AIMA)*.

## The Puzzle Environment
The environment consists of an `n x n` grid where all puzzle pieces are in their correct locations, but their **rotations** are randomized (0, 90, 180, or 270 degrees). 

The goal of the agents is to navigate the grid and correct the orientation of every piece within a limited number of moves. Movement over the grid costs 1 step, and rotating a piece costs 1 step.

## The Agents

### 1. Simple Reflex Agent
The Reflex Agent acts entirely on its current percept (what it sees at its current cell) and has **no memory**. 
* **Strategy**: If a piece is incorrectly rotated, it rotates it. If the piece is correct, it moves in a completely random direction to find more work.
* **Result**: Highly inefficient. It often revisits already-solved cells and wanders aimlessly, wasting its limited move count.

### 2. Model-Based Agent
The Model-Based Agent maintains an **internal state (memory)** of the grid as it explores. 
* **Strategy**: It records the rotation of every cell it visits. After fixing a cell, it scans its internal map to find the nearest unsolved cell (using Manhattan distance) and navigates directly to it. 
* **Result**: Highly efficient. It never revisits solved cells, systematically clears the board, and features an early-termination mechanism when its internal model confirms the puzzle is completely solved.

## How to Run

Run the simulation via the command line by providing the grid size (`n`) and the maximum number of moves allowed.

```bash
# Usage: python jigsaw.py <grid_size> <max_moves>
python jigsaw.py 5 100
