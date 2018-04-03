# pylint: disable=I0011,W0613,W0201,W0212,E1101,E1103

from __future__ import absolute_import, division, print_function

import os

import numpy as np

from numpy.testing import assert_equal, assert_allclose

from glue.core import Data
from glue.core.roi import XRangeROI
from glue.app.qt import GlueApplication
from glue.core.component_link import ComponentLink
from glue.viewers.matplotlib.qt.tests.test_data_viewer import BaseTestMatplotlibDataViewer
from glue.viewers.profile.tests.test_state import SimpleCoordinates

from ..data_viewer import ProfileViewer

DATA = os.path.join(os.path.dirname(__file__), 'data')


class TestProfileCommon(BaseTestMatplotlibDataViewer):
    def init_data(self):
        return Data(label='d1',
                    x=np.random.random(24).reshape((3, 4, 2)))
    viewer_cls = ProfileViewer


class TestProfileViewer(object):

    def setup_method(self, method):

        self.data = Data(label='d1')
        self.data.coords = SimpleCoordinates()
        self.data['x'] = np.arange(24).reshape((3, 4, 2))

        self.app = GlueApplication()
        self.session = self.app.session
        self.hub = self.session.hub

        self.data_collection = self.session.data_collection
        self.data_collection.append(self.data)

        self.viewer = self.app.new_data_viewer(ProfileViewer)

    def teardown_method(self, method):
        self.viewer.close()

    def test_functions(self):
        self.viewer.add_data(self.data)
        self.viewer.state.function = np.nanmean
        assert len(self.viewer.layers) == 1
        layer_artist = self.viewer.layers[0]
        assert_allclose(layer_artist._visible_data[0], [0, 1, 2])
        assert_allclose(layer_artist._visible_data[1], [3.5, 11.5, 19.5])

    def test_incompatible(self):
        self.viewer.add_data(self.data)
        data2 = Data(y=np.random.random((3, 4, 2)))
        self.data_collection.append(data2)
        self.viewer.add_data(data2)
        assert len(self.viewer.layers) == 2
        assert self.viewer.layers[0].enabled
        assert not self.viewer.layers[1].enabled

    def test_selection(self):

        self.viewer.add_data(self.data)

        self.viewer.state.x_att = self.data.pixel_component_ids[0]

        roi = XRangeROI(0.9, 2.1)

        self.viewer.apply_roi(roi)

        assert len(self.data.subsets) == 1
        assert_equal(self.data.subsets[0].to_mask()[:, 0, 0], [0, 1, 1])

        self.viewer.state.x_att = self.data.world_component_ids[0]

        roi = XRangeROI(1.9, 3.1)

        self.viewer.apply_roi(roi)

        assert len(self.data.subsets) == 1
        assert_equal(self.data.subsets[0].to_mask()[:, 0, 0], [0, 1, 0])

    def test_enabled_layers(self):

        data2 = Data(label='d1', y=np.arange(24).reshape((3, 4, 2)))
        self.data_collection.append(data2)

        self.viewer.add_data(self.data)
        self.viewer.add_data(data2)

        assert self.viewer.layers[0].enabled
        assert not self.viewer.layers[1].enabled

        self.data_collection.add_link(ComponentLink([data2.world_component_ids[1]], self.data.world_component_ids[0], using=lambda x: 2 * x))

        assert self.viewer.layers[0].enabled
        assert not self.viewer.layers[1].enabled

        self.data_collection.add_link(ComponentLink([data2.id['y']], self.data.id['x'], using=lambda x: 3 * x))

        assert self.viewer.layers[0].enabled
        assert self.viewer.layers[1].enabled
