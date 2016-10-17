import tkinter as tk
#from famenu import famenu_config
import famenu_config
import sys
import re
import subprocess
import shlex
from Xlib.display import Display
from Xlib import X, XK
from functools import reduce
from itertools import chain, combinations
import pprint

MODIFIERS = {
    'mod1': X.Mod1Mask,
    'mod3': X.Mod3Mask,
    'mod4': X.Mod4Mask,
    'shift': X.ShiftMask,
    'control': X.ControlMask
    }

IGNORED_MODIFIERS = [X.Mod2Mask, X.LockMask]

def powerset(iterable):
    """C{powerset([1,2,3])} --> C{() (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)}

    @rtype: iterable
    """
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s) + 1))

def err_exit(msg, rv=1):
    print(msg)
    sys.exit(1)

def key_state(key, state):
    return "%s%d"%(key, state)

def parse_modifier_mask(mask_str):
    modifiers = []
    hotkey = None
    toks = mask_str.lower().split('>')
    for token in toks:
        if token[0] == '<':
            modifier = MODIFIERS.get(token[1:])
            if modifier in modifiers:
                err_exit("Modifier specified multiple times in config.")
            elif modifier:
                modifiers.append(modifier)
            else:
                err_exit("Invalid modifier specified in config.")
        elif hotkey == None:
            hotkey = token
        else:
            err_exit("Multiple hotkeys specified in config.")
    if len(modifiers) == 0 or hotkey == None:
        err_exit("One or more modifiers and one key are required.")
    return modifiers, hotkey

class FaButton(tk.Label):
    def __init__(self, parent, menu_item, root, app, *args, **kwargs):
        tk.Label.__init__(self, parent, text=menu_item.item_name, anchor="w", justify=tk.LEFT, underline=menu_item.hot_key_index, *args, **kwargs)
        self.menu_item = menu_item
        self.label_text = menu_item.item_name
        self.bind("<Button-1>", self.on_click)
        self.parent=parent
        self.root=root
        self.app=app

    def on_click(self, event):
        self.menu_item.action.run(self.app)
        self.app.do_withdraw()

    def on_key(self, event):
        if event.char == self.menu_item.hot_key or event.keysym == "space" or event.keysym == "Return":
            return self.menu_item.action.run(self.app)

class FaMenuApp():

    def __init__(self, config, menus):
        self.menus = menus
        self.keycode_to_char = {}
        self.menu_hot_keys = {}
        self.root = tk.Tk()
        self.menu_font=config['font']
        self.xroot = None
        self.dpy = None
        self.root.bind("<Key>", self.on_key)
        self.buttons = []
        for menu_name, fa_menu in self.menus.items():
            self.add_menu(menu_name, fa_menu)
        self.root.config()
        self.running = False

    def add_menu(self, menu_name, fa_menu):
        this_menu = {}
        max_width = max((len(item.item_name) for item in fa_menu.menu_content))
        menu_frame = tk.Frame(self.root, #width=320, height=200,
                           borderwidth=2, relief=tk.RAISED)
        menu_frame.pack_propagate(True)
        menu_label = tk.Label(menu_frame, text=menu_name, font=self.menu_font, anchor="w", justify=tk.LEFT)
        menu_label.pack(fill="y")
        for menu_item in fa_menu.menu_content:
            jb = FaButton(menu_frame, menu_item, self.root, self, font=self.menu_font, borderwidth=2, relief=tk.RAISED, width=max_width)
            if menu_item.hot_key != None:
                fa_menu.hot_keys[menu_item.hot_key] = jb.on_key
            jb.pack(fill="y")
            menu_item.button = jb
            fa_menu.menu_frame = menu_frame
            fa_menu.menu_buttons.append(jb)
        if fa_menu.menu_hot_key != None:
            if self.menu_hot_keys.get(fa_menu.menu_hot_key) == None:
                hot_key, hot_key_states = self.bind_key(fa_menu.menu_hot_key)
                for state in hot_key_states:
                    key_state_str = key_state(hot_key, state)
                    self.menu_hot_keys[key_state_str] = fa_menu.menu_name
        fa_menu.select_button()


    def on_key(self, event):
        run = self.hot_keys.get(event.char)
        if run == None:
            if event.keysym == "Up":
                self.menus[self.menu_name].prev_button()
            elif event.keysym == "Down":
                self.menus[self.menu_name].next_button()
            elif event.keysym == "Return" or event.keysym == "space":
                run = self.menus[self.menu_name].button().on_key
            elif event.keysym == "Escape":
                self.do_withdraw()
        if run != None:
            if run(event):
                self.do_withdraw()

    def do_withdraw(self):
        self.menus[self.menu_name].menu_frame.pack_forget()
        self.root.withdraw()
        self.root.quit()

    def switch_to_menu(self, menu_name):
        old_menu = self.menus[self.menu_name]
        old_menu.menu_frame.pack_forget()
        self.root.withdraw()
        new_menu = self.menus[menu_name]
        self.show_menu(new_menu)

    def show_menu(self, menu):
        self.menu_name = menu.menu_name
        if self.running:
            menu.menu_frame.pack()
            self.hot_keys = menu.hot_keys
            self.root.update()
            self.root.deiconify()
        else:
            self.running = True
            menu.menu_frame.pack()
            self.hot_keys = menu.hot_keys

    def do_loop(self):
        while True:
            ev = self.xroot.display.next_event()
            if ev.type == X.KeyPress:
                key = self.keycode_to_char.get(ev.detail)
                state = ev.state
                key_state_str = key_state(key, state)
                menu_name = self.menu_hot_keys.get(key_state_str)
                if menu_name != None:
                    menu = self.menus[menu_name]
                    self.show_menu(menu)
                    self.root.mainloop()

    def run(self):
        self.do_loop()

    def bind_key(self, key_spec):
        modifiers, key = parse_modifier_mask(key_spec)
        if self.dpy is None:
            self.dpy = Display()
        if self.xroot is None:
            self.xroot = self.dpy.screen().root
        keysym = XK.string_to_keysym(key)
        keycode = self.dpy.keysym_to_keycode(keysym)
        if not keycode in self.keycode_to_char.keys():
            self.keycode_to_char[keycode] = key
        modifier_mask = reduce(lambda x, y: x | y, modifiers, 0)
        self.xroot.change_attributes(event_mask=X.KeyPressMask)
        states = []
        for ignored in powerset(IGNORED_MODIFIERS):
            modmask = reduce(lambda x, y: x | y, ignored, 0)
            modmask |= modifier_mask
            states.append(modmask)
            self.xroot.grab_key(keycode, modmask, 1,
                                X.GrabModeAsync, X.GrabModeAsync)
        return key, states

