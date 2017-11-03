#!/usr/bin/env python
# -*- coding: utf-8 -*-

__version__ = '0.1'
__author__ = 'Lionel Roubeyrie'
__mail__ = 'lionel.roubeyrie@gmail.com'
__license__ = 'matplotlib license'

import matplotlib
import matplotlib.cm as cm
import numpy as N
from matplotlib.patches import Rectangle, Polygon
from matplotlib.transforms import Interval, Value
from matplotlib.ticker import ScalarFormatter, AutoLocator
from matplotlib.text import Text, FontProperties
from matplotlib.axes import PolarAxes, _process_plot_var_args
from matplotlib.cbook import popd, popall
from numpy.lib.twodim_base import histogram2d


class WindroseAxes(PolarAxes):
    """

    Makes a windrose axes

    """

    RESOLUTION = 100

    def __init__(self, *args, **kwargs):
        """
        See Axes base class for args and kwargs documentation
        """
        PolarAxes.__init__(self, *args, **kwargs)
        self.set_aspect('equal', adjustable='box', anchor='C')
        self.radii_angle = 67.5
        self.cla()

    def _init_axis(self):
        self.xaxis = None
        self.yaxis = None

    def cla(self):
        """
        Clear the current axes
        """

        self._get_lines = _process_plot_var_args(self)
        self._get_patches_for_fill = _process_plot_var_args(self, 'fill')
        self._gridOn = matplotlib.rcParams['polaraxes.grid']
        self.thetagridlabels = []
        self.thetagridlines = []
        self.rgridlabels = []
        self.rgridlines = []
        self.lines = []
        self.images = []
        self.patches = []
        self.artists = []
        self.collections = []
        self.texts = []     # text in axis coords
        self.legend_ = None
        self.grid(self._gridOn)
        self.title =  Text(
            x=0.5, y=1.05, text='',
            fontproperties=FontProperties(size=matplotlib.rcParams['axes.titlesize']),
            verticalalignment='bottom',
            horizontalalignment='center',
            )
        self.title.set_transform(self.transAxes)
        self._set_artist_props(self.title)
        self.thetas = N.linspace(0, 2*N.pi, self.RESOLUTION)
        verts = zip(self.thetas, N.ones(self.RESOLUTION))
        self.axesPatch = Polygon(
            verts,
            facecolor=self._axisbg,
            edgecolor=matplotlib.rcParams['axes.edgecolor'],
            )
        self.axesPatch.set_figure(self.figure)
        self.axesPatch.set_transform(self.transData)
        self.axesPatch.set_linewidth(matplotlib.rcParams['axes.linewidth'])
        self.axison = True
        self.rintv = Interval(Value(0), Value(1))
        self.rintd = Interval(Value(0), Value(1))
        self.rformatter  = ScalarFormatter()
        self.rformatter.set_view_interval(self.rintv)
        self.rformatter.set_data_interval(self.rintd)

        class RadialLocator(AutoLocator):
            'enforce strictly positive radial ticks'

            def __call__(self):
                ticks = AutoLocator.__call__(self)
                return [t for t in ticks if t>0]

        self.rlocator = RadialLocator()
        self.rlocator.set_view_interval(self.rintv)
        self.rlocator.set_data_interval(self.rintd)

        self.theta_angles = N.arange(0, 360, 45)
        self.theta_labels = ['E','N-E','N','N-W','W','S-W','S','S-E']
        self.set_thetagrids(angles=self.theta_angles, labels=self.theta_labels)

        self._info = {'dir' : list(),
                      'bins' : list(),
                      'table' : list()}

        self.patches_list = list()


    def _colors(self, cmap, n):
        '''
        Returns a list of n colors based on the colormap cmap

        '''
        return [cmap(i) for i in N.linspace(0.0, 1.0, n)]


    def set_radii_angle(self, **kwargs):
        """
        Set the radii labels angle
        """

        null = popd(kwargs, 'labels', None)
        angle = popd(kwargs, 'angle', None)
        if angle is None:
            angle = self.radii_angle
        self.radii_angle = angle
        radii = N.linspace(0.1, self.get_rmax(), 6)
        radii_labels = [ "%.1f" %r for r in radii ]
        radii_labels[0] = "" #Removing label 0
        null = self.set_rgrids(radii=radii, labels=radii_labels,
                               angle=self.radii_angle, **kwargs)


    def _update(self):
        self.regrid(self.get_rmax())
        self.set_radii_angle(angle=self.radii_angle)


    def legend(self, loc='lower left', **kwargs):
        """
        Sets the legend location and her properties.
        The location codes are

          'best'         : 0,
          'upper right'  : 1,
          'upper left'   : 2,
          'lower left'   : 3,
          'lower right'  : 4,
          'right'        : 5,
          'center left'  : 6,
          'center right' : 7,
          'lower center' : 8,
          'upper center' : 9,
          'center'       : 10,

        If none of these are suitable, loc can be a 2-tuple giving x,y
        in axes coords, ie,

          loc = (0, 1) is left top
          loc = (0.5, 0.5) is center, center

        and so on.  The following kwargs are supported:

        isaxes=True           # whether this is an axes legend
        prop = FontProperties(size='smaller')  # the font property
        pad = 0.2             # the fractional whitespace inside the legend border
        shadow                # if True, draw a shadow behind legend
        labelsep = 0.005     # the vertical space between the legend entries
        handlelen = 0.05     # the length of the legend lines
        handletextsep = 0.02 # the space between the legend line and legend text
        axespad = 0.02       # the border between the axes and legend edge
        """

        def get_handles():
            handles = list()
            for p in self.patches_list:
                if isinstance(p, matplotlib.patches.Polygon) or \
                isinstance(p, matplotlib.patches.Rectangle):
                    color = p.get_facecolor()
                elif isinstance(p, matplotlib.lines.Line2D):
                    color = p.get_color()
                else:
                    raise AttributeError("Can't handle patches")
                handles.append(Rectangle((0, 0), 0.2, 0.2,
                    facecolor=color, edgecolor='black'))
            return handles

        def get_labels():
            labels = N.copy(self._info['bins'])
            labels = ["[%.1f : %0.1f[" %(labels[i], labels[i+1]) \
                      for i in range(len(labels)-1)]
            return labels

        null = popd(kwargs, 'labels', None)
        null = popd(kwargs, 'handles', None)
        handles = get_handles()
        labels = get_labels()
        self.legend_ = matplotlib.legend.Legend(self, handles, labels,
                                                loc, **kwargs)
        return self.legend_


    def _init_plot(self, dir, var, **kwargs):
        """
        Internal method used by all plotting commands
        """
        #self.cla()
        null = popd(kwargs, 'zorder', None)

        #Init of the bins array if not set
        bins = popd(kwargs, 'bins', None)
        if bins is None:
            bins = N.linspace(N.min(var), N.max(var), 6)
        if isinstance(bins, int):
            bins = N.linspace(N.min(var), N.max(var), bins)
        nbins = len(bins)

        #Init of the number of sectors
        nsector = popd(kwargs, 'nsector', None)
        if nsector is None:
            nsector = 16

        #Sets the colors table based on the colormap or the "colors" argument
        colors = popd(kwargs, 'colors', None)
        cmap = popd(kwargs, 'cmap', None)
        if colors is not None:
            if isinstance(colors, str):
                colors = [colors]*nbins
            if isinstance(colors, (tuple, list)):
                if len(colors) != nbins:
                    raise ValueError("colors and bins must have same length")
        else:
            if cmap is None:
                cmap = cm.jet
            colors = self._colors(cmap, nbins)

        #Building the list of angles
        angles = N.arange(0, -2*N.pi, -2*N.pi/nsector) + N.pi/2

        normed = popd(kwargs, 'normed', False)
        blowto = popd(kwargs, 'blowto', False)

        #Set the global information dictionnary
        self._info['dir'], self._info['bins'], self._info['table'] = histogram(dir, var, bins, nsector, normed, blowto)

        return bins, nbins, nsector, colors, angles, kwargs


    def contour(self, dir, var, **kwargs):
        """
        Plot a windrose in linear mode. For each var bins, a line will be
        draw on the axes, a segment between each sector (center to center).
        Each line can be formated (color, width, ...) like with standard plot
        pylab command.

        Mandatory:
        * dir : 1D array - directions the wind blows from, North centred
        * var : 1D array - values of the variable to compute. Typically the wind
        speeds
        Optional:
        * nsector: integer - number of sectors used to compute the windrose
        table. If not set, nsectors=16, then each sector will be 360/16=22.5°,
        and the resulting computed table will be aligned with the cardinals
        points.
        * bins : 1D array or integer- number of bins, or a sequence of
        bins variable. If not set, bins=6, then
            bins=linspace(min(var), max(var), 6)
        * blowto : bool. If True, the windrose will be pi rotated,
        to show where the wind blow to (usefull for pollutant rose).
        * colors : string or tuple - one string color ('k' or 'black'), in this
        case all bins will be plotted in this color; a tuple of matplotlib
        color args (string, float, rgb, etc), different levels will be plotted
        in different colors in the order specified.
        * cmap : a cm Colormap instance from matplotlib.cm.
          - if cmap == None and colors == None, a default Colormap is used.

        others kwargs : see help(pylab.plot)

        """

        bins, nbins, nsector, colors, angles, kwargs = self._init_plot(dir, var,
                                                                       **kwargs)

        #closing lines
        angles = N.hstack((angles, angles[0]))
        vals = N.hstack((self._info['table'],
                         N.reshape(self._info['table'][:,0],
                                   (self._info['table'].shape[0], 1))))

        offset = 0
        for i in range(nbins):
            val = vals[i,:] + offset
            offset += vals[i, :]
            zorder = nbins - i
            patch = self.plot(angles, val, color=colors[i], zorder=zorder,
                              **kwargs)
            self.patches_list.extend(patch)
        self._update()


    def contourf(self, dir, var, **kwargs):
        """
        Plot a windrose in filled mode. For each var bins, a line will be
        draw on the axes, a segment between each sector (center to center).
        Each line can be formated (color, width, ...) like with standard plot
        pylab command.

        Mandatory:
        * dir : 1D array - directions the wind blows from, North centred
        * var : 1D array - values of the variable to compute. Typically the wind
        speeds
        Optional:
        * nsector: integer - number of sectors used to compute the windrose
        table. If not set, nsectors=16, then each sector will be 360/16=22.5°,
        and the resulting computed table will be aligned with the cardinals
        points.
        * bins : 1D array or integer- number of bins, or a sequence of
        bins variable. If not set, bins=6, then
            bins=linspace(min(var), max(var), 6)
        * blowto : bool. If True, the windrose will be pi rotated,
        to show where the wind blow to (usefull for pollutant rose).
        * colors : string or tuple - one string color ('k' or 'black'), in this
        case all bins will be plotted in this color; a tuple of matplotlib
        color args (string, float, rgb, etc), different levels will be plotted
        in different colors in the order specified.
        * cmap : a cm Colormap instance from matplotlib.cm.
          - if cmap == None and colors == None, a default Colormap is used.

        others kwargs : see help(pylab.plot)

        """

        bins, nbins, nsector, colors, angles, kwargs = self._init_plot(dir, var,
                                                                       **kwargs)
        null = popd(kwargs, 'facecolor', None)
        null = popd(kwargs, 'edgecolor', None)
        offset = 0
        for i in range(nbins):
            val = self._info['table'][i, :] + offset
            offset += self._info['table'][i, :]
            zorder = nbins - i
            patch = self.fill(angles, val, facecolor=colors[i],
                              edgecolor=colors[i], zorder=zorder, **kwargs)
            self.patches_list.extend(patch)


    def bar(self, dir, var, **kwargs):
        """
        Plot a windrose in bar mode. For each var bins and for each sector,
        a colored bar will be draw on the axes.

        Mandatory:
        * dir : 1D array - directions the wind blows from, North centred
        * var : 1D array - values of the variable to compute. Typically the wind
        speeds
        Optional:
        * nsector: integer - number of sectors used to compute the windrose
        table. If not set, nsectors=16, then each sector will be 360/16=22.5°,
        and the resulting computed table will be aligned with the cardinals
        points.
        * bins : 1D array or integer- number of bins, or a sequence of
        bins variable. If not set, bins=6 between min(var) and max(var).
        * blowto : bool. If True, the windrose will be pi rotated,
        to show where the wind blow to (usefull for pollutant rose).
        * colors : string or tuple - one string color ('k' or 'black'), in this
        case all bins will be plotted in this color; a tuple of matplotlib
        color args (string, float, rgb, etc), different levels will be plotted
        in different colors in the order specified.
        * cmap : a cm Colormap instance from matplotlib.cm.
          - if cmap == None and colors == None, a default Colormap is used.
        edgecolor : string - The string color each edge bar will be plotted.
        Default : no edgecolor
        * opening : float - between 0.0 and 1.0, to control the space between
        each sector (1.0 for no space)

        """

        bins, nbins, nsector, colors, angles, kwargs = self._init_plot(dir, var,
                                                                       **kwargs)
        null = popd(kwargs, 'facecolor', None)
        edgecolor = popd(kwargs, 'edgecolor', None)
        if edgecolor is not None:
            if not isinstance(edgecolor, str):
                raise ValueError('edgecolor must be a string color')
        opening = popd(kwargs, 'opening', None)
        if opening is None:
            opening = 0.8
        dtheta = 2*N.pi/nsector
        opening = dtheta*opening

        for j in range(nsector):
            offset = 0
            for i in range(nbins):
                if i > 0:
                    offset += self._info['table'][i-1, j]
                val = self._info['table'][i, j]
                zorder = nbins - i
                patch = Rectangle((angles[j]-opening/2, offset), opening, val,
                    facecolor=colors[i], edgecolor=edgecolor, zorder=zorder,
                    **kwargs)
                self.add_patch(patch)
                if j == 0:
                    self.patches_list.append(patch)
        self._update()


    def box(self, dir, var, **kwargs):
        """
        Plot a windrose in proportional bar mode. For each var bins and for each
        sector, a colored bar will be draw on the axes.

        Mandatory:
        * dir : 1D array - directions the wind blows from, North centred
        * var : 1D array - values of the variable to compute. Typically the wind
        speeds
        Optional:
        * nsector: integer - number of sectors used to compute the windrose
        table. If not set, nsectors=16, then each sector will be 360/16=22.5°,
        and the resulting computed table will be aligned with the cardinals
        points.
        * bins : 1D array or integer- number of bins, or a sequence of
        bins variable. If not set, bins=6 between min(var) and max(var).
        * blowto : bool. If True, the windrose will be pi rotated,
        to show where the wind blow to (usefull for pollutant rose).
        * colors : string or tuple - one string color ('k' or 'black'), in this
        case all bins will be plotted in this color; a tuple of matplotlib
        color args (string, float, rgb, etc), different levels will be plotted
        in different colors in the order specified.
        * cmap : a cm Colormap instance from matplotlib.cm.
          - if cmap == None and colors == None, a default Colormap is used.
        edgecolor : string - The string color each edge bar will be plotted.
        Default : no edgecolor

        """

        bins, nbins, nsector, colors, angles, kwargs = self._init_plot(dir, var,
                                                                       **kwargs)
        null = popd(kwargs, 'facecolor', None)
        edgecolor = popd(kwargs, 'edgecolor', None)
        if edgecolor is not None:
            if not isinstance(edgecolor, str):
                raise ValueError('edgecolor must be a string color')
        opening = N.linspace(0.0, N.pi/16, nbins)

        for j in range(nsector):
            offset = 0
            for i in range(nbins):
                if i > 0:
                    offset += self._info['table'][i-1, j]
                val = self._info['table'][i, j]
                zorder = nbins - i
                patch = Rectangle((angles[j]-opening[i]/2, offset), opening[i],
                    val, facecolor=colors[i], edgecolor=edgecolor,
                    zorder=zorder, **kwargs)
                self.add_patch(patch)
                if j == 0:
                    self.patches_list.append(patch)
        self._update()

