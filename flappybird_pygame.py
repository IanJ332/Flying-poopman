import pygame
import random
import sys
import os
import math

# Constants
PLAYER_FILE = "players.txt"
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
BLUE = (135, 206, 250)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)

# Game settings
BIRD_RADIUS = 20
PIPE_WIDTH = 70
GAP_HEIGHT = 150
GRAVITY = 0.4
FLAP_STRENGTH = -7
PIPE_SPEED = 3

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("The Flying Poopman!")
clock = pygame.time.Clock()

# Utility Functions
def display_text(text, x, y, color=BLACK, font_size=36, center=True):
    font = pygame.font.SysFont(None, font_size)
    rendered_text = font.render(text, True, color)
    text_rect = rendered_text.get_rect(center=(x, y) if center else (x, y))
    screen.blit(rendered_text, text_rect)

def load_players():
    if not os.path.exists(PLAYER_FILE):
        return {}
    with open(PLAYER_FILE, "r") as file:
        return {line.split(",")[0]: int(line.split(",")[1]) for line in file}

def save_players(players):
    with open(PLAYER_FILE, "w") as file:
        for name, score in players.items():
            file.write(f"{name},{score}\n")

def get_new_username(players):
    count = 1
    base_name = "Guest"
    username = base_name

    # 如果 "Guest" 已存在，加编号
    while username in players:
        username = f"{base_name} {count}"
        count += 1

    players[username] = 0  # 新玩家分数初始化为0
    save_players(players)
    return username


# 检查圆与矩形是否碰撞
def check_collision(circle_x, circle_y, circle_radius, rect_x, rect_y, rect_width, rect_height):
    # 找到小鸟距离矩形最近的点
    closest_x = max(rect_x, min(circle_x, rect_x + rect_width))
    closest_y = max(rect_y, min(circle_y, rect_y + rect_height))
    # 计算小鸟中心点与最近点的距离
    distance = math.sqrt((circle_x - closest_x) ** 2 + (circle_y - closest_y) ** 2)
    # 如果距离小于等于小鸟半径，则发生碰撞
    return distance <= circle_radius

# Welcome Screen
def welcome_screen(players, selected_player=None):
    index = 0
    options = ["Start", "Rank", "New Character", "Exit"]

    # 如果players中没有玩家，自动添加一个Guest
    if not selected_player:
        selected_player = list(players.keys())[0] if players else get_new_username(players)

    while True:
        screen.fill(WHITE)
        display_text("Welcome to The Flying Poopman", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 5, font_size=36)
        for i, option in enumerate(options):
            color = GREEN if i == index else BLACK
            display_text(option, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + i * 40, color=color, font_size=32)
        display_text(f"Hi! {selected_player}", SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80, font_size=28)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    index = (index - 1) % len(options)
                if event.key == pygame.K_DOWN:
                    index = (index + 1) % len(options)
                if event.key == pygame.K_RETURN:
                    if options[index] == "Start":
                        return selected_player  # 返回当前选中的玩家
                    elif options[index] == "Rank":
                        show_rank(players)
                    elif options[index] == "New Character":
                        new_username = input_new_character(players)
                        if new_username:
                            selected_player = new_username
                    elif options[index] == "Exit":
                        pygame.quit()
                        sys.exit()

# Show Rank
def show_rank(players):
    while True:
        screen.fill(WHITE)
        display_text("Player Rankings", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 6, font_size=36)
        sorted_players = sorted(players.items(), key=lambda x: x[1], reverse=True)
        for i, (name, score) in enumerate(sorted_players):
            display_text(f"{i + 1}. {name} - {score}", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4 + i * 30, font_size=28)
        display_text("Press ESC to return", SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50, font_size=28)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(), sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: return

