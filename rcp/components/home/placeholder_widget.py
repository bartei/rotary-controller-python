from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget


class PlaceholderWidget(BoxLayout):
    """A placeholder widget that exactly matches the size and layout properties of a CoordBar"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        self.size_hint_y = 1  # Same as CoordBar
        
        # Create a simple widget with the same dimensions as the button in CoordBar
        left_widget = Widget(
            width=96,
            size_hint_x=None
        )
        self.add_widget(left_widget)
        
        # Add a widget to fill the remaining space
        content_widget = Widget()
        self.add_widget(content_widget)
