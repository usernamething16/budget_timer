import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib, Gdk

class TimerApp(Gtk.Window):
    def __init__(self):
        #Setting title
        super().__init__(title="Simple Timer")

        # Importing CSS
        css_provider = Gtk.CssProvider()
        css_provider.load_from_path("style.css")

        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )


        # Setting windows and borders
        self.set_default_size(300, 300)
        self.set_border_width(10)

        # Makes it possible to close app
        self.connect("destroy", Gtk.main_quit)

        # Vertical box
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.add(vbox)

        # Input field
        self.entry = Gtk.Entry()
        self.entry.set_placeholder_text("Enter time in seconds")
        vbox.pack_start(self.entry, False, False, 0)

        # Countdown label
        self.label = Gtk.Label(label="-- | --")
        self.label.get_style_context().add_class("time_label")
        vbox.pack_start(self.label, False, False, 0)

        # Start button
        self.button = Gtk.Button(label="Start Timer")
        self.button.connect("clicked", self.on_start_clicked)
        vbox.pack_start(self.button, False, False, 0)

        self.remaining = 0
        self.timer_id = None

    def on_start_clicked(self, button):
        try:
            self.remaining = int(self.entry.get_text())
        except ValueError:
            self.label.set_text("Please enter a valid number.")
            return
        
        if self.remaining <= 0:
            self.label.set_test("Please enter a positive number")
            return
        
        self.label.set_text(f"Timer: {self.remaining} sec")

        # deletes previous instance of timer
        if self.timer_id:
            GLib.source_remove(self.timer_id)

        # Calls this update every second
        self.timer_id = GLib.timeout_add(1000, self.update_timer)

    def update_timer(self):
        self.remaining -= 1
        
        if self.remaining > 0:
            self.label.set_text(f"Timer: {self.remaining} sec")
            return True
        else: 
            self.label.set_text("Timer: 0 sec")
            return False


if __name__ == "__main__":
    win = TimerApp()
    win.show_all()
    Gtk.main()