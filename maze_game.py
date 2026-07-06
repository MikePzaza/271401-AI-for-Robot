"""
maze_game.py
------------
เกมเขาวงกตสำหรับ "หนู" (ผู้เล่น) ขนาด 16cm เดินในเขาวงกต 30x30 ช่อง (ช่องละ 16cm)
ที่จุดออกมีชีสรออยู่ ต้องเดินอย่างน้อย 5 ครั้งที่ต้องเลี้ยว (คิดเส้นทาง) จึงจะไปถึง
ควบคุมด้วย W (ขึ้น) A (ซ้าย) S (ลง) D (ขวา) — เดินได้ทีละ 1 ช่องต่อการกดปุ่ม 1 ครั้ง
แผนที่เขาวงกตทั้งหมดจะแสดงให้ผู้เล่นเห็นตลอดเวลา (ไม่มีการบังส่วนใดของแผนที่)

วิธีติดตั้ง:
    pip install pygame

วิธีรัน:
    python maze_game.py
"""

import sys
import pygame
from maze_core import Maze, DIRS

# ---------------- ตั้งค่าตามโจทย์ ----------------
ROWS, COLS = 30, 30          # ขนาดเขาวงกต 30x30 ช่อง
CELL_SIZE = 16                # แต่ละช่อง 16 หน่วย (ตรงกับขนาดจริง 16cm ต่อช่อง)
MOUSE_SIZE_RATIO = 0.7        # ขนาดตัวหนู เทียบเป็นสัดส่วนของช่อง
MIN_TURNS = 5                 # ต้องเลี้ยวอย่างน้อย 5 ครั้งจากจุดเข้าไปจุดออก
WALL_THICKNESS = 2
SEED = None                   # ใส่เลข เช่น 42 ถ้าต้องการเขาวงกตแบบเดิมทุกครั้ง

MARGIN = 20   # ขอบจอ (พิกเซล)
STATUS_BAR_H = 40  # พื้นที่แถบข้อความด้านล่าง

# หน้าต่างเกมจะถูกปรับขนาดอัตโนมัติให้พอดีกับจอ ไม่เกินสัดส่วนนี้ของความสูง/กว้างหน้าจอ
SCREEN_FIT_RATIO = 0.85
# ถ้าอยากบังคับขนาดช่องเอง (พิกเซลต่อช่อง) ให้ใส่ตัวเลขแทน None เช่น CELL_PX_OVERRIDE = 12
CELL_PX_OVERRIDE = None

# สี
COLOR_BG = (250, 248, 240)
COLOR_WALL = (40, 40, 40)
COLOR_MOUSE = (150, 120, 110)
COLOR_MOUSE_EAR = (200, 160, 150)
COLOR_START = (60, 170, 90)
COLOR_CHEESE = (245, 197, 66)
COLOR_CHEESE_HOLE = (250, 230, 160)
COLOR_TEXT = (30, 30, 30)


def build_maze():
    maze = Maze(rows=ROWS, cols=COLS, seed=SEED)
    maze.generate(min_turns=MIN_TURNS)
    return maze


