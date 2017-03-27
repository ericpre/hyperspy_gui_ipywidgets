from traitlets import TraitError as TraitletError
from ipywidgets import (
    Accordion, FloatSlider, FloatText, Layout, HBox, VBox, Checkbox)

from hyperspy.misc.link_traits import link_traits
from hyperspy.gui_ipywidgets.utils import add_display_arg


def _interactive_slider_bounds(obj, index=None):
    """Guesstimates the bounds for the slider. They will probably have to
    be changed later by the user.

    """
    fraction = 10.
    _min, _max, step = None, None, None
    value = obj.value if index is None else obj.value[index]
    if obj.bmin is not None:
        _min = obj.bmin
    if obj.bmax is not None:
        _max = obj.bmax
    if _max is None and _min is not None:
        _max = value + fraction * (value - _min)
    if _min is None and _max is not None:
        _min = value - fraction * (_max - value)
    if _min is None and _max is None:
        if obj is obj.component._position:
            axis = obj._axes_manager.signal_axes[-1]
            _min = axis.axis.min()
            _max = axis.axis.max()
            step = np.abs(axis.scale)
        else:
            _max = value + np.abs(value * fraction)
            _min = value - np.abs(value * fraction)
    if step is None:
        step = (_max - _min) * 0.001
    return {'min': _min, 'max': _max, 'step': step}


def _interactive_tuple_update(obj, value=None, index=None):
    """Callback function for the widgets, to update the value
    """
    if value is not None:
        if index is None:
            obj.value = value['new']
        else:
            obj.value = obj.value[:index] + (value['new'],) +\
                obj.value[index + 1:]


def _get_value_widget(obj, index=None):
    widget_bounds = _interactive_slider_bounds(obj, index=index)
    thismin = FloatText(value=widget_bounds['min'],
                        description='min',
                        layout=Layout(flex='0 1 auto',
                                      width='auto'),)
    thismax = FloatText(value=widget_bounds['max'],
                        description='max',
                        layout=Layout(flex='0 1 auto',
                                      width='auto'),)
    current_value = obj.value if index is None else obj.value[index]
    current_name = obj.name
    if index is not None:
        current_name += '_{}'.format(index)
    widget = FloatSlider(value=current_value,
                         min=thismin.value,
                         max=thismax.value,
                         step=widget_bounds['step'],
                         description=current_name,
                         layout=Layout(flex='1 1 auto', width='auto'))

    def on_min_change(change):
        if widget.max > change['new']:
            widget.min = change['new']
            widget.step = np.abs(widget.max - widget.min) * 0.001

    def on_max_change(change):
        if widget.min < change['new']:
            widget.max = change['new']
            widget.step = np.abs(widget.max - widget.min) * 0.001

    thismin.observe(on_min_change, names='value')
    thismax.observe(on_max_change, names='value')
    if index is not None:  # value is tuple, expanding
        this_observed = functools.partial(obj._interactive_tuple_update,
                                          index=index)
        widget.observe(this_observed, names='value')
    else:
        link_traits((obj, "value"), value, "value")

    container = HBox((thismin, widget, thismax))
    return container


@add_display_arg
def get_parameter_widget(obj, **kwargs):
    """Creates interactive notebook widgets for the parameter, if
    available.

    """
    if obj._number_of_elements == 1:
        container = obj._get_value_widget()
    else:
        children = [obj._get_value_widget(index=i) for i in
                    range(obj._number_of_elements)]
        container = VBox(children)
    return container


@add_display_arg
def get_component_widget(obj, **kwargs):
    """Creates interactive notebook widgets for all component parameters,
    if available.

    """
    active = Checkbox(description='active', value=obj.active)

    def on_active_change(change):
        obj.active = change['new']
    active.observe(on_active_change, names='value')

    container = VBox([active])
    for parameter in obj.parameters:
        container.children += get_parameter_widget(parameter),
    return container


@add_display_arg
def get_model_widget(obj, **kwargs):
    """Creates interactive notebook widgets for all components and
    parameters, if available.

    """

    children = [get_component_widget(component) for component in
                obj]
    accordion = Accordion(children=children)
    for i, comp in enumerate(obj):
        accordion.set_title(i, comp.name)
    return accordion


@add_display_arg
def get_eelscl_widget(obj, **kwargs):
    """Create ipywidgets for the EELSCLEDge component.

    """
    active = Checkbox(description='active', value=obj.active)
    fine_structure = Checkbox(description='Fine structure',
                              value=obj.fine_structure_active)
    fs_smoothing = FloatSlider(description='Fine structure smoothing',
                               min=0, max=1, step=0.001,
                               value=obj.fine_structure_smoothing)
    container = VBox([active, fine_structure, fs_smoothing])
    for parameter in [obj.intensity, obj.effective_angle,
                      obj.onset_energy]:
        container.children += get_parameter_widget(parameter),
    return container


@add_display_arg
def get_scalable_fixed_patter_widget(obj, **kwargs):
    container = get_component_widget(obj)
    interpolate = Checkbox(description='interpolate',
                           value=obj.interpolate)

    def on_interpolate_change(change):
        obj.interpolate = change['new']

    interpolate.observe(on_interpolate_change, names='value')

    container.children = (container.children[0], interpolate) + \
        container.children[1:]
    return container
