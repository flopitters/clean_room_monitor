#!/usr/bin/python

# ============================================================================
# File: monitor.py
# ------------------------------
#
# Clean room monitor based on rpi with dht22, bmp186 and dc17000.
#
# Notes:
#   -
#
# Status:
#   basic functionality is there
#
# Author: Florian Pitters
#
# ============================================================================

import os
import sys
import wx
import time

from optparse import OptionParser

import numpy as np
import datetime as dt
import matplotlib as mpl
mpl.use('WXAgg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as Canvas
from matplotlib.backends.backend_wxagg import NavigationToolbar2WxAgg as NavigationToolbar


def init_plot_style():
    plt.rcParams['axes.spines.left'] = True
    plt.rcParams['axes.spines.bottom'] = True
    plt.rcParams['axes.spines.top'] = True
    plt.rcParams['axes.spines.right'] = True
    plt.rcParams['axes.grid'] = True

    plt.rcParams['xtick.color'] = 'k'
    plt.rcParams['xtick.labelsize'] = 'small'
    plt.rcParams['ytick.color'] = 'k'
    plt.rcParams['ytick.labelsize'] = 'small'
    plt.rcParams['xtick.minor.visible'] = True
    plt.rcParams['ytick.minor.visible'] = True
    plt.rcParams['xtick.direction'] = 'in'
    plt.rcParams['ytick.direction'] = 'in'

    plt.gca().xaxis.set_ticks_position('both')
    plt.gca().yaxis.set_ticks_position('both')
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.gca().xaxis.set_major_locator(mdates.DayLocator())



# Plot Panel
# -------------------------------------

class plotPanel(wx.Panel):

    def __init__(self, parent, ID, key, dpi = None, **kwargs):
        wx.Panel.__init__(self, parent, ID, **kwargs)

        self.id = ID
        self.key = key
        plt.ion()

        # TODO: Find out how to get rid of the ugly grey frames
        self.SetBackgroundColour("white")

        self.x = np.array([])
        self.y = np.array([])

        self.fig = mpl.figure.Figure(dpi=dpi, figsize=(4,3))
        self.canvas = Canvas(self, -1, self.fig)
        self.ax = self.fig.add_subplot(111)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.fig.canvas, 1, wx.EXPAND)
        self.SetSizer(sizer)


    def update_plot(self, x, y):
        self.x = x
        self.y = y
        self.ax.clear()
        self.ax.plot(self.x, self.y, ls=' ', ms=1, marker='o', mfc='k')
        self.fig.autofmt_xdate()

        if (self.key == 'temp'):
            self.ax.set_ylim([18, 28])
            self.ax.set_ylabel('temperature [C]')
        elif (self.key == 'hum'):
            self.ax.set_ylim([20, 80])
            self.ax.set_ylabel('humidity [%]')
        elif (self.key == 'pres'):
            self.ax.set_ylim([90000, 110000])
            self.ax.set_ylabel('pressure [Pa]')
        elif (self.key == 'cnt5'):
            self.ax.set_ylim([0, 150])
            self.ax.set_ylabel('# particles > 0.5 um [1/in^3]')

        self.canvas.draw()



# Main frame
# -------------------------------------

