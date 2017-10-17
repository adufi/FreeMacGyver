import os
import sys
import pygame
import random

from pygame.locals import *

WINDOW_SIZE = (600, 600)

BOARD_WIDTH = 15
BOARD_LENGTH = 15

SPRITE_SIZE = (40, 40)

COLOR_GRAY = (128, 128, 128)
COLOR_WHITE = (255, 255, 255)

OVER = False
tiles = []
EVENTS = None

"""
    Utils
"""


def load_image(file):
    try:
        surface = pygame.image.load(file)
    except pygame.error:
        str = 'Could not load image "%s" %s'
        raise SystemExit(str % (file, pygame.get_error()))
    return surface.convert()


def load_images(*files):
    surfaces = []
    for file in files:
        surfaces.append(load_image(file))
    return surfaces


def posToIndex(x, y):
    return (y * BOARD_WIDTH) + x


def indexToPos(i):
    return [(i % BOARD_WIDTH), int(i / BOARD_WIDTH)]


def posToOffset(pos):
    return [pos[0] * SPRITE_SIZE[0], pos[1] * SPRITE_SIZE[0]]

"""
    Sprites
"""


class WallSprite(pygame.sprite.Sprite):
    at = []
    images = []

    """docstring for WallSprite"""
    def __init__(self):
        super(WallSprite, self).__init__()

        self.image = pygame.Surface(SPRITE_SIZE)
        self.image.blit(self.images[0], (0, 0), (self.at[0], SPRITE_SIZE))

        self.rect = self.image.get_rect()


class GuardianSprite(pygame.sprite.Sprite):
    images = []

    """docstring for GuardianSprite"""
    def __init__(self):
        super(GuardianSprite, self).__init__()

        self.image = self.images[0]
        self.image.set_colorkey(COLOR_GRAY)
        self.image = pygame.transform.scale(self.image, SPRITE_SIZE)

        self.rect = self.image.get_rect()


class MacGyverSprite(pygame.sprite.Sprite):
    index = 0
    images = []
    objects = 0

    """docstring for MacGyverSprite"""
    def __init__(self):
        super(MacGyverSprite, self).__init__()

        self.image = self.images[0]
        self.image.set_colorkey(COLOR_GRAY)
        self.image = pygame.transform.scale(self.image, SPRITE_SIZE)

        self.rect = self.image.get_rect()

    def update(self):
        step = 0
        key_event = False

        for event in EVENTS:

            if event.type == pygame.KEYUP:

                if event.key == pygame.K_LEFT:
                    step = -1

                    if self.index % BOARD_WIDTH != 0:
                        key_event = True

                elif event.key == pygame.K_RIGHT:
                    step = 1

                    if (self.index + 1) % BOARD_WIDTH != 0:
                        key_event = True

                elif event.key == pygame.K_UP:
                    step = -BOARD_LENGTH

                    if self.index + step > -1:
                        key_event = True

                elif event.key == pygame.K_DOWN:
                    step = BOARD_LENGTH

                    if self.index + step < BOARD_WIDTH * BOARD_LENGTH:
                        key_event = True

        if key_event:

            if tiles[self.index + step] != 'X':

                if tiles[self.index + step] == 'C':
                    self.objects += 1
                    print ('object collected')

                elif tiles[self.index + step] == 'G':
                    global OVER
                    OVER = True

                    if self.objects == 3:
                        print ('Victoire, Felicitation vous avez gagnez')

                    else:
                        print ('Dommage vous avez perdu')

                self.updateRender(step)

    def updateRender(self, step):
        off = posToOffset(indexToPos(self.index + step))
        self.rect.x = off[0]
        self.rect.y = off[1]

        tiles[self.index] = 'O'
        tiles[self.index + step] = 'M'
        self.index += step


class ObjectSprite(pygame.sprite.Sprite):
    at = []
    sizes = []
    images = []

    index = 0

    """docstring for ObjectSprite"""
    def __init__(self, i):
        super(ObjectSprite, self).__init__()

        self.image = pygame.Surface(self.sizes[i])
        self.image.blit(self.images[i], (0, 0), (self.at[i], self.sizes[i]))
        self.image = pygame.transform.scale(self.image, SPRITE_SIZE)
        self.image.set_colorkey(COLOR_GRAY)

        self.rect = self.image.get_rect()

    def update(self):
        if tiles[self.index] == 'M':
            print ('object kill')
            self.kill()

