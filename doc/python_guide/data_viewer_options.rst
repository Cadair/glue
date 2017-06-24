==================================
Programmatically configuring plots
==================================

Plots in Glue are designed to be easily configured
with Python. As much as possible, plot settings are
controlled by simple properties on data viewer objects.
For example::

    from glue.core import Data, DataCollection
    from glue.app.qt.application import GlueApplication
    from glue.viewers.scatter.qt import ScatterViewer
    import numpy as np

    # create some data
    d = Data(x=np.random.random(100), y=np.random.random(100))
    dc = DataCollection([d])

    # create a GUI session
    ga = GlueApplication(dc)

    # plot x vs y, flip the x axis, log-scale y axis
    scatter = ga.new_data_viewer(ScatterViewer)
    scatter.add_data(d)
    scatter.xatt = d.id['x']
    scatter.yatt = d.id['y']
    scatter.xflip = True
    scatter.ylog = True

    # show the GUI
    ga.start()


Plot Options
============

Here are the settings associated with each data viewer:

.. currentmodule:: glue.viewers.scatter.qt.viewer_widget

:class:`Scatter Plots <ScatterViewer>`
--------------------------------------

.. autosummary::
    ~ScatterViewer.xlog
    ~ScatterViewer.ylog
    ~ScatterViewer.xflip
    ~ScatterViewer.yflip
    ~ScatterViewer.xmin
    ~ScatterViewer.xmax
    ~ScatterViewer.ymin
    ~ScatterViewer.ymax
    ~ScatterViewer.hidden
    ~ScatterViewer.xatt
    ~ScatterViewer.yatt

.. currentmodule:: glue.viewers.image.qt.viewer_widget

:class:`Image Viewer <ImageWidget>`
------------------------------------

.. autosummary::
    ~ImageWidget.data
    ~ImageWidget.attribute
    ~ImageWidget.rgb_mode
    ~ImageWidget.slice

Histogram Viewer
----------------

The :class:`~glue.viewers.histogram.qt.data_viewer.HistogramViewer` class has a
``state`` attribute which is an instance of
:class:`~glue.viewers.histogram.state.HistogramViewerState`. To modify any settings
in the viewer, set the appropriate attributes on ``state``, for example
``state.x_min``. See :class:`~glue.viewers.histogram.state.HistogramViewerState`
to find out the full list of available attributes.

Customizing Plots with Matplotlib
=================================

If you want, you can directly manipulate the Matplotlib
plot objects that underly Glue plots. This can be useful
if you want to create static plots with custom annotation,
styles, etc.

From the GUI
------------
Open the IPython terminal window. The ``application.viewers`` variable
is a list of lists of all the
open plot windows. Each inner list contains the data viewers
open on a single tab. Every viewer has an ``axes`` attribute,
which points to a :class:`Matplotlib Axes <matplotlib.axes.Axes>`
object::

    plot = application.viewers[0][0]
    ax = plot.axes
    ax.set_title('Custom title')
    ax.figure.canvas.draw()  # update the plot

From a script
-------------

Save the current glue session via ``File->Save Session``. You can
reload this session programmatically as follows::

    from glue.app.qt.application import GlueApplication
    app = GlueApplication.restore('output.glu', show=False)
    plot = app.viewers[0][0]
    ax = plot.axes
