# encoding: utf-8
"""

                   GNU GENERAL PUBLIC LICENSE

                       Version 3, 29 June 2007


 Copyright (C) 2007 Free Software Foundation, Inc. <http://fsf.org/>

 Everyone is permitted to copy and distribute verbatim copies

 of this license document, but changing it is not allowed.
 """

# background image Designed by kjpargeter modified by me
from random import uniform, randint

import numpy
from math import atan2, degrees

__author__ = "Yoann Berenguer"
__copyright__ = "Copyright 2007, Cobra Project"
__credits__ = ["Yoann Berenguer"]
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Yoann Berenguer"
__email__ = "yoyoberenguer@hotmail.com"

import pygame
from pygame import gfxdraw


def wavelength_to_rgb(wavelength, gamma=0.8):

    """
    :param wavelength: wavelength of light in nanometer
    :param gamma: default gamma = 0.8
    :return: return RGB color

    == A few notes about color ==

    Color   Wavelength(nm) Frequency(THz)
    Red     620-750        484-400
    Orange  590-620        508-484
    Yellow  570-590        526-508
    Green   495-570        606-526
    Blue    450-495        668-606
    Violet  380-450        789-668

    f is frequency (cycles per second)
    l (lambda) is wavelength (meters per cycle)
    e is energy (Joules)
    h (Plank's constant) = 6.6260695729 x 10^-34 Joule*seconds
                         = 6.6260695729 x 10^-34 m^2*kg/seconds
    c = 299792458 meters per second
    f = c/l
    l = c/f
    e = h*f
    e = c*h/l

    List of peak frequency responses for each type of
    photoreceptor cell in the human eye:
        S cone: 437 nm
        M cone: 533 nm
        L cone: 564 nm
        rod:    550 nm in bright daylight, 498 nm when dark adapted.
                Rods adapt to low light conditions by becoming more sensitive.
                Peak frequency response shifts to 498 nm.

    This converts a given wavelength of light to an
    approximate RGB color value. The wavelength must be given
    in nanometers in the range from 380 nm through 750 nm
    (789 THz through 400 THz).

    Based on code by Dan Bruton
    http://www.physics.sfasu.edu/astro/color/spectra.html
    """

    wavelength = float(wavelength)
    if 380 <= wavelength <= 440:
        attenuation = 0.3 + 0.7 * (wavelength - 380) / (440 - 380)
        R = ((-(wavelength - 440) / (440 - 380)) * attenuation) ** gamma
        G = 0.0
        B = (1.0 * attenuation) ** gamma
    elif 440 <= wavelength <= 490:
        R = 0.0
        G = ((wavelength - 440) / (490 - 440)) ** gamma
        B = 1.0
    elif 490 <= wavelength <= 510:
        R = 0.0
        G = 1.0
        B = (-(wavelength - 510) / (510 - 490)) ** gamma
    elif 510 <= wavelength <= 580:
        R = ((wavelength - 510) / (580 - 510)) ** gamma
        G = 1.0
        B = 0.0
    elif 580 <= wavelength <= 645:
        R = 1.0
        G = (-(wavelength - 645) / (645 - 580)) ** gamma
        B = 0.0
    elif 645 <= wavelength <= 750:
        attenuation = 0.3 + 0.7 * (750 - wavelength) / (750 - 645)
        R = (1.0 * attenuation) ** gamma
        G = 0.0
        B = 0.0
    else:
        R = 0.0
        G = 0.0
        B = 0.0
    R *= 255
    G *= 255
    B *= 255
    return int(R), int(G), int(B), 22


class LayeredUpdatesModified(pygame.sprite.LayeredUpdates):

    def __init__(self):
        pygame.sprite.LayeredUpdates.__init__(self)

    def draw(self, surface_):
        """draw all sprites in the right order onto the passed surface

        LayeredUpdates.draw(surface): return Rect_list

        """
        spritedict = self.spritedict
        surface_blit = surface_.blit
        dirty = self.lostsprites
        self.lostsprites = []
        dirty_append = dirty.append
        init_rect = self._init_rect
        for spr in self.sprites():
            rec = spritedict[spr]

            if hasattr(spr, '_blend') and spr._blend is not None:
                newrect = surface_blit(spr.image, spr.rect, special_flags=spr._blend)
            else:
                newrect = surface_blit(spr.image, spr.rect)

            if rec is init_rect:
                dirty_append(newrect)
            else:
                if newrect.colliderect(rec):
                    dirty_append(newrect.union(rec))
                else:
                    dirty_append(newrect)
                    dirty_append(rec)
            spritedict[spr] = newrect
        return dirty


