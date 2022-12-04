# distutils: extra_compile_args = -fopenmp
# distutils: extra_link_args = -fopenmp

from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
import numpy


ext_modules = [Extension("MAPPING", ["Mapping.pyx"],
                         include_dirs=[numpy.get_include()],
                         extra_compile_args=['/openmp']
                         
                         ),

               Extension("bloom", ["bloom.pyx"],
                         include_dirs=[numpy.get_include()],
                         extra_compile_args=['/openmp']),
                         
               Extension("FLARES", ["Flares.pyx"],
                         include_dirs=[numpy.get_include()],
                         extra_compile_args=['/openmp'])
                        

               ]

setup(
  name="FLARES",
  cmdclass={"build_ext": build_ext},
  ext_modules=ext_modules,
  include_dirs=[numpy.get_include()]
)
