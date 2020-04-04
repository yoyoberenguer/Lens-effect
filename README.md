# Lens-effect

### Pseudo Lens flare effect for 2D video game

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


![alt text](https://github.com/yoyoberenguer/lens-effect/blob/master/color_spectrum.png) 

![alt text](https://github.com/yoyoberenguer/lens-effect/blob/master/LensFlare.gif) 