class LensFlareEffect(pygame.sprite.Sprite):

    images = None       # Sprite
    containers = None   # pygame.Group
    vector = None       # Lens Vector (origin : sprite center)
    _a = 10             # Octagon parameter
    _b = 30             # Octagon parameter
    _centerx, _centery = (50, 50)   # Octagon's center
    # Octagon sides (Octagon second flares)
    list_ = numpy.array([[_centerx - _a, _centery - _b],
                         [_centerx + _a, _centery - _b],
                         [_centerx + _b, _centery - _a],
                         [_centerx + _b, _centery + _a],
                         [_centerx + _a, _centery + _b],
                         [_centerx - _a, _centery + _b],
                         [_centerx - _b, _centery + _a],
                         [_centerx - _b, _centery - _a]])
    FLARE_POSITION = None   # Sprite center (Bright star center)
    SECOND_FLARES = []      # list all second flares (list of octagon and lights)
    star_burst4x = None     # pygame.Surface (star sprite x4)
    star_burst = None       # pygame.Surface (star sprite)
    CHILD = []              # list all child instance(s)

    def __init__(self,
                 alpha_,                        # vector fraction (scale_to_length, determine the sprite position along
                                                # the lens vector)
                 gl_,                           # global variable
                 timing_=15,                    # Refreshing time
                 layer_=0,                      # Layer to use
                 blend_= pygame.BLEND_RGB_ADD,   # Blend additive mode
                 event_='CHILD',                # define parent or child class
                 delete_=False
                 ):
        pygame.sprite.Sprite.__init__(self, LensFlareEffect.containers)
        if isinstance(gl_.All, pygame.sprite.LayeredUpdates):
            gl_.All.change_layer(self, layer_)

        self.image = self.images[0] if isinstance(self.images, list) else self.images
        self.rect = self.image.get_rect(center=(LensFlareEffect.vector + LensFlareEffect.FLARE_POSITION))
        self.position = LensFlareEffect.FLARE_POSITION      # sprite center position
        self.timing = timing_                               # Refreshing time
        self.layer = layer_                                 # pygame layer
        self.gl = gl_                                       # global variable
        self.dt = 0                                         # timing variable
        self._blend = blend_                                # use additive mode or not
        self.alpha = alpha_                                 # vector fraction
        self.event = event_                                 # event name
        self.delete = delete_
        self.screenrect = pygame.display.get_surface().get_rect()
        if self.event != 'PARENT':                          # Parent or child instance
            LensFlareEffect.CHILD.append(self)

    @staticmethod
    def get_angle(
            object1: pygame.math.Vector2,  # Target center coordinates (x, y)
            object2: pygame.math.Vector2
    ):
        # calculate the angle (returns angle in radians) between a parent object
        # and a target object (center to center)
        dx = object2.x - object1.x
        dy = object2.y - object1.y

        return -atan2(dy, dx), pygame.math.Vector2(dx, dy)

    @staticmethod
    def second_flares(
            texture_,   # Polygon texture
            size_,      # Polygon multiplier
            polygon_,   # polygon (hexagon)
            light_position_: pygame.math.Vector2,  # Glow position
            exception_  # texture exception
            ):

        w, h = texture_.get_size()
        dist = uniform(-0.4, 2)
        color_c = lambda x: 380 + (750 - 380) * x

        if texture_ not in exception_:
            texture = pygame.Surface((w, h))
            texture.fill(tuple(wavelength_to_rgb(color_c(abs(dist)/2))))
            texture.set_alpha(randint(30, 50))
            texture_ = pygame.transform.smoothscale(texture, (int(w * (size_ * abs(dist))),
                                                               int(h * size_ * abs(dist))))
            w, h = texture_.get_size()
            s_2 = pygame.math.Vector2(w / 2, h / 2)
            surface_ = pygame.Surface((w, h), flags=pygame.SRCALPHA)
            # gfxdraw.textured_polygon(surface_, polygon_ * size_ * abs(dist), texture_, 0, 0)
            gfxdraw.textured_polygon(surface_, polygon_ * size_ * abs(dist), texture_, 0, 0)
            pos_ = tuple(light_position_ - s_2)
            LensFlareEffect.SECOND_FLARES.append([surface_, pos_, dist])
        else:

            s_ = uniform(0.2, size_)
            texture_ = pygame.transform.smoothscale(texture_,
                                                    (int(w * s_ * abs(dist)), int(h * s_ * abs(dist))))
            w, h = texture_.get_size()
            s_2 = pygame.math.Vector2(w / 2, h / 2)
            pos_ = tuple(light_position_ - s_2)
            LensFlareEffect.SECOND_FLARES.append([texture_, pos_, dist])

    def update(self):

        if self.dt > self.timing:

            if self.event == 'PARENT':

                if self.rect.top > self.screenrect.bottom / 4:
                    for child in LensFlareEffect.CHILD:
                        child.kill()
                    self.kill()

                    return
                # When the vector is below 80, increase light intensity
                if 0 < LensFlareEffect.vector.length() < 10:
                    self.image = LensFlareEffect.star_burst4x
                    self.rect = self.image.get_rect(center=self.position)
                    if self.delete:
                        for child in LensFlareEffect.CHILD:
                            child.kill()

                elif 0 < LensFlareEffect.vector.length() < 80:
                    self.image = LensFlareEffect.star_burst4x
                    self.rect = self.image.get_rect(center=self.position)

                else:
                    self.image = LensFlareEffect.star_burst
                    self.rect = self.image.get_rect(center=self.position)

            else:
                v1 = pygame.math.Vector2(LensFlareEffect.vector.x, LensFlareEffect.vector.y)
                if v1.length() != 0:
                    v1.scale_to_length(LensFlareEffect.vector.length() * self.alpha)

                    self.rect.center = self.position + v1
            self.dt = 0
        self.dt += self.gl.TIME_PASSED_SECONDS


