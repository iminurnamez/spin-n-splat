from math import degrees, pi
from random import randint, choice
import os

import pygame as pg

from .. import tools, prepare
from ..components.angles import get_angle, get_distance, project
from ..components.labels import Button, ButtonGroup


class Palette(pg.sprite.Sprite):
    def __init__(self):
        colors = ["dodgerblue", "darkcyan", "royalblue1", "orchid3", "seagreen", "darkslategray3",
                      "plum2", "lightseagreen", "steelblue", "seagreen3", "mediumpurple3", 
                      "palegreen1", "orchid", "springgreen3", "skyblue2"]
        self.colors = [pg.Color(color) for color in colors]
        self.make_image()
        self.color = "rainbow"
        
    def make_image(self):
        self.topleft = (5, 650)
        rainbow = pg.Surface((16, 16))
        surf = pg.Surface((84, 84))
        surf.fill(pg.Color("white"))
        top = 4
        left = 4
        rainbow_left = 0
        rainbow_top = 0
        last = self.colors[-1]
        self.color_rects = []
        for i, c in enumerate(self.colors):
            if i and not i % 4:
                top += 20
                left = 4
                rainbow_left = 0
                rainbow_top += 4
            rect = pg.Rect(left, top, 16, 16)
            pg.draw.rect(surf, c, rect)
            self.color_rects.append((rect.move(self.topleft), c))
            pg.draw.rect(rainbow, c, (rainbow_left, rainbow_top, 4, 4))
            if c == last:
                left += 20
                surf.blit(rainbow, (left, top))
                r_rect = pg.Rect(left, top, 16, 16)
                self.color_rects.append((r_rect.move(self.topleft), "rainbow"))
            left += 20
            rainbow_left += 4
        self.idle_image = surf.copy()
        self.idle_image.set_alpha(150)
        self.hover_image = surf
        self.rect = self.hover_image.get_rect(topleft=self.topleft)
    
    def get_event(self, event):
        if event.type == pg.MOUSEBUTTONUP:
            for rect, color in self.color_rects:
                if rect.collidepoint(event.pos):
                    self.color = color

    def update(self, mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            self.image = self.hover_image
        else:
            self.image = self.idle_image
            
    def draw(self, surface):
        surface.blit(self.image, self.rect)
        
        
class Canvas(object):
    def __init__(self):
        self.img_size = (700, 700)
        self.surf_size = (500, 500)
        self.img_center = self.img_size[0] // 2, self.img_size[1] // 2
        self.surf = pg.Surface(self.img_size)
        half = (self.img_size[0] - self.surf_size[0]) // 2
        self.surf.fill(pg.Color("white"), ((half, half), self.surf_size))
        #self.surf.set_colorkey(pg.Color("white"))
        self.rect = self.surf.get_rect(center=prepare.SCREEN_RECT.center)
        self.cover = pg.Surface(self.img_size)
        self.cover.fill(pg.Color("black"))
        self.cover.set_colorkey(pg.Color("purple"))
        cover_rect = pg.Rect((0, 0), self.surf_size)
        cover_rect.center = self.surf.get_rect().center
        pg.draw.rect(self.cover, pg.Color("purple"), cover_rect)
        self.surf.blit(self.cover, (0, 0))
        
        self.rot_angle = 0
        self.rotation_speed = .01
        self.speed_timer = 0
        self.drawing = False
        
        self.palette = Palette()
        
        self.image_num = 0
        
        self.splatters = {
                "small": ((2, 6), (-4, 4), (1, 3)),
                "medium": ((2, 6), (-8, 8), (2, 4)),
                "large": ((3, 6), (-12, 12), (2, 6))}
        self.splatter_size = "medium"
        self.make_buttons()
        self.speeding_up = False
        self.slowing_down =False
        
    def make_buttons(self):    
        self.buttons = ButtonGroup()
        names = ("small", "medium", "large")
        spots = ((5, 622), (25, 620), (60, 610))
        for name, spot in zip(names, spots):
            hover = prepare.GFX["splat-{}".format(name)]
            idle = hover.copy()
            idle.set_alpha(150)
            size = hover.get_size()
            Button(spot, self.buttons, button_size=size, idle_image=idle, hover_image=hover,
                       call=self.change_brush, args=name)
                       
    def change_brush(self, size):
        self.splatter_size = size
        
    def speed_up(self):
        if not self.speeding_up:
            self.speeding_up = True
            self.rotation_speed += .0005
            self.speed_timer = 0
        
    def slow_down(self):
        if not self.slowing_down:
            self.slowing_down = True
            self.rotation_speed -= .0005
            self.speed_timer = 0
            
    def get_event(self, event):
        self.buttons.get_event(event)
        if event.type == pg.MOUSEBUTTONDOWN:
            self.drawing = True 
        elif event.type == pg.MOUSEBUTTONUP:
            self.drawing = False
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_UP:
                self.speed_up()
            elif event.key == pg.K_DOWN:
                self.slow_down()
        elif event.type == pg.KEYUP:
            self.speeding_up = self.slowing_down = False
            self.speed_timer = 0
            if event.key == pg.K_SPACE:
                self.save_image()
    
    def save_image(self):
        left = (self.img_size[0] - self.surf_size[0]) // 2
        top = (self.img_size[1] - self.surf_size[1]) // 2
        rect = pg.Rect((left, top), self.surf_size)
        img = self.surf.subsurface(rect)
        img_name = "image{}.png".format(self.image_num)
        p = os.path.join("saved", img_name)
        pg.image.save(img, p)
        self.image_num += 1
    
    def splatter(self, pos):        
        num_splatters = self.splatters[self.splatter_size][0]
        offset_range = self.splatters[self.splatter_size][1]
        radius_range = self.splatters[self.splatter_size][2]
        for _ in range(randint(*num_splatters)):
            x_offset = randint(*offset_range)
            y_offset = randint(*offset_range)
            adj_pos = pos[0] + x_offset, pos[1] + y_offset
            if self.palette.color == "rainbow":
                color = choice(self.palette.colors)
            else:
                color = self.palette.color
            radius = randint(*radius_range)
            pg.draw.circle(self.surf, color, adj_pos, radius)
            
    def update(self, dt, mouse_pos):
        self.speed_timer += dt
        if self.speed_timer >= 500:
            if self.speeding_up:
                self.rotation_speed += .001
                self.speed_timer -= 500
            elif self.slowing_down:
                self.rotation_speed -= .001
                self.speed_timer -= 500
        
        self.rot_angle += self.rotation_speed * dt
        self.rot_angle = self.rot_angle % (2 * pi)
        if self.drawing:
            angle = get_angle(prepare.SCREEN_RECT.center, mouse_pos)
            dist = get_distance(prepare.SCREEN_RECT.center, mouse_pos)
            adj_angle = (angle - self.rot_angle) % (2 * pi)
            pos_ = project(self.img_center, adj_angle, dist)
            pos = int(pos_[0]), int(pos_[1])
            self.splatter(pos)
            self.surf.blit(self.cover, (0, 0))
        self.image = pg.transform.rotate(self.surf, degrees(self.rot_angle))
        self.rect = self.image.get_rect(center=self.rect.center)   
        self.palette.update(mouse_pos) 
        self.buttons.update(mouse_pos)        
            
    def draw(self, surface):
        surface.blit(self.image, self.rect)
        self.palette.draw(surface)
        self.buttons.draw(surface)
        

class Drawing(tools._State):
    def __init__(self):
        super(Drawing, self).__init__()
        self.canvas = Canvas()

    def startup(self, persistent):
        self.persist = persistent
        
    def get_event(self, event):
        if event.type == pg.QUIT:
            self.quit = True
        elif event.type == pg.KEYUP:
            if event.key == pg.K_ESCAPE:
                self.quit = True            
        self.canvas.palette.get_event(event)
        self.canvas.get_event(event)
            
    def update(self, dt):
        mouse_pos = pg.mouse.get_pos()
        self.canvas.update(dt, mouse_pos)
        
    def draw(self, surface):
        surface.fill(pg.Color("black"))
        self.canvas.draw(surface)

        