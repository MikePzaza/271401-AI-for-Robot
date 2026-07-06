"""
export_maze_image.py
---------------------
สร้างเขาวงกตแล้ววาดออกมาเป็นไฟล์รูปภาพ (PNG) เช่น สำหรับพิมพ์ออกมาดู
หรือใช้ตรวจสอบเขาวงกตก่อนเอาไปทำเกม/สร้างสนามจริง

วิธีติดตั้ง:
    pip install matplotlib

วิธีรัน:
    python export_maze_image.py
    -> จะได้ไฟล์ maze_output.png ในโฟลเดอร์เดียวกัน
"""

import matplotlib
matplotlib.use("Agg")  # เผื่อรันแบบไม่มีหน้าจอ (เช่นบนเซิร์ฟเวอร์)
import matplotlib.pyplot as plt
from maze_core import Maze

ROWS, COLS = 30, 30
MIN_TURNS = 5
SEED = 42          # ใส่ None ถ้าต้องการสุ่มทุกครั้ง
OUTPUT_FILE = "maze_output.png"


def draw_maze_image(maze: Maze, output_file: str = OUTPUT_FILE):
    fig, ax = plt.subplots(figsize=(10, 10))

    for r in range(maze.rows):
        for c in range(maze.cols):
            walls = maze.grid[r][c]
            x0, y0 = c, maze.rows - r  # กลับแกน y เพื่อให้แถวบนอยู่บนสุด
            if walls["N"]:
                ax.plot([x0, x0 + 1], [y0, y0], color="black", linewidth=1.5)
            if walls["S"]:
                ax.plot([x0, x0 + 1], [y0 - 1, y0 - 1], color="black", linewidth=1.5)
            if walls["W"]:
                ax.plot([x0, x0], [y0 - 1, y0], color="black", linewidth=1.5)
            if walls["E"]:
                ax.plot([x0 + 1, x0 + 1], [y0 - 1, y0], color="black", linewidth=1.5)

    # ทำเครื่องหมายจุดเข้า (เขียว) และจุดออก (แดง)
    sr, sc = maze.start
    er, ec = maze.end
    ax.scatter([sc + 0.5], [maze.rows - sr - 0.5], color="green", s=200, label="Start (entrance)", zorder=5)
    ax.scatter([ec + 0.5], [maze.rows - er - 0.5], color="red", s=200, label="Exit", zorder=5)

    ax.set_xlim(-0.5, maze.cols + 0.5)
    ax.set_ylim(-0.5, maze.rows + 0.5)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, 1.05), ncol=2)
    turns = Maze._count_turns(maze.solution_path)
    ax.set_title(f"Maze {maze.rows}x{maze.cols} cells (16cm/cell) - solution path has {turns} turns")

    plt.tight_layout()
    plt.savefig(output_file, dpi=150)
    plt.close(fig)
    print(f"บันทึกรูปภาพเขาวงกตแล้วที่: {output_file}")


if __name__ == "__main__":
    maze = Maze(rows=ROWS, cols=COLS, seed=SEED)
    maze.generate(min_turns=MIN_TURNS)
    draw_maze_image(maze)
