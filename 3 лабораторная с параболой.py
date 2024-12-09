import random
import pygame
import json

widthscreen = 800
screen_height = 600
min_pillars = 5
max_pillars = 10
max_birds_per_pillar = 15
bird_speed = 0.5
pillar_width = 20
repair_time = 100
pillar_spacing = 30

# Начальные значения для частоты появления птиц и столбов
bspawn = 1260  # Количество кадров до появления новой птицы
pspawn = 960  # Количество кадров до появления нового столба

# Определение состояний
state_flying_in = 0
state_moving_to_pillar = 1
state_sitting_on_pillar = 2
state_flying_up = 3

class Bird:
    def __init__(self, color, widthscreen, screen_height):
        self.color = color
        self.x = random.randint(0, widthscreen)  # Начальная позиция X
        self.y = -20  # Начальная позиция Y (за верхней границей)
        self.target_pillar = None  # Целевой столб
        self.sit_time = random.randint(60, 180)  # Время сидения на столбе
        self.current_time = 0  # Текущее время сидения
        self.state = state_flying_in  # Начальное состояние - летят сверху
        self.flight_duration = random.randint(120, 240)  # Случайная продолжительность полета к столбу
        self.flight_progress = 0  # Прогресс полета
        self.bird_speed = 2  # Скорость птицы
        self.delay = random.randint(20, 200)  # Случайная задержка перед началом полета
        self.delay_counter = 0  # Счетчик задержки
        self.pillar_width = pillar_width
        self.screen_height = screen_height

    def update(self, pillars):
        if self.state == state_flying_in:
            # Увеличиваем счетчик задержки
            self.delay_counter += 1
            if self.delay_counter >= self.delay:
                self.y += self.bird_speed  # Птица начинает лететь вниз
                if self.y >= 0:  # Если птица достигла экрана
                    self.choose_target_pillar(pillars)  # Выбираем, что делать дальше

        elif self.state == state_moving_to_pillar:
            if self.target_pillar:
                self.flight_progress += 1  # отслеживает, сколько времени прошло с начала движения.
                t = self.flight_progress / self.flight_duration  # отношение текущего прогресса полета к общему времени полета

                # Получаем координаты целевого столба
                target_x = self.target_pillar.x + self.pillar_width // 2
                target_y = self.target_pillar.y

                # Находим начальные координаты
                start_x = self.x
                start_y = self.y

                # Параболическая траектория с высотой
                height_offset = 30 * (1 - t)  # максимальная высота параболы
                self.y = start_y + (target_y - start_y) * t - height_offset * (0.5 - t)  # линейная интерполяция между начальной и целевой позицией, с учетом уменьшенного вертикального отклонения

                # Плавное движение к цели по оси X
                self.x += (target_x - start_x) * 0.15  # множитель для плавности

                # Проверка на приземление
                if self.flight_progress >= self.flight_duration:
                    if self.target_pillar.add_bird():
                        self.state = state_sitting_on_pillar
                        self.current_time = 0  # Сбрасываем прогресс сидения
                    else:
                        self.state = state_flying_in  # Если столб сломан, птица снова летит

        elif self.state == state_sitting_on_pillar:
            self.current_time += 1
            if self.current_time >= self.sit_time:  # Птица сидит на столбе
                # Решаем, что делать дальше: перелететь на другой столб или улететь
                if random.choice([True, False]):  # 50% шансов
                    self.choose_target_pillar(pillars)  # Перелет на другой столб
                else:
                    self.state = state_flying_up  # Улететь вверх
        #ограничения по границам экрана
        elif self.state == state_flying_up:
            self.y -= self.bird_speed
            if self.y < 0:
                self.state = state_flying_in
                self.y = -20
                self.choose_target_pillar(pillars)
        if self.x < 0:
            self.x = 0
        elif self.x > widthscreen:
            self.x = widthscreen
        # Ограничение по верхней границе экрана
        if self.y < 0:
            self.y = 0

    def choose_target_pillar(self, pillars):
        valid_pillars = [pillar for pillar in pillars if not pillar.is_broken]
        if valid_pillars:
            self.target_pillar = random.choice(valid_pillars)
            self.state = state_moving_to_pillar
            self.flight_progress = 0  # Сбрасываем прогресс полета

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), 10)

