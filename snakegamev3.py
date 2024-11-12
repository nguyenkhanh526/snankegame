import cv2
import mediapipe as mp
import pygame
import random

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

# Kích thước rắn và tốc độ
SNAKE_SIZE = 20
SNAKE_SPEED = 2

# Khởi tạo Mediapipe cho phát hiện bàn tay
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

# Hàm đếm số ngón tay giơ lên
def count_fingers(hand_landmarks):
    fingers_up = [False] * 5
    # Kiểm tra vị trí các ngón tay so với điểm đặc trưng của tay
    if hand_landmarks:
        # Ngón cái
        fingers_up[0] = hand_landmarks[4].x < hand_landmarks[3].x
        # Các ngón còn lại
        fingers_up[1] = hand_landmarks[8].y < hand_landmarks[6].y
        fingers_up[2] = hand_landmarks[12].y < hand_landmarks[10].y
        fingers_up[3] = hand_landmarks[16].y < hand_landmarks[14].y
        fingers_up[4] = hand_landmarks[20].y < hand_landmarks[18].y
    return sum(fingers_up)

# Hàm chính của trò chơi
def game():
    cap = cv2.VideoCapture(0)
    game_over = False
    game_close = False

    # Tọa độ ban đầu của rắn và thức ăn
    x, y = WIDTH // 2, HEIGHT // 2
    food_x = round(random.randrange(0, WIDTH - SNAKE_SIZE) / SNAKE_SIZE) * SNAKE_SIZE
    food_y = round(random.randrange(0, HEIGHT - SNAKE_SIZE) / SNAKE_SIZE) * SNAKE_SIZE

    # Đường di chuyển của rắn
    dx, dy = 0, 0

    # Cấu trúc rắn
    snake_body = []
    snake_length = 1

    # Vòng lặp trò chơi
    clock = pygame.time.Clock()
    while not game_over:
        while game_close:
            win.fill(WHITE)
            font = pygame.font.SysFont(None, 50)
            msg = font.render("Game Over! Press Q to Quit", True, RED)
            win.blit(msg, [WIDTH / 4, HEIGHT / 2])
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                    game_over = True
                    game_close = False

        # Xử lý hình ảnh từ camera
        success, img = cap.read()
        img = cv2.flip(img, 1)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = hands.process(img_rgb)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_draw.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                finger_count = count_fingers(hand_landmarks.landmark)
                
                # Điều khiển rắn bằng cử chỉ
                if finger_count == 1:
                    dx, dy = 0, -SNAKE_SIZE  # Đi lên
                elif finger_count == 2:
                    dx, dy = 0, SNAKE_SIZE   # Đi xuống
                elif finger_count == 3:
                    dx, dy = -SNAKE_SIZE, 0  # Sang trái
                elif finger_count == 4:
                    dx, dy = SNAKE_SIZE, 0   # Sang phải

        # Kiểm tra giới hạn màn hình
        if x >= WIDTH or x < 0 or y >= HEIGHT or y < 0:
            game_close = True

        # Cập nhật vị trí của rắn
        x += dx
        y += dy

        # Vẽ màn hình và thức ăn
        win.fill(WHITE)
        pygame.draw.rect(win, RED, [food_x, food_y, SNAKE_SIZE, SNAKE_SIZE])

        # Xây dựng thân rắn
        snake_head = [x, y]
        snake_body.append(snake_head)
        if len(snake_body) > snake_length:
            del snake_body[0]

        # Kiểm tra va chạm thân rắn
        for segment in snake_body[:-1]:
            if segment == snake_head:
                game_close = True

        # Vẽ rắn
        for segment in snake_body:
            pygame.draw.rect(win, GREEN, [segment[0], segment[1], SNAKE_SIZE, SNAKE_SIZE])

        # Kiểm tra va chạm với thức ăn
        if x == food_x and y == food_y:
            food_x = round(random.randrange(0, WIDTH - SNAKE_SIZE) / SNAKE_SIZE) * SNAKE_SIZE
            food_y = round(random.randrange(0, HEIGHT - SNAKE_SIZE) / SNAKE_SIZE) * SNAKE_SIZE
            snake_length += 1

        # Hiển thị camera lên cửa sổ
        cv2.imshow("Camera", img)
        pygame.display.update()
        clock.tick(SNAKE_SPEED)

        # Thoát khi nhấn 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            game_over = True

    cap.release()
    cv2.destroyAllWindows()
    pygame.quit()

# Chạy game
game()
