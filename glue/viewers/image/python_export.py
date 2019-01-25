from __future__ import absolute_import, division, print_function

from glue.viewers.common.python_export import code, serialize_options


def python_export_image_layer(layer, *args):

    if not layer.enabled or not layer.visible:
        return [], None

    script = ""
    imports = ["from glue.viewers.image.state import get_sliced_data_maker"]

    slices, agg_func, transpose = layer._viewer_state.numpy_slice_aggregation_transpose

    # TODO: implement aggregation, ignore for now

    script += "# Define a function that will get a fixed resolution buffer\n"

    options = {'data': code('layer_data'),
               'x_axis': layer._viewer_state.x_att.axis,
               'y_axis': layer._viewer_state.y_att.axis,
               'slices': slices,
               'target_cid': code("layer_data.id['{0}']".format(layer.state.attribute))}

    script += "array_maker = get_sliced_data_maker({0})\n\n".format(serialize_options(options))

    # if transpose:
    #     script += ".transpose()"

    script += "composite.allocate('{0}')\n".format(layer.uuid)

    if layer._viewer_state.color_mode == 'Colormaps':
        color = code('plt.cm.' + layer.state.cmap.name)
    else:
        color = layer.state.color

    options = dict(array=code('array_maker.get_array'),
                   clim=(layer.state.v_min, layer.state.v_max),
                   visible=layer.state.visible,
                   zorder=layer.state.zorder,
                   color=color,
                   contrast=layer.state.contrast,
                   bias=layer.state.bias,
                   alpha=layer.state.alpha,
                   stretch=layer.state.stretch)

    script += "composite.set('{0}', {1})\n\n".format(layer.uuid, serialize_options(options))

    return imports, script.strip()


def python_export_image_subset_layer(layer, *args):

    if not layer.enabled or not layer.visible:
        return [], None

    script = ""
    imports = ["from glue.viewers.image.state import get_sliced_data_maker"]

    slices, agg_func, transpose = layer._viewer_state.numpy_slice_aggregation_transpose

    # TODO: implement aggregation, ignore for now

    script += "# Define a function that will get a fixed resolution buffer of the mask\n"

    options = {'data': code('layer_data'),
               'x_axis': layer._viewer_state.x_att.axis,
               'y_axis': layer._viewer_state.y_att.axis,
               'slices': slices}

    script += "array_maker = get_sliced_data_maker({0})\n\n".format(serialize_options(options))

    if transpose:
        script += ".transpose()"

    script += "\n\n"

    options = dict(origin='lower', interpolation='nearest', color=layer.state.color,
                   vmin=0, vmax=1, aspect=layer._viewer_state.aspect,
                   zorder=layer.state.zorder, alpha=layer.state.alpha)

    script += "imshow(ax, {0}, {1})\n".format(code('array_maker'), serialize_options(options))

    return imports, script.strip()