class Pillar:
    def __init__(self, x, max_birds):
        self.max_birds = max_birds
        self.current_load = 0
        self.height = random.randint(100, 300)
        self.x = x
        self.y = screen_height - self.height
        self.is_broken = False
        self.repair_time = repair_time
        self.color = (128, 128, 128)
        self.rect = pygame.Rect(self.x, self.y, pillar_width, self.height)

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

    def update(self):
        if self.is_broken:
            self.repair_time -= 1
            if self.repair_time <= 0:
                self.is_broken = False

    def check_if_broken(self):
        if self.current_load > self.max_birds:
            self.is_broken = True  # Столб разрушен, если на нем больше птиц, чем он может выдержать
            self.repair_time = random.randint(repair_time, repair_time * 3)

    def draw(self, screen):
        if not self.is_broken:
            self.rect = pygame.Rect(self.x, self.y, pillar_width, self.height)
            pygame.draw.rect(screen, self.color, self.rect)

class SpinBox:
    def __init__(self, x, y, min_value, max_value, initial_value, update_function=None, pillars=None, is_global=False):
        self.rect = pygame.Rect(x, y, 80, 30)
        self.min_value = min_value
        self.max_value = max_value
        self.value = initial_value
        self.increase_button = pygame.Rect(x + 90, y, 20, 15)
        self.decrease_button = pygame.Rect(x + 90, y + 15, 20, 15)
        self.update_function = update_function
        self.pillars = pillars
        self.is_global = is_global

    def draw(self, screen):
        pygame.draw.rect(screen, (0, 0, 0), self.rect, 2)
        font = pygame.font.Font(None, 24)
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
                            self.update_function()
                elif self.decrease_button.collidepoint(event.pos):
                    if self.value > self.min_value:
                        self.value -= 1
                        if self.update_function:
                            self.update_function()

    def update_bird_spawn_rate(self, world):
        global bspawn
        bspawn = 1260 - 60 * self.value

    def update_pillar_spawn_rate(self, world):
        global pspawn
        pspawn = 960 - self.value * 60

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
        self.paused = False  # Флаг для паузы

    def create_objects(self):
        num_pillars = random.randint(min_pillars, max_pillars)
        for _ in range(num_pillars):
            while True:
                new_x = random.randint(0, widthscreen - pillar_width)
                if not self.pillars or all(abs(new_x - pillar.x) > pillar_spacing for pillar in self.pillars):
                    pillar = Pillar(new_x, max_birds_per_pillar)
                    self.pillars.append(pillar)
                    break
        for _ in range(random.randint(5, 15)):
            self.birds.append(Bird(random.choice(["red", "blue", "green"]), widthscreen, screen_height))

    def update(self):
        if not self.paused:  # Обновляем только если не на паузе
            for bird in self.birds:
                bird.update(self.pillars)
            for pillar in self.pillars:
                pillar.update()

            self.bird_spawn_timer += 1
            self.pillar_spawn_timer += 1

            if self.bird_spawn_timer >= bspawn:
                if random.random() < 0.5:  # 50% шанс на появление
                    self.birds.append(Bird(random.choice(["red", "blue", "green"]), widthscreen, screen_height))
                self.bird_spawn_timer = 0

            if self.pillar_spawn_timer >= pspawn:
                while True:
                    new_x = random.randint(0, widthscreen - pillar_width)
                    if not self.pillars or all(abs(new_x - pillar.x) > pillar_spacing for pillar in self.pillars):
                        self.pillars.append(Pillar(new_x, max_birds_per_pillar))
                        break
                self.pillar_spawn_timer = 0

    def update_strength(self, change):
        if self.selected_pillar:
            new_value = self.selected_pillar.max_birds + change
            if 1 <= new_value <= 20:
                self.selected_pillar.max_birds = new_value
                self.selected_pillar.check_if_broken()

    def draw(self):
        self.screen.fill((255, 255, 255))
        for pillar in self.pillars:
            pillar.draw(self.screen)
        for bird in self.birds:
            bird.draw(self.screen)
        bird_spawn_spin_box.draw(self.screen)
        pillar_spawn_spin_box.draw(self.screen)
        self.draw_labels()
        pygame.display.flip()

    def draw_labels(self):
        font = pygame.font.Font(None, 24)
        labels = ["Птицы", "Столбы"]
        positions = [(150, 20), (300, 20)]
        for label, pos in zip(labels, positions):
            label_surface = font.render(label, True, (0, 0, 0))
            self.screen.blit(label_surface, pos)

    def save_game(self, filename):
        game_state = {
            'birds': [{'color': bird.color, 'x': bird.x, 'y': bird.y, 'state': bird.state} for bird in self.birds],
            'pillars': [{'x': pillar.x, 'max_birds': pillar.max_birds, 'current_load': pillar.current_load,
                         'is_broken': pillar.is_broken} for pillar in self.pillars],
            'bspawn': bspawn,
            'pspawn': pspawn,
            'paused': self.paused
        }
        with open(filename, 'w') as f:
            json.dump(game_state, f)

    def load_game(self, filename):
        with open(filename, 'r') as f:
            game_state = json.load(f)
            self.birds = [Bird(bird['color'], widthscreen, screen_height) for bird in game_state['birds']]
            for bird, state in zip(self.birds, game_state['birds']):
                bird.x = state['x']
                bird.y = state['y']
                bird.state = state['state']
            self.pillars = [Pillar(pillar['x'], pillar['max_birds']) for pillar in game_state['pillars']]
            for pillar, state in zip(self.pillars, game_state['pillars']):
                pillar.current_load = state['current_load']
                pillar.is_broken = state['is_broken']
            global bspawn, pspawn
            bspawn = game_state['bspawn']
            pspawn = game_state['pspawn']
            self.paused = game_state['paused']

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if event.button == 1 and mouse_pos[1] > screen_height / 2:
                        for pillar in self.pillars:
                            if pillar.rect.collidepoint(mouse_pos):
                                if pillar.is_broken:
                                    pillar.is_broken = False
                                    pillar.repair_time = repair_time
                                else:
                                    self.selected_pillar = pillar  # Запоминаем выбранный столб
                                break
                        else:
                            while True:
                                new_x = random.randint(0, widthscreen - pillar_width)
                                if not self.pillars or all(abs(new_x - pillar.x) > pillar_spacing for pillar in self.pillars):
                                    self.pillars.append(Pillar(new_x, max_birds_per_pillar))
                                    break

                    elif event.button == 3 and mouse_pos[1] > screen_height / 2:
                        for pillar in self.pillars:
                            if pillar.rect.collidepoint(mouse_pos):
                                pillar.is_broken = True
                                pillar.repair_time = random.randint(repair_time, repair_time * 3)
                                break

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_s:  # Сохранение игры при нажатии 'S'
                        self.save_game('savefile.json')
                    elif event.key == pygame.K_l:  # Загрузка игры при нажатии 'L'
                        self.load_game('savefile.json')
                    elif event.key == pygame.K_SPACE:  # Пауза при нажатии пробела
                        self.paused = not self.paused
                    elif event.key == pygame.K_UP:  # Увеличение прочности
                        self.update_strength(1)
                    elif event.key == pygame.K_DOWN:  # Уменьшение прочности
                        self.update_strength(-1)
                    if event.key == pygame.K_KP_PLUS:
                        new_bird = Bird(random.choice(["red", "blue", "green"]), widthscreen, screen_height)
                        self.birds.append(new_bird)

                bird_spawn_spin_box.handle_event(event)
                pillar_spawn_spin_box.handle_event(event)

            self.update()
            self.draw()
            self.clock.tick(60)

bird_spawn_spin_box = SpinBox(150, 40, 1, 20, 1, update_function=None)
pillar_spawn_spin_box = SpinBox(300, 40, 1, 15, 1, update_function=None)

bird_spawn_spin_box.update_function = lambda: bird_spawn_spin_box.update_bird_spawn_rate(world)
pillar_spawn_spin_box.update_function = lambda: pillar_spawn_spin_box.update_pillar_spawn_rate(world)

# Инициализация игры
world = World()
world.run()