import pygame
import random

# --- 1. 初始化与配置 ---
pygame.init()

# 颜色
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (213, 50, 80)
BLACK = (30, 30, 30)  # 深灰色背景更高级

# 尺寸
WIDTH, HEIGHT = 600, 400
BLOCK_SIZE = 20

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('高级感贪吃蛇 - 顺滑操作版')
clock = pygame.time.Clock()
font_style = pygame.font.SysFont("simhei", 25)


def show_score(score):
    value = font_style.render("得分: " + str(score), True, WHITE)
    screen.blit(value, [10, 10])


def game_loop():
    game_over = False
    game_close = False

    # 初始位置
    x, y = WIDTH // 2, HEIGHT // 2

    # 移动逻辑：dx, dy 代表方向
    dx, dy = BLOCK_SIZE, 0  # 初始向右动
    next_direction = (dx, dy)  # 缓冲下一个方向

    snake_list = []
    snake_length = 1

    # 食物坐标
    foodx = round(random.randrange(0, WIDTH - BLOCK_SIZE) / 20.0) * 20.0
    foody = round(random.randrange(0, HEIGHT - BLOCK_SIZE) / 20.0) * 20.0

    # 关键变量：控制蛇移动的计时器
    move_time = 0
    MOVE_DELAY = 100  # 每 100 毫秒移动一格 (0.1秒)，你可以改这个数字调速

    while not game_over:

        # --- A. 游戏结束界面 ---
        while game_close:
            screen.fill(BLACK)
            msg = font_style.render("撞墙啦！按 C 重玩，按 Q 退出", True, RED)
            screen.blit(msg, [WIDTH // 6, HEIGHT // 3])
            show_score(snake_length - 1)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        game_over = True
                        game_close = False
                    if event.key == pygame.K_c:
                        game_loop()

        # --- B. 极速输入检测 (每秒检测60次) ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            if event.type == pygame.KEYDOWN:
                # 使用 next_direction 缓冲，防止快速按“上左”导致无效
                if event.key == pygame.K_LEFT and dx == 0:
                    next_direction = (-BLOCK_SIZE, 0)
                elif event.key == pygame.K_RIGHT and dx == 0:
                    next_direction = (BLOCK_SIZE, 0)
                elif event.key == pygame.K_UP and dy == 0:
                    next_direction = (0, -BLOCK_SIZE)
                elif event.key == pygame.K_DOWN and dy == 0:
                    next_direction = (0, BLOCK_SIZE)

        # --- C. 定时移动逻辑 ---
        dt = clock.tick(60)  # 保持 60 FPS 的刷新率
        move_time += dt

        if move_time >= MOVE_DELAY:
            move_time = 0  # 重置计时器
            dx, dy = next_direction  # 正式转向

            x += dx
            y += dy

            # 边界检测
            if x >= WIDTH or x < 0 or y >= HEIGHT or y < 0:
                game_close = True

            # 更新蛇身
            snake_head = [x, y]
            snake_list.append(snake_head)

            if len(snake_list) > snake_length:
                del snake_list[0]

            # 自撞检测
            for segment in snake_list[:-1]:
                if segment == snake_head:
                    game_close = True

            # 吃到食物
            if x == foodx and y == foody:
                foodx = round(random.randrange(0, WIDTH - BLOCK_SIZE) / 20.0) * 20.0
                foody = round(random.randrange(0, HEIGHT - BLOCK_SIZE) / 20.0) * 20.0
                snake_length += 1

        # --- D. 绘图渲染 ---
        screen.fill(BLACK)

        # 画食物 (红色圆点)
        pygame.draw.circle(screen, RED, (foodx + BLOCK_SIZE // 2, foody + BLOCK_SIZE // 2), BLOCK_SIZE // 2 - 2)

        # 画蛇 (绿色方块)
        for i, block in enumerate(snake_list):
            color = GREEN if i == len(snake_list) - 1 else (0, 200, 0)  # 蛇头颜色亮一点
            pygame.draw.rect(screen, color, [block[0], block[1], BLOCK_SIZE - 1, BLOCK_SIZE - 1])

        show_score(snake_length - 1)
        pygame.display.update()

    pygame.quit()
    quit()


if __name__ == "__main__":
    game_loop()
