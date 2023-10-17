from IPython import get_ipython
import numpy as _np
from vispy.scene import SceneCanvas as _SceneCanvas
from vispy.scene import AxisWidget as _AxisWidget
from vispy.scene import Text as _Text
from vispy.scene.visuals import GridLines as _GridLines
from vispy import color as _color
from vispy import app as _app

from .line_label import Curve, Label

class CurvePlot(_SceneCanvas):
    
    MAX_HL = 15
    
    def __init__(self, curves, size=(950, 500), inline=False):
        
        if inline == False:
            ipython = get_ipython()
            ipython.magic("gui qt5")
            _app.use_app('pyqt5')
        else:
            _app.use_app('jupyter_rfb')
        
        _SceneCanvas.__init__(self,
                                size=size,
                                position=(200, 200),
                                keys="interactive",
                                bgcolor="#222")
        
        self.unfreeze()
        
        self.grid = self.central_widget.add_grid(spacing=0)

        self.x_axis = _AxisWidget(orientation="bottom")
        self.y_axis = _AxisWidget(orientation="left")
        self.x_axis.stretch = (1, 0.05)
        self.y_axis.stretch = (0.05, 1)
        self.grid.add_widget(self.x_axis, row=2, col=1)
        self.grid.add_widget(self.y_axis, row=1, col=0)
        self.view = self.grid.add_view(row=1, col=1, camera="panzoom")
        self.x_axis.link_view(self.view)
        self.y_axis.link_view(self.view)
        
        self.view_label = self.grid.add_view(row=3, col=1)
        self.view_label.height_max=50
        
        self.view_info = self.grid.add_view(row=0, col=1)
        self.view_info.height_max=50
        
        self.ctrl_pressed = False
        self.shift_pressed = False
        self.alt_pressed = False
        self.x_pressed = False
        self.y_pressed = False
        self.h_pressed = False
        self.mouse_left_pressed = False

        self.connect(self.on_key_press)
        self.connect(self.on_key_release)
        self.connect(self.on_mouse_press)
        self.connect(self.on_mouse_release)
        
        _GridLines(parent=self.view.scene)
        
        self._init_pos = None
        self.connect(self.on_mouse_move)
        
        self.lines = []
        self.labels = []
        self.selected_lines = []
        
        self._init_pos = None
        
        self.reset_text = _Text("Reset Curve", bold=True, font_size=12, color='w', pos=(self.size[0]*0.85, 25), parent=self.view_info.scene)
        self.point_text = _Text("Point: ", bold=True, font_size=12, color='w', pos=(120, 25), parent=self.view_info.scene)
        self.reset_text.interactive = True
        self.events.resize.connect(self.resize_handle)
        
        self.inline = inline
        
        if curves is not None:
            self.draw_curves(curves)
        
    def draw_curves(self, curves_):
        curves = _np.array(curves_)
        self.shape_ = curves.shape
                
        if len(curves.shape) == 1:
            ## Single curve
            curves = _np.array([curves])
            
        if len(curves.shape) == 1:
            ## Single curve
            curves = _np.array([curves])

        nb_traces, size = curves.shape
            
        colormap = _color.colormap.HSL(curves.shape[0]+1, (curves.shape[0]*10)%360).colors

        for i, curve in enumerate(curves):
            pos = _np.zeros((len(curve), 2))
            pos[:, 0] = _np.arange(0, len(curve))
            pos[:, 1] = curve
            line = Curve(
                index=i,
                color=colormap[i],
                pos=pos,
                parent=self.view.scene
            )
            
            label = Label(
                index=i,
                color=colormap[i],
                parent=self.view_label.scene
            )
            
            self.lines.append(line)
            self.labels.append(label)
            
        self.view.camera.set_range(x=(-1, size), y=(curves.min(), curves.max()))
        if(self.inline == False):
            self.show()
        
    def hide_curve(self, index):
        self.lines[index].hide_curve()
        self.labels[index].hide_label()
        
    def show_curve(self, index):
        self.lines[index].show_curve()
        self.labels[index].show_label()
        
    def selected_curve(self, index):
        self.lines[index].selected_curve()
        self.labels[index].selected_label()
        
    def unselected_curve(self, index):
        self.lines[index].unselected_curve()
        self.labels[index].unselected_label()
        
    def apply_offset(self, index, offset):
        self.lines[index].pos[:, 0] += offset[0]
        self.lines[index].pos[:, 1] += offset[1]
        self.lines[index].set_data(pos=self.lines[index].pos)
        
    def on_mouse_press(self, event):
        self._init_pos = event.pos
        self.mouse_left_pressed = True
        if(event.button ==1):
            selected = self.visual_at(event.pos)
            if(isinstance(selected, Curve) or isinstance(selected, Label)):
                index = selected.select()
                if(self.ctrl_pressed):
                    if(self.labels[index].hide == False):
                        self.hide_curve(index)
                    else:
                        self.show_curve(index)
                else:
                    if(self.labels[index].hide == False):
                        if(self.labels[index].selected == False):
                            self.selected_curve(index)
                            self.selected_lines.append(index)
                        else:
                            if(self.x_pressed != True and self.y_pressed != True):
                                self.unselected_curve(index)
                                self.selected_lines.remove(index)
            if(selected == self.reset_text):
                for line in self.lines:
                    line.reset_curve()
        
    def on_mouse_release(self, event):
        self.mouse_left_pressed = False
        self.view.camera.interactive = True
    
    def on_key_press(self, event):
        if event.key == "Control":
            self.ctrl_pressed = True
        if event.key == "Shift":
            self.shift_pressed = True
        if event.key == "Alt":
            self.alt_pressed = True
        if event.key == "X":
            self.x_pressed = True
        if event.key == "Y":
            self.y_pressed = True
    
    def on_key_release(self, event):
        if event.key == "Control":
            self.ctrl_pressed = False
        if event.key == "Shift":
            self.shift_pressed = False
        if event.key == "Alt":
            self.alt_pressed = False
        if event.key == "X":
            self.x_pressed = False
        if event.key == "Y":
            self.y_pressed = False
            
    def resize_handle(self, event):
        self.reset_text.pos=[self.size[0]*0.85, 25]
    
    def on_mouse_move(self, event):
        tr = self.scene.node_transform(self.view.scene)
        x, y, _, _ = tr.map(event.pos)
        self.point_text.text = f'X: {int(x)}, Y:{round(y, 2)}'
        if(self.mouse_left_pressed == True):
            if(self.x_pressed or self.y_pressed):
                self.view.camera.interactive = False
                if self._init_pos is None:
                        self._init_pos = event.pos
                # map to screen displacement
                x, y, _, _ = tr.map(event.pos)
                init_x, init_y, _, _ = tr.map(self._init_pos)
                delta_x = x - init_x
                delta_y = y - init_y
                for line in self.selected_lines:
                    self.apply_offset(line, (0.0, delta_y) if self.y_pressed else (delta_x, 0.0))
                self._init_pos = event.pos
                self.update()
        