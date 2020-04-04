
#include <stdlib.h>
#include <stdint.h>
#include <stdio.h>
#include <memory.h>
#include <math.h>
#include <float.h>
#include <assert.h>
#include <time.h>


struct rgba_color{
    int r;
    int g;
    int b;
    int a;
};

struct vector2d{
    double x;
    double y;
};

struct angle_vector{
  struct vector2d vector;
};

inline struct rgba_color wavelength_to_rgba(int wavelength, double gamma);
float uniform(float lower, float upper);
int randint(int lower, int upper);
inline void scale_to_length(struct vector2d *v, float length);
inline void normalize (struct vector2d *v);
float v_length(struct vector2d *vector);
struct angle_vector get_angle(struct vector2d *object1, struct vector2d *object2);



inline struct rgba_color wavelength_to_rgba(int wavelength, double gamma){
    /*

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
    */

    struct rgba_color color = {.r=0, .g=0, .b=0, .a=0};
    double attenuation=0;
    if ((wavelength >= 380) & (wavelength <= 440))
    {
      attenuation = 0.3 + 0.7 * (wavelength - 380.0) / 60.0;
      color.r = (int)(pow((((440 - wavelength) / 60.0) * attenuation), gamma) * 255.0f);
      // color.g = 0;
      color.b = (int)(pow(attenuation, gamma) * 255.0f);
    }
    else if((wavelength >=440) && (wavelength <= 490))
    {
      // color.r = 0;
      color.g = (int)(pow((wavelength - 440) / 50.0, gamma) * 255.0f);
      color.b = 255;
    }
    else if ((wavelength>=490) && (wavelength <= 510)){
      // color.r = 0;
      color.g = 255;
      color.b = (int)(pow((510 - wavelength) / 20.0, gamma) * 255.0f);
    }
    else if ((wavelength>=510) && (wavelength <= 580)){
      color.r = (int)(pow((wavelength - 510) / 70.0, gamma) * 255.0f);
      color.g = 255;
      // color.b = 0;
    }
    else if ((wavelength>=580) && (wavelength <= 645)){
      color.r = 255;
      color.g = (int)(pow((645 - wavelength) / 65.0, gamma) * 255.0f);
      // color.b = 0;
    }
    else if ((wavelength>=645) && (wavelength <= 750)){
      attenuation = 0.3 + 0.7 * (750 - wavelength) / 105.0;
      color.r = (int)(pow(attenuation, gamma) * 255.0f);
      // color.g = 0;
      // color.b = 0;
    }
//    else{
//    color.r = 0;
//    color.g = 0;
//    color.b = 0;
//
//    }
    color.a = 22;
    return color;
}


inline float uniform_c(float lower, float upper)
{
  return lower + ((float)rand()/(float)(RAND_MAX)) * (upper - lower);
}

inline int randint_c(int lower, int upper)
{
  return (int)((rand() % (upper - lower  + 1)) + lower);
}


/*
Vector normalisation (dividing components x&y by vector magnitude) v / |v|
*/
inline void normalize (struct vector2d *v)
{
  float length_ = v_length(v);
  assert (length_ !=0);
  v->x = v->x / length_;
  v->y = v->y / length_;
}


/*
Normalize a 2d vector and rescale it to a given length. (v / |v|) * scalar
*/
inline void scale_to_length(struct vector2d *v, float length)
{
  normalize(v);
  v->x = v->x * length;
  v->y = v->y * length;
}

/*
Return vector length (scalar value)
*/
inline float v_length(struct vector2d *vector){
  return sqrt((float)(vector->x * vector->x) + (float)(vector->y * vector->y));
}

inline struct angle_vector get_angle_c(struct vector2d *object1, struct vector2d *object2){
  struct angle_vector av;
  double dx = object2->x - object1->x;
  double dy = object2->y - object1->y;
  av.vector.x = dx;
  av.vector.y = dy;
  return av;
}


int main(){
return 0;
}