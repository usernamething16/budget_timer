import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib, Gdk
import pygame

class TimerApp(Gtk.Window):
    def __init__(self):
        #Setting title
        super().__init__(title="Simple Timer")

        # pygame init
        pygame.init()
        pygame.mixer.init()
        self.sound_mixer = None

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

        # boxes
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        h_btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.add(vbox)

        # Countdown labels
        self.label = Gtk.Label(label="00 : 00 : 00")
        self.label.get_style_context().add_class("time_label")

        # buttons

        self.button = Gtk.Button()
        self.button.connect("clicked", self.on_start_clicked)
        self.button.get_style_context().add_class("pause_button")
        self.button.set_image(Gtk.Image.new_from_file("gfx/play.png"))
        #self.button.set_always_show_image(True)

        h_btn_box.pack_start(self.button, False, False, 0)

        self.btn_restart = Gtk.Button()
        self.btn_restart.connect("clicked", self.on_restart_clicked)
        self.btn_restart.get_style_context().add_class("pause_button")
        self.btn_restart.set_image(Gtk.Image.new_from_file("gfx/restart.png"))
        h_btn_box.pack_start(self.btn_restart, False, False, 0)

        # up buttons
        self.up_hour = Gtk.Button()
        self.up_hour.get_style_context().add_class("transparent_button")
        self.up_hour.set_image(Gtk.Image.new_from_file("gfx/up.png"))

        self.up_min = Gtk.Button()
        self.up_min.get_style_context().add_class("transparent_button")
        self.up_min.set_image(Gtk.Image.new_from_file("gfx/up.png"))

        self.up_sec = Gtk.Button()
        self.up_sec.get_style_context().add_class("transparent_button")
        self.up_sec.set_image(Gtk.Image.new_from_file("gfx/up.png"))

        self.up_hour.connect("clicked", self.adjust_time, "hour", 1)
        self.up_min.connect("clicked", self.adjust_time, "min", 1)
        self.up_sec.connect("clicked", self.adjust_time, "sec", 1)
        
        # down buttons
        self.down_hour = Gtk.Button()
        self.down_hour.get_style_context().add_class("transparent_button")
        self.down_hour.set_image(Gtk.Image.new_from_file("gfx/down.png"))

        self.down_min = Gtk.Button()
        self.down_min.get_style_context().add_class("transparent_button")
        self.down_min.set_image(Gtk.Image.new_from_file("gfx/down.png"))

        self.down_sec = Gtk.Button()
        self.down_sec.get_style_context().add_class("transparent_button")
        self.down_sec.set_image(Gtk.Image.new_from_file("gfx/down.png"))

        self.down_hour.connect("clicked", self.adjust_time, "hour", -1)
        self.down_min.connect("clicked", self.adjust_time, "min", -1)
        self.down_sec.connect("clicked", self.adjust_time, "sec", -1)

        # arrow boxes

        arr_up = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=50)
        arr_down = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=50)

        arr_up.pack_start(self.up_hour, False, False, 0)
        arr_up.pack_start(self.up_min, False, False, 0)
        arr_up.pack_start(self.up_sec, False, False, 0)

        arr_down.pack_start(self.down_hour, False, False, 0)
        arr_down.pack_start(self.down_min, False, False, 0)
        arr_down.pack_start(self.down_sec, False, False, 0)

        # packing stuff into vbox
        vbox.pack_start(arr_up, False, False, 0)
        arr_up.set_halign(Gtk.Align.CENTER)
        vbox.pack_start(self.label, False, False, 0)
        vbox.pack_start(arr_down, False, False, 0)
        arr_down.set_halign(Gtk.Align.CENTER)
        vbox.pack_start(h_btn_box, False, False, 0)
        h_btn_box.set_halign(Gtk.Align.CENTER)
        

        # Variables
        self.starter_time = 0
        self.remaining = 0
        self.timer_id = None
        self.paused = True
        self.started = False

    def on_start_clicked(self, button):
        if self.sound_mixer: self.sound_mixer.stop()
        if self.remaining <= 0: 
            self.on_restart_clicked(None)
            return
        if self.started == False: 
            self.starter_time = self.remaining
            self.started = True
            self.toggle_arrows(True)

        if self.paused == False: 
            self.button.set_image(Gtk.Image.new_from_file("gfx/play.png"))
            self.paused = True
        else:
            self.button.set_image(Gtk.Image.new_from_file("gfx/pause.png"))
            self.paused = False
            self.compute_time(False)

            # deletes previous instance of timer
            if self.timer_id and self.remaining > 0:
                GLib.source_remove(self.timer_id)
                self.timer_id = None

            # Calls update every second
            self.timer_id = GLib.timeout_add(1000, self.update_timer)

    def on_restart_clicked(self, button):
        if self.sound_mixer: self.sound_mixer.stop()
        if self.started == True:
            self.button.set_image(Gtk.Image.new_from_file("gfx/play.png"))
            if self.timer_id and self.remaining > 0:
                GLib.source_remove(self.timer_id)
                self.timer_id = None
            self.remaining = self.starter_time
            self.started = False
            self.paused = True
            self.toggle_arrows(False)
            self.compute_time(True)

    def update_timer(self):
        if self.paused == False: self.remaining -= 1
        
        if self.remaining > 0:
            self.compute_time(False)
            return True
        else: 
            self.label.set_text("DONE")
            self.play_alarm()
            return False
        
    def compute_time(self, initial):
        timer_time = ''
        hour = self.remaining // 3600
        minute = 0
        second = 0
        rest = self.remaining % 3600
        if(rest < 60):
            minute = 0
            second = rest
        else:
            minute = rest // 60
            second = rest % 60

        if hour > 0: timer_time += f"{hour:02} : "
        elif initial: timer_time += "00 : "

        if minute > 0: timer_time += f"{minute:02} : "
        elif hour != 0 or initial: timer_time += "00 : "

        timer_time += f"{second:02}"

        self.label.set_text(timer_time)

    def play_alarm(self):
        try:
            sound = pygame.mixer.Sound("ralsei-splat.mp3")
            self.sound_mixer = sound.play(loops=-1)
        except pygame.error as e:
            print(f"Error playing sound: {e}")

    def adjust_time(self, button, unit, amount):
        match unit:
            case "hour": self.remaining += amount * 3600
            case "min": self.remaining += amount * 60
            case "sec": self.remaining += amount
        self.compute_time(True)

    def toggle_arrows(self, command):
        if command:
            self.down_hour.set_sensitive(False)
            self.down_hour.set_opacity(0)
            
            self.down_min.set_sensitive(False)
            self.down_min.set_opacity(0)

            self.down_sec.set_sensitive(False)
            self.down_sec.set_opacity(0)

            self.up_hour.set_sensitive(False)
            self.up_hour.set_opacity(0)
            
            self.up_min.set_sensitive(False)
            self.up_min.set_opacity(0)

            self.up_sec.set_sensitive(False)
            self.up_sec.set_opacity(0)
        else:
            self.down_hour.set_sensitive(True)
            self.down_hour.set_opacity(1)
            
            self.down_min.set_sensitive(True)
            self.down_min.set_opacity(1)

            self.down_sec.set_sensitive(True)
            self.down_sec.set_opacity(1)

            self.up_hour.set_sensitive(True)
            self.up_hour.set_opacity(1)
            
            self.up_min.set_sensitive(True)
            self.up_min.set_opacity(1)

            self.up_sec.set_sensitive(True)
            self.up_sec.set_opacity(1)

if __name__ == "__main__":
    win = TimerApp()
    win.show_all()
    Gtk.main()