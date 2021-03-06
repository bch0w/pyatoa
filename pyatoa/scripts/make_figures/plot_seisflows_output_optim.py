"""
Plots output files from Seisflows
"""
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import cm

mpl.rcParams['font.size'] = 12
mpl.rcParams['lines.linewidth'] = 1.25
mpl.rcParams['lines.markersize'] = 5
mpl.rcParams['axes.linewidth'] = 2


def parse_output_optim(path_to_optim):
    """
    Seisflows creates a file 'output.optim' which provides a log of the
    optimization procedures, including trial step lengths, associated misfits.
    This function parses that file into a few arrays for use in the workflow.

    :type path_to_optim: str
    :param path_to_optim: path to 'output.optim' created by Seisflows
    :rtype: np.arrays
    :return: numpy arrays which define the iterations, steplengths and misfits
    """
    with open(path_to_optim, 'r') as f:
        lines = f.readlines()

    # Parse the file, skip the header, ignore any tail
    iterations, steplens, misfits = [], [], []
    for line in lines[2:]:
        line = line.strip().split()
        # Each iteration will have an integer to represent the iter number
        if len(line) == 3:
            iteration = line[0]
            iterations.append(int(iteration))
            steplens.append(float(line[1]))
            misfits.append(float(line[2]))
        # Each trial step length will follow and will carry the same iteration
        elif len(line) == 2:
            iterations.append(int(iteration))
            steplens.append(float(line[0]))
            misfits.append(float(line[1]))
        elif len(line) == 0:
            continue
        else:
            print(line)
            print("invalid line length encountered in output.optim")
            return

    # Set the lists as numpy arrays for easier manipulation
    iterations = np.asarray(iterations)
    steplens = np.asarray(steplens)
    misfits = np.asarray(misfits)

    return iterations, steplens, misfits


def plot_output_optim(path_to_optim, show=False, save=''):
    """
    Sesiflows specific function

    Read the text file output.optim, which contains
    misfit values, step length values and iteration numbers.
    Parse the values and plot them on a scatter plot to show how the misfit
    evolves with subsequent iterations. Put some auxiliary plot information on
    for a more informative overall plot

    :type path_to_optim: str
    :param path_to_optim: path to the 'output.optim' text file
    :type show: bool
    :param show: show the plot
    :type save: str
    :param save: output filename to save the figure
    """
    # read in the values of the file
    iterations, steplens, misfits = parse_output_optim(path_to_optim)

    # Plot the misfit values, and steplengths on a twin axis
    f, ax = plt.subplots(1)
    twax = ax.twinx()

    # Set the normalized colormap to differentiate iterations
    colormap = cm.nipy_spectral
    norm = mpl.colors.Normalize(vmin=min(iterations), vmax=max(iterations))

    # Offset allows for cumulative plotting despite restarting scatter plot
    offset = 0
    for itr in np.unique(iterations):
        # Determine unique arrays for each iteration
        indices = np.where(iterations == itr)
        misfits_ = misfits[indices]
        steplens_ = steplens[indices]

        # Set a specific color for each iteration and plot as a scatterplot
        color = [colormap(norm(itr))] * len(misfits_)

        # Plot the misfit values
        ax.scatter(range(offset, offset + len(misfits_)), misfits_, c=color,
                   zorder=5, s=60)
        ax.annotate(s=f"iter {itr}", xytext=(offset+0.2, misfits_[0]),
                    xy=(offset, misfits_[0]), color=colormap(norm(itr)),
                    fontsize=9, zorder=6
                    )

        # Plot the steplengths, remove values of 0 steplength
        steplens_[steplens_ == 0] = 'nan'
        twax.scatter(range(offset, offset + len(steplens_)), steplens_, c=color,
                     zorder=3, marker='d', alpha=0.75, s=50, edgecolor='w')

        # Connect scatter plots with a line in the back
        ax.plot(range(offset, offset + len(misfits_)), misfits_,
                c=colormap(norm(itr)))

        # Make sure scatter points overlap because the starting misfit of the
        # next iteration is the same misfit as the last iteration
        offset += len(misfits_) - 1

    # Scatter points outside the plot for legend
    ax.scatter(-1, min(misfits), c='w', edgecolor='k', marker='o',
               label='misfits')
    ax.scatter(-1, min(misfits), c='w', edgecolor='k', marker='d',
               label='step lengths')

    # Put a line at y=1 for step lengths to show where L-BFGS is working
    twax.axhline(y=1, xmin=0, xmax=1, linestyle='--', linewidth=1.5, c='k',
                 alpha=0.5, zorder=2)

    # Because the scatter plots overlap, number of points must be defined 
    num_points = len(iterations) - len(np.unique(iterations))
    steplens_min_notzero = steplens[np.where(steplens > 0)].min()
    # Set plot attributes
    if max(misfits)/min(misfits) > 10:
        ax.set_yscale('log')
    twax.set_yscale('log')
    twax.set_ylim(bottom=steplens_min_notzero)
    plt.title("seisflows output.optim")
    ax.set_xlim([-0.5, num_points + 0.5])
    ax.set_xlabel("step count")
    ax.set_ylabel("pyatoa misfits")
    ax.legend()
    twax.set_ylabel("step lengths", rotation=270, labelpad=15)

    # Set the tick labelling based on the number of iterations
    plt.xticks(range(0, num_points, num_points//10 or 1))

    # Set the format of the plot to match pretty_grids formatting
    for axis in [ax, twax]:
        axis.tick_params(which='both', direction='in', top=True, right=True)
    for axis_ in ['major', 'minor']:
        ax.grid(which=axis_, linestyle=':', linewidth='0.5',
                color='k', alpha=0.25)

    if show:
        plt.show()
    if save:
        plt.savefig(save)



