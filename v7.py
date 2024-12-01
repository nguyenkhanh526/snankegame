import cv2
import mediapipe as mp
import pygame
import random
import sys

# Khởi tạo pygame
pygame.init()

# Kích thước màn hình
WIDTH, HEIGHT = 600, 400
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game with Hand Control")

# Màu sắc
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLACK = (0, 0, 0)

# Kích thước rắn
SNAKE_SIZE = 20

# Khởi tạo Mediapipe cho phát hiện bàn tay
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

# Hàm đếm số ngón tay giơ lên
def count_fingers(hand_landmarks):
    fingers_up = [False] * 5
    if hand_landmarks:
        fingers_up[0] = hand_landmarks[4].x < hand_landmarks[3].x
        fingers_up[1] = hand_landmarks[8].y < hand_landmarks[6].y
        fingers_up[2] = hand_landmarks[12].y < hand_landmarks[10].y
        fingers_up[3] = hand_landmarks[16].y < hand_landmarks[14].y
        fingers_up[4] = hand_landmarks[20].y < hand_landmarks[18].y
    return sum(fingers_up)

# Hàm hiển thị menu chính
def main_menu():
    running = True
    selected_option = 0
    font_title = pygame.font.SysFont(None, 60)
    font_option = pygame.font.SysFont(None, 40)

    menu_options = ["BAT DAU TRO CHOI", "HUONG DAN", "DIEU CHINH TOC DO", "THOAT"]

    while running:
        win.fill(BLACK)

        # Hiển thị tiêu đề
        title = font_title.render("RAN SAN MOI", True, GREEN)
        win.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))

        # Hiển thị các tùy chọn menu
        for i, option in enumerate(menu_options):
            color = RED if i == selected_option else WHITE
            text_surface = font_option.render(option, True, color)
            win.blit(text_surface, (WIDTH // 2 - text_surface.get_width() // 2, 150 + i * 50))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_option = (selected_option - 1) % len(menu_options)
                elif event.key == pygame.K_DOWN:
                    selected_option = (selected_option + 1) % len(menu_options)
                elif event.key == pygame.K_RETURN:
                    if selected_option == 0:  # Bắt đầu trò chơi
                        return "play"
                    elif selected_option == 1:  # Hướng dẫn
                        return "instructions"
                    elif selected_option == 2:  # Điều chỉnh tốc độ
                        return "speed"
                    elif selected_option == 3:  # Thoát
                        pygame.quit()
                        sys.exit()

# Hàm hiển thị hướng dẫn
def show_instructions():
    running = True
    font = pygame.font.SysFont(None, 40)
    instructions = [
        "Huong dan tro choi:",
        "1. Di chuyen ran bang so ngon tay mo:",
        "   - 1 ngon: Đi len.",
        "   - 2 ngon: Đi xuong.",
        "   - 3 ngon: Sang trai.",
        "   - 4 ngon: Sang phai.",
        "2. An thuc an de tang chieu dai ran.",
        "3. Tranh va cham voi tuong va chinh minh.",
        "Nhan ESC de quay lai."
    ]

    while running:
        win.fill(WHITE)
        for i, line in enumerate(instructions):
            text_surface = font.render(line, True, BLACK)
            win.blit(text_surface, (20, 20 + i * 40))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

# Hàm điều chỉnh tốc độ
def adjust_speed():
    running = True
    selected_speed = 2  # Giá trị mặc định
    speeds = [1, 2, 4, 7]
    selected_index = 1  # Mặc định là tốc độ 2
    font = pygame.font.SysFont(None, 40)

    while running:
        win.fill(BLACK)

        # Hiển thị tiêu đề
        title = font.render("CHỌN TỐC ĐỘ RẮN", True, GREEN)
        win.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))

        # Hiển thị các tùy chọn tốc độ
        for i, speed in enumerate(speeds):
            color = RED if i == selected_index else WHITE
            text_surface = font.render(f"Tốc độ: {speed}", True, color)
            win.blit(text_surface, (WIDTH // 2 - text_surface.get_width() // 2, 150 + i * 50))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_index = (selected_index - 1) % len(speeds)
                elif event.key == pygame.K_DOWN:
                    selected_index = (selected_index + 1) % len(speeds)
                elif event.key == pygame.K_RETURN:
                    return speeds[selected_index]
                elif event.key == pygame.K_ESCAPE:
                    return selected_speed  # Giữ tốc độ hiện tại nếu thoát
                
# Thêm âm thanh
pygame.mixer.init()
eat_sound = pygame.mixer.Sound("eat_sound.mp3")  # Âm thanh ăn thức ăn
                

# Thêm background
BACKGROUND_IMG = pygame.image.load("background.jpg")  # Đảm bảo file "background.jpg" tồn tại trong thư mục
BACKGROUND_IMG = pygame.transform.scale(BACKGROUND_IMG, (WIDTH, HEIGHT))  # Scale để khớp màn hình
SNAKE_IMG = pygame.image.load("snake.png")
SNAKE_IMG = pygame.transform.scale(SNAKE_IMG, (SNAKE_SIZE, SNAKE_SIZE))  # Chỉnh kích thước phù hợp
APPLE_SIZE = SNAKE_SIZE * 5.0
APPLE_IMG = pygame.image.load("apple.png")
APPLE_IMG = pygame.transform.scale(APPLE_IMG, (SNAKE_SIZE*1.5, SNAKE_SIZE*1.5))

# Hàm chính của trò chơi với background
def game(speed):
    cap = cv2.VideoCapture(0)
    game_over = False
    game_close = False

    # Tọa độ ban đầu của rắn và thức ăn
    x, y = WIDTH // 2, HEIGHT // 2
    food_x = round(random.randrange(0, WIDTH - SNAKE_SIZE) / SNAKE_SIZE) * SNAKE_SIZE
    food_y = round(random.randrange(0, HEIGHT - SNAKE_SIZE) / SNAKE_SIZE) * SNAKE_SIZE

    dx, dy = 0, 0
    current_direction = None  # Lưu hướng hiện tại
    snake_body = []
    snake_length = 1
    clock = pygame.time.Clock()

    while not game_over:
        while game_close:
            win.fill(WHITE)
            font = pygame.font.SysFont(None, 50)
            msg = font.render("Game Over! Nhan Q de thoat", True, RED)
            win.blit(msg, [WIDTH / 8, HEIGHT / 2])
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                    game_over = True
                    game_close = False

        success, img = cap.read()
        img = cv2.flip(img, 1)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = hands.process(img_rgb)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_draw.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                finger_count = count_fingers(hand_landmarks.landmark)

                # Xác định hướng mới nếu hợp lệ
                if finger_count == 1 and current_direction != "DOWN":
                    dx, dy = 0, -SNAKE_SIZE
                    current_direction = "UP"
                elif finger_count == 2 and current_direction != "UP":
                    dx, dy = 0, SNAKE_SIZE
                    current_direction = "DOWN"
                elif finger_count == 3 and current_direction != "RIGHT":
                    dx, dy = -SNAKE_SIZE, 0
                    current_direction = "LEFT"
                elif finger_count == 4 and current_direction != "LEFT":
                    dx, dy = SNAKE_SIZE, 0
                    current_direction = "RIGHT"

        if x >= WIDTH or x < 0 or y >= HEIGHT or y < 0:
            game_close = True

        x += dx
        y += dy

        # Vẽ background trước
        win.blit(BACKGROUND_IMG, (0, 0))

        # Vẽ thức ăn v
        win.blit(APPLE_IMG, (food_x - (SNAKE_SIZE // 2), food_y - (SNAKE_SIZE // 2)))


        snake_head = [x, y]
        snake_body.append(snake_head)
        if len(snake_body) > snake_length:
            del snake_body[0]

        for segment in snake_body[:-1]:
            if segment == snake_head:
                game_close = True

        for segment in snake_body:
            win.blit(SNAKE_IMG, (segment[0], segment[1]))

        

        if x == food_x and y == food_y:
            food_x = round(random.randrange(0, WIDTH - SNAKE_SIZE) / SNAKE_SIZE) * SNAKE_SIZE
            food_y = round(random.randrange(0, HEIGHT - SNAKE_SIZE) / SNAKE_SIZE) * SNAKE_SIZE
            snake_length += 1
            eat_sound.play()

        cv2.imshow("Camera", img)
        pygame.display.update()
        clock.tick(speed)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            game_over = True

    cap.release()
    cv2.destroyAllWindows()
    pygame.quit()

# Chạy chương trình
snake_speed = 4  # Giá trị mặc định
while True:
    choice = main_menu()
    if choice == "play":
        game(snake_speed)
    elif choice == "instructions":
        show_instructions()
    elif choice == "speed":
        snake_speed = adjust_speed()
