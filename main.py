import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib, Gdk, GObject
import pygame
import cairo
import math

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
        self.ax = 350
        self.set_default_size(300, 300)
        self.set_border_width(10)

        # Makes it possible to close app
        self.connect("destroy", Gtk.main_quit)

        # overlay
        overlay = Gtk.Overlay()

        # boxes
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        h_btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.add(overlay)

        # drawing area
        self.draw_area = Gtk.DrawingArea()
        self.draw_area.connect("draw", self.on_draw)
        self.draw_area.set_size_request(self.ax, self.ax)

        overlay.add(self.draw_area)

        vbox.set_halign(Gtk.Align.CENTER)
        vbox.set_valign(Gtk.Align.CENTER)
        vbox.set_margin_top(65)

        # Countdown labels
        self.label = Gtk.Label(label="00 : 00 : 00")
        self.label.get_style_context().add_class("time_label")
        self.label.set_vexpand(False)
        self.label.set_hexpand(False)


        # buttons
        
        self.button = Gtk.Button()
        self.button.connect("clicked", self.on_start_clicked)
        self.button.get_style_context().add_class("pause_button")
        self.button.set_image(Gtk.Image.new_from_file("gfx/play.png"))

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
        overlay.add_overlay(self.label)
        overlay.add_overlay(vbox)

        spacer = Gtk.Box()

        vbox.pack_start(arr_up, False, False, 0)
        arr_up.set_halign(Gtk.Align.CENTER)
        
        vbox.pack_start(spacer, True, True, 15)

        vbox.pack_start(arr_down, False, False, 0)
        arr_down.set_halign(Gtk.Align.CENTER)
        vbox.pack_start(h_btn_box, False, False, 0)
        h_btn_box.set_halign(Gtk.Align.CENTER)

        # Variables
        self.starter_time = 1
        self.remaining = 0
        self.timer_id = None
        self.paused = True
        self.started = False
        self.circle_visible = False

    def on_start_clicked(self, button):
        self.check_font_size()
        self.circle_visible = True
        self.draw_area.queue_draw()
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
            self.adjust_font(32)
            self.circle_visible = False
            self.draw_area.queue_draw()
            self.remaining = self.starter_time
            self.started = False
            self.paused = True
            self.toggle_arrows(False)
            self.compute_time(True)

    def update_timer(self):
        if self.paused == False: 
            self.remaining -= 1
            self.check_font_size()
            self.draw_area.queue_draw()
        
        if self.remaining > 0:
            self.compute_time(False)
            return True
        else: 
            self.label.set_text("DONE")
            self.play_alarm()
            return False
        
        
    def on_draw(self, widget, cr):
        width = self.ax
        height = self.ax

        radius = min(width, height) / 2 - 20
        center_x = widget.get_allocated_width() / 2
        center_y = widget.get_allocated_height() / 2

        cr.set_line_width(25)
        cr.set_source_rgba(0.3, 0.3, 0.3, 0.2)
        cr.arc(center_x, center_y, radius, 0, 2 * math.pi)
        cr.stroke()

        cr.set_source_rgb(0.2, 0.8, 0.4) 
        cr.set_line_width(25)
        if self.circle_visible: angle = 2 * math.pi * (1 - self.remaining / self.starter_time)
        else: angle = 2 * math.pi
        cr.arc(center_x, center_y, radius, -math.pi * 0.5, math.pi * 1.5 - angle)
        cr.stroke()

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

    def adjust_font(self, pt):
        css = f"label.time_label {{ font-size: {pt}pt;}}"

        provider = Gtk.CssProvider()
        provider.load_from_data(css)

        self.label.get_style_context().add_provider(provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)

    def check_font_size(self):
        if self.remaining < 3600:
            if self.remaining < 60: self.adjust_font(72)
            else: self.adjust_font(48)

if __name__ == "__main__":
    win = TimerApp()
    win.show_all()
    Gtk.main()