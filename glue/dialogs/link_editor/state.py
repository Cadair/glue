from __future__ import absolute_import, division, print_function

try:
    from inspect import getfullargspec
except ImportError:  # Python 2.7
    from inspect import getargspec as getfullargspec

# from glue.config import link_function, link_helper

from glue.core.component_link import ComponentLink
from glue.core.state_objects import State
from glue.external.echo import CallbackProperty, SelectionCallbackProperty, delay_callback
from glue.core.data_combo_helper import DataCollectionComboHelper, ComponentIDComboHelper


__all__ = ['LinkEditorState']


class LinkWrapper(State):
    link = CallbackProperty()


class LinkEditorState(State):

    data1 = SelectionCallbackProperty()
    data2 = SelectionCallbackProperty()
    links = SelectionCallbackProperty()
    link_type = SelectionCallbackProperty()

    def __init__(self, data_collection, links):

        # Note that we could access the links in the data collection, but we
        # instead want to use the edited list of links in the links variable

        super(LinkEditorState, self).__init__()

        self.data1_helper = DataCollectionComboHelper(self, 'data1', data_collection)
        self.data2_helper = DataCollectionComboHelper(self, 'data2', data_collection)

        self.data_collection = data_collection
        self._all_links = links

        if len(data_collection) == 2:
            self.data1, self.data2 = self.data_collection
        else:
            self.data1 = self.data2 = None

        self.on_data_change()

        self.add_callback('data1', self.on_data_change)
        self.add_callback('data2', self.on_data_change)

    def on_data_change(self, *args):

        if self.data1 is None or self.data2 is None:
            LinkEditorState.links.set_choices(self, [])
            return

        links = []
        for link in self._all_links:
            if ((link.data_in is self.data1 and link.data_out is self.data2) or
                    (link.data_in is self.data2 and link.data_out is self.data1)):
                links.append(link)

        with delay_callback(self, 'links'):
            LinkEditorState.links.set_choices(self, links)
            if len(links) > 0:
                self.links = links[0]

    def new_link(self, function_or_helper):

        if hasattr(function_or_helper, 'function'):
            link = EditableLinkFunctionState(function_or_helper.function,
                                             data_in=self.data1, data_out=self.data2,
                                             output_name=function_or_helper.output_labels[0],
                                             description=function_or_helper.info)
        else:
            raise NotImplementedError("link helper support not implemented yet")

        self._all_links.append(link)
        with delay_callback(self, 'links'):
            self.on_data_change()
            self.links = link

    def remove_link(self):
        self._all_links.remove(self.links)
        self.on_data_change()


class EditableLinkFunctionState(State):

    function = CallbackProperty()
    data_in = CallbackProperty()
    data_out = CallbackProperty()

    def __new__(cls, function, data_in=None, data_out=None, cids_in=None,
                cid_out=None, input_names=None, output_name=None,
                description=None):

        if isinstance(function, ComponentLink):
            input_names = function.input_names
            output_name = function.output_name

        class CustomizedStateClass(EditableLinkFunctionState):
            pass

        setattr(CustomizedStateClass, 'input_names', input_names or getfullargspec(function)[0])
        setattr(CustomizedStateClass, 'output_name', output_name or 'output')

        for index, input_arg in enumerate(CustomizedStateClass.input_names):
            print("INIT1", input_arg)
            setattr(CustomizedStateClass, input_arg, SelectionCallbackProperty(default_index=index))

            print("INIT2", CustomizedStateClass.output_name)
        setattr(CustomizedStateClass, CustomizedStateClass.output_name, SelectionCallbackProperty(default_index=0))

        return super(EditableLinkFunctionState, cls).__new__(CustomizedStateClass)

    def __init__(self, function, data_in=None, data_out=None, cids_in=None,
                 cid_out=None, input_names=None, output_name=None,
                 description=None):

        super(EditableLinkFunctionState, self).__init__()

        if isinstance(function, ComponentLink):
            self.function = function.get_using()
            self.inverse = function.get_inverse()
            cids_in = function.get_from_ids()
            cid_out = function.get_to_id()
            data_in = cids_in[0].parent
            data_out = cid_out.parent
            description = function.description
        else:
            self.function = function
            self.inverse = None

        self.data_in = data_in
        self.data_out = data_out

        for name in self.input_names:
            helper = ComponentIDComboHelper(self, name)
            helper.append_data(data_in)
            setattr(self, '_' + name + '_helper', helper)

        helper = ComponentIDComboHelper(self, self.output_name)
        setattr(self, '_' + self.output_name + '_helper', helper)
        helper.append_data(data_out)

        if cids_in is not None:
            print("CIDS_IN", cids_in)
            for name, cid in zip(self.input_names, cids_in):
                setattr(self, name, cid)

        if cid_out is not None:
            print("CID_OUT", cid_out)
            setattr(self, self.output_name, cid_out)

    @property
    def link(self):
        """
        Return a `glue.core.component_link.ComponentLink` object.
        """
        cids_in = [getattr(self, name) for name in self.input_names]
        cid_out = getattr(self, self.output_name)
        return ComponentLink(cids_in, cid_out, using=self.function)
