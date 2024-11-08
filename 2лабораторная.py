import pygame
import random
import json


SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
NUM_BIRDS = random.randint(5, 15)
MIN_PILLARS = 5
MAX_PILLARS = 10
MAX_BIRDS_PER_PILLAR = 10
BIRD_SPEED = 3
PILLAR_WIDTH = 20
REPAIR_TIME = 100
PILLAR_SPACING = 50

STATE_FLYING_IN = 0  # Летят сверху в начале игры
STATE_FLYING_UP = 1  # Летят вверх
STATE_MOVING_TO_PILLAR = 2  # Двигаются к столбу
STATE_SITTING_ON_PILLAR = 3  # Сидят на столбе


class Bird:
    def __init__(self, color):
        self.color = color
        self.x = random.randint(0, SCREEN_WIDTH)  # Начальная позиция X
        self.y = -20  # Начальная позиция Y (за верхней границей)
        self.target_pillar = None  # Целевой столб
        self.sit_time = random.randint(60, 180)  # Время сидения на столбе
        self.current_time = 0  # Текущее время сидения
        self.state = STATE_FLYING_IN  # Начальное состояние - летят сверху

    def update(self):

        if self.state == STATE_FLYING_IN:
            self.y += BIRD_SPEED
            if self.y >= 0:
                # Достигли верхней границы, выбираем действие
                self.choose_next_action()
        elif self.state == STATE_FLYING_UP:
            # Летят вверх
            self.y -= BIRD_SPEED
            if self.y < -20:
                # Скрылись за верхней границей, появляются снова сверху
                self.y = -20
                self.choose_next_action()
        elif self.state == STATE_MOVING_TO_PILLAR:
            # Двигаются к столбу
            if self.target_pillar and not self.target_pillar.is_broken:
                #столб существует и не сломан
                dx = self.target_pillar.x - self.x
                dy = self.target_pillar.y - self.y
                distance = (dx**2 + dy**2) ** 0.5
                if distance > BIRD_SPEED:
                    # Двигаются к столбу
                    self.x += dx / distance * BIRD_SPEED
                    self.y += dy / distance * BIRD_SPEED
                else:
                    # Достигли столба, пытаются сесть
                    if self.target_pillar.add_bird():
                        # Успешно сели
                        self.state = STATE_SITTING_ON_PILLAR
                        self.current_time = 0
                    else:
                        # Столб сломан, выбор другого действия
                        self.choose_next_action()
            else:
                # Целевой столб не существует или сломан, выбор другого действия
                self.choose_next_action()
        elif self.state == STATE_SITTING_ON_PILLAR:
            # Сидят на столбе
            if self.target_pillar and not self.target_pillar.is_broken:
                # Столб существует и не сломан
                self.current_time += 1
                if self.current_time >= self.sit_time:
                    # Прошло время сидения, слетаем
                    self.target_pillar.remove_bird()
                    self.choose_next_action()
            else:
                # Столб сломался, выбор другого действия
                self.choose_next_action()
    def choose_next_action(self):
        # Выбор следующего действия для птицы
        if random.random() < 0.1 and self.state != STATE_FLYING_IN:
            # 10% шанс начать лететь вверх, если не в состоянии "летят сверху"
            self.state = STATE_FLYING_UP
        else:
            # Ищу целевой столб
            self.find_target_pillar()
            if self.target_pillar:
                # Если найден целевой столб, двигаюсь к нему
                self.state = STATE_MOVING_TO_PILLAR
            else:
                # Если нет доступных столбов, летим вверх
                self.state = STATE_FLYING_UP

    def find_target_pillar(self):
        # Поиск доступного столба
        valid_pillars = [
            pillar for pillar in world.pillars if not pillar.is_broken
        ]
        if valid_pillars:
            # Если есть доступные столбы, выбираем один случайным образом
            self.target_pillar = random.choice(valid_pillars)
        else:
            # Если нет доступных столбов, сбрасываем целевой столб
            self.target_pillar = None

    def draw(self, screen):
        # Отрисовка птицы на экране
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), 10)