"""
    Main
"""


def loadScene():
    directory = os.listdir('levels')

    files = []
    for file in directory:
        if ".fmg" in file:
            files.append(file)

        if len(files) == 0:
            print ('Error no .fmg file(s)')
            return False

    # DEBUG
    # print ('Files in dir: ', files)

    # Load a random lvl
    rand = random.randint(0, len(files) - 1)

    # Get file
    f = open('levels/' + files[rand], 'r')

    fw = ''
    for line in f.readlines():
        fw += line.split('\n')[0]

    # DEBUG
    # print ('number of words: ', len(fw))

    # Test file integrity
    if len(fw) != (BOARD_WIDTH * BOARD_LENGTH):
        print ('Error file too short')

    if 'M' not in fw and 'G' not in fw:
        print ('Error no MacGyver or Guardian in file')

    return fw


def buildScene(scene):
    sprites = pygame.sprite.Group()
    for i in range(len(scene)):
        tiles.append(scene[i])

        sprite = pygame.sprite.Sprite

        isSprite = True
        if scene[i] == 'X':
            sprite = WallSprite()

        elif scene[i] == 'M':
            sprite = MacGyverSprite()
            sprite.index = i

        elif scene[i] == 'G':
            sprite = GuardianSprite()

        elif scene[i] == 'O':
            isSprite = False

        else:
            return False

        if isSprite:
            off = posToOffset(indexToPos(i))
            sprite.rect.x = off[0]
            sprite.rect.y = off[1]

            sprites.add(sprite)

    for i in range(3):
        ok = False
        while not ok:
            rand = random.randint(0, (BOARD_WIDTH * BOARD_LENGTH) - 1)
            if tiles[rand] == 'O':
                # print ('rand -', rand)

                sprite = ObjectSprite(i)
                sprite.index = rand

                off = posToOffset(indexToPos(rand))
                sprite.rect.x = off[0]
                sprite.rect.y = off[1]

                sprites.add(sprite)

                tiles[rand] = 'C'
                ok = True
    """
    for i in range(3):
        sprite = ObjectSprite(i)
        sprite.index = i + 1

        off = posToOffset(indexToPos(i + 1))
        sprite.rect.x = off[0]
        sprite.rect.y = off[1]

        sprites.add(sprite)

        tiles[i + 1] = 'C'
        ok = True
    """
    # DEBUG
    # print (tiles)

    return (tiles, sprites)


def main():
    # Initialization
    pygame.init()

    # create window
    screen = pygame.display.set_mode(WINDOW_SIZE)
    pygame.display.set_caption('Free MacGyver')

    # background
    background = pygame.Surface(WINDOW_SIZE)
    background.fill(COLOR_WHITE)
    screen.blit(background, (0, 0))

    # sprites
    WallSprite.at = [(244, 8)]
    WallSprite.images = [load_image('assets/tc-image005.jpg')]

    GuardianSprite.images = [load_image('assets/guardian.png')]
    MacGyverSprite.images = [load_image('assets/macgyver.png')]

    ObjectSprite.at = [(872, 0), (2024, 0), (164, 0)]
    ObjectSprite.sizes = [(17, 32), (17, 32), (24, 32)]
    ObjectSprite.images.append(load_image('assets/equipment-32x32.png'))
    ObjectSprite.images.append(load_image('assets/equipment-32x32.png'))
    ObjectSprite.images.append(load_image('assets/extras-32x-32.png'))

    # load the file scene
    scene = loadScene()
    if not scene:
        return False

    # load and prepare sprites
    (tiles, all) = buildScene(scene)
    if not all:
        print ('buildScene return False')
        return False

    global OVER
    global EVENTS

    isAlive = True
    clock = pygame.time.Clock()
    while isAlive:
        OVER = False
        # Events
        EVENTS = pygame.event.get()
        for event in EVENTS:
            if event.type == pygame.QUIT:
                isAlive = False

            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_ESCAPE:
                    isAlive = False

        # Logic
        all.update()

        if OVER:
            isAlive = False

        # Render
        all.clear(screen, background)

        all.draw(screen)

        pygame.display.flip()

        clock.tick(60)

    # destruction
    pygame.quit()

if __name__ == '__main__':
    main()
