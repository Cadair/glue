"""
Matplotlib artist for fixed resolution buffers.
"""

from __future__ import print_function, division

from mpl_scatter_density.base_image_artist import BaseImageArtist

import numpy as np


class FRBArtist(BaseImageArtist):

    def __init__(self, ax, **kwargs):
        self._array_maker = None
        super(FRBArtist, self).__init__(ax, update_while_panning=False,
                                        array_func=self.array_func_wrapper,
                                        **kwargs)

    def array_func_wrapper(self, bins=None, range=None):
        if self._array_maker is None:
            return np.array([[np.nan]])
        else:
            ny, nx = bins
            (ymin, ymax), (xmin, xmax) = range
            bounds = [(ymin, ymax, ny), (xmin, xmax, nx)]
            array = self._array_maker.get_array(bounds)
            if array is None:
                return np.array([[np.nan]])
            else:
                return array

    def set_array_maker(self, array_maker):
        self._array_maker = array_maker

    def invalidate_cache(self):
        self.stale = True
        self.set_visible(True)


def imshow(axes, X, aspect=None, vmin=None, vmax=None, **kwargs):
    """
    Similar to matplotlib's imshow command, but produces a FRBArtist
    """

    axes.set_aspect(aspect)

    im = FRBArtist(axes, **kwargs)

    im.set_array_maker(X)
    axes._set_artist_props(im)

    if im.get_clip_path() is None:
        # image does not already have clipping set, clip to axes patch
        im.set_clip_path(axes.patch)

    if vmin is not None or vmax is not None:
        im.set_clim(vmin, vmax)

    axes.images.append(im)

    def remove(h):
        axes.images.remove(h)

    # The following is needed for Matplotlib's .remove() method to work
    im._remove_method = remove

    return im
