from __future__ import absolute_import, division, print_function

from qtpy import compat
from glue import config

from glue.core.io.subset_mask import SubsetMaskImporter, SubsetMaskExporter

__all__ = ['QtSubsetMaskImporter', 'QtSubsetMaskExporter']


def _make_filters_dict(registry):

    filters = {}
    for e in registry:
        if e.extension == '':
            fltr = "{0} (*)".format(e.label)
        else:
            fltr = "{0} ({1})".format(e.label, ' '.join('*.' + ext for ext in e.extension))
        filters[fltr] = e.function

    return filters


class QtSubsetMaskImporter(SubsetMaskImporter):

    def get_filename_and_reader(self):

        subset_mask_importers = _make_filters_dict(config.subset_mask_importer)

        filters = ';;'.join(sorted(subset_mask_importers))

        filename, fltr = compat.getopenfilename(caption="Choose a subset mask file",
                                                filters=filters)

        filename = str(filename)

        if filename:
            return filename, subset_mask_importers[fltr]
        else:
            return None, None


class QtSubsetMaskExporter(SubsetMaskExporter):

    def get_filename_and_writer(self):

        subset_mask_exporters = _make_filters_dict(config.subset_mask_exporter)

        filters = ';;'.join(sorted(subset_mask_exporters))

        filename, fltr = compat.getsavefilename(caption="Choose a subset mask filename",
                                                filters=filters)

        filename = str(filename)

        if filename:
            return filename, subset_mask_exporters[fltr]
        else:
            return None, None
