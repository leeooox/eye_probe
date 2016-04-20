from __future__ import division as _division, print_function as _print_function
import wx
import numpy as np
import matplotlib as mpl
mpl.use("WXAgg")
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wx import NavigationToolbar2Wx
from matplotlib.figure import Figure
from matplotlib.widgets import Slider
from scipy.signal import resample
from eye_core import calc_eye_heatmap,get_demo_data,seg_map_scope
from wx.lib.intctrl import IntCtrl
import wx.lib.agw.floatspin as FS
import wx.lib.filebrowsebutton as filebrowse
scope_cmap = mpl.colors.LinearSegmentedColormap("scope_cmap",seg_map_scope,N=4096)
#norm_mask1 = np.array( [[0.315,0.5], [0.50,0.53], [0.685,0.5], [0.5,0.47]])



class MyFrame(wx.Frame):

    def __init__(self):
        wx.Frame.__init__(self, None, -1, 
                "Eye Probe", 
                size=(1024, 620))
        
        panel = wx.Panel(self,-1)
       




        self.fbb_waveform_path = filebrowse.FileBrowseButton(
            panel, -1, size=(300, -1), labelText="Waveform")

        self.int_npui = IntCtrl(panel,-1,32,min=1,max=99999,limited=True,size=(50,-1))


        self.fs_datarate = FS.FloatSpin(panel, -1,size=(65,-1), min_val=0, max_val=9999,
                                       increment=0.1, value=10, agwStyle=FS.FS_LEFT)

        self.fs_datarate.SetFormat("%G")
        self.fs_datarate.SetDigits(5)



        self.cb_sinc_interp_n = wx.ComboBox(panel, -1,"Off", (-1, -1), 
                         (-1, -1), ["Off","2pts","4pts","8pts","16pts"],
                         wx.CB_DROPDOWN
                         |wx.CB_READONLY
                         )

        self.cb_CRU =  wx.ComboBox(panel, -1,"Constant clock", (-1, -1), 
                         (-1, -1), ["Constant clock","Clock times file"],
                         wx.CB_DROPDOWN
                         |wx.CB_READONLY
                         )

        self.fbb_clock_time_file = filebrowse.FileBrowseButton(
            panel, -1, size=(300, -1), labelText="Clock times")

        self.fbb_clock_time_file.Enable(False)

        self.int_ignor_cycles = IntCtrl(panel,-1,0,min=0,max=9999999,limited=True,size=(50,-1))
        self.int_ignor_cycles.Enable(False)

        self.cb_colorbar_en= wx.CheckBox(panel,-1,"Enable Colorbar")

        self.cb_mask_en= wx.CheckBox(panel,-1,"Enable Mask")


        self.sld_maskadj = wx.Slider(panel,-1, 0, -100, 100,size=(300,-1))

        self.fbb_mask_path = filebrowse.FileBrowseButton(
            panel, -1, size=(300, -1), labelText="Mask")
        self.fbb_mask_path.Enable(False)
        self.sld_maskadj.Enable(False)

        self.btn_plot = wx.Button(panel,-1,"Plot Eye")


        self.canvas = FigureCanvas(panel, -1, Figure())
        self.figure = self.canvas.figure
        self.axes1 = self.figure.add_subplot(1,1,1)
        self.axes1.set_axis_bgcolor('k')
        self.axes1.grid(c="w")
        self.axes2 = None

        toolbar = NavigationToolbar2Wx(self.canvas)


        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer_left = wx.GridBagSizer(hgap=5, vgap=10)
        sizer_left.Add(self.fbb_waveform_path,pos=(0,0),span=(1,3),flag=wx.ALIGN_CENTER_VERTICAL)


        sizer_left.Add(wx.StaticText(panel,-1,"Samples per UI"),pos=(1,0),flag=wx.ALIGN_CENTER_VERTICAL)
        sizer_left.Add(self.int_npui,pos=(1,1),flag=wx.ALIGN_CENTER_VERTICAL)

        sizer_left.Add(wx.StaticText(panel,-1,"Data Rate"),pos=(2,0),flag=wx.ALIGN_CENTER_VERTICAL)
        sizer_left.Add(self.fs_datarate,pos=(2,1),flag=wx.ALIGN_CENTER_VERTICAL)
        sizer_left.Add(wx.StaticText(panel,-1,"Gbps"),pos=(2,2),flag=wx.ALIGN_CENTER_VERTICAL)

        sizer_left.Add(wx.StaticText(panel,-1,"Sin(x)/x Interp"),pos=(3,0),flag=wx.ALIGN_CENTER_VERTICAL)
        sizer_left.Add(self.cb_sinc_interp_n,pos=(3,1),flag=wx.ALIGN_CENTER_VERTICAL)

        sizer_left.Add(wx.StaticText(panel,-1,"Clock Recovery"),pos=(4,0),flag=wx.ALIGN_CENTER_VERTICAL)
        sizer_left.Add(self.cb_CRU,pos=(4,1),span=(1,2),flag=wx.ALIGN_CENTER_VERTICAL)

        sizer_left.Add(self.fbb_clock_time_file,pos=(5,0),span=(1,3),flag=wx.ALIGN_CENTER_VERTICAL)
        sizer_left.Add(wx.StaticText(panel,-1,"Ignore cycles"),pos=(6,0),flag=wx.ALIGN_CENTER_VERTICAL)
        sizer_left.Add(self.int_ignor_cycles,pos=(6,1),flag=wx.ALIGN_CENTER_VERTICAL)

        sizer_left.Add(self.cb_colorbar_en,pos=(7,0),span=(1,3),flag=wx.ALIGN_CENTER_VERTICAL)
        sizer_left.Add(self.cb_mask_en,pos=(8,0),span=(1,3),flag=wx.ALIGN_CENTER_VERTICAL)

        sizer_left.Add(self.fbb_mask_path,pos=(9,0),span=(1,3),flag=wx.ALIGN_CENTER_VERTICAL)
        sizer_left.Add(self.sld_maskadj,pos=(10,0),span=(1,3),flag=wx.ALIGN_CENTER_VERTICAL)
        
        sizer_left.Add(self.btn_plot,pos=(11,0),span=(1,3),flag=wx.ALIGN_CENTER_VERTICAL)


        sizer_right = wx.BoxSizer(wx.VERTICAL)

        sizer_right.Add(toolbar, 0, wx.EXPAND|wx.RIGHT)
        sizer_right.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.GROW)
        
        sizer.Add(sizer_left,0,wx.ALL,10)
        sizer.Add(sizer_right,1,wx.GROW)

        panel.SetSizer(sizer)
        sizer.Fit(panel)


        self.eye_mask_en = True

        self.btn_plot.Bind(wx.EVT_BUTTON, self.OnPlot)
        self.sld_maskadj.Bind(wx.EVT_SCROLL_CHANGED, self.OnAdjustMask)
        self.cb_mask_en.Bind(wx.EVT_CHECKBOX, self.OnEnableEyeMask)
        self.cb_CRU.Bind(wx.EVT_COMBOBOX, self.OnChangeCRU)

        #sig,samps_per_ui,ui = get_demo_data() 

        #self.plot_eye(sig,samps_per_ui,ui,colorbar_en=False)


    def _get_conf(self):
        sig_file = self.fbb_waveform_path.GetValue()
        samps_per_ui = self.int_npui.GetValue()
        data_rate = self.fs_datarate.GetValue()
        sinc_interp_str = self.cb_sinc_interp_n.GetValue()
        if sinc_interp_str == "Off":
            sinc_interp_n = 0
        else:
            sinc_interp_n = int(sinc_interp_str[:-3])
    
        CRU_str = self.cb_CRU.GetValue()
        if CRU_str == "Clock times file":
            clock_times_file = self.fbb_clock_time_file.GetValue()
        else:
            clock_times_file = None

        ignor_cycles = self.int_ignor_cycles.GetValue()

        colorbar_en = self.cb_colorbar_en.GetValue()
        mask_en = self.cb_mask_en.GetValue()
        mask_path = self.fbb_mask_path.GetValue()

        return (sig_file,samps_per_ui,data_rate,
                sinc_interp_n,clock_times_file,
                ignor_cycles,colorbar_en,mask_en,
                mask_path)

    def OnChangeCRU(self,evt):
        CRU_str = evt.GetEventObject().GetValue()

        if CRU_str == "Clock times file":
            self.fbb_clock_time_file.Enable(True)
            self.int_ignor_cycles.Enable(True)
        else:
            self.fbb_clock_time_file.Enable(False)
            self.int_ignor_cycles.Enable(False)


    def OnPlot(self,evt):
        #print (self._get_conf())
        #print("plot")
        sig_file,samps_per_ui,data_rate,sinc_interp_n,\
        clock_times_file,ignor_cycles,colorbar_en,\
        mask_en,mask_path = self._get_conf()
        sig = np.loadtxt(sig_file)
        if clock_times_file is not None:
            clock_times = np.loadtxt(clock_times_file)[ignor_cycles:]
        else:
            clock_times = None
        #print(len(sig))
        if sinc_interp_n>0: 
            sig = resample(sig,len(sig)*sinc_interp_n)
            samps_per_ui *= sinc_interp_n

        ui = 1e-9/data_rate
        if mask_en:
            if mask_path:
                norm_mask1 = np.loadtxt(mask_path,delimiter=",")
                eye_mask = self.get_mask(norm_mask1,ui*1e12)
            else:
                eye_mask = None # should print some errors
        else:
            eye_mask = None

        self.plot_eye(sig,samps_per_ui,ui,clock_times,
                colorbar_en,eye_mask)

    def OnAdjustMask(self,evt):
        val = evt.EventObject.GetValue()
        mask_temp = self.mask_array.copy()
        mask_temp[:,0] = self.mask_array[:,0]+val
        self.mask_poly.set_xy(mask_temp)
        self.canvas.draw_idle()
        
    def OnEnableEyeMask(self,evt):
        mask_en = evt.EventObject.GetValue()
        self.fbb_mask_path.Enable(mask_en)
        self.sld_maskadj.Enable(mask_en)



    def get_mask(self,norm_mask,ui,vhigh=1,vlow=-1):
        mask = norm_mask.copy()
        mask[:,0]-=0.5
        mask[:,0] *= ui
        mask[:,1] -= 0.5
        mask[:,1] *= (vhigh-vlow)
        return mask



    def plot_eye(self,sig, samps_per_ui, ui, clock_times=None,
            colorbar_en=False,eye_mask=None,grid_size=(480,640)):
        
        #def update_mask(val):
            #print(val)
        #    mask_temp = mask_array.copy()
        #    mask_temp[:,0]=mask_array[:,0]+val
        #    mask_poly.set_xy(mask_temp)
        #    self.canvas.draw_idle()
        
        self.figure.clf()
        
        self.axes1 = self.figure.add_subplot(1,1,1)
        self.eye_mask_en = False if eye_mask == None else True
        xs,ys,eye_heat = calc_eye_heatmap(sig, samps_per_ui, ui, clock_times, grid_size) 
        im = self.axes1.pcolormesh(xs,ys,eye_heat,cmap=scope_cmap,
                shading="gouraud")

        self.axes1.set_xlabel("Time(ps)")
        self.axes1.set_ylabel("Voltage(v)")
        
        if colorbar_en:
            self.figure.colorbar(im, ax=self.axes1)
        self.axes1.set_xlim([xs.min(),xs.max()])
        self.axes1.set_ylim([ys.min(),ys.max()])
        self.axes1.grid(color="w")


        if self.eye_mask_en:
            #self.figure.subplots_adjust(bottom=0.25)        
            #self.axes2 = self.figure.add_axes([0.2, 0.1, 0.65, 0.03])
            #self.slide_mask = Slider(self.axes2, 'Mask Adjust', -ui*1e12,
            #        ui*1e12, valinit=0)
            #self.slide_mask.on_changed(update_mask)
        
            self.mask_array = eye_mask
            self.mask_poly = mpl.patches.Polygon(self.mask_array,color='#3F3F3F',
                    alpha=0.75)

            self.axes1.add_patch(self.mask_poly) 
            self.sld_maskadj.SetRange(xs.min(),xs.max())
        #else:
        #    self.figure.subplots_adjust(bottom=0.1)   

 

        self.canvas.draw()
    
        


    


if __name__ == "__main__":
    app = wx.PySimpleApp()
    frame = MyFrame()
    frame.Show()
    app.MainLoop()
        
