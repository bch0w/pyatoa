"""
General utility functions used in plotting scripts
"""


def align_yaxis(ax1, ax2):
    """
    adjust ax2 ylimit so that v2 in ax2 is aligned to v1 in ax1

    :type ax1: matplotlib axis
    :param ax1: axes to adjust
    :type ax2: matplotlib axis
    :param ax2: axes to adjust
    """
    ymin_a1, ymax_a1 = ax1.get_ylim()
    ymin_a2, ymax_a2 = ax2.get_ylim()

    _, y1 = ax1.transData.transform((0, (ymax_a1+ymin_a1)/2))
    _, y2 = ax2.transData.transform((0, (ymax_a2+ymin_a2)/2))
    inv = ax2.transData.inverted()
    _, dy = inv.transform((0, 0)) - inv.transform((0, y1-y2))
    ax2.set_ylim(ymin_a2+dy, ymax_a2+dy)


def pretty_grids(input_ax, twax=False):
    """
    standard plot skeleton formatting, thick lines and internal tick marks etc.

    :type input_ax: matplotlib axis
    :param input_ax: axis to prettify
    :type twax: bool
    :param twax: If twax (twin axis), do not set grids
    """
    input_ax.set_axisbelow(True)
    input_ax.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
    input_ax.tick_params(which='both', direction='in', top=True, right=True)
    # Set the grids 'on' only if main axis
    if not twax:
        input_ax.minorticks_on()
        for axis_ in ['major', 'minor']:
            input_ax.grid(which=axis_, linestyle=':', linewidth='0.5',
                          color='k', alpha=0.25)


def format_axis(input_ax):
    """
    Sit the tick marks away from the plot edges to prevent overlapping when
    multiple subplots are stacked atop one another, and for general gooood looks
    will check if the plot is two sided (e.g. waveforms) or only positive

    :type input_ax: matplotlib axis
    :param input_ax: axis to prettify
    """
    ymin, ymax = input_ax.get_ylim()
    maxvalue = max([abs(_) for _ in input_ax.get_ylim()])
    percentover = maxvalue * 0.125
    if abs(round(ymin/ymax)) != 0:
        bounds = (-1 * (maxvalue+percentover), (maxvalue+percentover))
    else:  # elif abs(round(ymin/ymax)) == 0:
        bounds = (-0.05, 1.05)
    input_ax.set_ylim(bounds)


def combine_figures(path_to_figure_a, path_to_figure_b, path_to_output):
    """
    UNFINISHED
    We want station maps and waveform maps on the same plot but matplotlib makes
    it difficult to combine two figure objects, so the hacky way of doing it is
    to save two separate images and combine them afterwards
    :param path_to_figure_a:
    :param path_to_figure_b:
    :return:
    """
    import PIL
    import numpy as np

    raise NotImplementedError
    imgs = [PIL.Image.open(i) for i in [path_to_figure_a, path_to_figure_b]]
    min_shape = sorted(sorted([(np.sum(i.size), i.size) for i in imgs])[0][1])
    imgs_comb = np.hstack(imgs)
    import ipdb;ipdb.set_trace()
    imgs_comb = PIL.Image.fromarray(imgs_comb)
    imgs_comb.save(path_to_output)
