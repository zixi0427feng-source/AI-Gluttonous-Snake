import pygame
import random
import sys
from collections import deque

# --- 1. 初始化与配置 ---
pygame.init()
WHITE, GREEN, RED, BLACK, WALL_COLOR = (255, 255, 255), (0, 255, 0), (213, 50, 80), (30, 30, 30), (100, 100, 100)
BLOCK_SIZE = 20
WIDTH, HEIGHT = 600, 400
grid_width, grid_height = WIDTH // BLOCK_SIZE, HEIGHT // BLOCK_SIZE

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('高级AI贪吃蛇：虚拟演算版 (按 A 开关 AI)')
clock = pygame.time.Clock()
font_style = pygame.font.SysFont("simhei", 20)


# --- 2. 核心寻路算法  ---
def get_path(start, target, snake_list):
    """基础 BFS：寻找从 start 到 target 的最短路径坐标"""
    queue = deque([start])
    parent = {start: None}
    obstacles = set(tuple(s) for s in snake_list)

    while queue:
        current = queue.popleft()
        if current == target:
            path = []
            while current in parent and parent[current] is not None:
                path.append(current)
                current = parent[current]
            return path[::-1]  # 返回下一步到终点的坐标序列

        for dx, dy in [(BLOCK_SIZE, 0), (-BLOCK_SIZE, 0), (0, BLOCK_SIZE), (0, -BLOCK_SIZE)]:
            nxt = (current[0] + dx, current[1] + dy)
            if BLOCK_SIZE <= nxt[0] < WIDTH - BLOCK_SIZE and BLOCK_SIZE <= nxt[1] < HEIGHT - BLOCK_SIZE:
                if nxt not in obstacles and nxt not in parent:
                    parent[nxt] = current
                    queue.append(nxt)
    return None


# --- 3. 高级 AI 决策 ---
def ai_decision(head, food, snake_list):
    head_tuple = tuple(head)

    # 1. 尝试寻找通往食物的安全路径
    path_to_food = get_path(head_tuple, tuple(food), snake_list)
    if path_to_food:
        virtual_snake = snake_list + [list(food)]
        # 只要虚拟状态下还能找到尾巴，就果断去吃
        if get_path(tuple(food), tuple(virtual_snake[0]), virtual_snake):
            return path_to_food[0][0] - head[0], path_to_food[0][1] - head[1]

    # 2. 如果吃果子不安全，追逐尾巴
    path_to_tail = get_path(head_tuple, tuple(snake_list[0]), snake_list)
    if path_to_tail:
        # 基础追尾逻辑（如果你想更高级，可以在这里写一个 Longest Path 算法）
        return path_to_tail[0][0] - head[0], path_to_tail[0][1] - head[1]

    # 3. 兜底逻辑：如果连尾巴都看不见了，找一个离食物最近的可走空格
    best_move = (0, 0)
    min_dist = float('inf')
    for dx, dy in [(BLOCK_SIZE, 0), (-BLOCK_SIZE, 0), (0, BLOCK_SIZE), (0, -BLOCK_SIZE)]:
        tx, ty = head[0] + dx, head[1] + dy
        if BLOCK_SIZE <= tx < WIDTH - BLOCK_SIZE and BLOCK_SIZE <= ty < HEIGHT - BLOCK_SIZE:
            if [tx, ty] not in snake_list:
                # 计算到食物的曼哈顿距离
                dist = abs(tx - food[0]) + abs(ty - food[1])
                if dist < min_dist:
                    min_dist = dist
                    best_move = (dx, dy)
    return best_move

# --- 4. 辅助函数 ---
def draw_walls():
    pygame.draw.rect(screen, WALL_COLOR, [0, 0, WIDTH, HEIGHT], BLOCK_SIZE)


def draw_snake_with_eyes(snake_list, dx, dy):
    for i, block in enumerate(snake_list):
        is_head = (i == len(snake_list) - 1)
        pygame.draw.rect(screen, GREEN if is_head else (0, 180, 0),
                         [block[0], block[1], BLOCK_SIZE - 1, BLOCK_SIZE - 1])
        if is_head:
            # 简单的圆眼睛
            ex, ey = (block[0] + 7, block[1] + 7), (block[0] + 13, block[1] + 13)
            pygame.draw.circle(screen, BLACK, ex, 2)
            pygame.draw.circle(screen, BLACK, ey, 2)


def game_loop():
    game_over, game_close = False, False
    ai_mode = True  # 默认开启 AI 看看效果
    x, y = (grid_width // 2) * BLOCK_SIZE, (grid_height // 2) * BLOCK_SIZE
    dx, dy = BLOCK_SIZE, 0
    snake_list, snake_length = [[x, y]], 1

    # 初始食物
    foodx, foody = (grid_width // 2 + 5) * BLOCK_SIZE, (grid_height // 2) * BLOCK_SIZE
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
                    if event.key == pygame.K_q: pygame.quit(); sys.exit()
                    if event.key == pygame.K_c: game_loop()
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()

        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a: ai_mode = not ai_mode
                if not ai_mode:
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

        # 控制速度
        speed_limit = 30 if ai_mode else 100
        if move_time >= speed_limit:
            move_time = 0

            if ai_mode:
                dx, dy = ai_decision([x, y], [foodx, foody], snake_list)

            x += dx
            y += dy

            # 碰撞检测
            if x < BLOCK_SIZE or x >= WIDTH - BLOCK_SIZE or y < BLOCK_SIZE or y >= HEIGHT - BLOCK_SIZE or [x,
                                                                                                           y] in snake_list:
                game_close = True
            else:
                snake_head = [x, y]
                snake_list.append(snake_head)
                if len(snake_list) > snake_length: del snake_list[0]

                if x == foodx and y == foody:
                    snake_length += 1
                    # 安全刷新食物
                    empty_slots = [[tx, ty] for tx in range(BLOCK_SIZE, WIDTH - BLOCK_SIZE, BLOCK_SIZE)
                                   for ty in range(BLOCK_SIZE, HEIGHT - BLOCK_SIZE, BLOCK_SIZE)
                                   if [tx, ty] not in snake_list]
                    if empty_slots:
                        foodx, foody = random.choice(empty_slots)
                    else:
                        game_close = True  # 满屏胜利

        # 绘图（增加 display 状态检查防止报错）
        if not game_over:
            screen.fill(BLACK)
            draw_walls()
            pygame.draw.circle(screen, RED, (int(foodx + BLOCK_SIZE // 2), int(foody + BLOCK_SIZE // 2)),
                               BLOCK_SIZE // 2 - 2)
            draw_snake_with_eyes(snake_list, dx, dy)
            mode_text = font_style.render(f"模式: {'自动' if ai_mode else '手动'} (按A切换)", True, WHITE)
            screen.blit(mode_text, [WIDTH - 220, 10])
            pygame.display.update()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    game_loop()
game_loop()
