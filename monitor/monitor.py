import os
import sys
import wx
import time

import numpy as np
import matplotlib as mpl
mpl.use('WXAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as Canvas
from matplotlib.backends.backend_wxagg import NavigationToolbar2WxAgg as NavigationToolbar




# Plot Panel
# -------------------------------------

class plotPanel(wx.Panel):

    def __init__(self, parent, ID, dpi = None, **kwargs):
        wx.Panel.__init__(self, parent, ID, **kwargs)

        self.id = ID
        plt.ion()

        self.fig = mpl.figure.Figure(dpi=dpi, figsize=(4,3))
        self.canvas = Canvas(self, -1, self.fig)
        self.ax = self.fig.add_subplot(111)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.fig.canvas, 1, wx.EXPAND)
        self.SetSizer(sizer)


    def update_plot(self, x, y):
        self.ax.clear()
        self.ax.plot(x, y)
        self.fig.autofmt_xdate()
        self.canvas.draw()




# Main frame
# -------------------------------------

class mainFrame(wx.Frame):
    """ The main frame of the application. """

    title = 'Clean room monitor'

    def __init__(self):
        wx.Frame.__init__(self, None, -1, self.title, size=(800,650))

        self.plots = []
        self.paused = 0

        # Main GUI
        self.create_menu()
        self.create_status_bar()
        self.create_main_panel()


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
        self.statusbar = wx.StatusBar(self)


    def create_main_panel(self):
        self.panel = wx.Panel(self)

        self.update_button = wx.Button(self, -1, label="Update", size=(60,20), pos=(370, 600))
        self.update_button.Bind(wx.EVT_BUTTON, self.on_update)

        self.tab_temp = wx.Notebook(self, -1, style=0, size=(400,300), pos=(0,0))
        self.sheet_temp1 = self.add_plot(self.tab_temp, 1, "Last 24 hours")
        self.sheet_temp2 = self.add_plot(self.tab_temp, 2, "Last 30 days")
        self.plots.append(self.sheet_temp1)
        self.plots.append(self.sheet_temp2)

        self.tab_hum = wx.Notebook(self, -1, style=0, size=(400,300), pos=(400,0))
        self.sheet_hum1 = self.add_plot(self.tab_hum, 3, "Last 24 hours")
        self.sheet_hum2 = self.add_plot(self.tab_hum, 4, "Last 30 days")
        self.plots.append(self.sheet_hum1)
        self.plots.append(self.sheet_hum2)

        self.tab_pres = wx.Notebook(self, -1, style=0, size=(400,300), pos=(0,300))
        self.sheet_pres1 = self.add_plot(self.tab_pres, 5, "Last 24 hours")
        self.sheet_pres2 = self.add_plot(self.tab_pres, 6, "Last 30 days")
        self.plots.append(self.sheet_pres1)
        self.plots.append(self.sheet_pres2)

        self.tab_cnt = wx.Notebook(self, -1, style=0, size=(400,300), pos=(400,300))
        self.sheet_cnt1 = self.add_plot(self.tab_cnt, 7, "Last 24 hours")
        self.sheet_cnt2 = self.add_plot(self.tab_cnt, 8, "Last 30 days")
        self.plots.append(self.sheet_cnt1)
        self.plots.append(self.sheet_cnt2)


    def on_start(self, event):
        self.paused = 0

    def on_stop(self, event):
        self.paused = 1

    def on_exit(self, event):
        self.Destroy()

    def on_update(self, event):
        self.update()


    def on_toggle(self, event):
        if self.timer.IsRunning():
            self.timer.Stop()
            self.toggle_button.SetLabel("Start")
            print "timer stopped!"
        else:
            print "starting timer..."
            self.timer.Start(30000)
            self.toggle_button.SetLabel("Stop")


    def add_plot(self, tab, id, name="plot"):
        page = plotPanel(tab, id)
        tab.AddPage(page, name)
        return page


    def update(self):
        data = np.array([])
        data_path = "/Users/Home/Documents/Works/rpi/monitor/data/"
        file_list =  [f for f in os.listdir(data_path) if (os.path.isfile(os.path.join(data_path, f)) and ('.txt' in f))]

        # TODO: Reads all 30 files everytime. Better: Check if new file and if not only re-read last one.

        k = 0
        for f in file_list[-30:]:
            d = np.genfromtxt(data_path + f, comments='#', dtype=[('date', 'S10'), ('time', 'S8'), ('temp', '<f8'), ('hum', '<f8'), ('pres', '<i8'), ('cnt5', '<i8'), ('cnt25', '<i8'), ('iso', '<i8'), ('class', '<i8')])
            if k == 0:
                data = d
            else:
                data = np.concatenate((data, d), axis=0)
            k += 1

        for plot in self.plots:
            if (plot.id == 1):
                # last 24 hours, one per 2 min, assuming 1 measurement per 2 min
                plot.update_plot(data['time'][-720::1], data['temp'][-720::1])

            elif (plot.id == 2):
                # last 30 days, one per 2 hours, assuming 1 measurement per 2 min
                plot.update_plot(data['date'][-21600::30], data['temp'][-21600::30])

            elif (plot.id == 3):
                plot.update_plot(data['time'][-720::1], data['hum'][-720::1])

            elif (plot.id == 4):
                plot.update_plot(data['date'][-21600::30], data['hum'][-21600::30])

            elif (plot.id == 5):
                plot.update_plot(data['time'][-720::1], data['pres'][-720::1])

            elif (plot.id == 6):
                plot.update_plot(data['date'][-21600::30], data['pres'][-21600::30])

            elif (plot.id == 7):
                plot.update_plot(data['time'][-720::1], data['cnt5'][-720::1])

            elif (plot.id == 8):
                plot.update_plot(data['date'][-21600::30], data['cnt5'][-21600::30])



# Main app
# -------------------------------------

if __name__ == '__main__':
    app = wx.App()
    app.frame = mainFrame()
    app.frame.Show()
    app.MainLoop()
