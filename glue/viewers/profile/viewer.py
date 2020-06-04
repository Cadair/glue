from glue.core.subset import roi_to_subset_state
from glue.core.coordinates import Coordinates, LegacyCoordinates
from astropy.wcs import WCS
from astropy.visualization.wcsaxes.frame import RectangularFrame1D

__all__ = ['MatplotlibProfileMixin']


def get_identity_wcs(naxis):

    wcs = WCS(naxis=naxis)
    wcs.wcs.ctype = ['X'] * naxis
    wcs.wcs.crval = [0.] * naxis
    wcs.wcs.crpix = [1.] * naxis
    wcs.wcs.cdelt = [1.] * naxis

    return wcs


class MatplotlibProfileMixin(object):

    def setup_callbacks(self):
        self.state.add_callback('x_att', self._update_axes)
        self.state.add_callback('normalize', self._update_axes)
        # self.axes.set_adjustable('datalim')
        self.state.add_callback('x_att', self._set_wcs)
        self.state.add_callback('reference_data', self._set_wcs)

    def _update_axes(self, *args):

        # if self.state.x_att is not None:
        #     self.state.x_axislabel = self.state.x_att.label

        # if self.state.normalize:
        #     self.state.y_axislabel = 'Normalized data values'
        # else:
        #     self.state.y_axislabel = 'Data values'

        self.axes.figure.canvas.draw_idle()

    def apply_roi(self, roi, override_mode=None):

        # Force redraw to get rid of ROI. We do this because applying the
        # subset state below might end up not having an effect on the viewer,
        # for example there may not be any layers, or the active subset may not
        # be one of the layers. So we just explicitly redraw here to make sure
        # a redraw will happen after this method is called.
        self.redraw()

        if len(self.layers) == 0:
            return

        subset_state = roi_to_subset_state(roi, x_att=self.state.x_att)
        self.apply_subset_state(subset_state, override_mode=override_mode)

    def _set_wcs(self, event=None, relim=True):
        ref_coords = getattr(self.state.reference_data, 'coords', None)

        print(f"{self.state.wcsaxes_slice=}, {ref_coords=}")

        self.axes.frame_class = RectangularFrame1D
        if ref_coords is None or isinstance(ref_coords, LegacyCoordinates):
            self.axes.reset_wcs(slices=self.state.wcsaxes_slice,
                                wcs=get_identity_wcs(self.state.reference_data.ndim))
        else:
            self.axes.reset_wcs(slices=self.state.wcsaxes_slice, wcs=ref_coords)

        # Reset the axis labels to match the fact that the new axes have no labels
        self.state.x_axislabel = ''
        self.state.y_axislabel = ''

        self._update_appearance_from_settings()
        self._update_axes()

        self.update_x_ticklabel()
        self.update_y_ticklabel()

        if relim:
            self.state.reset_limits()
