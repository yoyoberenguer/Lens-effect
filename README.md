# Lens-effect

## Pseudo Lens flare effect for 2D video game

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

![alt text](https://github.com/yoyoberenguer/lens-effect/blob/master/color_spectrum.png) 

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
C:\
python setup_flares.py build_ext --inplace
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


![alt text](https://github.com/yoyoberenguer/lens-effect/blob/master/LensFlare.gif) 

