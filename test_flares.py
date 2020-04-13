"""
MIT License

Copyright (c) 2019 Yoann Berenguer

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

### PROJECT:
```
Lens flare effect demonstration using a wavelength to RGB algorithm
written by Noah.org in python and adapted into C language for speed improvement.
You can find the wavelength to RGB algorithm in the C file wavelength.c under the main
project directory.
Note:
If you change the C file, don't forget to build it with gcc and to re-build the project
using the command "C:>python setup_fares.py build_ext --inplace"
```

### TECHNIQUE:
```
1) A vector direction is calculated from the mouse cursor position to the centre of
the effect (FLARE_EFFECT_CENTRE).
2) Polygons of various sizes and colors are added along that vector (with sizes
proportional to the distance from the centre).
3) All polygons are filled with RGB color corresponding to the wavelength relative to
their distances.
When the polygon is placed at the end of the vector, the RGB color will vary from purple,
blue, green yellow, orange and red when moving along the lens vector (red being the
closest from the user position, see color_spectrum image)
```

Color Spectrum



### HOW TO CREATE FLARES
```
1) Create a texture
TEXTURE = pygame.image.load('Assets\\Untitled3.png').convert(24)
TEXTURE = pygame.transform.smoothscale(TEXTURE, (100, 100))
TEXTURE.set_colorkey((0, 0, 0, 0), pygame.RLEACCEL)

2) Create a polygon
octagon = polygon()

3) Instantiate the flare
for r in range(20):
    FLARES.append(second_flares(TEXTURE, octagon.copy(),
                                make_vector2d(FLARE_EFFECT_CENTRE), 0.8, 1.2, exc))

In the above example, we are creating 20 sub-flares with texture (image Untitled3.png)
All instance will be added to the python list FLARES.
The method second_flares assign the texture and give a random position to the
flare along the direction vector. Float values 0.8 and 1.2 are the minimum and maximum
of the polygon size.
Texture contain in the list named <exc> will be blit directly
on the flare vector without creating a textured polygon

4) Create the sprites

for flares in FLARES:
    create_flare_sprite(
        images_=flares[0], distance_=flares[1], vector_=VECTOR,
        position_=FLARE_EFFECT_CENTRE, layer_=0, gl_=GL,
        child_group_=CHILD, blend_=pygame.BLEND_RGB_ADD, event_type='CHILD', delete_=False)

flares[0] : correspond to the texture
flares[1] : the distance from the centre of the effect
vector    : the flare vector
position  : Polygon position along the flare vector
layer     : layer used for displaying the sprite (this is not implemented yet)
GL        : Global constant
CHILD     : is the group containing all the instances
blend     : default additive mode
event     : can be 'CHILD' or 'PARENT' child is used for the flares (polygons)
            Child polygon 's size is inalterable.

4) Fisplay the sprites in your mainloop
display_flare_sprite(CHILD, STAR_BURST, STAR_BURST3x, GL, VECTOR)
```

### REQUIREMENT:
```
- python > 3.0
- numpy arrays
- pygame with SDL version 1.2 (SDL version 2 untested)
  Cython
- A compiler such visual studio, MSVC, CGYWIN setup correctly
  on your system
```

### BUILDING PROJECT:
```
Use the following command:
C:>\\python setup_bloom.py build_ext --inplace
C:>\\python setup_flares.py build_ext --inplace
```

#### Reference see page https://www.noah.org/wiki/Wavelength_to_RGB_in_Python

```
Wavelength to RGB in Python - Noah.org
Based on code by Dan Bruton
http://www.physics.sfasu.edu/astro/color/spectra.html


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


```
"""

import timeit
import os

# NUMPY IS REQUIRED
try:
    import numpy
    from numpy import ndarray, zeros, empty, uint8, int32, float64, float32, dstack, full, ones, \
        asarray, ascontiguousarray
except ImportError:
    raise ImportError("\n<numpy> library is missing on your system."
                      "\nTry: \n   C:\\pip install numpy on a window command prompt.")

# PYGAME IS REQUIRED
try:
    import pygame
    from pygame import Color, Surface, SRCALPHA, RLEACCEL, BufferProxy, gfxdraw
    from pygame.surfarray import pixels3d, array_alpha, pixels_alpha, array3d
    from pygame.image import frombuffer

except ImportError:
    raise ImportError("\n<Pygame> library is missing on your system."
                      "\nTry: \n   C:\\pip install pygame on a window command prompt.")

