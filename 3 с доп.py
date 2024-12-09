import random
import pygame

widthscreen = 800
screen_height = 600
min_pillars = 5
max_pillars = 10
max_birds_per_pillar = 15
bird_speed = 3
pillar_width = 20
repair_time = 100
pillar_spacing = 20

# Начальные значения для частоты появления птиц и столбов
bird_spawn_rate = 1260  # Количество кадров до появления новой птицы
pillar_spawn_rate = 960  # Количество кадров до появления нового столба

# Определение состояний
STATE_FLYING_IN = 0
STATE_FLYING_UP = 1
STATE_MOVING_TO_PILLAR = 2
STATE_SITTING_ON_PILLAR = 3

class Bird:
    def __init__(self, color):
        self.color = color
        self.x = random.randint(0, widthscreen)  # Начальная позиция X
        self.y = random.randint(-100, -20)  # Начальная позиция Y (за верхней границей)
        self.target_pillar = None  # Целевой столб
        self.sit_time = random.randint(60, 180)  # Время сидения на столбе
        self.current_time = 0  # Текущее время сидения
        self.state = STATE_FLYING_IN  # Начальное состояние - летят сверху

    def update(self, pillars):
        if self.state == STATE_FLYING_IN:
            self.y += bird_speed
            if self.y >= 0:
                self.choose_next_action(pillars)
        elif self.state == STATE_FLYING_UP:
            self.y -= bird_speed
            if self.y < -20:
                self.y = -20
                self.choose_next_action(pillars)
        elif self.state == STATE_MOVING_TO_PILLAR:
            if self.target_pillar and not self.target_pillar.is_broken:
                dx = self.target_pillar.x - self.x
                dy = self.target_pillar.y - self.y
                distance = (dx ** 2 + dy ** 2) ** 0.5
                if distance > bird_speed:
                    self.x += dx / distance * bird_speed
                    self.y += dy / distance * bird_speed
                else:
                    if self.target_pillar.add_bird():
                        self.state = STATE_SITTING_ON_PILLAR
                        self.current_time = 0
                    else:
                        self.choose_next_action(pillars)
            else:
                self.choose_next_action(pillars)
        elif self.state == STATE_SITTING_ON_PILLAR:
            if self.target_pillar and not self.target_pillar.is_broken:
                self.current_time += 1
                if self.current_time >= self.sit_time:
                    self.target_pillar.remove_bird()
                    self.choose_next_action(pillars)
            else:
                self.choose_next_action(pillars)

    def choose_next_action(self, pillars):
        if random.random() < 0.1 and self.state != STATE_FLYING_IN:
            self.state = STATE_FLYING_UP
        else:
            self.find_target_pillar(pillars)
            if self.target_pillar:
                self.state = STATE_MOVING_TO_PILLAR
            else:
                self.state = STATE_FLYING_UP

    def find_target_pillar(self, pillars):
        valid_pillars = [pillar for pillar in pillars if not pillar.is_broken]
        if valid_pillars:
            self.target_pillar = random.choice(valid_pillars)
        else:
            self.target_pillar = None

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), 10)

class Pillar:
    def __init__(self, x, max_birds):
        self.max_birds = max_birds  # Максимальное количество птиц на столбе
        self.current_load = 0
        self.x = x
        self.y = screen_height - random.randint(100, 300)
        self.is_broken = False
        self.repair_time = repair_time
        self.color = (128, 128, 128)
        self.rect = pygame.Rect(self.x, self.y, pillar_width, screen_height - self.y)  # Определяем прямоугольник для столкновений

    def add_bird(self):
        if self.current_load < self.max_birds:
            self.current_load += 1
            return True
        else:
            self.is_broken = True
            self.repair_time = random.randint(repair_time, repair_time * 3)
            return False

    def remove_bird(self):
        if self.current_load > 0:
            self.current_load -= 1

    def check_if_broken(self):
        if self.current_load > self.max_birds:
            self.is_broken = True  # Столб разрушен, если на нем больше птиц, чем он может выдержать
            self.repair_time = random.randint(repair_time, repair_time * 3)

    def update(self):
        if self.is_broken:
            self.repair_time -= 1
            if self.repair_time <= 0:
                self.is_broken = False

    def draw(self, screen):
        if not self.is_broken:
            self.rect = pygame.Rect(self.x, self.y, pillar_width, screen_height - self.y)  # Обновляем прямоугольник
            pygame.draw.rect(screen, self.color, self.rect)

