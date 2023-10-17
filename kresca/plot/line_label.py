from vispy.scene import Rectangle as _Rectangle
from vispy.scene import Line as _Line


class Label(_Rectangle):
    
    def __init__(self, index, color, parent):
        super().__init__(
            center = [20+index*40, 30],
            height = 20,
            width = 20,
            radius = 0,
            color = color,
            border_color = 'white',
            parent = parent
        )
        
        self.unfreeze()
        
        self.index = index
        self.color_ = color
        self.selected = False
        self.hide = False
        self.interactive = True
        
    def select(self):
        return self.index
    
    def hide_label(self):
        self.hide = True
        self.color = 'black'
        
    def show_label(self):
        self.hide =  False
        self.color = self.color_
        
    def selected_label(self):
        self.selected = True
        self.color = 'white'
        
    def unselected_label(self):
        self.selected = False
        self.color = self.color_

class Curve(_Line):
    
    def __init__(self, index, color, pos, parent):
        
        super().__init__(
            pos = pos,
            color = color,
            parent = parent,
            width = 1.5,
        )
        
        self.unfreeze()
        
        self.index = index
        self.color_ = color
        self.pos_ = pos.copy()
        self.selected = False
        self.hide = False
        self.interactive = True
        
    def select(self):
        return self.index
    
    def hide_curve(self):
        self.hide = True
        self.visible = False
        
    def show_curve(self):
        self.hide = False
        self.visible = True
        
    def selected_curve(self):
        self.selected = True
        self.set_data(color = 'white')
        
    def unselected_curve(self):
        self.selected = False
        self.set_data(color = self.color_)
        
    def reset_curve(self):
        self.set_data(pos=self.pos_.copy())