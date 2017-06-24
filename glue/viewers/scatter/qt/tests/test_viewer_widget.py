# pylint: disable=I0011,W0613,W0201,W0212,E1101,E1103

from __future__ import absolute_import, division, print_function

import os

import pytest

from numpy.testing import assert_allclose

from glue.core import Data
from glue.core.roi import RectangularROI
from glue.core.subset import RoiSubsetState, AndState
from glue import core
from glue.core.component_id import ComponentID
from glue.core.tests.util import simple_session
from glue.utils.qt import combo_as_string
from glue.viewers.common.qt.tests.test_mpl_data_viewer import BaseTestMatplotlibDataViewer
from glue.core.state import GlueUnSerializer

from ..data_viewer import ScatterViewer

DATA = os.path.join(os.path.dirname(__file__), 'data')


class TestScatterCommon(BaseTestMatplotlibDataViewer):
    def init_data(self):
        return Data(label='d1', x=[3.4, 2.3, -1.1, 0.3], y=['a', 'b', 'c', 'a'])
    viewer_cls = ScatterViewer


class TestScatterViewer(object):

    def setup_method(self, method):

        self.data = Data(label='d1', x=[3.4, 2.3, -1.1, 0.3],
                         y=[3.2, 3.3, 3.4, 3.5], z=['a', 'b', 'c', 'a'])
        self.data_2d = Data(label='d2', a=[[1, 2], [3, 4]], b=[[5, 6], [7, 8]])

        self.session = simple_session()
        self.hub = self.session.hub

        self.data_collection = self.session.data_collection
        self.data_collection.append(self.data)
        self.data_collection.append(self.data_2d)

        self.viewer = ScatterViewer(self.session)

        self.data_collection.register_to_hub(self.hub)
        self.viewer.register_to_hub(self.hub)

    def teardown_method(self, method):
        self.viewer.close()

    def test_basic(self):

        viewer_state = self.viewer.state

        # Check defaults when we add data
        self.viewer.add_data(self.data)

        assert combo_as_string(self.viewer.options_widget().ui.combodata_x_att) == 'x:y:z'
        assert combo_as_string(self.viewer.options_widget().ui.combodata_y_att) == 'x:y:z'

        assert viewer_state.x_att is self.data.id['x']
        assert viewer_state.x_min == -1.1
        assert viewer_state.x_max == 3.4

        assert viewer_state.y_att is self.data.id['y']
        assert viewer_state.y_min == 3.2
        assert viewer_state.y_max == 3.5

        assert not viewer_state.x_log
        assert not viewer_state.y_log

        assert len(viewer_state.layers) == 1

        # Change to categorical component and check new values

        viewer_state.y_att = self.data.id['z']

        assert viewer_state.x_att is self.data.id['x']
        assert viewer_state.x_min == -1.1
        assert viewer_state.x_max == 3.4

        assert viewer_state.y_att is self.data.id['z']
        assert viewer_state.y_min == -0.5
        assert viewer_state.y_max == 2.5

        assert not viewer_state.x_log
        assert not viewer_state.y_log

    def test_flip(self):

        viewer_state = self.viewer.state

        self.viewer.add_data(self.data)

        assert viewer_state.x_min == -1.1
        assert viewer_state.x_max == 3.4

        self.viewer.options_widget().button_flip_x.click()

        assert viewer_state.x_min == 3.4
        assert viewer_state.x_max == -1.1

        assert viewer_state.y_min == 3.2
        assert viewer_state.y_max == 3.5

        self.viewer.options_widget().button_flip_y.click()

        assert viewer_state.y_min == 3.5
        assert viewer_state.y_max == 3.2

    def test_remove_data(self):
        self.viewer.add_data(self.data)
        assert combo_as_string(self.viewer.options_widget().ui.combodata_x_att) == 'x:y:z'
        assert combo_as_string(self.viewer.options_widget().ui.combodata_y_att) == 'x:y:z'
        self.data_collection.remove(self.data)
        assert combo_as_string(self.viewer.options_widget().ui.combodata_x_att) == ''
        assert combo_as_string(self.viewer.options_widget().ui.combodata_y_att) == ''

    def test_update_component_updates_title(self):
        self.viewer.add_data(self.data)
        assert self.viewer.windowTitle() == '2D Scatter'
        self.viewer.state.x_att = self.data.id['y']
        assert self.viewer.windowTitle() == '2D Scatter'

    def test_combo_updates_with_component_add(self):
        self.viewer.add_data(self.data)
        self.data.add_component([3, 4, 1, 2], 'a')
        assert self.viewer.state.x_att is self.data.id['x']
        assert self.viewer.state.y_att is self.data.id['y']
        assert combo_as_string(self.viewer.options_widget().ui.combodata_x_att) == 'x:y:z:a'
        assert combo_as_string(self.viewer.options_widget().ui.combodata_y_att) == 'x:y:z:a'

    def test_nonnumeric_first_component(self):
        # regression test for #208. Shouldn't complain if
        # first component is non-numerical
        data = core.Data()
        data.add_component(['a', 'b', 'c'], label='c1')
        data.add_component([1, 2, 3], label='c2')
        self.data_collection.append(data)
        self.viewer.add_data(data)

    def test_apply_roi(self):

        self.viewer.add_data(self.data)

        roi = RectangularROI(0, 3, 3.25, 3.45)

        assert len(self.viewer.layers) == 1

        self.viewer.apply_roi(roi)

        assert len(self.viewer.layers) == 2
        assert len(self.data.subsets) == 1

        assert_allclose(self.data.subsets[0].to_mask(), [0, 1, 0, 0])

        state = self.data.subsets[0].subset_state
        assert isinstance(state, RoiSubsetState)

    def test_apply_roi_categorical(self):

        viewer_state = self.viewer.state

        self.viewer.add_data(self.data)

        viewer_state.y_att = self.data.id['z']

        roi = RectangularROI(0, 3, -0.4, 0.3)

        assert len(self.viewer.layers) == 1

        self.viewer.apply_roi(roi)

        assert len(self.viewer.layers) == 2
        assert len(self.data.subsets) == 1

        assert_allclose(self.data.subsets[0].to_mask(), [0, 0, 0, 1])

        state = self.data.subsets[0].subset_state
        assert isinstance(state, AndState)

    def test_axes_labels(self):

        viewer_state = self.viewer.state

        self.viewer.add_data(self.data)

        assert self.viewer.axes.get_xlabel() == 'x'
        assert self.viewer.axes.get_ylabel() == 'y'

        viewer_state.x_log = True

        assert self.viewer.axes.get_xlabel() == 'Log x'
        assert self.viewer.axes.get_ylabel() == 'y'

        viewer_state.x_att = self.data.id['y']

        assert self.viewer.axes.get_xlabel() == 'y'
        assert self.viewer.axes.get_ylabel() == 'y'

        viewer_state.y_log = True

        assert self.viewer.axes.get_xlabel() == 'y'
        assert self.viewer.axes.get_ylabel() == 'Log y'

    def test_component_replaced(self):

        # regression test for 508 - if a component ID is replaced, we should
        # make sure that the component ID is selected if the old component ID
        # was selected

        self.viewer.add_data(self.data)
        self.viewer.state.x_att = self.data.components[0]
        test = ComponentID('test')
        self.data.update_id(self.viewer.state.x_att, test)
        assert self.viewer.state.x_att is test
        assert combo_as_string(self.viewer.options_widget().ui.combodata_x_att) == 'test:y:z'

    @pytest.mark.parametrize('protocol', [0])
    def test_session_back_compat(self, protocol):

        filename = os.path.join(DATA, 'scatter_v{0}.glu'.format(protocol))

        with open(filename, 'r') as f:
            session = f.read()

        state = GlueUnSerializer.loads(session)

        ga = state.object('__main__')

        dc = ga.session.data_collection

        assert len(dc) == 1

        assert dc[0].label == 'basic'

        viewer1 = ga.viewers[0][0]
        assert len(viewer1.state.layers) == 3
        assert viewer1.state.x_att is dc[0].id['a']
        assert viewer1.state.y_att is dc[0].id['b']
        assert_allclose(viewer1.state.x_min, -1.04)
        assert_allclose(viewer1.state.x_max, 1.04)
        assert_allclose(viewer1.state.y_min, 1.98)
        assert_allclose(viewer1.state.y_max, 3.02)
        assert not viewer1.state.x_log
        assert not viewer1.state.y_log
        assert viewer1.state.layers[0].visible
        assert viewer1.state.layers[1].visible
        assert viewer1.state.layers[2].visible

        viewer2 = ga.viewers[0][1]
        assert len(viewer2.state.layers) == 3
        assert viewer2.state.x_att is dc[0].id['a']
        assert viewer2.state.y_att is dc[0].id['c']
        assert_allclose(viewer2.state.x_min, 9.5e-6)
        assert_allclose(viewer2.state.x_max, 1.05)
        assert_allclose(viewer2.state.y_min, 0.38)
        assert_allclose(viewer2.state.y_max, 5.25)
        assert viewer2.state.x_log
        assert viewer2.state.y_log
        assert viewer2.state.layers[0].visible
        assert not viewer2.state.layers[1].visible
        assert viewer2.state.layers[2].visible

        viewer3 = ga.viewers[0][2]
        assert len(viewer3.state.layers) == 3
        assert viewer3.state.x_att is dc[0].id['b']
        assert viewer3.state.y_att is dc[0].id['a']
        assert_allclose(viewer3.state.x_min, 0)
        assert_allclose(viewer3.state.x_max, 5)
        assert_allclose(viewer3.state.y_min, -5)
        assert_allclose(viewer3.state.y_max, 5)
        assert not viewer3.state.x_log
        assert not viewer3.state.y_log
        assert viewer3.state.layers[0].visible
        assert viewer3.state.layers[1].visible
        assert not viewer3.state.layers[2].visible

    def test_save_svg(self, tmpdir):
        # Regression test for a bug in AxesCache that caused SVG saving to
        # fail (because renderer.buffer_rgba did not exist)
        self.viewer.add_data(self.data)
        filename = tmpdir.join('test.svg').strpath
        self.viewer.axes.figure.savefig(filename)

    def test_2d(self):

        viewer_state = self.viewer.state

        self.viewer.add_data(self.data_2d)

        assert viewer_state.x_att is self.data_2d.id['a']
        assert viewer_state.x_min == 1
        assert viewer_state.x_max == 4

        assert viewer_state.y_att is self.data_2d.id['b']
        assert viewer_state.y_min == 5
        assert viewer_state.y_max == 8

        assert len(self.viewer.layers[0].mpl_artists) == 1
