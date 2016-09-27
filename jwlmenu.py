import tkinter as tk
import configparser


class JwlButton(tk.Label):
    def __init__(self, parent, label_text, *args, **kwargs):
        tk.Label.__init__(self, parent, text=label_text, anchor="w", justify=tk.LEFT, *args, **kwargs)
        self.label_text = label_text
        self.bind("<Button-1>", self.callback)

    def callback(self, event):
        print("-"*20)
        print("JwlButton label_text:", self.label_text)
        print("JwlButton clicked at:", event.x, event.y)
        print("JwlButton keys:", self.keys())
        print("JwlButton self['anchor']:", self['anchor'])
        print("JwlButton width, height:", self.winfo_width(), self.winfo_height())

class App():

    base_width=20
    buttondefs=["cat", "dog", "antidisestablishmentarianism", "led zeppelin!!!"]

    def __init__(self):
        self.root = tk.Tk()
        self.root.bind("<Key>", self.key)
        #self.root.overrideredirect(1)
        self.frame = tk.Frame(self.root, #width=320, height=200,
                           borderwidth=2, relief=tk.RAISED)
        self.frame.pack_propagate(True)
        # self.frame.bind("<Button-1>", self.callback)
        self.frame.pack()
        self.buttons = []
        max_width = max((len(x) for x in self.buttondefs))
        for button in self.buttondefs:
            jb = JwlButton(self.frame, button, font="Sans 18", borderwidth=2, relief=tk.RAISED, width=max_width, underline=1)
            #jb.pack_propagate(0)
            jb.pack(fill="y")
            self.buttons.append(jb)
        #self.jb = tk.Frame(self.root, width=320, height=200)
        # self.jb.label = tk.Label(self.jb, text="catcat", anchor="w")
        # self.jb.label.pack()
        #self.jb.bind("<Button-1>", self.cat_callback)
        # self.bQuit = Button(self.frame, text="Quit",
        #                     command=self.doQuit)
        # self.bQuit.pack(pady=2)
        # self.bHello = Button(self.frame, text="Hello",
        #                      command=self.hello)
        # self.bHello.pack(pady=2)
        self.root.config()


    def hello(self):
        # print("self.bHello: %s" % repr(self.bHello.winfo_geometry()))
        print("Hello")

    def doQuit(self):
        # print("self.bQuit: %s" % repr(self.bQuit.winfo_geometry()))
        self.root.quit()

    def cat_callback(self, event):
        print("clicked at", event.x, event.y)

    def callback(self, event):
        print("clicked at", event.x, event.y)
        self.doQuit()

    def key(self, event):
        print("="*10)
        print("pressed", repr(event.char))

def parse_menu_content(menu_content):
    menu_items = []
    for item_name, action in menu_content.items():
        menu_items.append(JwlMenu(item_name, action))
    return menu_items

class JwlMenu:
    def __init__(self, menu_name, menu_content):
        self.menu_name = menu_name
        self.menu_content = parse_menu_content(menu_content)

class JwlMenuItem:
    def __init__(self, item_name, action):
        self.item_name, self.hot_key = parse_menu_item_name(item_name)
        self.action = parse_menu_item_action(action)

config = configparser.ConfigParser()
config.read('menu_config.ini')
app = App()
app.root.mainloop()