try:
    import FLARES
    from FLARES import create_flare_sprite, make_vector2d, \
        LayeredUpdatesModified, second_flares, polygon, get_angle, display_flare_sprite
except ImportError:
    print("\nHave you build the project?"
          "\nC:>python setup_flare.py build_ext --inplace")

try:
    import bloom
    from bloom import bloom_effect_array24
except ImportError:
    print("\n library bloom is missing on your system.")


# ALL SHARE CONSTANT(s) GOES HERE
class GL:
    TIME_PASSED_SECONDS = 0
    All = 0
    screenrect = 0


AVG_FPS = []

SCREENRECT = pygame.Rect(0, 0, 500, 500)
GL.screenrect = SCREENRECT

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
GL.SCREEN = SCREEN


# ************************* TEXTURE ********************************
# LOAD ALL THE LENS AND FLARE TEXTURES
STOP_GAME = False
FRAME = 0
BCK1 = pygame.image.load('A1.jpg').convert(32, pygame.RLEACCEL)
BCK1 = pygame.transform.smoothscale(BCK1, (SCREENRECT.w, SCREENRECT.h))
BCK1.set_alpha(None)

# SUB FLARES
TEXTURE = pygame.image.load('Assets\\Untitled3.png').convert(24)
TEXTURE = pygame.transform.smoothscale(TEXTURE, (100, 100))
TEXTURE.set_colorkey((0, 0, 0, 0), pygame.RLEACCEL)

TEXTURE1 = pygame.image.load('Assets\\Untitled1.png').convert(24)
TEXTURE1 = pygame.transform.smoothscale(TEXTURE1, (100, 100))
TEXTURE1.set_colorkey((0, 0, 0, 0), pygame.RLEACCEL)

# GLARE SPRITE
TEXTURE2 = pygame.image.load('Assets\\untitled7.png').convert(24)
TEXTURE2 = pygame.transform.smoothscale(TEXTURE2, (256, 256))
TEXTURE2.set_colorkey((0, 0, 0, 0), pygame.RLEACCEL)

# SPRITE DISPLAY AT THE END OF THE VECTOR
TEXTURE3 = pygame.image.load('Assets\\untitled8.png').convert(24)
TEXTURE3 = pygame.transform.smoothscale(TEXTURE3, (256, 256))
TEXTURE3.set_colorkey((0, 0, 0, 0), pygame.RLEACCEL)

MODEL = FLARES.v_surface()
pygame.image.save(MODEL, "color_spectrum.png")

# ********************************************************************

# SPRITE OF THE STAR CAUSING THE FLARE EFFECT
STAR_BURST = pygame.image.load('Assets\\Untitled5.png').convert(24)
STAR_BURST.set_colorkey((0, 0, 0, 0), pygame.RLEACCEL)
w, h = STAR_BURST.get_size()
# STAR SIZE TIME 4 TO INCREASE BRIGHTNESS
STAR_BURST3x = pygame.transform.smoothscale(
    STAR_BURST.copy(), (w * 3, h * 3))

STAR_BURST3x = STAR_BURST3x.convert(24)

# CREATE A BLOOM EFFECT (INCREASE BRIGHTNESS)
A = pygame.transform.smoothscale(STAR_BURST3x, (w * 3, h * 3))
STAR_BURST3x = bloom_effect_array24(A, 0, smooth_=1)

# MOUSE POSITION INITIALISATION
mouse_pos = [0, 0]

VECTOR = pygame.math.Vector2(0, 0)


# BLUE STAR POSITION ONTO THE SCREEN (CENTRE OF THE EFFECT)
FLARE_EFFECT_CENTRE = pygame.math.Vector2(280, 120)


# GROUP USED FOR REFERENCING ALL THE SUB-FLARES.
# THE GROUP CONTAINS OBJECT WITH FOLLOWING ATTRIBUTES
# FLARES =[[SURFACE, DISTANCE], [...] ]
# SURFACE  : FLARE TEXTURE
# DISTANCE : DISTANCE FROM THE CENTER (FLOAT).
# OBJECT SIZE WILL CHANGE ACCORDING TO POSITION/DISTANCE FROM THE CENTRE.
# WE COULD HAVE USED A PYGAME.SPRITE.GROUP INSTEAD, BUT THIS OFFER BETTER
# PERFORMANCES.
FLARES = []

# CHILD FLARE(s) GROUP (SPRITE LIST)
# THIS IS NO A PYGAME.SPRITE.GROUP
CHILD = []

