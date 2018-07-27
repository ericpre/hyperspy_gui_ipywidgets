import ipywidgets

from hyperspy_gui_ipywidgets.utils import (
    labelme, register_ipy_widget, add_display_arg)
from link_traits import link


@register_ipy_widget(toolkey="navigation_sliders")
@add_display_arg
def ipy_navigation_sliders(obj, use_width=False, use_range=False, **kwargs):
    continuous_update = ipywidgets.Checkbox(True,
                                            description="Continous update")
    wdict = {}
    wdict["continuous_update"] = continuous_update
    widgets = []
    for i, axis in enumerate(obj):
        axis_dict = {}
        wdict["axis{}".format(i)] = axis_dict
        if use_range:
            range_widget = ipywidgets.IntRangeSlider(
                min=0,
                max=axis.size - 1,
                readout=True,
                description="range"
            )
            link((axis, "range"), (range_widget, "value"))
            link((continuous_update, "value"),
                 (range_widget, "continuous_update"))
        else:
            index_widget = ipywidgets.IntSlider(
                min=0,
                max=axis.size - 1,
                readout=True,
                description="index"
            )
            link((axis, "index"), (index_widget, "value"))
            link((continuous_update, "value"),
                 (index_widget, "continuous_update"))

        if use_width:
            width_widget = ipywidgets.IntSlider(
                min=0,
                max=axis.size - 1,
                readout=True,
                description="width"
            )

            def update_bound(change):
                width_widget.max = axis.size - change.new - 1
            index_widget.observe(update_bound, "value")
            link((axis, "width"), (width_widget, "value"))

        index_value_widget = ipywidgets.BoundedFloatText(
            min=axis.low_value,
            max=axis.high_value,
            step=axis.scale,
            description="value"
            # readout_format=".lf"
        )
        link((axis, "value"), (index_value_widget, "value"))
        link((axis, "high_value"), (index_value_widget, "max"))
        link((axis, "low_value"), (index_value_widget, "min"))
        link((axis, "scale"), (index_value_widget, "step"))
        link((continuous_update, "value"),
             (index_value_widget, "continuous_update"))

        name = ipywidgets.Label(str(axis),
                                layout=ipywidgets.Layout(width="15%"))
        units = ipywidgets.Label(layout=ipywidgets.Layout(width="5%"),
                                 disabled=True)
        link((axis, "name"), (name, "value"))
        link((axis, "units"), (units, "value"))

        w_list = [name, index_value_widget, units]
        if use_range:
            w_list.insert(0, range_widget)
        else:
            w_list.insert(0, index_widget)
        if use_width:
            w_list.insert(-1, width_widget)
        bothw = ipywidgets.HBox(w_list)
        # labeled_widget = labelme(str(axis), bothw)
        widgets.append(bothw)

        axis_dict["value"] = index_value_widget
        if use_range:
            axis_dict["range"] = range_widget
        else:
            axis_dict["index"] = index_widget
        if use_width:
            axis_dict["width"] = width_widget
        axis_dict["units"] = units
    widgets.append(continuous_update)
    box = ipywidgets.VBox(widgets)
    return {"widget": box, "wdict": wdict}


@register_ipy_widget(toolkey="DataAxis")
@add_display_arg
def _get_axis_widgets(obj):
    widgets = []
    wd = {}
    name = ipywidgets.Text()
    widgets.append(labelme(ipywidgets.Label("Name"), name))
    link((obj, "name"), (name, "value"))
    wd["name"] = name

    size = ipywidgets.IntText(disabled=True)
    widgets.append(labelme("Size", size))
    link((obj, "size"), (size, "value"))
    wd["size"] = size

    index_in_array = ipywidgets.IntText(disabled=True)
    widgets.append(labelme("Index in array", index_in_array))
    link((obj, "index_in_array"), (index_in_array, "value"))
    wd["index_in_array"] = index_in_array
    if obj.navigate:
        index = ipywidgets.IntSlider(min=0, max=obj.size - 1)
        widgets.append(labelme("Index", index))
        link((obj, "index"), (index, "value"))
        wd["index"] = index

        value = ipywidgets.FloatSlider(
            min=obj.low_value,
            max=obj.high_value,
        )
        wd["value"] = value
        widgets.append(labelme("Value", value))
        link((obj, "value"), (value, "value"))
        link((obj, "high_value"), (value, "max"))
        link((obj, "low_value"), (value, "min"))
        link((obj, "scale"), (value, "step"))

    units = ipywidgets.Text()
    widgets.append(labelme("Units", units))
    link((obj, "units"), (units, "value"))
    wd["units"] = units

    scale = ipywidgets.FloatText()
    widgets.append(labelme("Scale", scale))
    link((obj, "scale"), (scale, "value"))
    wd["scale"] = scale

    offset = ipywidgets.FloatText()
    widgets.append(labelme("Offset", offset))
    link((obj, "offset"), (offset, "value"))
    wd["offset"] = offset

    return {
        "widget": ipywidgets.VBox(widgets),
        "wdict": wd
    }


@register_ipy_widget(toolkey="AxesManager")
@add_display_arg
def ipy_axes_gui(obj, **kwargs):
    wdict = {}
    nav_widgets = []
    sig_widgets = []
    i = 0
    for axis in obj.navigation_axes:
        wd = _get_axis_widgets(axis, display=False)
        nav_widgets.append(wd["widget"])
        wdict["axis{}".format(i)] = wd["wdict"]
        i += 1
    for j, axis in enumerate(obj.signal_axes):
        wd = _get_axis_widgets(axis, display=False)
        sig_widgets.append(wd["widget"])
        wdict["axis{}".format(i + j)] = wd["wdict"]
    nav_accordion = ipywidgets.Accordion(nav_widgets)
    sig_accordion = ipywidgets.Accordion(sig_widgets)
    i = 0  # For when there is not navigation axes
    for i in range(obj.navigation_dimension):
        nav_accordion.set_title(i, "Axis %i" % i)
    for j in range(obj.signal_dimension):
        sig_accordion.set_title(j, "Axis %i" % (i + j + 1))
    tabs = ipywidgets.HBox([nav_accordion, sig_accordion])
    return {
        "widget": tabs,
        "wdict": wdict,
    }
