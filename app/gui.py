import sys, os, json, threading
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.checkbox import CheckBox
from kivy.uix.image import Image
from trading_strategy_optmizer import run_tso
from app.stdout import StdoutRedirector
 

class TSO(App):
    
    def build(self):
        self.inputs = {}

        root    = BoxLayout(orientation="vertical", padding=5, spacing=5)
        scroll  = ScrollView(do_scroll_x=False, do_scroll_y=True, size_hint=(1, 1))
        columns = BoxLayout(orientation="horizontal", spacing=10, size_hint=(1,None))
        columns.bind(minimum_height=columns.setter("height"),minimum_width=columns.setter("width"))
        form    = BoxLayout(orientation="vertical", size_hint_y=None, spacing=1)

        with open("config/config.json") as f:
            self.config = json.load(f)

        for section, values in self.config.items():
            if isinstance(values, dict):
                col = self.build_section(section, values)
                columns.add_widget(col)
        scroll.add_widget(columns)
        root.add_widget(scroll)

        # button
        btn = Button(text="Start TSO", size_hint_y=None, height=25)
        btn.bind(on_press=self.start_tso)
        root.add_widget(btn)
        
        # figure
        self.plot = Image(size_hint_y=0.8, allow_stretch=True, keep_ratio=True)
        root.add_widget(self.plot)
        
        # log
        self.log = TextInput(readonly=True, size_hint_y=0.3)
        root.add_widget(self.log)
        return root
    
    def build_section(self, section, values):
        col = BoxLayout(orientation="vertical", spacing=20, size_hint=(None, None), width=190)
        col.bind(minimum_height=col.setter("height"))

        # title
        col.add_widget(Label(text=section.upper(), size_hint_y=None, height=30, bold=True))

        # checkbox fields
        if section in {"simulated_annealing", "hill_climbing", "grid_search"}:
            row = BoxLayout(size_hint_y=None, height=35, spacing=5)
            lbl = Label(text="enabled", size_hint_x=0.7)
            lbl.bind(size=lbl.setter("text_size"))
            chk = CheckBox(active=bool(values.get("enabled", False)), size_hint=(None, None), size=(40, 40), opacity=1)

            row.add_widget(lbl)
            row.add_widget(chk)
            col.add_widget(row)
            self.inputs[f"{section}.enabled"] = chk

        # numeric fields
        for key, value in values.items():
            
            # jump enabled
            if key == "enabled": continue
            
            if isinstance(value, (int, float)):
                row = BoxLayout(size_hint_y=None, height=35, spacing=5)
                lbl = Label(text=key, size_hint_x=0.7, halign="left", valign="middle")
                lbl.bind(size=lbl.setter("text_size"))
                inp = TextInput(text=str(value), multiline=False, size_hint_x=0.3)

                row.add_widget(lbl)
                row.add_widget(inp)
                col.add_widget(row)
                self.inputs[f"{section}.{key}"] = inp
        return col
  
    def append_log(self, msg):
        self.log.text += msg +"\n"

    def start_tso(self, instance):
        self.log.text = ""
        
        # update config from GUI
        for path, widget in self.inputs.items():

            keys = path.split(".")
            ref  = self.config
            for k in keys[:-1]:
                ref = ref[k]

            # checkbox
            if hasattr(widget, "active"):
                ref[keys[-1]] = bool(widget.active)
            else:
                txt = widget.text
                ref[keys[-1]] = float(txt) if "." in txt else int(txt)
                
        # save config
        with open("config/config.json", "w") as f:
            json.dump(self.config, f, indent=4)

        threading.Thread(target=self.run_thread).start()
        
    def load_last_plot(self):
        plots_dir = "data/results"

        images = [os.path.join(plots_dir, f) for f in os.listdir(plots_dir) if f.lower().endswith(".png")]
        images = [f for f in images if "optimization" in os.path.basename(f)]
        if not images:
            self.append_log("No figure found.")
            return
        last_image = max(images, key=os.path.getmtime)

        self.plot.source = last_image
        self.plot.reload()

    def run_thread(self):
        def on_log(msg):
            Clock.schedule_once(lambda dt: self.append_log(msg))
        
        stdout_original = sys.stdout
        stderr_original = sys.stderr

        try:
            sys.stdout = StdoutRedirector(on_log)
            sys.stderr = StdoutRedirector(on_log)
            run_tso(on_log=on_log)
            Clock.schedule_once(lambda dt: self.load_last_plot())
            Clock.schedule_once(lambda dt: self.append_log("Optimization completed."))
            
        except Exception as err:
            def log_error(dt, err=str(err)):
                self.append_log(f"Error: {err}")
            Clock.schedule_once(log_error)
            
        finally:
            sys.stdout = stdout_original
            sys.stderr = stderr_original


if __name__ == "__main__":
    #Window.size = (1200, 800)
    TSO().run()