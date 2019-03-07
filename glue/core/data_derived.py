# Base classes for various types of derived datasets - these are basically
# wrapper classes around data objects that modify the data in some way
# on-the-fly. These work by exposting the common data API described in
# http://docs.glueviz.org/en/stable/developer_guide/data.html and transparently
# applying changes.

from glue.core.hub import HubListener
from glue.core.data import BaseCartesianData
from glue.core.message import NumericalDataChangedMessage
from glue.core.subset import SliceSubsetState


class DerivedData(BaseCartesianData):
    """
    Base class for all derived data classes.
    """


class IndexedData(BaseCartesianData, HubListener):
    """
    A dataset where some dimensions have been removed via indexing.

    The indices can be modified after the data has been created using the
    ``indices`` property.

    Parameters
    ----------
    original_data : `~glue.core.data.BaseCartesianData`
        The original data to reduce the dimension of
    indices : tuple of `int` or `None`
        The indices to apply to the data, or `None` if a dimension should be
        preserved. This tuple should have as many elements as there are
        dimensions in ``original_data``.
    """

    def __init__(self, original_data, indices):

        super(IndexedData, self).__init__()

        if len(indices) != original_data.ndim:
            raise ValueError("The 'indices' tuple should have length {0}"
                             .format(original_data.ndim))

        self._original_data = original_data
        self.indices = indices

    @property
    def indices(self):
        return self._indices

    @indices.setter
    def indices(self, value):

        if len(value) != self._original_data.ndim:
            raise ValueError("The 'indices' tuple should have length {0}"
                             .format(self._original_data.ndim))

        # For now we require the indices to be in the same position, i.e. we
        # don't allow changes in dimensionality of the derived dataset.
        if hasattr(self, '_indices'):
            changed = False
            for idim in range(self._original_data.ndim):
                before, after = self._indices[idim], value[idim]
                if type(before) != type(after):
                    raise TypeError("Can't change where the ``None`` values are in indices")
                elif before != after:
                    changed = True
        else:
            changed = False

        self._indices = value

        # Compute a subset state that represents the indexing - this is used
        # for compute_statistic and compute_histogram
        slices = [slice(x) if x is None else x for x in self._indices]
        self._indices_subset_state = SliceSubsetState(self._original_data, slices)

        # Construct a list of original pixel component IDs
        self._original_pixel_cids = []
        for idim in range(self._original_data.ndim):
            if self._indices[idim] is None:
                self._original_pixel_cids.append(self._original_data.pixel_component_ids[idim])

        # Tell glue that the data has changed
        if changed and self.hub is not None:
            msg = NumericalDataChangedMessage(self)
            self.hub.broadcast(msg)

    @property
    def label(self):
        slice = '[' + ','.join([':' if x is None else str(x) for x in self._indices]) + ']'
        return self._original_data.label + slice

    @property
    def shape(self):
        shape = []
        for idim in range(self._original_data.ndim):
            if self.indices[idim] is None:
                shape.append(self._original_data.shape[idim])
        return tuple(shape)

    @property
    def main_components(self):
        return self._original_data.main_components

    def get_kind(self, cid):
        return self._original_data.get_kind(cid)

    def _to_original_view(self, view):
        if view is None:
            view = [slice(None)] * self.ndim
        original_view = list(self.indices)
        idim_reduced = 0
        for idim in range(self._original_data.ndim):
            if original_view[idim] is None:
                if view is None:
                    original_view[idim] = slice(None)
                else:
                    original_view[idim] = view[idim_reduced]
                idim_reduced += 1
        return tuple(original_view)

    def register_to_hub(self, hub):
        hub.subscribe(self, NumericalDataChangedMessage,
                      handler=self._check_for_original_changes)
        super(IndexedData, self).register_to_hub(hub)

    def _check_for_original_changes(self, message):
        # If the parent's values are changed, we should assume the values
        # of the current dataset have changed too
        if message.data is self._original_data:
            msg = NumericalDataChangedMessage(self)
            self.hub.broadcast(msg)

    def get_data(self, cid, view=None):
        if cid in self.pixel_component_ids:
            cid = self._original_pixel_cids[cid.axis]
        original_view = self._to_original_view(view)
        return self._original_data.get_data(cid, view=original_view)

    def get_mask(self, subset_state, view=None):
        original_view = self._to_original_view(view)
        return self._original_data.get_mask(subset_state, view=original_view)

    def compute_fixed_resolution_buffer(self, *args, **kwargs):
        from glue.core.fixed_resolution_buffer import compute_fixed_resolution_buffer
        return compute_fixed_resolution_buffer(self, *args, **kwargs)

    def compute_statistic(self, *args, **kwargs):
        kwargs['view'] = self._to_original_view(kwargs.get('view'))
        return self._original_data.compute_statistic(*args, **kwargs)

    def compute_histogram(self, *args, **kwargs):
        if kwargs.get('subset_state') is None:
            kwargs['subset_state'] = self._indices_subset_state
        else:
            kwargs['subset_state'] &= self._indices_subset_state
        return self._original_data.compute_histogram(*args, **kwargs)
