#!/usr/bin/env pythonw

"""
FC_Rose.py

An implementation of the Wind rose in FloatCanvas.
"""

import os
import datetime
import wx
import numpy as np
# from math import radians
# from math import degrees

from windtools import MetData
from windtools import WindRose

# reload(WindRose)  # for developing
# import the installed version

from wx.lib.floatcanvas import FloatCanvas
#from wx.lib.floatcanvas.Utilities import Colors

import windtools.colormaps

months = ['All Year', 'January', 'February', 'March', 'April',
          'May', 'June', 'July', 'August', 'September', 'October',
          'November', 'December']

class MyFloatCanvas(FloatCanvas.FloatCanvas):
    ## New OnSizeTimer, so that it will zoom to the bounding box on each size event.
    def OnSizeTimer(self, event=None):
        self.MakeNewBuffers()
        self.ZoomToBB()

class RoseFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        wx.Frame.__init__(self, *args, **kwargs)

        self.LastDir = os.getcwd()

        MenuBar = wx.MenuBar()

        FileMenu = wx.Menu()

        item = FileMenu.Append(wx.ID_ANY, text = "&Open")
        self.Bind(wx.EVT_MENU, self.OnOpen, item)

        item = FileMenu.Append(wx.ID_ANY, text = "&Save Image")
        self.Bind(wx.EVT_MENU, self.OnSaveImage, item)

        item = FileMenu.Append(wx.ID_ANY, text = "&Save Data Table")
        self.Bind(wx.EVT_MENU, self.OnSaveData, item)

        item = FileMenu.Append(wx.ID_PREFERENCES, text = "&Preferences")
        self.Bind(wx.EVT_MENU, self.OnPrefs, item)

        item = FileMenu.Append(wx.ID_EXIT, text = "&Exit")
        self.Bind(wx.EVT_MENU, self.OnQuit, item)

        MenuBar.Append(FileMenu, "&File")

        HelpMenu = wx.Menu()

        item = HelpMenu.Append(wx.ID_HELP, "Test &Help",
                                "Help for this simple test")
        self.Bind(wx.EVT_MENU, self.OnHelp, item)

        ## this gets put in the App menu on OS-X
        item = HelpMenu.Append(wx.ID_ABOUT, "&About",
                                "More information About this program")
        self.Bind(wx.EVT_MENU, self.OnAbout, item)
        MenuBar.Append(HelpMenu, "&Help")

        self.SetMenuBar(MenuBar)

        self.Bind(wx.EVT_CLOSE, self.OnQuit)

        # a panel just to the the background color right on windows
        BGPanel = wx.Panel(self)
        self.WindRose = WindRosePanel(BGPanel, size=(600,600),)
        self.WindRose.SetSizeHints(50, 50, -1, -1)
        self.WindRose.Canvas.SetSizeHints(50, 50, -1, -1)

        self.MonthSelector = wx.Choice(BGPanel, choices=months)
        self.MonthSelector.Selection = 0
        self.MonthSelector.Bind(wx.EVT_CHOICE, self.OnSelectMonth)

        self.NumBinsSelector = wx.Choice(BGPanel, choices=['4', '8', '16', '32'])
        self.NumBinsSelector.Selection = 2
        self.NumBinsSelector.Bind(wx.EVT_CHOICE, self.OnSelectNumBins)

        Stop = wx.BoxSizer(wx.HORIZONTAL)
        Stop.Add(self.MonthSelector, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        Stop.Add((1,1), 1)
        Stop.Add(wx.StaticText(BGPanel, label="Number of Bins:"), 0, wx.ALIGN_CENTER_VERTICAL )
        Stop.Add(self.NumBinsSelector, 0, wx.ALIGN_RIGHT|wx.ALL, 5)

        S = wx.BoxSizer(wx.VERTICAL)
        S.Add(Stop, 0, wx.EXPAND)
        S.Add(self.WindRose, 1, wx.EXPAND)


        BGPanel.SetSizer(S)
        self.Show()

        #self.vel_bins = [1, 5, 10, 15, 21,]
        self.vel_bins = [3, 6, 10, 15, 20, 25, 35, 55]
        self.num_dir_bins = 16

    def OnQuit(self,Event):
        self.Destroy()

    def OnAbout(self, event):
        dlg = wx.MessageDialog(self,
                               "This is a small program to generate\n"
                               "Wind Roses from historical wind data\n"
                               " See Chris Barker for more info\n"
                               "About Me", wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()

    def OnHelp(self, event):
        dlg = wx.MessageDialog(self, "This would be help\n"
                                     "If there was any\n",
                                "Test Help", wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()

    def OnOpen(self, event):
        dlg = wx.FileDialog(self,
                            message="Choose a wind file",
                            defaultDir=self.LastDir,
                            defaultFile="",
                            #wildcard=wildcard,
                            style=wx.OPEN | wx.CHANGE_DIR
                            )

        if dlg.ShowModal() == wx.ID_OK:
            # This returns a Python list of files that were selected.
            path = dlg.GetPath()
            self.LastDir = os.path.split(path)[0]
            self.LoadNewFile(path)
        dlg.Destroy()

    def OnSaveImage(self, evt):
        dlg = wx.FileDialog(self,
                            message="Choose an image file name",
                            defaultDir=self.LastDir,
                            defaultFile="",
                            wildcard="*.png",
                            style=wx.SAVE | wx.CHANGE_DIR
                            )

        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.LastDir = os.path.split(path)[0]
            self.WindRose.SaveImage(path)
        dlg.Destroy()

    def OnSaveData(self, evt):
        dlg = wx.FileDialog(self,
                            message="Choose a data file",
                            defaultDir=self.LastDir,
                            defaultFile="",
                            wildcard="*.csv",
                            style=wx.SAVE | wx.CHANGE_DIR
                            )

        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.LastDir = os.path.split(path)[0]
            self.WindRose.SaveBinTable(path)
        dlg.Destroy()

    def OnPrefs(self, event):
        dlg = wx.MessageDialog(self, "This would be an preferences Dialog\n"
                                     "If there were any preferences to set.\n",
                               "Preferences", wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()

    def LoadNewFile(self, infilename):
        try:
            self.MetData = MetData(infilename)
        except Exception as err:
            dlg = wx.MessageDialog(self, str(err), "File Not Loaded", wx.OK | wx.ICON_WARNING)
            dlg.ShowModal()
            dlg.Destroy()
        self.MonthSelector.SetStringSelection("All Year")
        self.OnSelectMonth()

    def OnSelectMonth(self, evt=None):
        month = self.MonthSelector.StringSelection
        month_ind = months.index(month)

        if month_ind == 0:  # All Year
            data = self.MetData.GetFieldsAsArray(("WindSpeed", "WindDirection"))
        else:
            data = self.MetData.GetFieldsMonthlyAsArray((month_ind,), ("WindSpeed",
                                                                       "WindDirection"))

        if len(data) == 0:
            self.WindRose.DrawMessage("No Data for %s" % month)
        else:
            units = self.MetData.Units['WindSpeed']
            if units == 'knots':
                vel_bins = [3, 6, 10, 15, 20, 25, 35, 55]
            elif units == 'm/s':
                vel_bins = [1, 5, 10, 15, 21]
            else:
                vel_bins = self.vel_bins

            title = title = "%s: %s"%  (self.MetData.Name, month)
            Rose = WindRose(data,
                            vel_bins,
                            num_dir_bins=self.num_dir_bins,
                            units=units,
                            title=title,
                            )
            self.WindRose.DrawRose(Rose)

    def OnSelectNumBins(self, evt=None):
        self.num_dir_bins = int(self.NumBinsSelector.StringSelection)
        self.OnSelectMonth()


class WindRoseParametersPanel(wx.Panel):
    def __init__(self, parent,  Rose, *args, **kwargs):
        wx.Panel.__init__(self, parent, *args, **kwargs)

        self.Rose = Rose

        ## build the GUI:
        MainSizer = wx.GridSizer(rows=4, cols=2, vgap=5, hgap=5)


class WindRosePanel(wx.Panel):

    """
    A Panel with a WindRose in it

    """

    def __init__(self, parent,  *args, **kwargs):
        wx.Panel.__init__(self, parent, *args, **kwargs)

        # Add the Canvas
        # Canvas = FloatCanvas.FloatCanvas(self,
        Canvas = MyFloatCanvas(self,
                               wx.ID_ANY,
                               size = (500,500),
                               BackgroundColor = "White",
                               )
        S = wx.BoxSizer(wx.VERTICAL)
        S.Add(Canvas, 1, wx.EXPAND)

        self.Canvas = Canvas

        #FloatCanvas.EVT_MOTION(Canvas, self.OnMove )

        self.SetSizerAndFit(S)

        # assorted constants:
        self.small_text = 0.07
        self.med_text = 0.09
        self.large_text = 0.12
        self.font_family = wx.SWISS

        self.Show()



    def DrawMessage(self, message):
        Canvas = self.Canvas
        Canvas.ClearAll()
        Canvas.AddScaledText(message,
                             (0, 1.3),
                             Size = self.med_text,
                             Weight = wx.BOLD,
                             Family = self.font_family,
                             Position='tc',
                             )
        w = 2.7
        Canvas.AddRectangle((-w/2, -w/2), (w, w), LineStyle=None )

        Canvas.ZoomToBB()

    def DrawRose(self, Rose):
        self.Rose = Rose
        wfs = Rose.binned_data
        vel_bins = Rose.vel_bins
        units = Rose.units
        title = Rose.title

        Canvas = self.Canvas
        Canvas.ClearAll()

        calm = wfs[0,:].sum()
        n_dir = wfs.shape[1] # number of direction bins

        # remove the calm row
        wfs = wfs [1:,:]
        n = wfs.shape[0]
        c = (8. / n * np.linspace(0,n,n) + 2)[::-1]
        cm = windtools.colormaps.ColorMap("jet")
        clrs = cm.get_colors(c, (0,10))
        wf = wfs.sum(axis=0)
        max_percent = wf.max() # max percent in all direction bins

        #sc = float(rsize)**2/mwf #scale factor, pts per number
        da = 2.0 * np.pi / n_dir
        dah = .45 * da

        theta = np.linspace(0, 2*np.pi, n_dir+1)[:-1]

        #now plot :
        line_width=1
        fill_color="black"
        text_pos='cc'

        ## compute the locations of the circles
        if max_percent <= 12:
            circles = range(2, int(max_percent)+3, 2)
        elif max_percent <= 30:
            circles = [3] + range(5, int(max_percent)+6, 5)
        elif max_percent <= 60:
            circles = [5] + range(10, int(max_percent)+11, 10)
        else:
            circles = [5, 10] + range(20, int(max_percent)+21, 20)
        # compute the radius of the center calm circle
        r_center = np.sqrt(calm/n_dir)
        r_circles = np.sqrt(np.array(circles)) + r_center
        max_r = r_circles[-1]
        r_scale = 1/max_r
        r_circles *= r_scale
        r_center  *= r_scale

        # compute the radius of the center calm circle
        r_center = np.sqrt(calm/n_dir) * r_scale
        # generate the "petals"
        for i, a in enumerate(theta):
            percents = list(np.cumsum(wfs[:,i]))
            percents.reverse()
            for i, percent in enumerate(percents):
                if percent == 0:
                    continue
                r = (np.sqrt((percent))*r_scale + r_center)
                Canvas.AddObject(FloatCanvas.Arc(( r*np.sin(a+dah), r*np.cos(a+dah) ),
                                                 ( r*np.sin(a-dah), r*np.cos(a-dah) ),
                                                 (0,0),
                                                 #LineColor = "Black",
                                                 LineStyle = None,
                                                 LineWidth    = 1,
                                                 FillColor    = tuple(clrs[i]),
                                                 FillStyle    = "Solid",
                                                 )
                                 )

        for r, percent in zip(r_circles, circles): # make the blue circles
            Canvas.AddCircle((0,0),
                             r*2,
                             LineColor="blue",
                             )
            lab="%i%%" % (percent)
            Canvas.AddScaledText(lab,
                           (0, -r),
                           Size=self.small_text,
                           Family=self.font_family,
                           BackgroundColor='white',
                           Position='cc'
                           )

        # put the percent light and variable in the middle:
        Canvas.AddCircle((0,0),
                         r_center*2,
                         #LineColor="red",
                         LineColor=None,
                         FillColor="White"
                         #FillColor=None
                         )
        Canvas.AddScaledText("%.1f%%"%calm,
                       (0,0),
                       Family=self.font_family,
                       Position=text_pos,
                       BackgroundColor = "White",
                       Size=self.small_text)
        # Add the compass points
        r = 1.05
        text_style = {"Size": self.large_text,
                      "Weight":wx.BOLD,
                      "Family":self.font_family}
        Canvas.AddScaledText("N",
                       (0,r),
                       Position='bc',
                       **text_style)
        Canvas.AddScaledText("S",
                       (0,-r),
                       Position='tc',
                       **text_style)
        Canvas.AddScaledText("E",
                       (r,0),
                       Position='cl',
                       **text_style)
        Canvas.AddScaledText("W",
                       (-r,0),
                       Position='cr',
                       **text_style)

        # add the Title:
        if title is None:
            title = "Wind Rose"
        Canvas.AddScaledText(title,
                             (0, 1.4),
                             Size = self.med_text,
                             Weight = wx.BOLD,
                             Family = self.font_family,
                             Position='tc',
                             )

        # Add the legend:
        #vel_bins = vel_bins[1:-1]
        n = len(vel_bins)
        W = 2.0
        dw = W/n
        X0 = -W/2.0
        Y = -1.5
        H = 0.1
        for i, vel in enumerate(vel_bins):
            X = X0 + i*dw
            Canvas.AddRectangle((X, Y),
                                (dw*1.03, 0.1),
                                LineStyle = None,
                                FillColor = tuple(clrs[-(i+1)]),
                                )
            Canvas.AddScaledText("%i"%vel,
                                 (X, Y+H),
                                 Size = self.small_text,
                                 Family=self.font_family,
                                 #Weight = wx.BOLD,
                                 Position='bc',
                                 )
        Canvas.AddScaledText(units,
                             (X+dw, Y+H),
                             Size = self.small_text,
                             Family=self.font_family,
                             #Weight = wx.BOLD,
                             Position='bl',
                             )

        # add an invisible box for the Bounding Box:
        #Canvas._ResetBoundingBox()
        #w = np.abs(Canvas.BoundingBox).max() * 2
        #Canvas.AddRectangle((-w/2, -w/2), (w, w), LineStyle=None )

        Canvas.ZoomToBB()

    def SaveImage(self, filename):
        if filename[-4:].lower() != ".png":
            filename = filename + ".png"
        self.Canvas.SaveAsImage(filename)

    def SaveBinTable(self, path):
        self.Rose.SaveBinTable(path)

class RoseApp(wx.App):
    def OnInit(self):
        self.frame = RoseFrame(None, size=(500,500))
        self.frame.Show()

        import sys
        if len(sys.argv) > 1:
            infilename = sys.argv[1]
            self.frame.LoadNewFile(infilename)
        else:
            self.frame.MetData = make_random_data(5000)
            self.frame.OnSelectMonth()
        return True

#    def OpenFileMessage(self, filename):
#        dlg = wx.MessageDialog(None,
#                               "This app was just asked to open:\n%s\n"%filename,
#                               "File Dropped",
#                               wx.OK|wx.ICON_INFORMATION)
#        dlg.ShowModal()
#        dlg.Destroy()

    def MacOpenFile(self, filename):
        print filename
        print "%s dropped on app"%(filename) #code to load filename goes here.
        self.frame.LoadNewFile(filename)

def make_random_data(num_samples):
    dirs = np.r_[np.random.normal(loc=45, scale = 20, size=(num_samples,) ),
                 np.random.normal(loc=270, scale = 40, size=(num_samples,) )] % 360
    spds = np.random.normal(loc=10, scale = 6, size=(2*num_samples,) )
    spds = np.where((spds<0), 0, spds)
    data = np.c_[spds, dirs]
    # make an hourly time series
    Times = [datetime.datetime(2009,1,1) + datetime.timedelta(hours=i) for i in range(len(data))]
    data = MetData( FileReader=None,
                            DataArray=data,
                            Fields = { "WindSpeed": 0,
                                       "WindDirection": 1,
                                       },
                            Units = {"WindSpeed": "knots",   # most often?
                                     "WindDirection": "degrees",
                                     },
                            Times=[datetime.datetime(2009,1,1) + datetime.timedelta(hours=i) for i in range(len(data))],
                            Name='Fake Sample Data',
                            )
    return data

if __name__ == "__main__":
    print "getting app:", wx.GetApp()
    if wx.GetApp() is None:
        print "no app -- making one"
        app = RoseApp(False)
    else:
        print "there is already an app"

    try: # see if we're running in ipython
        print "using ipython to start"
        from IPython import appstart_wx
        appstart_wx(app)
    except ImportError: # we're not -- do the regular start up
        print "Ipython did not import"
        app.MainLoop()

