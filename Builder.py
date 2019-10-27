import pygame
import os
import sys
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("map", type=str, nargs="?", default="map.map")
args = parser.parse_args()
map_file = args.map


def load_image(name, color_key=None):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print('Не удаётся загрузить:', name)
        raise SystemExit(message)
    image = image.convert_alpha()
    if color_key is not None:
        if color_key is -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    return image


pygame.init()
screen_size = (650, 650)
screen = pygame.display.set_mode(screen_size)
FPS = 50

tile_images = {
    'wall': load_image('zab2.png'),
    'empty': load_image('grass.png'),
    'apple': load_image('apple2.png'),
    'cow': load_image('cow2.png')
}
player_image = load_image('fer3.png')

tile_width = tile_height = 50


class SpriteGroup(pygame.sprite.Group):

    def __init__(self):
        super().__init__()

    def get_event(self, event):
        for sprite in self:
            sprite.get_event(event)


class Sprite(pygame.sprite.Sprite):

    def __init__(self, group):
        super().__init__(group)
        self.rect = None

    def get_event(self, event):
        pass


class Tile(Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(sprite_group)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)
        self.abs_pos = [self.rect.x, self.rect.y]

    def set_pos(self, x, y):
        self.abs_pos = [x, y]


class Player(Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(hero_group)
        self.image = player_image
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)
        self.pos = (pos_x, pos_y)

    def move(self, x, y):
        camera.dx -= tile_width * (x - self.pos[0])
        camera.dy -= tile_height * (y - self.pos[1])
        self.pos = (x, y)
        for sprite in sprite_group:
            camera.apply(sprite)


class Camera:
    def __init__(self):
        self.dx = 0
        self.dy = 0

    def apply(self, obj):
        obj.rect.x = obj.abs_pos[0] + self.dx
        obj.rect.y = obj.abs_pos[1] + self.dy

    def update(self, target):
        self.dx = 0
        self.dy = 0


class Apples:
    def __init__(self):
        self.count = 0
        self.not_res_count = 0

    def incCount(self):
        self.count += 1
        self.not_res_count += 1

    def reset(self):
        self.count = 0

    def getCount(self):
        return self.count

    def get_not_res_count(self):
        return self.not_res_count

class Cow:
    def __init__(self):
        self.hunger = 0

    def incHunger(self):
        self.hunger += 1

    def decHunger(self, apples):
        self.hunger -= 100*apples
        if self.hunger < 0:
            self.hunger = 0

    def getHunger(self):
        return round(self.hunger/10)

player = None
running = True
clock = pygame.time.Clock()
sprite_group = SpriteGroup()
hero_group = SpriteGroup()


def terminate():
    pygame.quit()
    sys.exit


def start_screen():
    intro_text = ["ГОЛОДНАЯ КОРОВА",
                  "",
                  "Накормите корову яблоками",
                  "За раз фермер может нести не больше 3-ёх яблок",
                  "Если голод корове превысит 100% вы проиграли",
                  "Собирите все яблоки для победы!!"]

    fon = pygame.transform.scale(load_image('fon.jpg'), screen_size)
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('black'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return
        pygame.display.flip()
        clock.tick(FPS)


def end_screen(end_status):
    if end_status == 'looser':
        intro_text = ["Корова проголадалась!", "Вы проиграли!"]
    elif end_status == 'winner':
        intro_text = ["Победа!","Вы накормили корову!"]

    fon = pygame.transform.scale(load_image('fon.jpg'), screen_size)
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('black'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                pygame.quit()
        pygame.display.flip()
        clock.tick(FPS)


def load_level(filename):
    filename = "data/" + filename
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]
    max_width = max(map(len, level_map))
    return list(map(lambda x: list(x.ljust(max_width, '.')), level_map))


def generate_level(level):
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', x, y)
            elif level[y][x] == '#':
                Tile('wall', x, y)
            elif level[y][x] == '!':
                Tile('apple', x, y)
            elif level[y][x] == 'x':
                Tile('cow', x, y)
            elif level[y][x] == '@':
                Tile('empty', x, y)
                new_player = Player(x, y)
                level[y][x] = "."
    return new_player, x, y

def move_coor(y,x):
    status = 0
    if level_map[y][x] == ".":
        hero.move(x, y)
    if level_map[y][x] == "!":
        if apples.getCount() < 3:
            Tile('empty', x, y)
            level_map[y][x] = "."
            status = 1
        hero.move(x, y)
    if level_map[y][x] == "x":
        status = 2
        hero.move(x, y)
    return status

def move(hero, movement):
    x, y = hero.pos
    if movement == "up":
        y = y - 1
    elif movement == "down":
        y = y + 1
    elif movement == "left":
        x = x - 1
    elif movement == "right":
        x = x + 1
    status = move_coor(y, x)
    return status


def checkStatus(status):
    if status == 1:
        apples.incCount()

    if status == 2:
        if apples.getCount() > 0:
            cow.decHunger(apples.getCount())
            apples.reset()


start_screen()
camera = Camera()
apples = Apples()
cow = Cow()
level_map = load_level(map_file)
hero, max_x, max_y = generate_level(level_map)
camera.update(hero)
while running:
    cow.incHunger()
    if cow.getHunger() > 100:
        end_screen('looser')
    elif apples.get_not_res_count() == 11 and apples.getCount() == 0:
        end_screen('winner')
    else:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    tile_status = move(hero, "up")
                    checkStatus(tile_status)
                elif event.key == pygame.K_DOWN:
                    tile_status = move(hero, "down")
                    checkStatus(tile_status)
                elif event.key == pygame.K_LEFT:
                    tile_status = move(hero, "left")
                    checkStatus(tile_status)
                elif event.key == pygame.K_RIGHT:
                    tile_status = move(hero, "right")
                    checkStatus(tile_status)
        screen.fill(pygame.Color("black"))
        sprite_group.draw(screen)
        hero_group.draw(screen)
        intro_text = [
            "Яблок: " + str(apples.getCount()),
            "Корова проголадалась на: " + str(cow.getHunger()) + "%",
        ]
        font = pygame.font.Font(None, 30)
        text_coord = 10
        for line in intro_text:
            string_rendered = font.render(line, 1, pygame.Color('white'))
            intro_rect = string_rendered.get_rect()
            text_coord += 10
            intro_rect.top = text_coord
            intro_rect.x = 10
            text_coord += intro_rect.height
            screen.blit(string_rendered, intro_rect)
        clock.tick(FPS)
        pygame.display.flip()
pygame.quit()
