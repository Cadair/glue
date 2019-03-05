from mock import patch

from qtpy import QtWidgets
from glue.utils.qt import get_qapp
from glue.core import Data, DataCollection
from glue.core.component_link import identity
from glue.dialogs.link_editor.qt import LinkEditor
from glue.core.component_link import ComponentLink
from glue.plugins.coordinate_helpers.link_helpers import Galactic_to_FK5, ICRS_to_Galactic


def non_empty_rows_count(layout):
    """
    Determine how many rows of the QGridLayout are not empty
    """
    count = 0
    for row in range(layout.rowCount()):
        for col in range(layout.columnCount()):
            if layout.itemAtPosition(row, col) is not None:
                if layout.itemAtPosition(row, col).widget() is not None:
                    count += 1
                    break
    return count


def get_action(link_widget, text):
    for submenu in link_widget._menu.children():
        if isinstance(submenu, QtWidgets.QMenu):
            for action in submenu.actions():
                if action.text() == text:
                    return action
    raise ValueError("Action '{0}' not found".format(text))


class TestLinkEditor:

    def setup_method(self, method):

        self.data1 = Data(x=[1, 2, 3], y=[2, 3, 4], z=[6, 5, 4], label='data1')
        self.data2 = Data(a=[2, 3, 4], b=[4, 5, 4], c=[3, 4, 1], label='data2')
        self.data3 = Data(i=[5, 4, 3], j=[2, 2, 1], label='data3')

        self.data_collection = DataCollection([self.data1, self.data2, self.data3])

    def test_defaults(self):
        # Make sure the dialog opens and closes and check default settings.
        dialog = LinkEditor(self.data_collection)
        dialog.show()
        link_widget = dialog.link_widget

        assert link_widget.state.data1 is None
        assert link_widget.state.data2 is None
        assert not link_widget.button_add_link.isEnabled()
        assert not link_widget.button_remove_link.isEnabled()

        link_widget.state.data1 = self.data2

        assert not link_widget.button_add_link.isEnabled()
        assert not link_widget.button_remove_link.isEnabled()

        link_widget.state.data2 = self.data1

        assert link_widget.button_add_link.isEnabled()
        assert link_widget.button_remove_link.isEnabled()

        dialog.accept()

        assert len(self.data_collection.external_links) == 0

    def test_defaults_two(self):
        # Make sure the dialog opens and closes and check default settings. With
        # two datasets, the datasets should be selected by default.
        self.data_collection.remove(self.data3)
        dialog = LinkEditor(self.data_collection)
        dialog.show()
        link_widget = dialog.link_widget
        assert link_widget.state.data1 is self.data1
        assert link_widget.state.data2 is self.data2
        assert link_widget.button_add_link.isEnabled()
        assert link_widget.button_remove_link.isEnabled()
        dialog.accept()
        assert len(self.data_collection.external_links) == 0

    def test_ui_behavior(self):

        # This is a bit more detailed test that checks that things update
        # correctly as we change various settings

        app = get_qapp()

        dialog = LinkEditor(self.data_collection)
        dialog.show()
        link_widget = dialog.link_widget

        link_widget.state.data1 = self.data1
        link_widget.state.data2 = self.data2

        add_identity_link = get_action(link_widget, 'identity')
        add_lengths_volume_link = get_action(link_widget, 'lengths_to_volume')

        # At this point, there should be no links in the main list widget
        # and nothing on the right.
        assert link_widget.listsel_current_link.count() == 0
        assert link_widget.link_details.text() == ''
        assert link_widget.link_io.count() == 0

        # Let's add an identity link
        add_identity_link.trigger()

        # Ensure that all events get processed
        app.processEvents()

        # Now there should be one link in the main list and content in the
        # right hand panel.
        assert link_widget.listsel_current_link.count() == 1
        assert link_widget.link_details.text() == 'Link conceptually identical components'
        assert non_empty_rows_count(link_widget.link_io) == 5
        assert link_widget.link_io.itemAtPosition(1, 1).widget().currentText() == 'x'
        assert link_widget.link_io.itemAtPosition(4, 1).widget().currentText() == 'a'

        # Let's change the current components for the link
        link_widget.state.current_link.x = self.data1.id['y']
        link_widget.state.current_link.y = self.data2.id['b']

        # and make sure the UI gets updated
        assert link_widget.link_io.itemAtPosition(1, 1).widget().currentText() == 'y'
        assert link_widget.link_io.itemAtPosition(4, 1).widget().currentText() == 'b'

        # We now add another link of a different type
        add_lengths_volume_link.trigger()

        # Ensure that all events get processed
        app.processEvents()

        # and make sure the UI has updated
        assert link_widget.listsel_current_link.count() == 2
        assert link_widget.link_details.text() == 'Convert between linear measurements and volume'
        assert non_empty_rows_count(link_widget.link_io) == 7
        assert link_widget.link_io.itemAtPosition(1, 1).widget().currentText() == 'x'
        assert link_widget.link_io.itemAtPosition(2, 1).widget().currentText() == 'y'
        assert link_widget.link_io.itemAtPosition(3, 1).widget().currentText() == 'z'
        assert link_widget.link_io.itemAtPosition(6, 1).widget().currentText() == 'a'

        # Now switch back to the first link
        link_widget.state.current_link = type(link_widget.state).current_link.get_choices(link_widget.state)[0]

        # and make sure the UI updates and has preserved the correct settings
        assert link_widget.listsel_current_link.count() == 2
        assert link_widget.link_details.text() == 'Link conceptually identical components'
        assert non_empty_rows_count(link_widget.link_io) == 5
        assert link_widget.link_io.itemAtPosition(1, 1).widget().currentText() == 'y'
        assert link_widget.link_io.itemAtPosition(4, 1).widget().currentText() == 'b'

        # Next up, we try changing the data

        link_widget.state.data1 = self.data3

        # At this point there should be no links in the list

        assert link_widget.listsel_current_link.count() == 0
        assert link_widget.link_details.text() == ''
        assert non_empty_rows_count(link_widget.link_io) == 0

        # Add another identity link
        add_identity_link.trigger()

        # Ensure that all events get processed
        app.processEvents()

        # Now there should be one link in the main list
        assert link_widget.listsel_current_link.count() == 1
        assert link_widget.link_details.text() == 'Link conceptually identical components'
        assert non_empty_rows_count(link_widget.link_io) == 5
        assert link_widget.link_io.itemAtPosition(1, 1).widget().currentText() == 'i'
        assert link_widget.link_io.itemAtPosition(4, 1).widget().currentText() == 'a'

        # Switch back to the original data
        link_widget.state.data1 = self.data1

        # And check the output is as before
        assert link_widget.listsel_current_link.count() == 2
        assert link_widget.link_details.text() == 'Link conceptually identical components'
        assert non_empty_rows_count(link_widget.link_io) == 5
        assert link_widget.link_io.itemAtPosition(1, 1).widget().currentText() == 'y'
        assert link_widget.link_io.itemAtPosition(4, 1).widget().currentText() == 'b'

        # Let's now remove this link
        link_widget.button_remove_link.click()

        # Ensure that all events get processed
        app.processEvents()

        # We should now see the lengths/volume link
        assert link_widget.listsel_current_link.count() == 1
        assert link_widget.link_details.text() == 'Convert between linear measurements and volume'
        assert non_empty_rows_count(link_widget.link_io) == 7
        assert link_widget.link_io.itemAtPosition(1, 1).widget().currentText() == 'x'
        assert link_widget.link_io.itemAtPosition(2, 1).widget().currentText() == 'y'
        assert link_widget.link_io.itemAtPosition(3, 1).widget().currentText() == 'z'
        assert link_widget.link_io.itemAtPosition(6, 1).widget().currentText() == 'a'

        dialog.accept()

        links = self.data_collection.external_links

        assert len(links) == 2

        assert isinstance(links[0], ComponentLink)
        assert links[0].get_from_ids()[0] is self.data1.id['x']
        assert links[0].get_from_ids()[1] is self.data1.id['y']
        assert links[0].get_from_ids()[2] is self.data1.id['z']
        assert links[0].get_to_id() is self.data2.id['a']

        assert isinstance(links[1], ComponentLink)
        assert links[1].get_from_ids()[0] is self.data3.id['i']
        assert links[1].get_to_id() is self.data2.id['a']

    def test_graph(self):

        dialog = LinkEditor(self.data_collection)
        dialog.show()
        link_widget = dialog.link_widget

        add_identity_link = get_action(link_widget, 'identity')

        graph = link_widget.graph_widget

        def click(node_or_edge):
            # We now simulate a selection - since we can't deterministically
            # figure out the exact pixel coordinates to use, we patch
            # 'find_object' to return the object we want to select.
            with patch.object(graph, 'find_object', return_value=node_or_edge):
                graph.mousePressEvent(None)

        def hover(node_or_edge):
            # Same as for select, we patch find_object
            with patch.object(graph, 'find_object', return_value=node_or_edge):
                graph.mouseMoveEvent(None)

        # To start with, no data should be selected
        assert link_widget.state.data1 is None
        assert link_widget.state.data2 is None

        # and the graph should have three nodes and no edges
        assert len(graph.nodes) == 3
        assert len(graph.edges) == 0

        click(graph.nodes[0])

        # Check that this has caused one dataset to be selected
        assert link_widget.state.data1 is self.data1
        assert link_widget.state.data2 is None

        # Click on the same node again and this should deselect the data
        # (but only once we move off from the node)

        click(graph.nodes[0])

        assert link_widget.state.data1 is self.data1
        assert link_widget.state.data2 is None

        hover(None)

        assert link_widget.state.data1 is None
        assert link_widget.state.data2 is None

        # Select it again
        click(graph.nodes[0])

        # and now select another node too
        click(graph.nodes[1])

        assert link_widget.state.data1 is self.data1
        assert link_widget.state.data2 is self.data2

        assert len(graph.nodes) == 3
        assert len(graph.edges) == 0

        add_identity_link.trigger()

        assert len(graph.nodes) == 3
        assert len(graph.edges) == 1

        # Unselect and select another node
        click(graph.nodes[1])
        click(graph.nodes[2])

        # and check the data selections have been updated
        assert link_widget.state.data1 is self.data1
        assert link_widget.state.data2 is self.data3

        # Deselect it and move off
        click(graph.nodes[2])
        hover(None)

        # and the second dataset should now once again be None
        assert link_widget.state.data1 is self.data1
        assert link_widget.state.data2 is None

        # Now change the data manually
        link_widget.state.data1 = self.data2
        link_widget.state.data2 = self.data3

        # and check that if we select the edge the datasets change back
        click(graph.edges[0])

        assert link_widget.state.data1 is self.data1
        assert link_widget.state.data2 is self.data2

        # Unselect and hover over nothing
        click(graph.edges[0])
        hover(None)
        assert link_widget.state.data1 is None
        assert link_widget.state.data2 is None

        # Hover over the edge and the datasets should change back
        hover(graph.edges[0])
        assert link_widget.state.data1 is self.data1
        assert link_widget.state.data2 is self.data2

        # And check that clicking outside of nodes/edges deselects everything
        click(None)
        assert link_widget.state.data1 is None
        assert link_widget.state.data2 is None

        # Select a node, select another, then make sure that selecting a third
        # one will deselect the two original ones
        click(graph.nodes[0])
        click(graph.nodes[1])
        click(graph.nodes[2])
        assert link_widget.state.data1 is self.data3
        assert link_widget.state.data2 is None

        dialog.accept()

    def test_preexisting_links(self):

        # Check that things work properly if there are pre-existing links

        app = get_qapp()

        link1 = ComponentLink([self.data1.id['x']], self.data2.id['c'])

        def add(x, y):
            return x + y

        def double(x):
            return x * 2

        def halve(x):
            return x / 2

        link2 = ComponentLink([self.data2.id['a'], self.data2.id['b']], self.data3.id['j'], using=add)
        link3 = ComponentLink([self.data3.id['i']], self.data2.id['c'], using=double, inverse=halve)

        self.data_collection.add_link(link1)
        self.data_collection.add_link(link2)
        self.data_collection.add_link(link3)

        dialog = LinkEditor(self.data_collection)
        dialog.show()
        link_widget = dialog.link_widget

        link_widget.state.data1 = self.data1
        link_widget.state.data2 = self.data2

        assert link_widget.listsel_current_link.count() == 1
        assert link_widget.link_details.text() == ''
        assert non_empty_rows_count(link_widget.link_io) == 5
        assert link_widget.link_io.itemAtPosition(1, 1).widget().currentText() == 'x'
        assert link_widget.link_io.itemAtPosition(4, 1).widget().currentText() == 'c'

        link_widget.state.data1 = self.data3

        assert link_widget.listsel_current_link.count() == 2
        assert link_widget.link_details.text() == ''
        assert non_empty_rows_count(link_widget.link_io) == 6
        assert link_widget.link_io.itemAtPosition(1, 1).widget().currentText() == 'a'
        assert link_widget.link_io.itemAtPosition(2, 1).widget().currentText() == 'b'
        assert link_widget.link_io.itemAtPosition(5, 1).widget().currentText() == 'j'

        link_widget.state.current_link = type(link_widget.state).current_link.get_choices(link_widget.state)[1]

        assert link_widget.listsel_current_link.count() == 2
        assert link_widget.link_details.text() == ''
        assert non_empty_rows_count(link_widget.link_io) == 5
        assert link_widget.link_io.itemAtPosition(1, 1).widget().currentText() == 'i'
        assert link_widget.link_io.itemAtPosition(4, 1).widget().currentText() == 'c'

        dialog.accept()

        links = self.data_collection.external_links

        assert len(links) == 3

        assert isinstance(links[0], ComponentLink)
        assert links[0].get_from_ids()[0] is self.data1.id['x']
        assert links[0].get_to_id() is self.data2.id['c']
        assert links[0].get_using() is identity

        assert isinstance(links[1], ComponentLink)
        assert links[1].get_from_ids()[0] is self.data2.id['a']
        assert links[1].get_from_ids()[1] is self.data2.id['b']
        assert links[1].get_to_id() is self.data3.id['j']
        assert links[1].get_using() is add

        assert isinstance(links[2], ComponentLink)
        assert links[2].get_from_ids()[0] is self.data3.id['i']
        assert links[2].get_to_id() is self.data2.id['c']
        assert links[2].get_using() is double
        assert links[2].get_inverse() is halve

    def test_add_helper(self):

        app = get_qapp()

        dialog = LinkEditor(self.data_collection)
        dialog.show()
        link_widget = dialog.link_widget

        link_widget.state.data1 = self.data1
        link_widget.state.data2 = self.data2

        add_coordinate_link = get_action(link_widget, 'ICRS <-> Galactic')

        # Add a coordinate link
        add_coordinate_link.trigger()

        # Ensure that all events get processed
        app.processEvents()

        assert link_widget.listsel_current_link.count() == 1
        assert link_widget.link_details.text() == 'Link ICRS and Galactic coordinates'
        assert non_empty_rows_count(link_widget.link_io) == 7
        assert link_widget.link_io.itemAtPosition(1, 1).widget().currentText() == 'x'
        assert link_widget.link_io.itemAtPosition(2, 1).widget().currentText() == 'y'
        assert link_widget.link_io.itemAtPosition(5, 1).widget().currentText() == 'a'
        assert link_widget.link_io.itemAtPosition(6, 1).widget().currentText() == 'b'

        dialog.accept()

        links = self.data_collection.external_links

        assert len(links) == 1

        assert isinstance(links[0], ICRS_to_Galactic)
        assert links[0].cids1[0] is self.data1.id['x']
        assert links[0].cids1[1] is self.data1.id['y']
        assert links[0].cids2[0] is self.data2.id['a']
        assert links[0].cids2[1] is self.data2.id['b']

    def test_preexisting_helper(self):

        app = get_qapp()

        link1 = Galactic_to_FK5(cids1=[self.data1.id['x'], self.data1.id['y']],
                                cids2=[self.data2.id['c'], self.data2.id['b']])

        self.data_collection.add_link(link1)

        dialog = LinkEditor(self.data_collection)
        dialog.show()
        link_widget = dialog.link_widget

        assert link_widget.listsel_current_link.count() == 0

        link_widget.state.data1 = self.data1
        link_widget.state.data2 = self.data2

        assert link_widget.listsel_current_link.count() == 1
        assert link_widget.link_details.text() == 'Link Galactic and FK5 (J2000) Equatorial coordinates'
        assert non_empty_rows_count(link_widget.link_io) == 7
        assert link_widget.link_io.itemAtPosition(1, 1).widget().currentText() == 'x'
        assert link_widget.link_io.itemAtPosition(2, 1).widget().currentText() == 'y'
        assert link_widget.link_io.itemAtPosition(5, 1).widget().currentText() == 'c'
        assert link_widget.link_io.itemAtPosition(6, 1).widget().currentText() == 'b'

        dialog.accept()

        links = self.data_collection.external_links

        assert len(links) == 1

        assert isinstance(links[0], Galactic_to_FK5)
        assert links[0].cids1[0] is self.data1.id['x']
        assert links[0].cids1[1] is self.data1.id['y']
        assert links[0].cids2[0] is self.data2.id['c']
        assert links[0].cids2[1] is self.data2.id['b']

# TODO: check that if we use a FunctionalMultiLink then either data can be used
# in input.
