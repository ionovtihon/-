"""Игра «Изгиб Питона» — классическая змейка на Pygame.

Реализована на принципах ООП: базовый класс GameObject и наследники Apple, Snake.
"""

import random

import pygame


# ── Константы ────────────────────────────────────────────────────────────────

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE   # 32
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE  # 24

BOARD_BACKGROUND_COLOR = (0, 0, 0)
CENTER_POSITION = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

# Векторы направлений
UP = (0, -GRID_SIZE)
DOWN = (0, GRID_SIZE)
LEFT = (-GRID_SIZE, 0)
RIGHT = (GRID_SIZE, 0)

# Все возможные позиции ячеек на поле
ALL_CELLS = {
    (x * GRID_SIZE, y * GRID_SIZE)
    for x in range(GRID_WIDTH)
    for y in range(GRID_HEIGHT)
}

# Карта смены направлений: (нажатая_клавиша, текущее_направление) → новое.
# Содержит 8 записей — по две на каждое текущее направление (исключая разворот).
DIRECTION_MAP = {
    (pygame.K_UP, RIGHT): UP,
    (pygame.K_UP, LEFT): UP,
    (pygame.K_DOWN, RIGHT): DOWN,
    (pygame.K_DOWN, LEFT): DOWN,
    (pygame.K_LEFT, UP): LEFT,
    (pygame.K_LEFT, DOWN): LEFT,
    (pygame.K_RIGHT, UP): RIGHT,
    (pygame.K_RIGHT, DOWN): RIGHT,
}


# ── Классы ───────────────────────────────────────────────────────────────────


class GameObject:
    """Базовый класс для всех игровых объектов.

    Содержит общие атрибуты позиции и цвета, а также заготовку метода отрисовки.
    """

    def __init__(self, position=CENTER_POSITION, body_color=None):
        """Инициализировать игровой объект с позицией и цветом.

        Args:
            position: координаты (x, y) объекта на игровом поле.
            body_color: RGB-кортеж цвета объекта.
        """
        self.position = position
        self.body_color = body_color

    def draw(self, surface):
        """Абстрактный метод отрисовки объекта.

        Должен быть переопределён в дочерних классах.

        Args:
            surface: поверхность Pygame, на которой происходит отрисовка.
        """
        pass


class Apple(GameObject):
    """Класс, описывающий яблоко и действия с ним."""

    def __init__(self, occupied_positions=None):
        """Инициализировать яблоко со случайной позицией вне занятых клеток.

        Args:
            occupied_positions: итерируемый объект с занятыми координатами
                (например, позиции сегментов змейки).
        """
        super().__init__(body_color=(255, 0, 0))
        self.randomize_position(occupied_positions)

    def randomize_position(self, occupied_positions=None):
        """Установить случайное положение яблока, избегая занятых клеток.

        Args:
            occupied_positions: итерируемый объект с координатами, которые
                нельзя занимать. Если None — используется всё поле.
        """
        if occupied_positions:
            free_cells = list(ALL_CELLS - set(occupied_positions))
        else:
            free_cells = list(ALL_CELLS)
        self.position = random.choice(free_cells)

    def draw(self, surface):
        """Отрисовать яблоко на игровой поверхности.

        Args:
            surface: поверхность Pygame для отрисовки.
        """
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(surface, self.body_color, rect)


class Snake(GameObject):
    """Класс, описывающий змейку и её поведение.

    Управляет движением, отрисовкой, обрабатывает действия пользователя.
    """

    def __init__(self):
        """Инициализировать змейку в центре экрана, движущейся вправо."""
        super().__init__(position=CENTER_POSITION, body_color=(0, 255, 0))
        self.length = 1
        self.positions = [CENTER_POSITION]
        self.direction = RIGHT
        self.next_direction = None
        self.last = None

    def update_direction(self):
        """Применить следующее направление, если оно было установлено."""
        if self.next_direction is not None:
            self.direction = self.next_direction
            self.next_direction = None

    def get_head_position(self):
        """Вернуть текущую позицию головы змейки.

        Returns:
            Кортеж (x, y) — координаты первого сегмента.
        """
        return self.positions[0]

    def move(self):
        """Обновить позицию змейки на один шаг.

        Вычисляет новую позицию головы с учётом направления и оборачивания
        по краям экрана. Проверяет столкновение с собой и управляет хвостом.
        """
        head_x, head_y = self.get_head_position()
        dx, dy = self.direction

        # Новая голова с оборачиванием через края экрана
        new_head = (
            (head_x + dx) % SCREEN_WIDTH,
            (head_y + dy) % SCREEN_HEIGHT,
        )

        # Проверка самоукуса (пропускаем голову и шею — positions[0] и [1])
        if new_head in self.positions[2:]:
            self.reset()
            return

        self.positions.insert(0, new_head)

        if len(self.positions) > self.length:
            self.last = self.positions.pop()
        else:
            self.last = None

    def reset(self):
        """Сбросить змейку в начальное состояние после столкновения с собой.

        Длина сбрасывается до 1, позиция — центр экрана,
        направление выбирается случайно.
        """
        self.length = 1
        self.positions = [CENTER_POSITION]
        self.direction = random.choice([UP, DOWN, LEFT, RIGHT])
        self.next_direction = None
        self.last = None

    def draw(self, surface):
        """Отрисовать змейку и затереть её след.

        Args:
            surface: поверхность Pygame для отрисовки.
        """
        # Отрисовка всех сегментов
        for position in self.positions:
            rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(surface, self.body_color, rect)

        # Затирание хвостового сегмента
        if self.last:
            last_rect = pygame.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(surface, BOARD_BACKGROUND_COLOR, last_rect)


# ── Вспомогательные функции ─────────────────────────────────────────────────


def handle_keys(snake):
    """Обработать нажатия клавиш и установить следующее направление змейки.

    Змейка не может развернуться на 180° — карта DIRECTION_MAP
    не содержит записей для противоположного направления.

    Args:
        snake: экземпляр класса Snake.

    Returns:
        bool: True, если игра должна продолжаться; False при QUIT или ESC.
    """
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return False
            new_direction = DIRECTION_MAP.get((event.key, snake.direction))
            if new_direction is not None:
                snake.next_direction = new_direction
    return True


# ── Основной игровой цикл ───────────────────────────────────────────────────


def main():
    """Запустить игру «Изгиб Питона».

    Инициализирует Pygame, создаёт объекты, запускает основной цикл:
    обработка ввода → обновление направления → движение змейки →
    проверка столкновений → отрисовка → обновление экрана.
    """
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('Изгиб Питона')
    clock = pygame.time.Clock()

    snake = Snake()
    apple = Apple(snake.positions)

    running = True
    while running:
        clock.tick(20)

        if not handle_keys(snake):
            running = False
            continue
        snake.update_direction()

        old_length = len(snake.positions)
        snake.move()

        # Если змейка сброшена (самоукус) — очистить экран и перегенерировать яблоко
        if len(snake.positions) < old_length:
            screen.fill(BOARD_BACKGROUND_COLOR)
            apple.randomize_position(snake.positions)

        # Змейка съела яблоко
        if snake.get_head_position() == apple.position:
            snake.length += 1
            apple.randomize_position(snake.positions)

        snake.draw(screen)
        apple.draw(screen)

        pygame.display.update()

    pygame.quit()


if __name__ == '__main__':
    main()