class mainFrame(wx.Frame):
    """ The main frame of the application. """

    title = 'Clean room monitor'

    def __init__(self, dat_path):
        wx.Frame.__init__(self, None, -1, self.title, size=(1200, 800))

        init_plot_style()

        ## Load data
        self.dat_path = dat_path
        self.plots = []
        self.dat = []
        self.file_list = []
        self.update()

        # Make main GUI
        self.create_menu()
        self.create_main_panel()
        self.create_status_bar()



    def create_menu(self):
        self.menubar = wx.MenuBar()
        menu_file = wx.Menu()

        # item: start
        m_start = menu_file.Append(-1, "&Start monitor\tCtrl-S", "Start monitoring")
        self.Bind(wx.EVT_MENU, self.on_start, m_start)
        menu_file.AppendSeparator()

        # item: stop
        m_stop = menu_file.Append(-1, "&Stop monitor\tCtrl-L", "Stop monitoring")
        self.Bind(wx.EVT_MENU, self.on_stop, m_stop)
        menu_file.AppendSeparator()

        # item: exit
        m_exit = menu_file.Append(-1, "Exit\tCtrl-X", "Exit")
        self.Bind(wx.EVT_MENU, self.on_exit, m_exit)

        self.menubar.Append(menu_file, "&File")
        self.SetMenuBar(self.menubar)


    def create_status_bar(self):
        self.statusbar = self.CreateStatusBar(2)
        self.statusbar.SetStatusText('Clean room monitor', 0)
        self.statusbar.SetStatusText('Running in manual mode', 1)


    def create_main_panel(self):
        self.panel = wx.Panel(self)
        self.panel.SetBackgroundColour("white")

        font = wx.SystemSettings.GetFont(wx.SYS_SYSTEM_FONT)
        font.SetPointSize(12)

        ## Timer
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_update, self.timer)


        ## Buttons
        self.start_button = wx.Button(self.panel, label='Start')
        self.start_button.Bind(wx.EVT_BUTTON, self.on_start)
        self.stop_button = wx.Button(self.panel, label='Stop')
        self.stop_button.Bind(wx.EVT_BUTTON, self.on_stop)
        self.quit_button = wx.Button(self.panel, label='Quit')
        self.quit_button.Bind(wx.EVT_BUTTON, self.on_exit)

        ## Plot frames
        self.tab_temp = wx.Notebook(self.panel, -1, style=0, size=(400, 200))
        self.sheet_temp1 = self.add_plot(self.tab_temp, 1, "Last 24 hours", 'temp')
        self.sheet_temp2 = self.add_plot(self.tab_temp, 2, "Last 30 days", 'temp')
        self.plots.append(self.sheet_temp1)
        self.plots.append(self.sheet_temp2)

        self.tab_hum = wx.Notebook(self.panel, -1, style=0, size=(400, 200))
        self.sheet_hum1 = self.add_plot(self.tab_hum, 3, "Last 24 hours", 'hum')
        self.sheet_hum2 = self.add_plot(self.tab_hum, 4, "Last 30 days", 'hum')
        self.plots.append(self.sheet_hum1)
        self.plots.append(self.sheet_hum2)

        self.tab_pres = wx.Notebook(self.panel, -1, style=0, size=(400, 200))
        self.sheet_pres1 = self.add_plot(self.tab_pres, 5, "Last 24 hours", 'pres')
        self.sheet_pres2 = self.add_plot(self.tab_pres, 6, "Last 30 days", 'pres')
        self.plots.append(self.sheet_pres1)
        self.plots.append(self.sheet_pres2)

        self.tab_cnt = wx.Notebook(self.panel, -1, style=0, size=(400, 200))
        self.sheet_cnt1 = self.add_plot(self.tab_cnt, 7, "Last 24 hours", 'cnt5')
        self.sheet_cnt2 = self.add_plot(self.tab_cnt, 8, "Last 30 days", 'cnt5')
        self.plots.append(self.sheet_cnt1)
        self.plots.append(self.sheet_cnt2)


        ## Grid & layout
        vbox = wx.BoxSizer(wx.VERTICAL)

        # hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        # txt1 = wx.StaticText(self.panel, label='Plots')
        # txt1.SetLabelMarkup("<big><b> Plots </b></big>")
        # hbox1.Add(txt1, flag=wx.ALIGN_CENTER, border=8)
        # vbox.Add(hbox1, flag=wx.ALIGN_CENTER | wx.EXPAND | wx.ALL, border=10)
        # vbox.Add((-1, 10))

        # hbox.Add(innerPanel, 0, wx.ALL|wx.ALIGN_CENTER)
        # vbox.Add(hbox, 1, wx.ALL, 5)

        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        hbox2.Add(self.tab_temp, proportion=1, flag=wx.EXPAND)
        hbox2.Add(self.tab_hum, proportion=1, flag=wx.EXPAND)
        vbox.Add(hbox2, proportion=1, flag=wx.LEFT | wx.RIGHT | wx.EXPAND, border=10)
        vbox.Add((-1, 25))

        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        hbox3.Add(self.tab_pres, proportion=1, flag=wx.EXPAND)
        hbox3.Add(self.tab_cnt, proportion=1, flag=wx.EXPAND)
        vbox.Add(hbox3, proportion=1, flag=wx.LEFT | wx.RIGHT | wx.EXPAND, border=10)
        vbox.Add((-1, 25))

        # hbox4 = wx.BoxSizer(wx.HORIZONTAL)
        # cb1 = wx.CheckBox(self.panel, label='Update')
        # cb1.SetFont(font)
        # hbox4.Add(cb1, flag=wx.RIGHT, border=10)
        # vbox.Add(hbox4, flag=wx.LEFT, border=10)

        vbox.Add((-1, 25))

        ## TODO: How to center these buttons?
        hbox5 = wx.BoxSizer(wx.HORIZONTAL)
        hbox5.Add(self.start_button, flag=wx.RIGHT | wx.BOTTOM, border=5)
        hbox5.Add(self.stop_button, flag=wx.LEFT | wx.BOTTOM, border=5)
        hbox5.Add(self.quit_button, flag=wx.EXPAND | wx.LEFT| wx.BOTTOM, border=5)
        vbox.Add(hbox5, flag=wx.ALIGN_CENTER | wx.LEFT | wx.EXPAND, border=10)

        self.panel.SetSizer(vbox)


    def on_start(self, event):
        # self.timer.Start(3000)
        self.update()

    def on_stop(self, event):
        # self.timer.Stop()
        self.update()

    def on_exit(self, event):
        self.Destroy()

    def on_update(self, event):
        self.update()

    def add_plot(self, tab, id, name='plot', key='temp'):
        page = plotPanel(tab, id, key)
        tab.AddPage(page, name)
        return page

    def set_temp_status(self, event, string):
        self.statusbar.PushStatusText(string)

    def restore_status(self, event):
        self.statusbar.PopStatusText()

    def update(self):
        file_list = [f for f in os.listdir(self.dat_path) if (os.path.isfile(os.path.join(self.dat_path, f)) and ('.txt' in f))]

        ## Load only last 30 days
        for f in file_list[-30:]:
            if f not in self.file_list:
                self.file_list.append(f)

                d = np.genfromtxt(self.dat_path + f, comments='#', \
                        dtype=[('date', 'S10'), ('time', 'S8'), ('temp', '<f8'), ('hum', '<f8'), \
                               ('pres', '<i8'), ('cnt5', '<i8'), ('cnt25', '<i8'), ('iso', '<i8'), ('class', '<i8')])

                if len(self.dat) == 0:
                    self.dat = d
                else:
                    self.dat = np.concatenate((self.dat, d), axis=0)

        ## Update plots and format
        for plot in self.plots:
            x = np.array([dt.datetime.combine(dt.datetime.strptime(self.dat['date'][i], '%Y-%m-%d').date(),
                          dt.datetime.strptime(self.dat['time'][i], '%H:%M:%S').time()) for i in range(len(self.dat))])

            if (plot.id == 1):
                # last 24 hours, assuming 1 measurement per 2 min
                plot.update_plot(x[-720::2], self.dat['temp'][-720::2])

            elif (plot.id == 2):
                # last 30 days, one per 2 hours, assuming 1 measurement per 2 min
                plot.update_plot(x[-21600::60], self.dat['temp'][-21600::60])

            elif (plot.id == 3):
                plot.update_plot(x[-720::2], self.dat['hum'][-720::2])

            elif (plot.id == 4):
                plot.update_plot(x[-21600::60], self.dat['hum'][-21600::60])

            elif (plot.id == 5):
                plot.update_plot(x[-720::2], self.dat['pres'][-720::2])

            elif (plot.id == 6):
                plot.update_plot(x[-21600::60], self.dat['pres'][-21600::60])

            elif (plot.id == 7):
                plot.update_plot(x[-720::2], self.dat['cnt5'][-720::2])

            elif (plot.id == 8):
                plot.update_plot(x[-21600::60], self.dat['cnt5'][-21600::60])



# Main app
# -------------------------------------

def main():
    usage = "usage: ./monitor.py -d [data_path]"

    parser = OptionParser(usage=usage, version="prog 0.01")
    parser.add_option("-d", "--dat_path", action="store", dest="dat_path", type="string", default="",  help="data path")

    (options, args) = parser.parse_args()
    if (options.dat_path == ""):
	       parser.error("You need to give a data path. Try '-h' for more info.")

    app = wx.App()
    app.frame = mainFrame(options.dat_path)
    app.frame.Show()
    app.MainLoop()



if __name__=="__main__":
	main()