class SpinBox:
    def __init__(self, x, y, min_value, max_value, initial_value, update_function=None, pillars=None):
        self.rect = pygame.Rect(x, y, 80, 30)  # Уменьшенный размер
        self.min_value = min_value
        self.max_value = max_value
        self.value = initial_value
        self.increase_button = pygame.Rect(x + 90, y, 20, 15)  # Уменьшенный размер кнопок
        self.decrease_button = pygame.Rect(x + 90, y + 15, 20, 15)
        self.update_function = update_function  # Функция обновления
        self.pillars = pillars  # Ссылка на столбы

    def draw(self, screen):
        pygame.draw.rect(screen, (0, 0, 0), self.rect, 2)
        font = pygame.font.Font(None, 24)  # Уменьшенный размер шрифта
        value_surface = font.render(str(self.value), True, (0, 0, 0))
        screen.blit(value_surface, (self.rect.x + 10, self.rect.y + 5))
        pygame.draw.rect(screen, (0, 0, 0), self.increase_button)
        pygame.draw.rect(screen, (0, 0, 0), self.decrease_button)
        increase_surface = font.render("+", True, (255, 255, 255))
        decrease_surface = font.render("-", True, (255, 255, 255))
        screen.blit(increase_surface, (self.increase_button.x + 5, self.increase_button.y))
        screen.blit(decrease_surface, (self.decrease_button.x + 5, self.decrease_button.y))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.increase_button.collidepoint(event.pos):
                    if self.value < self.max_value:
                        self.value += 1
                        if self.update_function:
                            self.update_function()  # Обновляем прочность
                elif self.decrease_button.collidepoint(event.pos):
                    if self.value > self.min_value:
                        self.value -= 1
                        if self.update_function:
                            self.update_function()  # Обновляем прочность

    def update_strength(self):
        global max_birds_per_pillar
        max_birds_per_pillar = self.value
        # Обновляем max_birds для всех существующих столбов
        for pillar in self.pillars:
            pillar.max_birds = self.value

    def update_bird_spawn_rate(self):
        global bird_spawn_rate
        bird_spawn_rate = 1260 - 60 * self.value

    def update_pillar_spawn_rate(self):
        global pillar_spawn_rate
        pillar_spawn_rate = 960 - self.value * 60