# Input New Character
def input_new_character(players):
    username = ""
    while True:
        screen.fill(WHITE)
        display_text("Enter New Character Name:", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3)
        display_text(username, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        display_text("Press ESC to Cancel", SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50, font_size=28)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(), sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and username:
                    players[username] = 0
                    save_players(players)
                    return username
                elif event.key == pygame.K_BACKSPACE: username = username[:-1]
                elif event.key == pygame.K_ESCAPE: return None
                elif event.unicode.isalnum(): username += event.unicode


# 游戏结束界面
def game_over_screen(score, high_score, bird_y, pipes, bird_x=100):
    while True:
        # 重新绘制最后一帧游戏画面
        screen.fill(BLUE)
        pygame.draw.circle(screen, YELLOW, (bird_x, int(bird_y)), BIRD_RADIUS)  # 绘制小鸟
        for pipe in pipes:
            pygame.draw.rect(screen, GREEN, (pipe['x'], 0, PIPE_WIDTH, pipe['top_height']))  # 上方管道
            pygame.draw.rect(screen, GREEN, (pipe['x'], pipe['top_height'] + GAP_HEIGHT, PIPE_WIDTH, SCREEN_HEIGHT))  # 下方管道

        # 显示 Game Over 文本
        display_text("Game Over!", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3, font_size=48)
        display_text(f"Your Score: {score}", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        if score > high_score:
            display_text("Congratulations! New High Score!", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40, GREEN)
        display_text("Press ENTER to return to Menu", SCREEN_WIDTH // 2, SCREEN_HEIGHT - 60, font_size=28)

        pygame.display.flip()

        # 等待用户输入
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:  # 按下回车键返回主菜单
                    return

# Main Game Logic
def main_game(username, players):
    bird_x, bird_y = 100, SCREEN_HEIGHT // 2
    bird_velocity, score = 0, 0
    pipes = [{'x': SCREEN_WIDTH, 'top_height': random.randint(100, 400)}]

    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE:
                bird_velocity = FLAP_STRENGTH

        # 重力与移动
        bird_velocity += GRAVITY
        bird_y += bird_velocity

        # 管道逻辑
        for pipe in pipes:
            pipe['x'] -= PIPE_SPEED

        # 确保生成新管道
        if pipes[-1]['x'] < SCREEN_WIDTH - 200:
            pipes.append({'x': SCREEN_WIDTH, 'top_height': random.randint(100, 400)})

        # 移除超出屏幕的管道
        pipes = [p for p in pipes if p['x'] > -PIPE_WIDTH]

        # 更新分数逻辑
        for pipe in pipes:
            if pipe['x'] + PIPE_WIDTH < bird_x and not pipe.get('scored', False):
                score += 1
                pipe['scored'] = True

        # 碰撞检测
        for pipe in pipes:
            if check_collision(bird_x, bird_y, BIRD_RADIUS, pipe['x'], 0, PIPE_WIDTH, pipe['top_height']) or \
                    check_collision(bird_x, bird_y, BIRD_RADIUS, pipe['x'], pipe['top_height'] + GAP_HEIGHT, PIPE_WIDTH,
                                    SCREEN_HEIGHT):
                game_over_screen(score, players.get(username, 0), bird_y, pipes, bird_x)  # 调用结束画面
                return score
        if bird_y < 0 or bird_y > SCREEN_HEIGHT:
            game_over_screen(score, players.get(username, 0), bird_y, pipes, bird_x)
            return score

        # 画面更新
        screen.fill(BLUE)
        pygame.draw.circle(screen, YELLOW, (bird_x, int(bird_y)), BIRD_RADIUS)
        for pipe in pipes:
            pygame.draw.rect(screen, GREEN, (pipe['x'], 0, PIPE_WIDTH, pipe['top_height']))
            pygame.draw.rect(screen, GREEN, (pipe['x'], pipe['top_height'] + GAP_HEIGHT, PIPE_WIDTH, SCREEN_HEIGHT))
        display_text(f"Score: {score}", 20, 20, WHITE, 28, False)
        display_text(f"Player: {username}", SCREEN_WIDTH - 150, 20, WHITE, 28, False)
        pygame.display.flip()
        clock.tick(FPS)

# Run Game
if __name__ == "__main__":
    players = load_players()
    current_player = welcome_screen(players)  # 当前玩家
    while True:
        score = main_game(current_player, players)  # 只处理 main_game 返回的分数
        if score > players.get(current_player, 0):
            players[current_player] = score  # 更新高分
            save_players(players)  # 保存分数
        current_player = welcome_screen(players, selected_player=current_player)  # 返回主菜单，保持玩家不变

