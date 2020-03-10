# This file was automatically generated by SWIG (http://www.swig.org).
# Version 4.0.1
#
# Do not make changes to this file unless you know what you are doing--modify
# the SWIG interface file instead.


from __future__ import absolute_import



from sys import version_info as _swig_python_version_info
if _swig_python_version_info < (2, 7, 0):
    raise RuntimeError("Python 2.7 or later required")

# Import the low-level C/C++ module
if __package__ or "." in __name__:
    from . import _EggNetExtension
else:
    import _EggNetExtension

try:
    import builtins as __builtin__
except ImportError:
    import __builtin__

def _swig_repr(self):
    try:
        strthis = "proxy of " + self.this.__repr__()
    except __builtin__.Exception:
        strthis = ""
    return "<%s.%s; %s >" % (self.__class__.__module__, self.__class__.__name__, strthis,)


def _swig_setattr_nondynamic_instance_variable(set):
    def set_instance_attr(self, name, value):
        if name == "thisown":
            self.this.own(value)
        elif name == "this":
            set(self, name, value)
        elif hasattr(self, name) and isinstance(getattr(type(self), name), property):
            set(self, name, value)
        else:
            raise AttributeError("You cannot add instance attributes to %s" % self)
    return set_instance_attr


def _swig_setattr_nondynamic_class_variable(set):
    def set_class_attr(cls, name, value):
        if hasattr(cls, name) and not isinstance(getattr(cls, name), property):
            set(cls, name, value)
        else:
            raise AttributeError("You cannot add class attributes to %s" % cls)
    return set_class_attr


def _swig_add_metaclass(metaclass):
    """Class decorator for adding a metaclass to a SWIG wrapped class - a slimmed down version of six.add_metaclass"""
    def wrapper(cls):
        return metaclass(cls.__name__, cls.__bases__, cls.__dict__.copy())
    return wrapper


class _SwigNonDynamicMeta(type):
    """Meta class to enforce nondynamic attributes (no new attributes) for a class"""
    __setattr__ = _swig_setattr_nondynamic_class_variable(type.__setattr__)



def relu_float_inplace(x: "float *") -> "int":
    return _EggNetExtension.relu_float_inplace(x)

def relu_double_inplace(x: "double *") -> "int":
    return _EggNetExtension.relu_double_inplace(x)

def relu_int8_t_inplace(x: "int8_t *") -> "int":
    return _EggNetExtension.relu_int8_t_inplace(x)

def relu_int16_t_inplace(x: "int16_t *") -> "int":
    return _EggNetExtension.relu_int16_t_inplace(x)

def relu_int32_t_inplace(x: "int32_t *") -> "int":
    return _EggNetExtension.relu_int32_t_inplace(x)

def relu_int64_t_inplace(x: "int64_t *") -> "int":
    return _EggNetExtension.relu_int64_t_inplace(x)

def relu_uint8_t_inplace(x: "uint8_t *") -> "int":
    return _EggNetExtension.relu_uint8_t_inplace(x)

def relu_uint16_t_inplace(x: "uint16_t *") -> "int":
    return _EggNetExtension.relu_uint16_t_inplace(x)

def relu_uint32_t_inplace(x: "uint32_t *") -> "int":
    return _EggNetExtension.relu_uint32_t_inplace(x)

def relu_uint64_t_inplace(x: "uint64_t *") -> "int":
    return _EggNetExtension.relu_uint64_t_inplace(x)

def conv2d_float(data_in: "float const *", kernel: "float const *", stride: "int") -> "int *":
    return _EggNetExtension.conv2d_float(data_in, kernel, stride)

def conv2d_double(data_in: "double const *", kernel: "double const *", stride: "int") -> "int *":
    return _EggNetExtension.conv2d_double(data_in, kernel, stride)

def conv2d_int8_t(data_in: "int8_t const *", kernel: "int8_t const *", stride: "int") -> "int *":
    return _EggNetExtension.conv2d_int8_t(data_in, kernel, stride)

def conv2d_int16_t(data_in: "int16_t const *", kernel: "int16_t const *", stride: "int") -> "int *":
    return _EggNetExtension.conv2d_int16_t(data_in, kernel, stride)

def conv2d_int32_t(data_in: "int32_t const *", kernel: "int32_t const *", stride: "int") -> "int *":
    return _EggNetExtension.conv2d_int32_t(data_in, kernel, stride)

def conv2d_int64_t(data_in: "int64_t const *", kernel: "int64_t const *", stride: "int") -> "int *":
    return _EggNetExtension.conv2d_int64_t(data_in, kernel, stride)

def conv2d_uint8_t(data_in: "uint8_t const *", kernel: "uint8_t const *", stride: "int") -> "int *":
    return _EggNetExtension.conv2d_uint8_t(data_in, kernel, stride)

def conv2d_uint16_t(data_in: "uint16_t const *", kernel: "uint16_t const *", stride: "int") -> "int *":
    return _EggNetExtension.conv2d_uint16_t(data_in, kernel, stride)

def conv2d_uint32_t(data_in: "uint32_t const *", kernel: "uint32_t const *", stride: "int") -> "int *":
    return _EggNetExtension.conv2d_uint32_t(data_in, kernel, stride)

def conv2d_uint64_t(data_in: "uint64_t const *", kernel: "uint64_t const *", stride: "int") -> "int *":
    return _EggNetExtension.conv2d_uint64_t(data_in, kernel, stride)

def NNE_print_error(code: "int") -> "char const *":
    return _EggNetExtension.NNE_print_error(code)

def conv2d(data_in: "float const *", kernel: "float const *", stride: "int") -> "int *":
    return _EggNetExtension.conv2d(data_in, kernel, stride)

def conv2d_3x3(data_in: "float const *", kernel: "float const *") -> "int *":
    return _EggNetExtension.conv2d_3x3(data_in, kernel)

def maxPool2D(data_in: "float const *") -> "int *":
    return _EggNetExtension.maxPool2D(data_in)

def relu1D(x: "float *") -> "int":
    return _EggNetExtension.relu1D(x)

def relu2D(x2: "float *") -> "int":
    return _EggNetExtension.relu2D(x2)

def relu3D(x3: "float *") -> "int":
    return _EggNetExtension.relu3D(x3)

def relu4D(x4: "float *") -> "int":
    return _EggNetExtension.relu4D(x4)