class World:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((widthscreen, screen_height))
        self.clock = pygame.time.Clock()
        self.birds = []
        self.pillars = []
        self.bird_spawn_timer = 0
        self.pillar_spawn_timer = 0
        self.selected_pillar = None  # Переменная для хранения выбранного столба
        self.create_objects()
        self.paused = False

    def create_objects(self):
        num_pillars = random.randint(min_pillars, max_pillars)
        for _ in range(num_pillars):
            while True:
                new_x = random.randint(0, widthscreen - pillar_width)
                if not self.pillars or all(abs(new_x - pillar.x) > pillar_spacing for pillar in self.pillars):
                    self.pillars.append(Pillar(new_x, max_birds_per_pillar))
                    break

        # Инициализация количества птиц
        for _ in range(random.randint(5, 15)):
            self.birds.append(Bird(random.choice(["red", "blue", "green"])))

    def update(self):
        if not self.paused:  # Обновляем только если не на паузе
            for bird in self.birds:
                bird.update(self.pillars)
            for pillar in self.pillars:
                pillar.update()
        # Обновление таймеров для появления новых объектов
        self.bird_spawn_timer += 1
        self.pillar_spawn_timer += 1
        # Проверка, нужно ли создать новую птицу
        if self.bird_spawn_timer >= bird_spawn_rate:
            self.birds.append(Bird(random.choice(["red", "blue", "green"])))
            self.bird_spawn_timer = 0  # Сброс таймера

        # Проверка, нужно ли создать новый столб
        if self.pillar_spawn_timer >= pillar_spawn_rate:
            while True:
                new_x = random.randint(0, widthscreen - pillar_width)
                if not self.pillars or all(abs(new_x - pillar.x) > pillar_spacing for pillar in self.pillars):
                    self.pillars.append(Pillar(new_x, max_birds_per_pillar))  # Передаем max_birds_per_pillar
                    break
            self.pillar_spawn_timer = 0  # Сброс таймера
    def update_strength(self, change):
        if self.selected_pillar:
            new_value = self.selected_pillar.max_birds + change
            if 1 <= new_value <= 20:  # Ensure valid values
                self.selected_pillar.max_birds = new_value
                self.selected_pillar.check_if_broken()  # Check if broken immediately

    def draw(self):
        self.screen.fill((255, 255, 255))  # Очистка экрана
        for pillar in self.pillars:
            pillar.draw(self.screen)
        for bird in self.birds:
            bird.draw(self.screen)  # Рисуем птиц на экране
        bird_spawn_spin_box.draw(self.screen)  # Рисуем SpinBox для частоты появления птиц
        pillar_spawn_spin_box.draw(self.screen)  # Рисуем SpinBox для частоты появления столбов
        strength_spin_box.draw(self.screen)  # Рисуем SpinBox для прочности
        self.draw_labels()  # Рисуем подписи
        pygame.display.flip()

    def draw_labels(self):
        font = pygame.font.Font(None, 24)
        labels = ["Птицы", "Столбы", "Прочность"]
        positions = [(150, 20), (300, 20), (450, 20)]
        for label, pos in zip(labels, positions):
            label_surface = font.render(label, True, (0, 0, 0))
            self.screen.blit(label_surface, pos)

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if event.button == 1 and mouse_pos[1] > screen_height / 2:  # Левая кнопка мыши
                        for pillar in self.pillars:
                            if pillar.rect.collidepoint(mouse_pos):
                                if pillar.is_broken:
                                    pillar.is_broken = False
                                    pillar.repair_time = repair_time  # Сброс времени ремонта
                                else:
                                    self.selected_pillar = pillar  # Запоминаем выбранный столб
                                break
                        else:
                            while True:
                                new_x = random.randint(0, widthscreen - pillar_width)
                                if not self.pillars or all(abs(new_x - pillar.x) > pillar_spacing for pillar in self.pillars):
                                    self.pillars.append(Pillar(new_x, max_birds_per_pillar))
                                    break

                    elif event.button == 3 and mouse_pos[1] > screen_height / 2:  # Правая кнопка мыши - сломать столб
                        for pillar in self.pillars:
                            if pillar.rect.collidepoint(mouse_pos):
                                pillar.is_broken = True
                                pillar.repair_time = random.randint(repair_time, repair_time * 3)
                                break
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:  # Пауза при нажатии пробела
                        self.paused = not self.paused
                    elif event.key == pygame.K_KP_PLUS:
                        new_bird = Bird(random.choice(["red", "blue", "green"]))
                        self.birds.append(new_bird)
                    elif event.key == pygame.K_UP:  # Увеличение прочности
                        self.update_strength(1)
                    elif event.key == pygame.K_DOWN:  # Уменьшение прочности
                        self.update_strength(-1)

                # Обработка кликов для SpinBox
                bird_spawn_spin_box.handle_event(event)
                pillar_spawn_spin_box.handle_event(event)
                strength_spin_box.handle_event(event)

            if not self.paused:  # Обновляем только если не на паузе
                self.update()
            self.draw()
            self.clock.tick(60)

# Инициализация SpinBox
bird_spawn_spin_box = SpinBox(150, 40, 1, 20, 1)
pillar_spawn_spin_box = SpinBox(300, 40, 1, 15, 1)
strength_spin_box = SpinBox(450, 40, 1, max_birds_per_pillar, 5)  # Создаем объект без функции и списка столбов

# Установка функций обновления и списка столбов
strength_spin_box.update_function = strength_spin_box.update_strength
strength_spin_box.pillars = []  # Передаем список столбов в SpinBox

# Установка функций обновления для других SpinBox
bird_spawn_spin_box.update_function = bird_spawn_spin_box.update_bird_spawn_rate
pillar_spawn_spin_box.update_function = pillar_spawn_spin_box.update_pillar_spawn_rate

world = World()
world.run()

