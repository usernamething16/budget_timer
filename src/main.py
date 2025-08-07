import sys
sys.path.append("/usr/lib/python3/dist-packages")

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib, Gdk
from pygame import mixer
import cairo
import math
import os
import json

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

#APP_DIR = os.path.join(BASE_DIR, "..", "share", "simple-timer")
APP_DIR = "/usr/share/simple-timer"
STATE_FILE = os.path.join(APP_DIR, "save_file.json")
os.makedirs(APP_DIR, exist_ok=True)

# empty json if it doesn't exist
if not os.path.exists(STATE_FILE):
    with open(STATE_FILE, "w") as f:
        json.dump({}, f)

class TimerApp(Gtk.Box):
    def __init__(self, flowbox, list, starter_time, remaining, started, circle_visible):
        # setting orientation
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        self.flowbox = flowbox
        self.list = list

        # pygame init
        mixer.init()
        self.sound_mixer = None

        # Importing CSS
        self.provider_label = Gtk.CssProvider()
        self.provider_label_font = Gtk.CssProvider()
        self.provider_button = Gtk.CssProvider()

        # Setting windows and borders
        self.ax = 350

        # overlay
        overlay = Gtk.Overlay()

        # boxes
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        h_btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.pack_start(overlay, False, False, 0)

        # drawing area
        self.draw_area = Gtk.DrawingArea()
        self.draw_area.connect("draw", self.on_draw)
        self.draw_area.set_size_request(self.ax, self.ax)

        overlay.add(self.draw_area)

        vbox.set_halign(Gtk.Align.CENTER)
        vbox.set_valign(Gtk.Align.CENTER)
        vbox.set_margin_top(69)

        # Countdown labels
        self.label = Gtk.Label(label="00 : 00 : 00")
        self.label.get_style_context().add_class("time_label")
        self.label.set_vexpand(False)
        self.label.set_hexpand(False)

        # Entry
        

        # Buttons
        self.button = Gtk.Button()
        self.button.connect("clicked", self.on_start_clicked)
        self.button.get_style_context().add_class("pause_button")
        self.button.set_image(Gtk.Image.new_from_file(f"{APP_DIR}/assets/gfx/play.png"))
        self.button.set_relief(Gtk.ReliefStyle.NONE)

        h_btn_box.pack_start(self.button, False, False, 0)

        self.btn_restart = Gtk.Button()
        self.btn_restart.connect("clicked", self.on_restart_clicked)
        self.btn_restart.get_style_context().add_class("pause_button")
        self.btn_restart.set_image(Gtk.Image.new_from_file(f"{APP_DIR}/assets/gfx/restart.png"))
        h_btn_box.pack_start(self.btn_restart, False, False, 0)

        # up buttons
        self.up_hour = Gtk.Button()
        self.up_hour.get_style_context().add_class("transparent_button")
        self.up_hour.set_image(Gtk.Image.new_from_file(f"{APP_DIR}/assets/gfx/up.png"))

        self.up_min = Gtk.Button()
        self.up_min.get_style_context().add_class("transparent_button")
        self.up_min.set_image(Gtk.Image.new_from_file(f"{APP_DIR}/assets/gfx/up.png"))

        self.up_sec = Gtk.Button()
        self.up_sec.get_style_context().add_class("transparent_button")
        self.up_sec.set_image(Gtk.Image.new_from_file(f"{APP_DIR}/assets/gfx/up.png"))

        self.up_hour.connect("clicked", self.adjust_time, "hour", 1)
        self.up_hour.connect("pressed", self.button_pressed, "hour", 1)
        self.up_hour.connect("released", self.button_released, "hour", 1)

        self.up_min.connect("clicked", self.adjust_time, "min", 1)
        self.up_min.connect("pressed", self.button_pressed, "min", 1)
        self.up_min.connect("released", self.button_released, "min", 1)

        self.up_sec.connect("clicked", self.adjust_time, "sec", 1)
        self.up_sec.connect("pressed", self.button_pressed, "sec", 1)
        self.up_sec.connect("released", self.button_released, "sec", 1)
        
        # down buttons
        self.down_hour = Gtk.Button()
        self.down_hour.get_style_context().add_class("transparent_button")
        self.down_hour.set_image(Gtk.Image.new_from_file(f"{APP_DIR}/assets/gfx/down.png"))

        self.down_min = Gtk.Button()
        self.down_min.get_style_context().add_class("transparent_button")
        self.down_min.set_image(Gtk.Image.new_from_file(f"{APP_DIR}/assets/gfx/down.png"))

        self.down_sec = Gtk.Button()
        self.down_sec.get_style_context().add_class("transparent_button")
        self.down_sec.set_image(Gtk.Image.new_from_file(f"{APP_DIR}/assets/gfx/down.png"))

        self.down_hour.connect("clicked", self.adjust_time, "hour", -1)
        self.down_hour.connect("pressed", self.button_pressed, "hour", -1)
        self.down_hour.connect("released", self.button_released, "hour", -1)

        self.down_min.connect("clicked", self.adjust_time, "min", -1)
        self.down_min.connect("pressed", self.button_pressed, "min", -1)
        self.down_min.connect("released", self.button_released, "min", -1)

        self.down_sec.connect("clicked", self.adjust_time, "sec", -1)
        self.down_sec.connect("pressed", self.button_pressed, "sec", -1)
        self.down_sec.connect("released", self.button_released, "sec", -1)

        # arrow boxes
        arr_up = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=50)
        arr_down = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=50)

        arr_up.pack_start(self.up_hour, False, False, 0)
        arr_up.pack_start(self.up_min, False, False, 0)
        arr_up.pack_start(self.up_sec, False, False, 0)

        arr_down.pack_start(self.down_hour, False, False, 0)
        arr_down.pack_start(self.down_min, False, False, 0)
        arr_down.pack_start(self.down_sec, False, False, 0)

        # delete button
        self.del_btn = Gtk.Button()
        self.del_btn.connect("clicked", self.terminate)
        self.del_btn.get_style_context().add_class("delete_button")
        self.del_btn.set_image(Gtk.Image.new_from_file(f"{APP_DIR}/assets/gfx/the_x.png"))

        self.del_btn.set_halign(Gtk.Align.END)
        self.del_btn.set_valign(Gtk.Align.START)
        self.del_btn.set_margin_top(5)
        self.del_btn.set_margin_end(5)


        # packing stuff into vbox
        overlay.add_overlay(self.label)
        overlay.add_overlay(self.del_btn)
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
        self.starter_time = starter_time
        self.remaining = remaining
        self.timer_id = None
        self.timer_id_arrows = None
        self.paused = True
        self.started = started
        self.circle_visible = circle_visible

        self.tick = 33

        self.hour = 0
        self.minute = 0
        self.second = 0
        self.milisec = 0

        self.r = 1
        self.g = 1
        self.b = 0.25

        self.on_load()

    def on_load(self):
        self.button.set_image(Gtk.Image.new_from_file(f"{APP_DIR}/assets/gfx/play.png"))
        if self.remaining < 0:
            self.on_restart_clicked(None)
        else:
            if self.started:
                if self.timer_id and self.remaining > 0:
                    GLib.source_remove(self.timer_id)
                    self.timer_id = None
                self.draw_area.queue_draw()
                self.toggle_arrows(True)
                self.compute_time(False)
                self.check_font_size()
            else:
                self.adjust_font(32)
                self.draw_area.queue_draw()
                self.compute_time(True)



    def to_dict(self):
        return {
            'starter_time': self.starter_time,
            'remaining': self.remaining,
            'started': self.started,
            'circle_visible': self.circle_visible,
        }
    
    @classmethod
    def from_dict(cls, data, flowbox, list):
        return cls(
            flowbox,
            list,
            starter_time = data['starter_time'],
            remaining = data['remaining'],
            started = data['started'],
            circle_visible = data['circle_visible']
        )

    def on_start_clicked(self, button):
        if self.remaining <= 0: 
            return
        self.circle_visible = True
        if self.sound_mixer: self.sound_mixer.stop()
        self.draw_area.queue_draw()
        if self.started == False: 
            self.starter_time = self.remaining
            self.started = True
            self.toggle_arrows(True)

        if self.paused == False: 
            self.button.set_image(Gtk.Image.new_from_file(f"{APP_DIR}/assets/gfx/play.png"))
            self.paused = True
            if self.timer_id and self.remaining > 0:
                GLib.source_remove(self.timer_id)
                self.timer_id = None
        else:
            self.button.set_image(Gtk.Image.new_from_file(f"{APP_DIR}/assets/gfx/pause.png"))
            self.paused = False
            self.compute_time(False)

            # deletes previous instance of timer
            if self.timer_id and self.remaining > 0:
                GLib.source_remove(self.timer_id)
                self.timer_id = None

            # Calls update every second
            self.timer_id = GLib.timeout_add(self.tick, self.update_timer)

    def on_restart_clicked(self, button):
        if self.sound_mixer: self.sound_mixer.stop()
        if self.started == True:
            self.button.set_image(Gtk.Image.new_from_file(f"{APP_DIR}/assets/gfx/play.png"))
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
            self.remaining -= self.tick
        
        if self.remaining > 0:
            self.compute_time(False)
            return True
        else: 
            self.label.set_text("DONE")
            self.remaining = -1
            self.play_alarm()
            if self.timer_id:
                GLib.source_remove(self.timer_id)
                self.timer_id = None
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

        cr.set_line_cap(cairo.LINE_CAP_ROUND)
        if self.circle_visible: 
            progress = 1 - self.remaining / self.starter_time
            self.determine_color(progress)
            cr.set_source_rgb(self.r, self.g, self.b) 
            angle = 2 * math.pi * (progress)
            cr.arc(center_x, center_y, radius, -math.pi * 0.5, math.pi * 1.5 - angle)
            cr.stroke()
        else: angle = 2 * math.pi
        self.adjust_font_color()

        return False
        

    def compute_time(self, initial):
        timer_time = ''
        
        self.hour = self.remaining // 3600000
        self.minute = self.remaining // 60000
        self.second = self.remaining // 1000

        self.minute -= self.hour * 60
        self.second -= self.minute * 60 + self.hour * 3600
        self.milisec = self.remaining % 1000 // 10

        if self.hour > 0: timer_time += f"{self.hour:02} : "
        elif initial: timer_time += "00 : "

        if self.minute > 0: timer_time += f"{self.minute:02} : "
        elif self.hour != 0 or initial: timer_time += "00 : "


        if self.minute == 0 and self.hour == 0 and initial == False: timer_time += f"{self.second:02} . {self.milisec:02}"
        else: timer_time += f"{self.second:02}"

        self.label.set_text(timer_time)
        if self.paused == False: self.check_font_size()

    def play_alarm(self):
        sound = mixer.Sound(f"{APP_DIR}/assets/ralsei-splat.mp3")
        self.sound_mixer = sound.play(loops=-1)

    def adjust_time(self, button, unit, amount):
        match unit:
            case "hour": 
                if amount < 0 and self.hour == 0: self.remaining += 99 * 3600000
                elif amount > 0 and self.hour == 99: self.remaining -= 99 * 3600000
                else: self.remaining += amount * 3600000
            case "min": 
                if amount < 0 and self.minute == 0: self.remaining += 59 * 60000
                elif amount > 0 and self.minute == 59: self.remaining -= 59 * 60000
                else: self.remaining += amount * 60000
            case "sec": 
                if amount < 0 and self.second == 0: self.remaining += 59 * 1000
                elif amount > 0 and self.second == 59: self.remaining -= 59 * 1000
                else: self.remaining += amount * 1000
        self.compute_time(True)
        return True

    def button_pressed(self, button, unit, amount):
        if self.timer_id_arrows is None:
            self.timer_id_arrows = GLib.timeout_add(100, self.adjust_time, button, unit, amount)

    def button_released(self, button, unit, amount):
        if self.timer_id_arrows:
            GLib.source_remove(self.timer_id_arrows)
            self.timer_id_arrows = None

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

        self.provider_label_font.load_from_data(css)

        self.label.get_style_context().add_provider(self.provider_label_font, Gtk.STYLE_PROVIDER_PRIORITY_USER)

    def check_font_size(self):
        if self.remaining < 3600000:
            self.adjust_font(48)

    def determine_color(self, progress):
        if(progress < 0.5):
            self.r = progress * 2
            self.g = 1
        else: 
            self.g = (1 - progress) * 2
            self.r = 1

    def adjust_font_color(self):
        if self.circle_visible: 
            css_label = f"label.time_label {{ color: rgb({math.floor(self.r * 255)}, {math.floor(self.g * 255)}, {math.floor(self.b * 255)});}}"
            css_button = f".pause_button {{ background: rgb({math.floor(self.r * 255)}, {math.floor(self.g * 255)}, {math.floor(self.b * 255)});}}"
        else: 
            css_label = "label.time_label {color: rgb(255, 255, 255);}"
            css_button = ".pause_button {background: rgb(255, 255, 255);}"
        self.provider_label.load_from_data(css_label)
        self.label.get_style_context().add_provider(self.provider_label, Gtk.STYLE_PROVIDER_PRIORITY_USER)

        self.provider_button.load_from_data(css_button)
        self.button.get_style_context().add_provider(self.provider_button, Gtk.STYLE_PROVIDER_PRIORITY_USER)
        self.btn_restart.get_style_context().add_provider(self.provider_button, Gtk.STYLE_PROVIDER_PRIORITY_USER)

    def terminate(self, button):
        if self.sound_mixer: self.sound_mixer.stop()
        if self.timer_id:
                GLib.source_remove(self.timer_id)
                self.timer_id = None
        self.flowbox.remove(self)
        self.list.remove(self)
        

