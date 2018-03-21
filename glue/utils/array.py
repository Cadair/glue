from __future__ import absolute_import, division, print_function

import numpy as np
from numpy.lib.stride_tricks import as_strided

import pandas as pd

from glue.external.six import string_types


__all__ = ['unique', 'shape_to_string', 'view_shape', 'stack_view',
           'coerce_numeric', 'check_sorted', 'broadcast_to', 'unbroadcast',
           'iterate_chunks']


def unbroadcast(array):
    """
    Given an array, return a new array that is the smallest subset of the
    original array that can be re-broadcasted back to the original array.

    See https://stackoverflow.com/questions/40845769/un-broadcasting-numpy-arrays
    for more details.
    """

    if array.ndim == 0:
        return array

    new_shape = np.where(np.array(array.strides) == 0, 1, array.shape)
    return as_strided(array, shape=new_shape)


def unique(array):
    """
    Return the unique elements of the array U, as well as
    the index array I such that U[I] == array

    Parameters
    ----------
    array : `numpy.ndarray`
        The array to use

    Returns
    -------
    U : `numpy.ndarray`
        The unique elements of the array
    I : `numpy.ndarray`
        The indices such that ``U[I] == array``
    """
    # numpy.unique doesn't handle mixed-types on python3,
    # so we use pandas
    U, I = pd.factorize(array, sort=True)
    return I, U


def shape_to_string(shape):
    """
    On Windows, shape tuples use long ints which results in formatted shapes
    such as (2L, 3L). This function ensures that the shape is always formatted
    without the Ls.
    """
    return "({0})".format(", ".join(str(int(item)) for item in shape))


def view_shape(shape, view):
    """
    Return the shape of a view of an array.

    Returns equivalent of ``np.zeros(shape)[view].shape`` but with minimal
    memory usage.

    Parameters
    ----------
    shape : tuple
        The shape of the array
    view : slice
        A valid index into a Numpy array, or None
    """
    if view is None:
        return shape
    else:
        return np.broadcast_to(1, shape)[view].shape


def stack_view(shape, *views):
    shp = tuple(slice(0, s, 1) for s in shape)
    result = np.broadcast_arrays(*np.ogrid[shp])
    for v in views:
        if isinstance(v, string_types) and v == 'transpose':
            result = [r.T for r in result]
            continue

        result = [r[v] for r in result]

    return tuple(result)


def coerce_numeric(arr):
    """
    Coerce an array into a numeric array, replacing non-numeric elements with
    nans.

    If the array is already a numeric type, it is returned unchanged

    Parameters
    ----------
    arr : `numpy.ndarray`
        The array to coerce
    """

    # Already numeric type
    if np.issubdtype(arr.dtype, np.number):
        return arr

    # Numpy datetime64 format
    if np.issubdtype(arr.dtype, np.datetime64):
        return arr

    # Convert booleans to integers
    if np.issubdtype(arr.dtype, np.bool_):
        return arr.astype(np.int)

    # a string dtype, or anything else
    try:
        return pd.to_numeric(arr, errors='coerce')
    except AttributeError:  # pandas < 0.19
        return pd.Series(arr).convert_objects(convert_numeric=True).values


def check_sorted(array):
    """
    Return `True` if the array is sorted, `False` otherwise.
    """
    # this ignores NANs, and does the right thing if nans
    # are concentrated at beginning or end of array
    # otherwise, it will miss things at nan/finite boundaries
    array = np.asarray(array)
    return not (array[:-1] > array[1:]).any()


def pretty_number(numbers):
    """
    Convert a list/array of numbers into a nice list of strings

    Parameters
    ----------
    numbers : list
        The numbers to convert
    """
    try:
        return [pretty_number(n) for n in numbers]
    except TypeError:
        pass

    n = numbers
    if n == 0:
        result = '0'
    elif (abs(n) < 1e-3) or (abs(n) > 1e3):
        result = "%0.3e" % n
    elif abs(int(n) - n) < 1e-3 and int(n) != 0:
        result = "%i" % n
    else:
        result = "%0.3f" % n
        if result.find('.') != -1:
            result = result.rstrip('0')

    return result


def broadcast_to(array, shape):
    """
    Compatibility function - can be removed once we support only Numpy 1.10
    and above
    """
    try:
        return np.broadcast_to(array, shape)
    except AttributeError:
        array = np.asarray(array)
        return np.broadcast_arrays(array, np.ones(shape, array.dtype))[0]


def find_chunk_shape(shape, n_max=None):
    """
    Given the shape of an n-dimensional array, and the maximum number of
    elements in a chunk, return the largest chunk shape to use for iteration.

    This currently assumes the optimal chunk shape to return is for C-contiguous
    arrays.
    """

    if n_max is None:
        return tuple(shape)

    block_shape = []

    max_repeat_remaining = n_max

    for size in shape[::-1]:

        if max_repeat_remaining > size:
            block_shape.append(size)
            max_repeat_remaining = max_repeat_remaining // size
        else:
            block_shape.append(max_repeat_remaining)
            max_repeat_remaining = 1

    return tuple(block_shape[::-1])


def iterate_chunks(shape, chunk_shape=None, n_max=None):
    """
    Given a data shape and a chunk shape (or maximum chunk size), iteratively
    return slice objects that can be used to slice the array.
    """

    if chunk_shape is None and n_max is None:
        raise ValueError('Either chunk_shape or n_max should be specified')
    elif chunk_shape is not None and n_max is not None:
        raise ValueError('Either chunk_shape or n_max should be specified (not both)')
    elif chunk_shape is None:
        chunk_shape = find_chunk_shape(shape, n_max)
    else:
        if len(chunk_shape) != len(shape):
            raise ValueError('chunk_shape should have the same length as shape')
        elif any(x > y for (x, y) in zip(chunk_shape, shape)):
            raise ValueError('chunk_shape should fit within shape')

    ndim = len(chunk_shape)
    start_index = [0] * ndim

    shape = list(shape)

    while start_index <= shape:

        end_index = [min(start_index[i] + chunk_shape[i], shape[i]) for i in range(ndim)]

        slices = [slice(start_index[i], end_index[i]) for i in range(ndim)]

        yield slices

        # Update chunk index. What we do is to increment the
        # counter for the first dimension, and then if it
        # exceeds the number of elements in that direction,
        # cycle back to zero and advance in the next dimension,
        # and so on.
        start_index[0] += chunk_shape[0]
        for i in range(ndim - 1):
            if start_index[i] >= shape[i]:
                start_index[i] = 0
                start_index[i + 1] += chunk_shape[i + 1]

        # We can now check whether the iteration is finished
        if start_index[-1] >= shape[-1]:
            break
