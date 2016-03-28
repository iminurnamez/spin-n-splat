import os
import pygame as pg
from . import tools


SCREEN_SIZE = (1080, 740)
ORIGINAL_CAPTION = "Spin 'n Splat"

pg.init()
os.environ['SDL_VIDEO_CENTERED'] = "TRUE"
pg.display.set_caption(ORIGINAL_CAPTION)
SCREEN = pg.display.set_mode(SCREEN_SIZE)
SCREEN_RECT = SCREEN.get_rect()


GFX   = tools.load_all_gfx(os.path.join("resources", "graphics"))