class MainApp(Gtk.Window):
    def __init__(self):
        # initialising window
        super().__init__(title="Simple Timer")
        self.set_default_size(800, 400)
        self.set_border_width(0)

        # importing css
        css_provider = Gtk.CssProvider()
        css_provider.load_from_path(f"{APP_DIR}/assets/style.css")

        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
        super().get_style_context().add_class("window")

        # list of timers
        self.timer_list = []

        # box
        self.vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.vbox.set_margin_start(10)
        self.vbox.set_margin_end(10)
        self.add(self.vbox)

        scroll_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        scroll_box.set_margin_top(10)
        scroll_box.set_margin_bottom(10)


        # flowbox
        self.timer_container = Gtk.FlowBox()
        self.timer_container.set_valign(Gtk.Align.START)
        self.timer_container.set_halign(Gtk.Align.FILL)
        self.timer_container.set_max_children_per_line(25)
        self.timer_container.set_selection_mode(Gtk.SelectionMode.NONE)
        self.timer_container.set_row_spacing(10)
        self.timer_container.set_column_spacing(10)

        self.timer_container.set_hexpand(True)
        
        # scroll
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll.set_shadow_type(Gtk.ShadowType.NONE)
        scroll.get_style_context().add_class("scroll_timers")
        scroll.set_kinetic_scrolling(False)
        scroll.set_hexpand(True)
        scroll.set_vexpand(True)

        # button
        self.add_btn = Gtk.Button(label="+")
        self.add_btn.set_size_request(370, 370)
        self.add_btn.connect("clicked", self.add_timer, None)
        self.add_btn.get_style_context().add_class("box_button")
        self.add_btn.set_name("add_btn")
        

        # packing
        self.vbox.pack_start(scroll, True, True, 0)
        scroll.add(scroll_box)
        scroll_box.pack_start(self.timer_container, True, True, 0)

        self.timer_container.add(self.add_btn)

        self.load_data()
        GLib.timeout_add_seconds(10, self.save_data)

    
    def add_timer(self, button, timer):
        if timer is None: timer = TimerApp(self.timer_container, self.timer_list, 1, 0, False, False)

        timer.set_valign(Gtk.Align.START)
        timer.set_valign(Gtk.Align.START)
        timer.get_style_context().add_class("box_background")

        children = self.timer_container.get_children()
        index = len(children) - 1

        self.timer_container.insert(timer, index)

        self.timer_list.append(timer)

        timer.show_all()
        super().show_all()

    def save_data(self, *args):
        data = [timer.to_dict() for timer in self.timer_list]

        with open(STATE_FILE, "w") as f:
            json.dump(data, f)
        return True

    def load_data(self):
        with open(STATE_FILE, "r") as f:
            data = json.load(f)

        for timer_data in data:
            timer = TimerApp.from_dict(timer_data, self.timer_container, self.timer_list)
            self.add_timer(None, timer)


if __name__ == "__main__":
    win = MainApp()
    win.show_all()
    win.connect("destroy", win.save_data)
    win.connect("destroy", Gtk.main_quit)
    Gtk.main()