def histogram(dir, var, bins, nsector, normed=False, blowto=False):
    """
    Returns an array where, for each sector of wind
    (centred on the north), we have the number of time the wind comes with a
    particular var (speed, polluant concentration, ...).
    * dir : 1D array - directions the wind blows from, North centred
    * var : 1D array - values of the variable to compute. Typically the wind
        speeds
    * bins : list - list of var category against we're going to compute the table
    * nsector : integer - number of sectors
    * normed : boolean - The resulting table is normed in percent or not.
    * blowto : boolean - Normaly a windrose is computed with directions
    as wind blows from. If true, the table will be reversed (usefull for
    pollutantrose)

    """

    if len(var) != len(dir):
        raise ValueError, "var and dir must have same length"

    angle = 360./nsector

    dir_bins=N.arange(-angle/2 ,360.+angle, angle, dtype=N.float)
    dir_edges = dir_bins.tolist()
    dir_edges.pop(-1)
    dir_edges[0] = dir_edges.pop(-1)
    dir_bins[0] = 0.

    var_bins = bins.tolist()
    var_bins.append(N.inf)

    if blowto:
        dir = dir + 180.
        dir[dir>=360.] = dir[dir>=360.] - 360

    table = histogram2d(x=var, y=dir, bins=[var_bins, dir_bins],
                          normed=False)[0]
    # add the last value to the first to have the table of North winds
    table[:,0] = table[:,0] + table[:,-1]
    # and remove the last col
    table = table[:, :-1]
    if normed:
        table = table*100/table.sum()

    return dir_edges, var_bins, table


if __name__=='__main__':
    from pylab import figure, show, setp, random
    vv=random(500)*6
    dv=random(500)*360
    fig = figure(figsize=(8, 8), dpi=80, facecolor='w', edgecolor='w')
    rect = [0.1, 0.1, 0.8, 0.8]
    ax = WindroseAxes(fig, rect, axisbg='w')
    fig.add_axes(ax)

    ax.contourf(dv, vv, bins=N.arange(0,8,1), cmap=cm.hot)
    ax.contour(dv, vv, bins=N.arange(0,8,1), colors='k')
    #ax.bar(dv, vv, normed=True)

    l = ax.legend(axespad=-0.10)
    setp(l.get_texts(), fontsize=8)
    #print ax._info

    show()
