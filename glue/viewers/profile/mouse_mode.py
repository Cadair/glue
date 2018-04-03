from glue.external.echo import CallbackProperty, delay_callback
from glue.core.state_objects import State
from glue.viewers.common.qt.mouse_mode import MouseMode

__all__ = ['NavigateMouseMode', 'RangeMouseMode']


COLOR = (0.0, 0.25, 0.7)


class NavigationModeState(State):
    x = CallbackProperty(None)


class NavigateMouseMode(MouseMode):

    def __init__(self, viewer):
        super(NavigateMouseMode, self).__init__(viewer)
        self.state = NavigationModeState()
        self.state.add_callback('x', self._update_artist)
        self.pressed = False
        self._viewer = viewer

    def press(self, event):
        self.pressed = True
        if not event.inaxes:
            return
        self.state.x = event.xdata

    def move(self, event):
        if not self.pressed or not event.inaxes:
            return
        self.state.x = event.xdata

    def release(self, event):
        self.pressed = False

    def _update_artist(self, *args):
        if hasattr(self, '_line'):
            self._line.set_data([self.state.x, self.state.x], [0, 1])
        else:
            self._line = self._axes.axvline(self.state.x, color=COLOR)
        self._canvas.draw()

    def deactivate(self):
        if hasattr(self, '_line'):
            self._line.set_visible(False)
        self._canvas.draw()
        super(NavigateMouseMode, self).deactivate()

    def activate(self):
        if hasattr(self, '_line'):
            self._line.set_visible(True)
        self._canvas.draw()
        super(NavigateMouseMode, self).activate()


class RangeModeState(State):
    x_min = CallbackProperty(None)
    x_max = CallbackProperty(None)


PICK_THRESH = 0.05


class RangeMouseMode(MouseMode):

    def __init__(self, viewer):
        super(RangeMouseMode, self).__init__(viewer)
        self.state = RangeModeState()
        self.state.add_callback('x_min', self._update_artist)
        self.state.add_callback('x_max', self._update_artist)
        self.pressed = False

        self.mode = None
        self.move_params = None
        self._viewer = viewer

    def press(self, event):

        self.pressed = True

        if not event.inaxes:
            return

        x_min, x_max = self._axes.get_xlim()
        x_range = abs(x_max - x_min)

        if self.state.x_min is None or self.state.x_max is None:
            self.mode = 'move-x-max'
            with delay_callback(self.state, 'x_min', 'x_max'):
                self.state.x_min = event.xdata
                self.state.x_max = event.xdata
        elif abs(event.xdata - self.state.x_min) / x_range < PICK_THRESH:
            self.mode = 'move-x-min'
        elif abs(event.xdata - self.state.x_max) / x_range < PICK_THRESH:
            self.mode = 'move-x-max'
        elif (event.xdata > self.state.x_min) is (event.xdata < self.state.x_max):
            self.mode = 'move'
            self.move_params = (event.xdata, self.state.x_min, self.state.x_max)
        else:
            self.mode = 'move-x-max'
            self.state.x_min = event.xdata

    def move(self, event):

        if not self.pressed or not event.inaxes:
            return

        if self.mode == 'move-x-min':
            self.state.x_min = event.xdata
        elif self.mode == 'move-x-max':
            self.state.x_max = event.xdata
        elif self.mode == 'move':
            orig_click, orig_x_min, orig_x_max = self.move_params
            with delay_callback(self.state, 'x_min', 'x_max'):
                self.state.x_min = orig_x_min + (event.xdata - orig_click)
                self.state.x_max = orig_x_max + (event.xdata - orig_click)

    def release(self, event):
        self.pressed = False
        self.mode = None
        self.move_params

    def _update_artist(self, *args):
        y_min, y_max = self._axes.get_ylim()
        y_mid = 0.5 * (y_min + y_max)
        if hasattr(self, '_lines'):
            self._lines[0].set_data([self.state.x_min, self.state.x_min], [0, 1])
            self._lines[1].set_data([self.state.x_max, self.state.x_max], [0, 1])
            self._lines[2].set_data([self.state.x_min, self.state.x_max], [y_mid, y_mid])
        else:
            self._lines = (self._axes.axvline(self.state.x_min, color=COLOR),
                           self._axes.axvline(self.state.x_max, color=COLOR),
                           self._axes.plot([self.state.x_min, self.state.x_max], [y_mid, y_mid], color=COLOR)[0])
        self._canvas.draw()

    def deactivate(self):
        if hasattr(self, '_lines'):
            for line in self._lines:
                line.set_visible(False)
        self._canvas.draw()
        super(RangeMouseMode, self).deactivate()

    def activate(self):
        if hasattr(self, '_lines'):
            for line in self._lines:
                line.set_visible(True)
        self._canvas.draw()
        super(RangeMouseMode, self).activate()