class Pillar:
    def __init__(self, x):
        self.max_birds = random.randint(1, MAX_BIRDS_PER_PILLAR)  # Максимальное количество птиц на столбе
        self.current_load = 0  # Текущее количество птиц на столбе
        self.x = x  # Позиция X столба
        self.y = SCREEN_HEIGHT - random.randint(100, 300)  # Позиция Y столба
        self.is_broken = False  # Столб не сломан
        self.repair_time = REPAIR_TIME  # Время восстановления столба
        self.color = (128, 128, 128)  # Цвет столба

    def add_bird(self):
        # Попытка добавить птицу на столб
        if self.current_load < self.max_birds:
            self.current_load += 1  # Увеличиваем количество птиц
            return True  # Успешно добавили птицу
        else:
            # Если столб переполнен, он ломается
            self.is_broken = True
            self.repair_time = random.randint(REPAIR_TIME, REPAIR_TIME * 3)  # Устанавливаем время восстановления
            return False  # Не удалось добавить птицу

    def remove_bird(self):
        # Удаление птицы со столба
        if self.current_load > 0:
            self.current_load -= 1  # Уменьшаем количество птиц

    def update(self):
        # Обновление состояния столба
        if self.is_broken:
            # Если столб сломан, уменьшаем время восстановления
            self.repair_time -= 1
            if self.repair_time <= 0:
                # Если время восстановления истекло, столб восстанавливается
                self.is_broken = False
                self.current_load = 0  # Сбрасываем количество птиц

    def draw(self, screen):
        # Отрисовка столба на экране
        if not self.is_broken:
            # Если столб не сломан, рисуем его
            pygame.draw.rect(screen, self.color, (self.x, self.y, PILLAR_WIDTH, SCREEN_HEIGHT - self.y))


class World:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))  # Установка размера окна
        self.clock = pygame.time.Clock()  # Создание объекта часов для управления FPS
        self.birds = []
        self.pillars = []
        self.create_objects()

    def create_objects(self):
        # Создание столбов и птиц
        num_pillars = random.randint(MIN_PILLARS, MAX_PILLARS)  # Случайное количество столбов
        x = random.randint(0, SCREEN_WIDTH - (num_pillars * PILLAR_SPACING))  # Начальная позиция X для столбов
        for _ in range(num_pillars):
            self.pillars.append(Pillar(x))  # Добавляем новый столб в список
            x += PILLAR_SPACING  # Увеличиваем позицию X для следующего столба

        for _ in range(NUM_BIRDS):
            self.birds.append(Bird(random.choice(["red", "blue", "green"])))  # Добавляем случайные птицы в список

    def update(self):
        # Обновление состояния всех объектов в мире
        for bird in self.birds:
            bird.update()  # Обновляем каждую птицу
        for pillar in self.pillars:
            pillar.update()  # Обновляем каждый столб

    def draw(self):
        # Отрисовка всех объектов на экране
        self.screen.fill((255, 255, 255))  # фон белым цветом
        for pillar in self.pillars:
            pillar.draw(self.screen)  # Рисуем каждый столб
        for bird in self.birds:
            bird.draw(self.screen)  # Рисуем каждую птицу
        pygame.display.flip()  # Обновляем экран

    def run(self):
        # Основной цикл игры
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False  # Выход из игры при закрытии окна
            self.update()  # Обновление состояния объектов
            self.draw()  # Отрисовывание объектов
            self.clock.tick(60)  # Ограничивание FPS до 60

    def save_to_json(self, filename):
        # Сохраняем состояние игры в JSON файл
        data = {
            "birds": [bird.__dict__ for bird in self.birds],
            "pillars": [pillar.__dict__ for pillar in self.pillars]
        }
        with open(filename, 'w') as f:
            json.dump(data, f)

    def load_from_json(self, filename):
        # Загружаем состояние игры из JSON файла
        with open(filename, 'r') as f:
            data = json.load(f)

        self.birds = []
        self.pillars = []

        for bird_data in data['birds']:
            bird = Bird(bird_data['color'])
            bird.__dict__ = bird_data
            self.birds.append(bird)

        for pillar_data in data['pillars']:
            pillar = Pillar(pillar_data['x'])
            pillar.__dict__ = pillar_data
            self.pillars.append(pillar)

world = World()  # Создание экземпляра мира
world.run()  # Запуск игры

world.save_to_json("game_save.json")  # Сохранение игры
world.load_from_json("game_save.json")  # Загрузка игры