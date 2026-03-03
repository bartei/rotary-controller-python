from kivy.uix.boxlayout import BoxLayout


class ModeLayout(BoxLayout):
    """Base class for mode-specific home page layouts."""

    def __init__(self, **kwargs):
        from rcp.app import MainApp
        self.app: MainApp = MainApp.get_running_app()
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.axis_bars = []

    def build_axis_bars(self):
        """Override in subclasses to create axis bar widgets."""
        pass

    def rebuild_axes(self):
        """Remove old axis bars and rebuild from current app.axes."""
        for bar in self.axis_bars:
            self.remove_widget(bar)
        self.axis_bars.clear()
        self.build_axis_bars()
