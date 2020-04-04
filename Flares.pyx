#cython: boundscheck=False, wraparound=False, nonecheck=False, optimize.use_switch=True
# encoding: utf-8

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
"""


# NUMPY IS REQUIRED
try:
    import numpy
    from numpy import ndarray, zeros, empty, uint8, int32, float64, float32, dstack, full, ones,\
    asarray, ascontiguousarray
except ImportError:
    raise ImportError("\n<numpy> library is missing on your system."
          "\nTry: \n   C:\\pip install numpy on a window command prompt.")

# CYTHON IS REQUIRED
try:
    cimport cython
    from cython.parallel cimport prange
except ImportError:
    raise ImportError("\n<cython> library is missing on your system."
          "\nTry: \n   C:\\pip install cython on a window command prompt.")

# PYGAME IS REQUIRED
try:
    import pygame
    from pygame import Color, Surface, SRCALPHA, RLEACCEL, BufferProxy, gfxdraw
    from pygame.surfarray import pixels3d, array_alpha, pixels_alpha, array3d
    from pygame.image import frombuffer
    from pygame import Rect
    from pygame.time import get_ticks
    from operator import truth

except ImportError:
    raise ImportError("\n<Pygame> library is missing on your system."
          "\nTry: \n   C:\\pip install pygame on a window command prompt.")

from libc.math cimport atan2, fabs
from libc.stdlib cimport abs

cimport numpy as np

cdef extern from 'wavelength.c' nogil:
    struct rgba_color:
        int r;
        int g;
        int b;
        int a;

    struct vector2d:
        double x;
        double y;

    struct angle_vector:
        double rad_angle;
        vector2d vector;

    inline rgba_color wavelength_to_rgba(int wavelength, double gamma)
    float uniform_c(float lower, float upper)
    int randint_c(int lower, int upper)
    inline void scale_to_length(vector2d *v, float length)
    inline void normalize (vector2d *v)
    float v_length(vector2d *vector)
    angle_vector get_angle_c(vector2d *object1, vector2d *object2)



DEF HALF = 1.0/2.0

# --------------------------------------- IMPLEMENTATION --------------------------------------

@cython.boundscheck(False)
@cython.wraparound(False)
@cython.nonecheck(False)
@cython.cdivision(True)
cpdef make_vector2d(v):
    """
    Convert pygame.math.Vector2 object into a C type vector2d
    :param v: pygame.math.Vector2, vector to convert
    :return: return a C vector2d equivalent
    """
    assert isinstance(v, pygame.math.Vector2),\
        '\nIncorrect type for argument v got % ' % type(v)
    cdef vector2d v2d;
    v2d.x, v2d.y = v.x, v.y
    return v2d

@cython.boundscheck(False)
@cython.wraparound(False)
@cython.nonecheck(False)
@cython.cdivision(True)
cdef class Sprite(object):

    cdef dict __g
    cdef dict __dict__
    def __init__(self, *groups):
        self.__g = {}
        if groups:
            self.add(tuple(groups))


    @cython.boundscheck(False)
    @cython.wraparound(False)
    @cython.nonecheck(False)
    @cython.cdivision(True)
    cdef add(self, tuple groups):

        has = self.__g.__contains__
        for group in groups:
            if hasattr(group, '_spritegroup'):
                if not has(group):
                    group.add_internal(self)
                    self.add_internal(group)
            else:
                self.add(tuple(group))

    @cython.boundscheck(False)
    @cython.wraparound(False)
    @cython.nonecheck(False)
    @cython.cdivision(True)
    cdef remove(self, tuple groups):

        has = self.__g.__contains__
        for group in groups:
            if hasattr(group, '_spritegroup'):
                if has(group):
                    group.remove_internal(self)
                    self.remove_internal(group)
            else:
                self.remove(tuple(group))

    @cython.boundscheck(False)
    @cython.wraparound(False)
    @cython.nonecheck(False)
    @cython.cdivision(True)
    cdef add_internal(self, group):
        self.__g[group] = 0

    @cython.boundscheck(False)
    @cython.wraparound(False)
    @cython.nonecheck(False)
    @cython.cdivision(True)
    cdef remove_internal(self, tuple group):
        del self.__g[group]

    @cython.boundscheck(False)
    @cython.wraparound(False)
    @cython.nonecheck(False)
    @cython.cdivision(True)
    cpdef update(self, tuple args):
        pass

    @cython.boundscheck(False)
    @cython.wraparound(False)
    @cython.nonecheck(False)
    @cython.cdivision(True)
    cdef kill(self):

        for c in self.__g:
            c.remove_internal(self)
        self.__g.clear()

    @cython.boundscheck(False)
    @cython.wraparound(False)
    @cython.nonecheck(False)
    @cython.cdivision(True)
    cdef groups(self):
        return list(self.__g)

    @cython.boundscheck(False)
    @cython.wraparound(False)
    @cython.nonecheck(False)
    @cython.cdivision(True)
    cdef alive(self):
        return truth(self.__g)

    @cython.boundscheck(False)
    @cython.wraparound(False)
    @cython.nonecheck(False)
    @cython.cdivision(True)
    def __repr__(self):
        return "<%s sprite(in %d groups)>" % (self.__class__.__name__, len(self.__g))


@cython.boundscheck(False)
@cython.wraparound(False)
@cython.nonecheck(False)
@cython.cdivision(True)
# GROUP LayeredUpdatesModified subclass of LayeredUpdates(AbstractGroup)
cdef class LayeredUpdatesModified(LayeredUpdates):
    """
    Pygame Class LayerUpdates modified for use of flag RGB_BLEND_ADD
    When instantiating pygame sprites, use the attribute _blend to specify
    if the sprite needs to be render with additive mode
    """

    def __init__(self):
        LayeredUpdates.__init__(self)


    # cannot cynthonized due to __dict__
    cpdef draw(self, surface_):

        cdef dict spritedict = self.spritedict
        cdef list dirty = self.lostsprites
        self.lostsprites = []
        cdef list l = self.sprites()
        cdef int i, t = len(l)

        for i in range(0, t):
            spr = l[i]              # spr is a class instance
            rec = spritedict[spr]   # rec is a pygame.Rect object

            if hasattr(spr, '_blend') and spr._blend is not None:
                # display sprite with pygame additive mode
                newrect = surface_.blit(spr.image, spr.rect, special_flags=spr._blend)
            else:
                newrect = surface_.blit(spr.image, spr.rect)

            # check if the sprite is a new rectangle (initialised)
            if rec is self._init_rect:
                dirty.append(newrect)

            # Already exist
            else:

                if newrect.colliderect(rec):
                    dirty.append(newrect.union(rec))
                else:
                    dirty.append(newrect)
                    dirty.append(rec)

            spritedict[spr] = newrect
        return dirty


@cython.boundscheck(False)
@cython.wraparound(False)
@cython.nonecheck(False)
@cython.cdivision(True)
cpdef get_angle(vector2d obj1, vector2d obj2):
    """
    Return a pygame.math.Vector2 representing a vector 
    This angle represent the beam lens direction
     
    :param obj1: vector2d; object 1 vector
    :param obj2: vector2d; object 2 vector
    :return: pygame.math.Vector2; Return pygame Vector2d 
    """
    cdef angle_vector av;
    av = get_angle_c(&obj1, &obj2)
    return pygame.math.Vector2(av.vector.x, av.vector.y)


@cython.boundscheck(False)
@cython.wraparound(False)
@cython.nonecheck(False)
@cython.cdivision(True)
cpdef np.ndarray[np.int_t, ndim=2] polygon():
    """
    CREATE A FLARE POLYGON OCTAGON (REFERENCE) 
    POLYGON SHAPE IS HARD ENCODED WITH VARIABLES _a, _b, center_x, center_y  
    
    :return: Return a numpy.ndarray shape (w, h) numpy.int
    """
    cdef short int _a = 10                      # Octagon parameter
    cdef short int _b = 30                      # Octagon parameter
    cdef int center_x = 50, center_y = 50       # Octagon's center
    # Octagon sides (Octagon second flares)
    return numpy.array([[center_x - _a, center_y - _b],
                        [center_x + _a, center_y - _b],
                        [center_x + _b, center_y - _a],
                        [center_x + _b, center_y + _a],
                        [center_x + _a, center_y + _b],
                        [center_x - _a, center_y + _b],
                        [center_x - _b, center_y + _a],
                        [center_x - _b, center_y - _a]], dtype=numpy.int, copy=False)


@cython.boundscheck(False)
@cython.wraparound(False)
@cython.nonecheck(False)
@cython.cdivision(True)
cpdef second_flares(
        object texture_,
        np.ndarray[np.int_t, ndim=2] polygon_,
        vector2d light_position_,
        float min_size,
        float max_size,
        list exception_
        ):
    """
    CREATE A FLARE POLYGON ALONG THE FLARE VECTOR DIRECTION 
    SECOND FLARE(S) ARE BUILD OFFLINE BEFORE THE MAIN LOOP 
    THE POLYGON IS THEN FILLED WITH THE GIVEN TEXTURE (variable TEXTURE)
    
    :param polygon_: numpy.ndarray; polygon (octagon) This is the shape used for sub-flares.
      see python method polygon for more details
    :param max_size: float; Max factor for resizing the polygon 
    :param min_size: float; Min factor for resizing the polygon 
    :param texture_: pygame.Surface; Flare textures optional (TEXTURE 100x100, TEXTURE1 100x100,
     TEXTURE2 256x256, TEXTURE3 256x256 TEXTURE4 120x120). Note that TEXTURE2 and TEXTURE4 are 
     finalized textures, they will be blit onto the background. 
     Pygame surface compatible 24 bit without per-pixel transparency. This surface is converted for 
     fast blit and RLEACCEL 
    :param light_position_: vector2d; Vector position for the second flare
    :param exception_: list; List containing TEXTURE(s) that do not require to be blit onto 
      the polygon object.
    :return: Return a python list object containing flares's (TEXTURE, distance). 
    with TEXTURE : pygame.Surface, position vector2d (x, y), distance (float) 
    """

    # FIXME size range ?
    cdef:
        int w = texture_.get_width()
        int h = texture_.get_height()

        # -0.8 negative distance (behind focal point)
        # +2 after focal point
        float dist = uniform_c(-0.8, 2)

        float a_dist = <float>fabs(dist)
        float s_, v1, v2, size_
        int v
        rgba_color color1;
        vector2d s_2

    cdef list flare = []

    # FAST C UNIFORM (FASTER THAT PYTHON RANDOM.UNIFORM METHOD)
    size_ = uniform_c(min_size, max_size)

    # CHECK IF THE TEXTURE CAN
    # BE BLIT DIRECTLY ONTO THE SCREEN WITHOUT
    # BEING DRAWN ONTO THE POLYGON.
    if texture_ not in exception_:

        # EMPTY SURFACE with RLEACCEL and fast blit
        texture = pygame.Surface((w, h), flags=pygame.RLEACCEL).convert()

        # WAVELENGTH V
        v = <int>((dist * HALF) * 370.0 + 380.0)
        # GET RGBA color corresponding to the given wavelength v
        color1 = wavelength_to_rgba(v, 0.8)

        # FILL the TEXTURE and set_alpha
        texture.fill((color1.r, color1.g, color1.b, color1.a))
        texture.set_alpha(randint_c(30, 50))

        # RESIZE
        v1 = <float>(size_ * a_dist)
        texture_ = pygame.transform.scale(texture, (<int>(w * v1), <int>(h * v1)))

        w, h = texture_.get_size()
        s_2.x = <float> (w >> 1)
        s_2.y = <float> (h >> 1)

        # APPLY TEXTURE to polygon
        surface_ = pygame.Surface((w, h), flags=pygame.RLEACCEL).convert()
        gfxdraw.textured_polygon(surface_, polygon_ * v1, texture_, 0, 0)

        flare = [surface_, dist]

    # DIRECT BLIT
    else:
        s_ = uniform_c(0.2, size_)
        v2 = <float>(s_ * a_dist)
        texture_ = pygame.transform.scale(texture_, (<int>(w * v2), <int>(h * v2)))
        w, h = texture_.get_size()
        s_2.x, s_2.y = <float>(w >> 1), <float>(h >> 1)

        flare = [texture_, dist] #pos_, dist]

    return flare


@cython.boundscheck(False)
@cython.wraparound(False)
@cython.nonecheck(False)
@cython.cdivision(True)
cpdef display_flare_sprite(list child_group,
                           star_burst,
                           star_burst3x,
                           gl_,
                           vector):
    """
    Display all the flares sprites onto the background image
    
    :param child_group: list; Group or list that will contains all the sprites (this is not a pygame sprite group, 
      only a python list. We are using a list in order to boost performances. We do not need to use pygame 
      group methods of collision etc).
    :param star_burst: pygame Surface; Star surface   
    :param star_burst3x: Star surface size x 4
    :param gl_: Class constant (contains all the constants)
    :param vector: pygame.math.Vector2 
 
    """
    cdef vector2d v1
    cdef float length

    for spr in child_group:

        spr.vector = vector

        if spr.event_type == 'PARENT':

            # VECTOR DISTANCE FROM THE LOCAL POINT (STAR CENTRE) IS
            # BELOW 80, INCREASE BRIGHTNESS OF THE STAR USING A SURFACE
            # 4 TIMES LARGER.
            if 0 < spr.vector.length() < 80:
                spr.image = star_burst3x
                spr.rect = spr.image.get_rect(center=spr.position)

            else:
                # lv = spr.vector.length()
                # if lv ==0:
                #     return
                # l = 1/(lv * 0.002)
                #
                w, h = star_burst.get_size()
                # w = w * l
                # h = h * l
                #
                # w = <int>min(star_burst.get_width() * 2.95, w)
                # h = <int>min(star_burst.get_height() * 2.95, h)
                # w = <int>max(star_burst.get_width(), w)
                # h = <int>max(star_burst.get_height(), h)

                spr.image = pygame.transform.scale(star_burst, (w, h))
                spr.rect = spr.image.get_rect(center=(spr.position.x, spr.position.y))

        else:

            v1.x = spr.vector.x
            v1.y = spr.vector.y
            length = v_length(&v1)

            if length != 0:
                scale_to_length(&v1, length * spr.alpha)
                spr.rect.center = spr.position.x + v1.x, spr.position.y + v1.y

        spr.w2 = spr.image.get_width() >> 1
        spr.h2 = spr.image.get_height() >> 1
        gl_.SCREEN.blit(spr.image, (
            spr.rect.centerx - spr.w2,
            spr.rect.centery - spr.h2),
                        special_flags=pygame.BLEND_RGB_ADD)


cpdef create_flare_sprite(images_,
                          float distance_,
                          vector_,
                          position_,
                          int layer_,
                          gl_,
                          child_group_,
                          int blend_ = pygame.BLEND_RGB_ADD,
                          event_type = 'CHILD',
                          bint delete_=False
                          ):

    # CREATE A PYGAME SPRITE OBJECT
    flare_spr = pygame.sprite.Sprite()
    flare_spr.image = images_[0] if isinstance(images_, list) else images_
    flare_spr.alpha = distance_
    flare_spr.vector = vector_
    flare_spr.rect = flare_spr.image.get_rect(
        center=(vector_.x + position_.x, vector_.y + position_.y))
    flare_spr.position = position_
    flare_spr.layer = layer_
    flare_spr.gl = gl_
    flare_spr._blend = blend_
    flare_spr.event_type = event_type
    flare_spr.delete = delete_
    cdef int w, h
    w, h = flare_spr.image.get_size()
    flare_spr.w2, flare_spr.h2 = w >> 1, h >> 1

    child_group_.append(flare_spr)

    # OVERRIDE UPDATE METHOD
    # gl_.All.add(flare_spr, layer=0)
    # flare_spr.update = display_flare_sprite


# Python 3 does not have the callable function, but an equivalent can be made
# with the hasattr function.
if 'callable' not in dir(__builtins__):
    callable = lambda obj: hasattr(obj, '__call__')


@cython.boundscheck(False)
@cython.wraparound(False)
@cython.nonecheck(False)
@cython.cdivision(True)
cdef class AbstractGroup(object):

    cdef public dict spritedict
    cdef public list lostsprites
    # dummy val to identify sprite groups, and avoid infinite recursion
    # _spritegroup = True
    cdef public bint _spritegroup
    def __init__(self):
        self._spritegroup = True
        self.spritedict = {}
        self.lostsprites = []

    @cython.boundscheck(False)
    @cython.wraparound(False)
    @cython.nonecheck(False)
    @cython.cdivision(True)
    cdef sprites(self):
        return list(self.spritedict)

    @cython.boundscheck(False)
    @cython.wraparound(False)
    @cython.nonecheck(False)
    @cython.cdivision(True)
    cdef add_internal(self, sprite):
        self.spritedict[sprite] = 0

    @cython.boundscheck(False)
    @cython.wraparound(False)
    @cython.nonecheck(False)
    @cython.cdivision(True)
    cdef remove_internal(self, sprite):
        r = self.spritedict[sprite]
        if r:
            self.lostsprites.append(r)
        del self.spritedict[sprite]

    @cython.boundscheck(False)
    @cython.wraparound(False)
    @cython.nonecheck(False)
    @cython.cdivision(True)
    cdef has_internal(self, sprite):
        return sprite in self.spritedict

    @cython.boundscheck(False)
    @cython.wraparound(False)
    @cython.nonecheck(False)
    @cython.cdivision(True)
    cdef copy(self):
        return self.__class__(self.sprites())

    def __iter__(self):
        return iter(self.sprites())

    def __contains__(self, sprite):
        return self.has(sprite)

    @cython.boundscheck(False)
    @cython.wraparound(False)
    @cython.nonecheck(False)
    @cython.cdivision(True)
    cpdef add(self, sprites):

        for sprite in sprites:
            # It's possible that some sprite is also an iterator.
            # If this is the case, we should add the sprite itself,
            # and not the iterator object.
            if isinstance(sprite, Sprite):
                if not self.has_internal(sprite):
                    self.add_internal(sprite)
                    sprite.add_internal(self)
            else:
                try:
                    # See if sprite is an iterator, like a list or sprite
                    # group.
                    self.add(tuple(sprite))
                except (TypeError, AttributeError):
                    # Not iterable. This is probably a sprite that is not an
                    # instance of the Sprite class or is not an instance of a
                    # subclass of the Sprite class. Alternately, it could be an
                    # old-style sprite group.
                    if hasattr(sprite, '_spritegroup'):
                        for spr in sprite.sprites():
                            if not self.has_internal(spr):
                                self.add_internal(spr)
                                spr.add_internal(self)
                    elif not self.has_internal(sprite):
                        self.add_internal(sprite)
                        sprite.add_internal(self)

    @cython.boundscheck(False)
    @cython.wraparound(False)
    @cython.nonecheck(False)
    @cython.cdivision(True)
    cdef remove(self, tuple sprites):
        # This function behaves essentially the same as Group.add. It first
        # tries to handle each argument as an instance of the Sprite class. If
        # that failes, then it tries to handle the argument as an iterable
        # object. If that failes, then it tries to handle the argument as an
        # old-style sprite group. Lastly, if that fails, it assumes that the
        # normal Sprite methods should be used.
        for sprite in sprites:
            if isinstance(sprite, Sprite):
                if self.has_internal(sprite):
                    self.remove_internal(sprite)
                    sprite.remove_internal(self)
            else:
                try:
                    self.remove(tuple(sprite))
                except (TypeError, AttributeError):
                    if hasattr(sprite, '_spritegroup'):
                        for spr in sprite.sprites():
                            if self.has_internal(spr):
                                self.remove_internal(spr)
                                spr.remove_internal(self)
                    elif self.has_internal(sprite):
                        self.remove_internal(sprite)
                        sprite.remove_internal(self)

    @cython.boundscheck(False)
    @cython.wraparound(False)
    @cython.nonecheck(False)
    @cython.cdivision(True)
    cdef has(self, tuple sprites):
        cdef bint return_value = False

        for sprite in sprites:
            if isinstance(sprite, Sprite):
                # Check for Sprite instance's membership in this group
                if self.has_internal(sprite):
                    return_value = True
                else:
                    return False
            else:
                try:
                    if self.has(tuple(sprite)):
                        return_value = True
                    else:
                        return False
                except (TypeError, AttributeError):
                    if hasattr(sprite, '_spritegroup'):
                        for spr in sprite.sprites():
                            if self.has_internal(spr):
                                return_value = True
                            else:
                                return False
                    else:
                        if self.has_internal(sprite):
                            return_value = True
                        else:
                            return False

        return return_value

    @cython.boundscheck(False)
    @cython.wraparound(False)
    @cython.nonecheck(False)
    @cython.cdivision(True)
    def update(self, *args):

        for s in self.sprites():
            s.update(*args)

    @cython.boundscheck(False)
    @cython.wraparound(False)
    @cython.nonecheck(False)
    @cython.cdivision(True)
    cdef draw(self, surface):
        sprites = self.sprites()
        surface_blit = surface.blit
        for spr in sprites:
            self.spritedict[spr] = surface_blit(spr.image, spr.rect)
        self.lostsprites = []

    def clear(self, surface, bgd):

        if callable(bgd):
            for r in self.lostsprites:
                bgd(surface, r)
            for r in self.spritedict.values():
                if r:
                    bgd(surface, r)
        else:
            surface_blit = surface.blit
            for r in self.lostsprites:
                surface_blit(bgd, r, r)
            for r in self.spritedict.values():
                if r:
                    surface_blit(bgd, r, r)

    def empty(self):
        """remove all sprites

        Group.empty(): return None

        Removes all the sprites from the group.

        """
        for s in self.sprites():
            self.remove_internal(s)
            s.remove_internal(self)

    def __nonzero__(self):
        return truth(self.sprites())

    def __len__(self):
        """return number of sprites in group

        Group.len(group): return int

        Returns the number of sprites contained in the group.

        """
        return len(self.sprites())

    def __repr__(self):
        return "<%s(%d sprites)>" % (self.__class__.__name__, len(self))


class Group(AbstractGroup):

    def __init__(self, *sprites):
        AbstractGroup.__init__(self)
        self.add(*sprites)


@cython.boundscheck(False)
@cython.wraparound(False)
@cython.nonecheck(False)
@cython.cdivision(True)
cdef class LayeredUpdates(AbstractGroup):

    cdef public dict _spritelayers
    cdef public list _spritelist
    cdef public int _default_layer
    cdef public object _init_rect # = Rect(0, 0, 0, 0)   # --> cannot cynthonized
    cdef dict __dict__

    def __cinit__(self, *sprites, **kwargs):

        self._init_rect = Rect(0, 0, 0, 0)
        self._spritelayers = {}
        self._spritelist = []
        AbstractGroup.__init__(self)
        self._default_layer = kwargs.get('default_layer', 0)

        self.add(sprites)


    @cython.boundscheck(False)
    @cython.wraparound(False)
    @cython.nonecheck(False)
    @cython.cdivision(True)
    cpdef add_internal(self, sprite, layer_=None):

        self.spritedict[sprite] = self._init_rect

        cdef int layer
        if layer_ is None:
            try:
                layer = sprite._layer
            except AttributeError:
                layer = sprite._layer = self._default_layer

        elif hasattr(sprite, '_layer'):
            sprite._layer = layer

        cdef list sprites = self._spritelist # speedup
        cdef dict sprites_layers = self._spritelayers
        sprites_layers[sprite] = layer

        # add the sprite at the right position
        # bisect algorithmus
        cdef int leng = len(sprites)
        cdef int low = 0, mid = 0, high = leng -1

        while low <= high:
            mid = low + ((high - low) >> 1)
            if sprites_layers[sprites[mid]] <= layer:
                low = mid + 1
            else:
                high = mid - 1
        # linear search to find final position
        while mid < leng and sprites_layers[sprites[mid]] <= layer:
            mid += 1
        sprites.insert(mid, sprite)


    @cython.boundscheck(False)
    @cython.wraparound(False)
    @cython.nonecheck(False)
    @cython.cdivision(True)
    cpdef add(self, sprites, layer=None):

        if not sprites:
            return

        for sprite in sprites:
            # It's possible that some sprite is also an iterator.
            # If this is the case, we should add the sprite itself,
            # and not the iterator object.
            if isinstance(sprite, Sprite):
                if not self.has_internal(sprite):
                    self.add_internal(sprite, layer)
                    sprite.add_internal(self)
            else:
                try:
                    # See if sprite is an iterator, like a list or sprite
                    # group.
                    self.add(sprite)
                except (TypeError, AttributeError):
                    # Not iterable. This is probably a sprite that is not an
                    # instance of the Sprite class or is not an instance of a
                    # subclass of the Sprite class. Alternately, it could be an
                    # old-style sprite group.
                    if hasattr(sprite, '_spritegroup'):
                        for spr in sprite.sprites():
                            if not self.has_internal(spr):
                                self.add_internal(spr, layer)
                                spr.add_internal(self)
                    elif not self.has_internal(sprite):
                        self.add_internal(sprite, layer)
                        sprite.add_internal(self)


    @cython.boundscheck(False)
    @cython.wraparound(False)
    @cython.nonecheck(False)
    @cython.cdivision(True)
    cpdef remove_internal(self, sprite):
        """Do not use this method directly.

        The group uses it to add a sprite.

        """
        self._spritelist.remove(sprite)
        # these dirty rects are suboptimal for one frame
        r = self.spritedict[sprite]
        if r is not self._init_rect:
            self.lostsprites.append(r) # dirty rect
        if hasattr(sprite, 'rect'):
            self.lostsprites.append(sprite.rect) # dirty rect

        del self.spritedict[sprite]
        del self._spritelayers[sprite]


    @cython.boundscheck(False)
    @cython.wraparound(False)
    @cython.nonecheck(False)
    @cython.cdivision(True)
    cpdef sprites(self):
        """return a ordered list of sprites (first back, last top).

        LayeredUpdates.sprites(): return sprites

        """
        return list(self._spritelist)


    @cython.boundscheck(False)
    @cython.wraparound(False)
    @cython.nonecheck(False)
    @cython.cdivision(True)
    cpdef draw(self, surface):
        cdef dict spritedict = self.spritedict
        cdef dict dirty = self.lostsprites
        self.lostsprites = []
        cdef object init_rect = self._init_rect
        for spr in self.sprites():
            rec = spritedict[spr]
            newrect = surface.blit(spr.image, spr.rect)
            if rec is init_rect:
                dirty.append(newrect)
            else:
                if newrect.colliderect(rec):
                    dirty.append(newrect.union(rec))
                else:
                    dirty.append(newrect)
                    dirty.append(rec)
            spritedict[spr] = newrect
        return dirty

    cdef get_sprites_at(self, pos):
        """return a list with all sprites at that position

        LayeredUpdates.get_sprites_at(pos): return colliding_sprites

        Bottom sprites are listed first; the top ones are listed last.

        """
        _sprites = self._spritelist
        rect = Rect(pos, (0, 0))
        cdef int colliding_idx = rect.collidelistall(_sprites)
        colliding = [_sprites[i] for i in colliding_idx]
        return colliding

    cdef get_sprite(self, int idx):
        """return the sprite at the index idx from the groups sprites

        LayeredUpdates.get_sprite(idx): return sprite

        Raises IndexOutOfBounds if the idx is not within range.

        """
        return self._spritelist[idx]

    cdef remove_sprites_of_layer(self, int layer_nr):
        """remove all sprites from a layer and return them as a list

        LayeredUpdates.remove_sprites_of_layer(layer_nr): return sprites

        """
        sprites = self.get_sprites_from_layer(layer_nr)
        self.remove(tuple(sprites))
        return sprites

    #---# layer methods
    cpdef layers(self):
        """return a list of unique defined layers defined.

        LayeredUpdates.layers(): return layers

        """
        return sorted(set(self._spritelayers.values()))

    cpdef change_layer(self, sprite, new_layer):
        """change the layer of the sprite

        LayeredUpdates.change_layer(sprite, new_layer): return None

        The sprite must have been added to the renderer already. This is not
        checked.

        """
        cdef list sprites = self._spritelist # speedup
        cdef dict sprites_layers = self._spritelayers # speedup

        sprites.remove(sprite)
        sprites_layers.pop(sprite)

        # add the sprite at the right position
        # bisect algorithmus
        cdef int leng = len(sprites)
        cdef int low = 0, mid = 0
        cdef int high = leng -1
        while low <= high:
            mid = low + ((high - low) >> 1)
            if sprites_layers[sprites[mid]] <= new_layer:
                low = mid + 1
            else:
                high = mid - 1
        # linear search to find final position
        while mid < leng and sprites_layers[sprites[mid]] <= new_layer:
            mid += 1
        sprites.insert(mid, sprite)
        if hasattr(sprite, 'layer'):
            sprite.layer = new_layer

        # add layer info
        sprites_layers[sprite] = new_layer

    cpdef get_layer_of_sprite(self, sprite):
        """return the layer that sprite is currently in

        If the sprite is not found, then it will return the default layer.

        """
        return self._spritelayers.get(sprite, self._default_layer)

    cpdef get_top_layer(self):
        """return the top layer

        LayeredUpdates.get_top_layer(): return layer

        """
        return self._spritelayers[self._spritelist[-1]]

    cpdef get_bottom_layer(self):
        """return the bottom layer

        LayeredUpdates.get_bottom_layer(): return layer

        """
        return self._spritelayers[self._spritelist[0]]

    cpdef move_to_front(self, sprite):
        """bring the sprite to front layer

        LayeredUpdates.move_to_front(sprite): return None

        Brings the sprite to front by changing the sprite layer to the top-most
        layer. The sprite is added at the end of the list of sprites in that
        top-most layer.

        """
        self.change_layer(sprite, self.get_top_layer())

    cpdef move_to_back(self, sprite):
        """move the sprite to the bottom layer

        LayeredUpdates.move_to_back(sprite): return None

        Moves the sprite to the bottom layer by moving it to a new layer below
        the current bottom layer.

        """
        self.change_layer(sprite, self.get_bottom_layer() - 1)

    cpdef get_top_sprite(self):
        """return the topmost sprite

        LayeredUpdates.get_top_sprite(): return Sprite

        """
        return self._spritelist[-1]

    cpdef get_sprites_from_layer(self, layer):
        """return all sprites from a layer ordered as they where added

        LayeredUpdates.get_sprites_from_layer(layer): return sprites

        Returns all sprites from a layer. The sprites are ordered in the
        sequence that they where added. (The sprites are not removed from the
        layer.

        """
        sprites = []
        sprites_append = sprites.append
        sprite_layers = self._spritelayers
        for spr in self._spritelist:
            if sprite_layers[spr] == layer:
                sprites_append(spr)
            elif sprite_layers[spr] > layer:# break after because no other will
                                            # follow with same layer
                break
        return sprites

    cpdef switch_layer(self, layer1_nr, layer2_nr):
        """switch the sprites from layer1_nr to layer2_nr

        LayeredUpdates.switch_layer(layer1_nr, layer2_nr): return None

        The layers number must exist. This method does not check for the
        existence of the given layers.

        """
        sprites1 = self.remove_sprites_of_layer(layer1_nr)
        for spr in self.get_sprites_from_layer(layer2_nr):
            self.change_layer(spr, layer1_nr)
        self.add(sprites1, layer=layer2_nr)