def parse_menu_content(menu_content):
    menu_items = []
    for item_name, action in menu_content.items():
        if item_name == 'menu_hot_key':
            menu_content[item_name] = action[0]
            continue
        menu_items.append(FaMenuItem(item_name, action))
    return menu_items

class FaMenu:
    def __init__(self, menu_name, menu_content):
        self.menu_name = menu_name
        self.menu_content = parse_menu_content(menu_content)
        self.menu_hot_key = menu_content.get('menu_hot_key')
        self.menu_frame = None
        self.hot_keys = {}
        self.menu_buttons = []
        self.item_index = 0

    def select_button(self):
        current_button = self.menu_buttons[self.item_index]
        for button in self.menu_buttons:
            if button == current_button:
                button.configure(bg = 'white')
            else:
                button.configure(bg = 'lightgrey')

    def next_button(self):
        self.item_index = (self.item_index + 1) % len(self.menu_buttons)
        self.select_button()
        return self.menu_buttons[self.item_index]

    def prev_button(self):
        self.item_index = (self.item_index - 1) % len(self.menu_buttons)
        self.select_button()
        return self.menu_buttons[self.item_index]

    def button(self):
        return self.menu_buttons[self.item_index]


def parse_menu_item_name(item_name):
    match = re.search('[^\\\\]\&', item_name)
    if match != None:
        hot_key_index = match.start()
        hot_key = match.group(0)[0]
        new_name = re.sub(match.group(0), match.group(0)[0], item_name)
    else:
        hot_key_index = None
        hot_key = None
        new_name = item_name
    new_name = re.sub('\\\\&', '&', new_name)
    return new_name, hot_key, hot_key_index

class FaExecAction:
    def __init__(self, exec_command):
        # self.exec_command = shlex.split(exec_command[4:].strip())
        self.exec_command = exec_command

    def run(self, *args):
        subprocess.Popen(self.exec_command)
        return True

class FaMenuAction:
    def __init__(self, menu_name):
        self.menu_name = menu_name.strip().strip('"\'')

    def run(self, app, *args):
        app.switch_to_menu(self.menu_name)
        return False

class FaCommandAction:
    def __init__(self, command):
        self.commands = { "exit": self.do_exit }
        self.run = self.commands[command.lower()]

    def do_exit(self, *args):
        sys.exit(0)

def parse_menu_item_action(action):
    if action[0] == 'exec':
        return FaExecAction(action[1])
    elif action[0] == 'menu':
        return FaMenuAction(action[1])
    else:
        return FaCommandAction(action[0])

class FaMenuItem:
    def __init__(self, item_name, action):
        self.item_name, self.hot_key, self.hot_key_index = parse_menu_item_name(item_name)
        self.action = parse_menu_item_action(action)
        self.button = None

    def __repr__(self):
        return "[item_name: %s, hot_key: %s, hot_key_index: %d, action: %s]"%(self.item_name, self.hot_key, self.hot_key_index, self.action)

def main(args=None):
    menus = {}
    config = famenu_config.parse_config_file('menu_config.ini')
    for section, settings in config.items():
        if section == 'config':
            continue
        menus[section] = FaMenu(section, settings)

    app = FaMenuApp(config['config'], menus)

    app.run()


if __name__ == '__main__':
    sys.exit(main())
