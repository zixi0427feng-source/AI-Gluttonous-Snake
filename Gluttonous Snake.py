import pygame
import random

# --- 1. 初始化与配置 ---
pygame.init()

# 颜色定义
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (213, 50, 80)
BLACK = (30, 30, 30)  # 深灰色背景
EYE_COLOR = (0, 0, 0)  # 眼睛颜色
WALL_COLOR = (200, 200, 0)  # 墙壁颜色

# 尺寸配置
BLOCK_SIZE = 20
# 为了给墙留出空间，我们将实际的游戏区域稍微缩小，或者让屏幕稍微变大。
# 这里我们让屏幕保持 600x400，但游戏区域是内部的方格。
WIDTH, HEIGHT = 600, 400

# 计算内部游戏区域的格子数
grid_width = WIDTH // BLOCK_SIZE
grid_height = HEIGHT // BLOCK_SIZE

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('贪吃蛇：圆眼睛与围墙版')
clock = pygame.time.Clock()
font_style = pygame.font.SysFont("simhei", 25)


def show_score(score):
    value = font_style.render("得分: " + str(score), True, WHITE)
    screen.blit(value, [BLOCK_SIZE + 10, BLOCK_SIZE + 10])


def draw_walls():
    """在屏幕四周绘制一圈灰色方块"""
    # 绘制顶边和底边
    for x in range(0, grid_width):
        # 顶边
        pygame.draw.rect(screen, WALL_COLOR, [x * BLOCK_SIZE, 0, BLOCK_SIZE, BLOCK_SIZE])
        # 底边
        pygame.draw.rect(screen, WALL_COLOR, [x * BLOCK_SIZE, (grid_height - 1) * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE])

    # 绘制左边和右边（去掉角落，防止重复绘制）
    for y in range(1, grid_height - 1):
        # 左边
        pygame.draw.rect(screen, WALL_COLOR, [0, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE])
        # 右边
        pygame.draw.rect(screen, WALL_COLOR, [(grid_width - 1) * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE])


def draw_snake_with_eyes(snake_list, dx, dy):
    """绘制蛇身，并在蛇头上绘制圆形的眼睛"""
    for i, block in enumerate(snake_list):
        is_head = (i == len(snake_list) - 1)
        color = GREEN if is_head else (0, 200, 0)

        # 绘制蛇身节（留缝隙）
        pygame.draw.rect(screen, color, [block[0], block[1], BLOCK_SIZE - 1, BLOCK_SIZE - 1])

        # 如果是蛇头，则加上圆眼睛
        if is_head:
            head_x = block[0]
            head_y = block[1]
            eye_radius = 4  # 圆形眼睛半径
            eye_offset_side = 6  # 距离侧边的距离
            eye_offset_front = 5  # 距离前边的距离

            left_eye_pos = (0, 0)
            right_eye_pos = (0, 0)

            # 根据 dx, dy (方向) 动态调整圆心位置
            if dx > 0:  # 向右看
                left_eye_pos = (head_x + BLOCK_SIZE - eye_offset_front, head_y + eye_offset_side)
                right_eye_pos = (head_x + BLOCK_SIZE - eye_offset_front, head_y + BLOCK_SIZE - eye_offset_side)
            elif dx < 0:  # 向左看
                left_eye_pos = (head_x + eye_offset_front, head_y + eye_offset_side)
                right_eye_pos = (head_x + eye_offset_front, head_y + BLOCK_SIZE - eye_offset_side)
            elif dy < 0:  # 向上看
                left_eye_pos = (head_x + eye_offset_side, head_y + eye_offset_front)
                right_eye_pos = (head_x + BLOCK_SIZE - eye_offset_side, head_y + eye_offset_front)
            elif dy > 0:  # 向下看
                left_eye_pos = (head_x + eye_offset_side, head_y + BLOCK_SIZE - eye_offset_front)
                right_eye_pos = (head_x + BLOCK_SIZE - eye_offset_side, head_y + BLOCK_SIZE - eye_offset_front)

            pygame.draw.circle(screen, EYE_COLOR, left_eye_pos, eye_radius)
            pygame.draw.circle(screen, EYE_COLOR, right_eye_pos, eye_radius)


def game_loop():
    game_over = False
    game_close = False

    # 初始位置（调整到游戏区域中心，避免出生在墙里）
    x = (grid_width // 2) * BLOCK_SIZE
    y = (grid_height // 2) * BLOCK_SIZE

    # 移动逻辑
    dx, dy = BLOCK_SIZE, 0  # 初始向右
    next_direction = (dx, dy)

    snake_list = []
    snake_length = 1

    # 食物坐标（必须在墙内随机）
    foodx = round(random.randrange(BLOCK_SIZE, WIDTH - 2 * BLOCK_SIZE) / 20.0) * 20.0
    foody = round(random.randrange(BLOCK_SIZE, HEIGHT - 2 * BLOCK_SIZE) / 20.0) * 20.0

    move_time = 0
    MOVE_DELAY = 100

    while not game_over:

        while game_close:
            screen.fill(BLACK)
            draw_walls()
            msg = font_style.render("撞墙啦！按 C 重玩，按 Q 退出", True, RED)
            screen.blit(msg, [WIDTH // 6, HEIGHT // 3 + BLOCK_SIZE])
            show_score(snake_length - 1)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        game_over = True
                        game_close = False
                    if event.key == pygame.K_c:
                        game_loop()
                if event.type == pygame.QUIT:
                    game_over = True
                    game_close = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and dx == 0:
                    next_direction = (-BLOCK_SIZE, 0)
                elif event.key == pygame.K_RIGHT and dx == 0:
                    next_direction = (BLOCK_SIZE, 0)
                elif event.key == pygame.K_UP and dy == 0:
                    next_direction = (0, -BLOCK_SIZE)
                elif event.key == pygame.K_DOWN and dy == 0:
                    next_direction = (0, BLOCK_SIZE)

        dt = clock.tick(60)
        move_time += dt

        if move_time >= MOVE_DELAY:
            move_time = 0
            dx, dy = next_direction

            x += dx
            y += dy

            if x < BLOCK_SIZE or x >= WIDTH - BLOCK_SIZE or \
                    y < BLOCK_SIZE or y >= HEIGHT - BLOCK_SIZE:
                game_close = True

            snake_head = [x, y]
            snake_list.append(snake_head)

            if len(snake_list) > snake_length:
                del snake_list[0]

            for segment in snake_list[:-1]:
                if segment == snake_head:
                    game_close = True

            if x == foodx and y == foody:
                foodx = round(random.randrange(BLOCK_SIZE, WIDTH - 2 * BLOCK_SIZE) / 20.0) * 20.0
                foody = round(random.randrange(BLOCK_SIZE, HEIGHT - 2 * BLOCK_SIZE) / 20.0) * 20.0
                snake_length += 1

        screen.fill(BLACK)

        draw_walls()

        # 画食物
        pygame.draw.circle(screen, RED, (foodx + BLOCK_SIZE // 2, foody + BLOCK_SIZE // 2), BLOCK_SIZE // 2 - 2)

        draw_snake_with_eyes(snake_list, dx, dy)

        show_score(snake_length - 1)
        pygame.display.update()

    pygame.quit()
    quit()


if __name__ == "__main__":
    game_loop()