# CREATE AN OCTAGON (SECOND FLARE POLYGON)
# AT THIS STAGE THE POLYGON IS EMPTY (NO TEXTURE)
# OCTAGON IS A NUMPY NDARRAY SHAPE (W, H)
octagon = polygon()

# REFERENCE ALL SECOND FLARE TEXTURE WHOM DOES NOT NEED
# TO BE APPLY TO THE POLYGON SUCH AS TEXTURE2.
# THOSE TEXTURE ARE ALREADY FINALIZED AND JUST NEED TO BE
# BLIT ALONG THE LENS VECTOR DIRECTION
exc = [TEXTURE2]

# CREATE SUB-FLARE(s)
# FIRST ARGUMENT (TEXTURE) REPRESENT THE TEXTURE BLIT
# TO THE POLYGON. make_vector2d IS A FUNCTION THAT CONVERT
# PYGAME.MATH.VECTOR2 INTO C EQUIVALENT VECTOR OBJECT.
# 0.8 AND 1.2 ARE MIN AMD MAX OF THE RANDOMIZE VALUE USED
# FOR RESIZING THE POLYGON. NOTHING IS MORE BORING THAT
# POLYGON WITH EXACT SAME SIZES.

# DRAW POLYGON FLARES (TEXTURE & TEXTURE HAVE DIFFERENT TRANSPARENCY LEVEL)
# ALSO INSERT POLYGON INTO THE PYTHON LIST FLARES
for r in range(20):
    FLARES.append(second_flares(TEXTURE, octagon.copy(),
                                make_vector2d(FLARE_EFFECT_CENTRE), 0.8, 1.2, exc))
for r in range(5):
    FLARES.append(second_flares(TEXTURE1, octagon.copy(),
                                make_vector2d(FLARE_EFFECT_CENTRE), 0.8, 1.2, exc))
# DRAW GLARES
for r in range(5):
    FLARES.append(second_flares(TEXTURE2, octagon.copy(),
                                make_vector2d(FLARE_EFFECT_CENTRE), 0.8, 1.2, exc))

# GO TROUGH THE LIST FLARES AND CREATE FLARES SPRITES.
# THE SPRITE ARE INSERTED INTO THE PYTHON LIST CHILD
for flares in FLARES:
    create_flare_sprite(
        images_=flares[0], distance_=flares[1], vector_=VECTOR,
        position_=FLARE_EFFECT_CENTRE, layer_=0, gl_=GL,
        child_group_=CHILD, blend_=pygame.BLEND_RGB_ADD, event_type='CHILD', delete_=False)

# SPRITE DISPLAY AT THE END OF THE VECTOR
create_flare_sprite(
        images_=TEXTURE3, distance_=2.0, vector_=VECTOR,
        position_=FLARE_EFFECT_CENTRE, layer_=0, gl_=GL,
        child_group_=CHILD, blend_=pygame.BLEND_RGB_ADD, event_type='CHILD', delete_=False)

# BLUE BRIGHT STAR
create_flare_sprite(
        images_=STAR_BURST, distance_=0.5, vector_=VECTOR,
        position_=FLARE_EFFECT_CENTRE, layer_=0, gl_=GL,
        child_group_=CHILD, blend_=pygame.BLEND_RGB_ADD, event_type='PARENT', delete_=False)


# MAIN LOOP
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

            # VECTOR IS A PYGAME.MATH.VECTOR2 TYPE
            # VECTOR GIVEN BETWEEN THE MOUSE CURSOR AND THE CENTRE
            # OF THE BLUE STAR
            VECTOR = get_angle(
                make_vector2d(FLARE_EFFECT_CENTRE),
                make_vector2d(pygame.math.Vector2(mouse_pos[0], mouse_pos[1])))

    # DISPLAY THE BACKGROUND IMAGE
    SCREEN.blit(BCK1, (0, 0))

    # BLIT ALL THE SPRITE ONTO THE BACKGROUND
    # CHECK METHOD display_flare_sprite FOR MORE DETAILS
    display_flare_sprite(CHILD, STAR_BURST, STAR_BURST3x, GL, VECTOR)

    # WE DO NOT NEED TO UPDATE
    # SPRITE DOES NOT BELONG TO PYGAME GROUP
    # All.update()
    All.draw(SCREEN)

    # DISPLAY CHANGES
    pygame.display.flip()

    TIME_PASSED_SECONDS = clock.tick_busy_loop(400)
    GL.TIME_PASSED_SECONDS = TIME_PASSED_SECONDS
    avg_fps = clock.get_fps()
    print(avg_fps, 1000/(avg_fps + 0.001))

    FRAME += 1

pygame.quit()