def main():
    pygame.init()
    pygame.display.set_caption("เขาวงกตหนูน้อย 30x30 (ต้องเลี้ยว >= 5 ครั้ง)")

    # --- คำนวณขนาดช่อง (พิกเซล) ให้พอดีกับหน้าจอผู้ใช้อัตโนมัติ ---
    if CELL_PX_OVERRIDE:
        cell_px = CELL_PX_OVERRIDE
    else:
        info = pygame.display.Info()
        max_w = int(info.current_w * SCREEN_FIT_RATIO)
        max_h = int(info.current_h * SCREEN_FIT_RATIO)
        avail_w = max_w - MARGIN * 2
        avail_h = max_h - MARGIN * 2 - STATUS_BAR_H
        cell_px = max(6, min(avail_w // COLS, avail_h // ROWS))

    win_w = COLS * cell_px + MARGIN * 2
    win_h = ROWS * cell_px + MARGIN * 2 + STATUS_BAR_H
    screen = pygame.display.set_mode((win_w, win_h))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("tahoma", 18)

    maze = build_maze()
    player = maze.start
    steps = 0
    won = False

    key_to_dir = {
        pygame.K_w: "N",
        pygame.K_s: "S",
        pygame.K_a: "W",
        pygame.K_d: "E",
    }

    def cell_to_px(cell):
        r, c = cell
        x = MARGIN + c * cell_px
        y = MARGIN + r * cell_px
        return x, y

    def draw_cheese(center, size):
        cx, cy = center
        r = size // 2
        # ตัวชีสเป็นรูปสามเหลี่ยม (ลิ่ม) สีเหลือง
        points = [
            (cx, cy - r),
            (cx + r, cy + r * 0.7),
            (cx - r, cy + r * 0.7),
        ]
        pygame.draw.polygon(screen, COLOR_CHEESE, points)
        pygame.draw.polygon(screen, (200, 150, 40), points, 2)
        # รูชีส
        for dx, dy, hr in [(-0.15, 0.15, 0.16), (0.2, 0.35, 0.12), (0.0, -0.05, 0.1)]:
            pygame.draw.circle(
                screen, COLOR_CHEESE_HOLE,
                (int(cx + dx * size), int(cy + dy * size)),
                max(2, int(hr * size)),
            )

    def draw_mouse(center, size):
        cx, cy = center
        r = size // 2
        # หู 2 ข้าง
        pygame.draw.circle(screen, COLOR_MOUSE_EAR, (cx - r, cy - r), max(2, r // 2))
        pygame.draw.circle(screen, COLOR_MOUSE_EAR, (cx + r, cy - r), max(2, r // 2))
        # ตัว
        pygame.draw.circle(screen, COLOR_MOUSE, (cx, cy), r)
        # ตา
        eye_r = max(1, r // 6)
        pygame.draw.circle(screen, (20, 20, 20), (cx - r // 3, cy - r // 6), eye_r)
        pygame.draw.circle(screen, (20, 20, 20), (cx + r // 3, cy - r // 6), eye_r)

    def draw():
        screen.fill(COLOR_BG)

        # วาดกำแพงทีละช่อง
        for r in range(ROWS):
            for c in range(COLS):
                x, y = cell_to_px((r, c))
                walls = maze.grid[r][c]
                if walls["N"]:
                    pygame.draw.line(screen, COLOR_WALL, (x, y), (x + cell_px, y), WALL_THICKNESS)
                if walls["S"]:
                    pygame.draw.line(screen, COLOR_WALL, (x, y + cell_px), (x + cell_px, y + cell_px), WALL_THICKNESS)
                if walls["W"]:
                    pygame.draw.line(screen, COLOR_WALL, (x, y), (x, y + cell_px), WALL_THICKNESS)
                if walls["E"]:
                    pygame.draw.line(screen, COLOR_WALL, (x + cell_px, y), (x + cell_px, y + cell_px), WALL_THICKNESS)

        # จุดเข้า (พื้นสีเขียวอ่อน)
        sx, sy = cell_to_px(maze.start)
        pygame.draw.rect(screen, COLOR_START, (sx + 3, sy + 3, cell_px - 6, cell_px - 6))

        # จุดออก: มีชีสวางอยู่
        ex, ey = cell_to_px(maze.end)
        draw_cheese((ex + cell_px // 2, ey + cell_px // 2), int(cell_px * 0.8))

        # ตัวหนู (ผู้เล่น)
        px, py = cell_to_px(player)
        mouse_px = int(cell_px * MOUSE_SIZE_RATIO)
        draw_mouse((px + cell_px // 2, py + cell_px // 2), mouse_px)

        # ข้อความสถานะ
        status = f"ก้าวเดิน: {steps}   จุดเข้า: {maze.start}   จุดออก(ชีส): {maze.end}"
        if won:
            status = "หนูกินชีสสำเร็จ! ออกจากเขาวงกตได้แล้ว  (กด R เพื่อสร้างเขาวงกตใหม่)"
        text_surf = font.render(status, True, COLOR_TEXT)
        screen.blit(text_surf, (MARGIN, win_h - 30))

        pygame.display.flip()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    maze = build_maze()
                    player = maze.start
                    steps = 0
                    won = False
                elif not won and event.key in key_to_dir:
                    direction = key_to_dir[event.key]
                    if maze.can_move(player, direction):
                        player = maze.move(player, direction)
                        steps += 1
                        if player == maze.end:
                            won = True

        draw()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
