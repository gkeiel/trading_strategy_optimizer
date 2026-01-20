import json
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput


class Gui(App):

    def __init__(self, on_start_callback, **kwargs):
        super().__init__(**kwargs)
        self.on_start_callback = on_start_callback
        self.inputs = {}

    def build(self):        
        root    = BoxLayout(orientation="vertical", padding=5, spacing=5)
        scroll  = ScrollView(do_scroll_x=False, do_scroll_y=True, size_hint_y=0.6)
        columns = BoxLayout(orientation="horizontal", spacing=10, size_hint=(1,None))
        columns.bind(minimum_height=columns.setter("height"),minimum_width=columns.setter("width"))

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
        btn.bind(on_press=self.on_run)
        root.add_widget(btn)
           
        # log
        self.log = TextInput(readonly=True, size_hint_y=0.7)
        root.add_widget(self.log)
        
        return root
    
    def build_section(self, section, values):
        col = BoxLayout(orientation="vertical", spacing=20, size_hint=(None, None), width=240)
        col.bind(minimum_height=col.setter("height"))
        col.pos_hint = {"top": 1}

        # title
        col.add_widget(Label(text=section.upper(), size_hint_y=None, height=30, bold=True))
        
        # checkbox fields
        if section in {"simulated_annealing", "hill_climbing", "grid_search"}:
            row = BoxLayout(size_hint_y=None, height=30, spacing=5)
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
                row = BoxLayout(size_hint_y=None, height=30, spacing=5)
                lbl = Label(text=key, size_hint_x=0.7, halign="left", valign="middle")
                lbl.bind(size=lbl.setter("text_size"))
                inp = TextInput(text=str(value), multiline=False, size_hint_x=0.3)

                row.add_widget(lbl)
                row.add_widget(inp)
                col.add_widget(row)
                self.inputs[f"{section}.{key}"] = inp
        return col

    def on_run(self, *_):
        self.on_start_callback(self.collect_config())

    def collect_config(self):
        
        for path, widget in self.inputs.items():
            keys = path.split(".")
            ref = self.config
            
            for k in keys[:-1]:
                ref = ref[k]
            
            # checkbox
            if hasattr(widget, "active"):
                ref[keys[-1]] = bool(widget.active)
            else:
                txt = widget.text
                ref[keys[-1]] = float(txt) if "." in txt else int(txt)
                
        return self.config

    def append_log(self, msg):
        Clock.schedule_once(lambda dt: self.append(msg))

    def append(self, msg):
        self.log.text += msg +"\n"