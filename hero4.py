import pygame
import sys
import os

FPS = 50


def terminate():
    pygame.quit()
    sys.exit()


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


def load_level(filename):
    try:
        filename = os.path.join("data", filename)
        with open(filename, 'r') as mapFile:
            level_map = [line.strip() for line in mapFile]

        max_width = max(len(line) for line in level_map)
        return [line.ljust(max_width, '.') for line in level_map]
    except Exception:
        print(f"Файл '{filename}' не найден")
        sys.exit()


pygame.init()

level_name = input('Введите название уровня (map1.txt, map2.txt и тд...): ')
level = load_level(level_name)
max_width = len(level[0])
max_height = len(level)
tile_size = 50
WIDTH, HEIGHT = 550, 550

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Игра")
clock = pygame.time.Clock()


def start_screen():
    intro_text = ["Hero4", "",
                  'project created', 'by @st0rmeed']
    fon = pygame.transform.scale(load_image('fon.jpg'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        text = font.render(line, True, pygame.Color('black'))
        text_rect = text.get_rect()
        text_coord += 10
        text_rect.top = text_coord
        text_rect.x = 10
        text_coord += text_rect.height
        screen.blit(text, text_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                return
        pygame.display.flip()
        clock.tick(FPS)


tile_images = {
    'wall': load_image('box.png'),
    'empty': load_image('grass.png')
}
player_image = load_image('mario.png')


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.world_x = pos_x * tile_size
        self.world_y = pos_y * tile_size
        self.rect = self.image.get_rect(topleft=(self.world_x, self.world_y))


class Camera:
    def __init__(self):
        self.dx = 0
        self.dy = 0

        self.offset_x = WIDTH // 2
        self.offset_y = HEIGHT // 2

    def apply(self, obj):
        obj.rect.x = (obj.world_x + self.dx) % (max_width * tile_size)
        obj.rect.y = (obj.world_y + self.dy) % (max_height * tile_size)

    def update(self, target):
        self.dx = self.offset_x - target.world_x
        self.dy = self.offset_y - target.world_y


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = player_image

        if self.image.get_width() > tile_size or self.image.get_height() > tile_size:
            self.image = pygame.transform.scale(
                self.image,
                (tile_size - 10, tile_size - 10)
            )

        self.offset_x = -12.5
        self.offset_y = -20

        self.pos_x = pos_x
        self.pos_y = pos_y
        self.world_x = (pos_x * tile_size) + (tile_size // 2) + self.offset_x
        self.world_y = (pos_y * tile_size) + (tile_size // 2) + self.offset_y
        self.rect = self.image.get_rect(center=(self.world_x, self.world_y))

    def update_rect(self):
        self.world_x = (self.pos_x * tile_size) + (tile_size // 2) + self.offset_x
        self.world_y = (self.pos_y * tile_size) + (tile_size // 2) + self.offset_y
        self.rect.center = (self.world_x, self.world_y)

    def move(self, dx, dy):
        new_x = (self.pos_x + dx) % max_width
        new_y = (self.pos_y + dy) % max_height

        if level[new_y][new_x] != '#':
            self.pos_x = new_x
            self.pos_y = new_y
            self.update_rect()


all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()


def generate_level(level):
    new_player = None
    for y in range(len(level)):
        for x in range(len(level[y])):
            cell = level[y][x]
            if cell == '.':
                Tile('empty', x, y)
            elif cell == '#':
                Tile('wall', x, y)
            elif cell == '@':
                Tile('empty', x, y)
                new_player = Player(x, y)
                level[y] = level[y][:x] + '.' + level[y][x + 1:]
    return new_player, max_width, max_height


player, level_x, level_y = generate_level(level)

start_screen()

camera = Camera()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN):
                dx, dy = 0, 0
                if event.key == pygame.K_LEFT:
                    dx = -1
                elif event.key == pygame.K_RIGHT:
                    dx = 1
                elif event.key == pygame.K_UP:
                    dy = -1
                elif event.key == pygame.K_DOWN:
                    dy = 1

                new_x = (player.pos_x + dx) % max_width
                new_y = (player.pos_y + dy) % max_height

                if level[new_y][new_x] != '#':
                    player.pos_x = new_x
                    player.pos_y = new_y
                    player.update_rect()

    camera.update(player)
    for sprite in all_sprites:
        camera.apply(sprite)

    screen.fill((0, 0, 0))
    tiles_group.draw(screen)
    player_group.draw(screen)
    pygame.display.flip()
    clock.tick(FPS)

terminate()
