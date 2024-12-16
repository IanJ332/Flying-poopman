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

def save_players(players, highest_score=None):
    with open(PLAYER_FILE, "w") as file:
        for name, score in players.items():
            file.write(f"{name},{score}\n")
        if highest_score is not None:  # 如果提供了最高分，写入文件
            file.write(f"highest_score:{highest_score}\n")

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

def load_players():
    if not os.path.exists(PLAYER_FILE):
        return {}, 0  # 如果文件不存在，返回空的玩家字典和最高分0
    with open(PLAYER_FILE, "r") as file:
        lines = file.readlines()
        players = {}
        highest_score = 0
        for line in lines:
            if line.startswith("highest_score:"):
                highest_score = int(line.strip().split(":")[1])
            else:
                name, score = line.strip().split(",")
                players[name] = int(score)
        return players, highest_score

# Welcome Screen
def welcome_screen(players, selected_player=None):
    index = 0
    options = ["Start", "Select Character", "Rank", "New Character", "Exit"]

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
                    elif options[index] == "Select Character":
                        selected_player = select_character_screen(players)
                    elif options[index] == "Rank":
                        show_rank(players)
                    elif options[index] == "New Character":
                        new_username = input_new_character(players)
                        if new_username:
                            selected_player = new_username
                    elif options[index] == "Exit":
                        pygame.quit()
                        sys.exit()

def select_character_screen(players):
    index = 0
    existing_players = list(players.keys())

    while True:
        screen.fill(WHITE)
        display_text("Select Your Character", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 5, font_size=36)

        for i, player in enumerate(existing_players):
            color = GREEN if i == index else BLACK
            display_text(player, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + i * 40, color=color, font_size=32)

        display_text("Press ENTER to Select, ESC to Return", SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50, font_size=24)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    index = (index - 1) % len(existing_players)
                if event.key == pygame.K_DOWN:
                    index = (index + 1) % len(existing_players)
                if event.key == pygame.K_RETURN:
                    return existing_players[index]  # 返回选中的玩家名字
                if event.key == pygame.K_ESCAPE:
                    return None  # 取消选择

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
    warning_message = ""  # 用于显示警告信息
    while True:
        screen.fill(WHITE)
        display_text("Enter New Character Name:", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3)
        display_text(username, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

        # 显示警告信息（如果有）
        if warning_message:
            display_text(warning_message, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40, color=(255, 0, 0), font_size=24)

        display_text("Press ESC to Cancel", SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50, font_size=28)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if not username:  # 检查输入是否为空
                        warning_message = "Username cannot be empty!"
                    elif username in players:  # 检查用户名是否已存在
                        warning_message = "Username already exists!"
                    else:
                        players[username] = 0
                        save_players(players)
                        return username
                elif event.key == pygame.K_BACKSPACE:  # 处理退格键
                    username = username[:-1]
                    warning_message = ""  # 清除警告信息
                elif event.key == pygame.K_ESCAPE:  # 取消输入
                    return None
                elif event.unicode.isalnum():  # 限制输入字符为字母和数字
                    username += event.unicode
                    warning_message = ""  # 清除警告信息

# 游戏结束界面
def game_over_screen(score, is_global_high, bird_y, pipes, bird_x=100):
    while True:
        screen.fill(BLUE)
        pygame.draw.circle(screen, YELLOW, (bird_x, int(bird_y)), BIRD_RADIUS)
        for pipe in pipes:
            pygame.draw.rect(screen, GREEN, (pipe['x'], 0, PIPE_WIDTH, pipe['top_height']))
            pygame.draw.rect(screen, GREEN, (pipe['x'], pipe['top_height'] + GAP_HEIGHT, PIPE_WIDTH, SCREEN_HEIGHT))

        # 显示游戏结束和分数
        display_text("Game Over!", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3, font_size=48)
        display_text(f"Your Score: {score}", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

        if is_global_high:
            display_text("Congratulations! New Global High Score!", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3 - 50, (0, 191, 255), font_size=32)
        display_text("Press ENTER to return to Menu", SCREEN_WIDTH // 2, SCREEN_HEIGHT - 60, font_size=28)
        display_text("Press R to Restart", SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30, font_size=28)

        pygame.display.flip()

        # 事件监听
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:  # 返回主菜单
                    return "menu"
                if event.key == pygame.K_r:  # 重新开始游戏
                    return "restart"

# Main Game Logic
def main_game(username, players, highest_score):
    bird_x, bird_y = 100, SCREEN_HEIGHT // 2
    bird_velocity, score = 0, 0
    pipes = [{'x': SCREEN_WIDTH, 'top_height': random.randint(100, 400)}]
    original_highest_score = highest_score  # 保存原始最高分

    while True:
        # 事件处理
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE:
                bird_velocity = FLAP_STRENGTH

        # 更新逻辑（重力、管道等）
        bird_velocity += GRAVITY
        bird_y += bird_velocity

        for pipe in pipes:
            pipe['x'] -= PIPE_SPEED

        # 新管道生成
        if pipes[-1]['x'] < SCREEN_WIDTH - 200:
            pipes.append({'x': SCREEN_WIDTH, 'top_height': random.randint(100, 400)})
        pipes = [p for p in pipes if p['x'] > -PIPE_WIDTH]

        # 碰撞检测
        for pipe in pipes:
            if check_collision(bird_x, bird_y, BIRD_RADIUS, pipe['x'], 0, PIPE_WIDTH, pipe['top_height']) or \
               check_collision(bird_x, bird_y, BIRD_RADIUS, pipe['x'], pipe['top_height'] + GAP_HEIGHT, PIPE_WIDTH, SCREEN_HEIGHT):
                is_global_high = score > original_highest_score
                action = game_over_screen(score, is_global_high, bird_y, pipes, bird_x)
                return action, score, max(highest_score, score)

        if bird_y < 0 or bird_y > SCREEN_HEIGHT:
            is_global_high = score > original_highest_score
            action = game_over_screen(score, is_global_high, bird_y, pipes, bird_x)
            return action, score, max(highest_score, score)

        # 更新分数逻辑
        for pipe in pipes:
            if pipe['x'] + PIPE_WIDTH < bird_x and not pipe.get('scored', False):
                score += 1
                pipe['scored'] = True
                highest_score = max(highest_score, score)

        # 绘制画面
        screen.fill(BLUE)
        pygame.draw.circle(screen, YELLOW, (bird_x, int(bird_y)), BIRD_RADIUS)
        for pipe in pipes:
            pygame.draw.rect(screen, GREEN, (pipe['x'], 0, PIPE_WIDTH, pipe['top_height']))
            pygame.draw.rect(screen, GREEN, (pipe['x'], pipe['top_height'] + GAP_HEIGHT, PIPE_WIDTH, SCREEN_HEIGHT))
        display_text(f"Score: {score}", 70, 30, WHITE, 28, False)
        display_text(f"Player: {username}", SCREEN_WIDTH - 70, 30, WHITE, 28, False)
        pygame.display.flip()
        clock.tick(FPS)

# Run Game
if __name__ == "__main__":
    players, highest_score = load_players()
    current_player = welcome_screen(players)

    while True:
        # 开始游戏
        action, score, highest_score = main_game(current_player, players, highest_score)

        # 更新玩家分数
        if score > players.get(current_player, 0):
            players[current_player] = score
        save_players(players, highest_score)

        # 根据动作决定下一步
        if action == "menu":  # 返回主菜单
            current_player = welcome_screen(players, selected_player=current_player)
        elif action == "restart":  # 重新开始游戏
            continue  # 直接回到主循环重新开始游戏

