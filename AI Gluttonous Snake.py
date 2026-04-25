import pygame
import random
from collections import deque

# --- 1. 初始化与配置 ---
pygame.init()
WHITE, GREEN, RED, BLACK, WALL_COLOR = (255, 255, 255), (0, 255, 0), (213, 50, 80), (30, 30, 30), (100, 100, 100)
BLOCK_SIZE = 20
WIDTH, HEIGHT = 600, 400
grid_width, grid_height = WIDTH // BLOCK_SIZE, HEIGHT // BLOCK_SIZE

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('贪吃蛇：AI 自动寻路版 (按 A 开关 AI)')
clock = pygame.time.Clock()
font_style = pygame.font.SysFont("simhei", 20)


# --- 2. AI 寻路算法 (BFS) ---
def get_path_bfs(start, target, snake_list):
    """返回通往目标的下一个坐标点"""
    queue = deque([start])
    parent = {start: None}
    # 将蛇身和墙壁视为障碍
    obstacles = set(tuple(s) for s in snake_list)

    while queue:
        current = queue.popleft()
        if current == target:
            # 回溯路径找到第一步
            path = current
            while parent[path] != start:
                path = parent[path]
            return path

        # 检查四个方向
        for dx, dy in [(BLOCK_SIZE, 0), (-BLOCK_SIZE, 0), (0, BLOCK_SIZE), (0, -BLOCK_SIZE)]:
            next_node = (current[0] + dx, current[1] + dy)
            # 确保在墙内且不是蛇身
            if BLOCK_SIZE <= next_node[0] < WIDTH - BLOCK_SIZE and \
                    BLOCK_SIZE <= next_node[1] < HEIGHT - BLOCK_SIZE:
                if next_node not in obstacles and next_node not in parent:
                    parent[next_node] = current
                    queue.append(next_node)
    return None  # 没找到路径


# --- 3. 辅助绘制函数 ---
def draw_walls():
    for x in range(grid_width):
        pygame.draw.rect(screen, WALL_COLOR, [x * BLOCK_SIZE, 0, BLOCK_SIZE, BLOCK_SIZE])
        pygame.draw.rect(screen, WALL_COLOR, [x * BLOCK_SIZE, (grid_height - 1) * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE])
    for y in range(1, grid_height - 1):
        pygame.draw.rect(screen, WALL_COLOR, [0, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE])
        pygame.draw.rect(screen, WALL_COLOR, [(grid_width - 1) * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE])


def draw_snake_with_eyes(snake_list, dx, dy):
    for i, block in enumerate(snake_list):
        is_head = (i == len(snake_list) - 1)
        pygame.draw.rect(screen, GREEN if is_head else (0, 200, 0),
                         [block[0], block[1], BLOCK_SIZE - 1, BLOCK_SIZE - 1])
        if is_head:
            # 简化版圆眼睛绘制
            ex, ey = (5, 6) if dx != 0 else (6, 5)
            pygame.draw.circle(screen, (0, 0, 0), (block[0] + (BLOCK_SIZE // 2) + (5 if dx >= 0 else -5),
                                                   block[1] + (BLOCK_SIZE // 2) + (5 if dy >= 0 else -5)), 3)


def game_loop():
    game_over, game_close = False, False
    ai_mode = False  # AI 开关
    x, y = (grid_width // 2) * BLOCK_SIZE, (grid_height // 2) * BLOCK_SIZE
    dx, dy = BLOCK_SIZE, 0
    snake_list, snake_length = [], 1
    foodx = round(random.randrange(BLOCK_SIZE, WIDTH - 2 * BLOCK_SIZE) / 20.0) * 20.0
    foody = round(random.randrange(BLOCK_SIZE, HEIGHT - 2 * BLOCK_SIZE) / 20.0) * 20.0
    move_time = 0

    while not game_over:
        while game_close:
            screen.fill(BLACK)
            draw_walls()
            msg = font_style.render("游戏结束！按 C 重玩，按 Q 退出", True, RED)
            screen.blit(msg, [WIDTH // 6, HEIGHT // 3])
            pygame.display.update()
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q: game_over = True; game_close = False
                    if event.key == pygame.K_c: game_loop()

        for event in pygame.event.get():
            if event.type == pygame.QUIT: game_over = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:  # 按 A 切换 AI 模式
                    ai_mode = not ai_mode
                if not ai_mode:  # 手动模式
                    if event.key == pygame.K_LEFT and dx == 0:
                        dx, dy = -BLOCK_SIZE, 0
                    elif event.key == pygame.K_RIGHT and dx == 0:
                        dx, dy = BLOCK_SIZE, 0
                    elif event.key == pygame.K_UP and dy == 0:
                        dx, dy = 0, -BLOCK_SIZE
                    elif event.key == pygame.K_DOWN and dy == 0:
                        dx, dy = 0, BLOCK_SIZE

        dt = clock.tick(60)
        move_time += dt

        # --- AI 决策逻辑 ---
        if ai_mode and move_time >= 50:  # AI 可以跑快点
            next_step = get_path_bfs((x, y), (foodx, foody), snake_list)
            if next_step:
                dx, dy = next_step[0] - x, next_step[1] - y
            else:
                # 如果没路径，尝试随便走一步不撞墙的方向（简单避障）
                for adx, ady in [(BLOCK_SIZE, 0), (-BLOCK_SIZE, 0), (0, BLOCK_SIZE), (0, -BLOCK_SIZE)]:
                    tx, ty = x + adx, y + ady
                    if BLOCK_SIZE <= tx < WIDTH - BLOCK_SIZE and BLOCK_SIZE <= ty < HEIGHT - BLOCK_SIZE and [tx,
                                                                                                             ty] not in snake_list:
                        dx, dy = adx, ady
                        break

        if move_time >= (50 if ai_mode else 100):
            move_time = 0
            x += dx
            y += dy

            if x < BLOCK_SIZE or x >= WIDTH - BLOCK_SIZE or y < BLOCK_SIZE or y >= HEIGHT - BLOCK_SIZE:
                game_close = True

            snake_head = [x, y]
            snake_list.append(snake_head)
            if len(snake_list) > snake_length: del snake_list[0]
            for segment in snake_list[:-1]:
                if segment == snake_head: game_close = True

            # 吃到食物后刷新
            if x == foodx and y == foody:
                snake_length += 1
                # 获取所有可用的空地坐标
                all_empty_slots = []
                for tx in range(BLOCK_SIZE, WIDTH - BLOCK_SIZE, BLOCK_SIZE):
                    for ty in range(BLOCK_SIZE, HEIGHT - BLOCK_SIZE, BLOCK_SIZE):
                        if [tx, ty] not in snake_list:
                            all_empty_slots.append((tx, ty))

                # 如果还有空位，随机挑一个；如果没有空位，说明你通关了！
                if all_empty_slots:
                    foodx, foody = random.choice(all_empty_slots)
                else:
                    print("恭喜！你填满了整个屏幕！")
                    game_close = True
        screen.fill(BLACK)
        draw_walls()
        pygame.draw.circle(screen, RED, (int(foodx + BLOCK_SIZE // 2), int(foody + BLOCK_SIZE // 2)),
                           BLOCK_SIZE // 2 - 2)
        draw_snake_with_eyes(snake_list, dx, dy)

        # 显示模式状态
        mode_text = font_style.render(f"模式: {'自动(AI)' if ai_mode else '手动'} (按A切换)", True, WHITE)
        screen.blit(mode_text, [WIDTH - 220, 10])
        pygame.display.update()

    pygame.quit()
    quit()


game_loop()