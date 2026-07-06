"""
maze_core.py
------------
สร้างเขาวงกต (maze) แบบ "Perfect Maze" ด้วยอัลกอริทึม Recursive Backtracker
- มีทางเดินเชื่อมถึงกันได้ทุกช่อง (ทางเดียวระหว่างจุดสองจุดเสมอ)
- เลือกจุดเข้า (entrance) และจุดออก (exit) บนขอบเขาวงกต โดยบังคับว่า
  เส้นทางจากจุดเข้าไปจุดออก ต้อง "เลี้ยว" (เปลี่ยนทิศทาง) อย่างน้อย 5 ครั้ง
"""

import random
from collections import deque

# ทิศทางสี่ด้าน: ชื่อด้าน -> (delta_row, delta_col, ด้านตรงข้าม)
DIRS = {
    "N": (-1, 0, "S"),
    "S": (1, 0, "N"),
    "E": (0, 1, "W"),
    "W": (0, -1, "E"),
}


class Maze:
    def __init__(self, rows=30, cols=30, seed=None):
        self.rows = rows
        self.cols = cols
        self.seed = seed
        self.grid = None
        self.start = None
        self.end = None
        self.solution_path = None

    # ---------- 1) สร้างโครงเขาวงกต ----------
    def _carve(self):
        rnd = random.Random(self.seed)
        rows, cols = self.rows, self.cols
        # ทุกช่องเริ่มต้นมีกำแพงล้อมรอบทั้ง 4 ด้าน
        grid = [
            [{"N": True, "S": True, "E": True, "W": True} for _ in range(cols)]
            for _ in range(rows)
        ]
        visited = [[False] * cols for _ in range(rows)]
        stack = [(0, 0)]
        visited[0][0] = True

        while stack:
            r, c = stack[-1]
            neighbors = []
            for d, (dr, dc, _opp) in DIRS.items():
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols and not visited[nr][nc]:
                    neighbors.append((d, nr, nc))

            if neighbors:
                d, nr, nc = rnd.choice(neighbors)
                opp = DIRS[d][2]
                grid[r][c][d] = False       # ทุบกำแพงฝั่งปัจจุบัน
                grid[nr][nc][opp] = False   # ทุบกำแพงฝั่งตรงข้ามของช่องใหม่
                visited[nr][nc] = True
                stack.append((nr, nc))
            else:
                stack.pop()

        self.grid = grid

    # ---------- 2) หาทางเดินระหว่างจุดสองจุด (BFS บนต้นไม้ = ทางเดียว) ----------
    def _path_between(self, start, end):
        parent = {start: None}
        q = deque([start])
        while q:
            cur = q.popleft()
            if cur == end:
                break
            r, c = cur
            for d, (dr, dc, _opp) in DIRS.items():
                if not self.grid[r][c][d]:  # ไม่มีกำแพงกั้น = เดินได้
                    nxt = (r + dr, c + dc)
                    if nxt not in parent:
                        parent[nxt] = cur
                        q.append(nxt)
        if end not in parent:
            return []
        path = []
        cur = end
        while cur is not None:
            path.append(cur)
            cur = parent[cur]
        path.reverse()
        return path

    @staticmethod
    def _count_turns(path):
        if len(path) < 3:
            return 0
        steps = [
            (path[i][0] - path[i - 1][0], path[i][1] - path[i - 1][1])
            for i in range(1, len(path))
        ]
        turns = 0
        for i in range(1, len(steps)):
            if steps[i] != steps[i - 1]:
                turns += 1
        return turns

    def _border_cells(self):
        rows, cols = self.rows, self.cols
        cells = []
        for r in range(rows):
            for c in range(cols):
                if r == 0 or r == rows - 1 or c == 0 or c == cols - 1:
                    cells.append((r, c))
        return cells

    def _open_outer_wall(self, cell):
        """เจาะกำแพงรอบนอกตรงจุดเข้า/จุดออก ให้ดูเหมือนประตูทางเข้า-ออกจริง"""
        r, c = cell
        if r == 0:
            self.grid[r][c]["N"] = False
        elif r == self.rows - 1:
            self.grid[r][c]["S"] = False
        elif c == 0:
            self.grid[r][c]["W"] = False
        elif c == self.cols - 1:
            self.grid[r][c]["E"] = False

    # ---------- 3) สร้างเขาวงกตทั้งหมด พร้อมบังคับเงื่อนไขจำนวนเลี้ยว ----------
    def generate(self, min_turns=5, max_attempts=400):
        rnd = random.Random(self.seed)
        for attempt in range(max_attempts):
            # สุ่ม seed ใหม่ทุกครั้งที่ลองใหม่ (ยกเว้นรอบแรกใช้ seed ที่ผู้ใช้กำหนด)
            self.seed = rnd.randint(0, 10_000_000) if attempt > 0 else self.seed
            self._carve()

            cells = self._border_cells()
            rnd.shuffle(cells)
            # ลองจับคู่ จุดเข้า-จุดออก บนขอบ จนกว่าจะได้เส้นทางที่เลี้ยว >= min_turns
            for i in range(min(len(cells), 60)):
                start = cells[i]
                for j in range(i + 1, min(len(cells), i + 60)):
                    end = cells[j]
                    path = self._path_between(start, end)
                    if len(path) >= 2 and self._count_turns(path) >= min_turns:
                        self.start, self.end = start, end
                        self.solution_path = path
                        self._open_outer_wall(start)
                        self._open_outer_wall(end)
                        return self

        raise RuntimeError("สร้างเขาวงกตตามเงื่อนไขไม่สำเร็จ ลองเพิ่ม max_attempts")

    # ---------- helper สำหรับตอนเล่นเกม ----------
    def can_move(self, cell, direction):
        r, c = cell
        return not self.grid[r][c][direction]

    def move(self, cell, direction):
        dr, dc, _ = DIRS[direction]
        return (cell[0] + dr, cell[1] + dc)


if __name__ == "__main__":
    m = Maze(rows=30, cols=30, seed=42)
    m.generate(min_turns=5)
    print("ขนาด:", m.rows, "x", m.cols)
    print("จุดเข้า (start):", m.start)
    print("จุดออก (end):", m.end)
    print("จำนวนช่องในเส้นทางแก้ปัญหา:", len(m.solution_path))
    print("จำนวนครั้งที่ต้องเลี้ยว:", Maze._count_turns(m.solution_path))
