from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
import Cython.Compiler.Options 

Cython.Compiler.Options.annotate = True

ext_modules = [Extension("mciso", ["mciso.pyx"],extra_compile_args=['/O2','/openmp','/fp:fast'])]
#ext_modules = [Extension("cmolcore", ["cmolcore.pyx"],extra_compile_args=['/openmp'])]

setup(
  name = 'Marching Cube script',
  cmdclass = {'build_ext': build_ext},
  ext_modules = ext_modules
)