class GL:
    TIME_PASSED_SECONDS = 0
    All = 0
    screenrect = 0


if __name__ == '__main__':

    # cobra()

    import timeit

    print(timeit.timeit('wavelength_to_rgb(620)', 'from __main__ import wavelength_to_rgb', number=1000000) / 1000000)

    AVG_FPS = []

    SCREENRECT = pygame.Rect(0, 0, 800, 1024)
    GL.screenrect = SCREENRECT
    import os

    os.environ['SDL_VIDEODRIVER'] = 'windib'

    pygame.display.init()
    SCREEN = pygame.display.set_mode(SCREENRECT.size, pygame.SWSURFACE, 32)
    SCREEN.set_alpha(None)
    pygame.init()
    pygame.mixer.pre_init(44100, 16, 2, 4095)
    # globalisation
    clock = pygame.time.Clock()
    All = LayeredUpdatesModified()
    GL.All = All

    STOP_GAME = False
    FRAME = 0
    BCK1 = pygame.image.load('Assets\\Graphics\\Background\\BCK1.800x2048.png').convert()

    texture = pygame.image.load('Assets\\Untitled3.png').convert_alpha()
    texture = pygame.transform.smoothscale(texture, (100, 100))

    texture1 = pygame.image.load('Assets\\Untitled1.png').convert_alpha()
    texture1 = pygame.transform.smoothscale(texture1, (100, 100))

    texture2 = pygame.image.load('Assets\\untitled7.png').convert_alpha()
    texture2 = pygame.transform.smoothscale(texture2, (256, 256))

    texture3 = pygame.image.load('Assets\\untitled8.png').convert_alpha()
    texture3 = pygame.transform.smoothscale(texture3, (256, 256))

    texture4 = pygame.image.load('Assets\\untitled9.png').convert_alpha()
    texture4 = pygame.transform.smoothscale(texture4, (120, 120))

    LensFlareEffect.star_burst = pygame.image.load('Assets\\Untitled5.png').convert()
    LensFlareEffect.star_burst4x = pygame.transform.smoothscale(LensFlareEffect.star_burst.copy(),
                                                (LensFlareEffect.star_burst.get_width() * 3,
                                                 LensFlareEffect.star_burst.get_height() * 3))

    mouse_pos = [0, 0]
    vector = pygame.math.Vector2(0, 0)
    LensFlareEffect.containers = All
    LensFlareEffect.images = texture3
    LensFlareEffect.vector = vector
    LensFlareEffect.FLARE_POSITION = pygame.math.Vector2(500, 150)
    angle = 0
    LensFlareEffect.SECOND_FLARES = []

    for r in range(5):
        LensFlareEffect.second_flares(texture, uniform(0.8, 1.2),
                                      LensFlareEffect.list_,
                                      LensFlareEffect.FLARE_POSITION,
                                      (texture2, texture4))

    for r in range(5):
        LensFlareEffect.second_flares(texture2, uniform(0.8, 1.2),
                                      LensFlareEffect.list_,
                                      LensFlareEffect.FLARE_POSITION,
                                      (texture2, texture4))

    for r in range(5):
        LensFlareEffect.second_flares(texture1, uniform(0.8, 1.2),
                                      LensFlareEffect.list_,
                                      LensFlareEffect.FLARE_POSITION,
                                      (texture2, texture4))
    for r in range(5):
        LensFlareEffect.second_flares(texture4, uniform(0.8, 1.2),
                                      LensFlareEffect.list_,
                                      LensFlareEffect.FLARE_POSITION,
                                      (texture2, texture4))

    hidden_planer = LensFlareEffect(alpha_=2, gl_=GL, timing_=30, layer_=0, blend_=pygame.BLEND_RGB_ADD)
    LensFlareEffect.images = texture2
    glare = LensFlareEffect(alpha_=1, gl_=GL, timing_=30, layer_=0, blend_=pygame.BLEND_RGB_ADD)
    for flares in LensFlareEffect.SECOND_FLARES:
        LensFlareEffect.images = flares[0]
        LensFlareEffect(alpha_=flares[2], gl_=GL, timing_=30, layer_=0, blend_=pygame.BLEND_RGB_ADD)

    LensFlareEffect.vector = pygame.math.Vector2(0, 0)
    LensFlareEffect.images = LensFlareEffect.star_burst.copy()
    light = LensFlareEffect(alpha_=0.5, gl_=GL, timing_=30, layer_=0,
                            blend_=pygame.BLEND_RGB_ADD, event_='PARENT')

    LensFlareEffect(alpha_=0.5, gl_=GL, timing_=30, layer_=0, blend_=pygame.BLEND_RGB_ADD, event_='PARENT')

    screendump = 0
    while not STOP_GAME:


        pygame.event.pump()

        for event in pygame.event.get():

            keys = pygame.key.get_pressed()

            if keys[pygame.K_ESCAPE]:
                STOP_GAME = True

            # screenshots
            elif keys[pygame.K_F8]:
                pygame.image.save(SCREEN, 'Assets\\Screenshot\\Screendump'
                                  + str(screendump) + '.png')
                screendump += 1

            if event.type == pygame.MOUSEMOTION:
                mouse_pos = pygame.mouse.get_pos()
                angle, vector = LensFlareEffect.get_angle(LensFlareEffect.FLARE_POSITION,
                                                          pygame.math.Vector2(mouse_pos))
                angle %= 360

        # LensFlareEffect.FLARE_POSITION += (0, 1)
        SCREEN.fill((0, 0, 0, 255))
        SCREEN.blit(BCK1, (0, 0))
        All.update()
        All.draw(SCREEN)

        LensFlareEffect.vector = vector

        pygame.display.flip()
        TIME_PASSED_SECONDS = clock.tick_busy_loop(60)
        GL.TIME_PASSED_SECONDS = TIME_PASSED_SECONDS
        avg_fps = clock.get_fps()
        print(avg_fps)

        FRAME += 1

    pygame.quit()