
from tkinter import *
from tkinter import font as FNT
from tkinter import filedialog as fd
from tkinter import ttk
from PIL import Image, ImageTk
from pathlib import Path as PATH
import tkinter as TKIN
import binascii, re, hashlib, os, json


config_path = "./data/config.json"
speed_index = 26228429


class Config:

    def __init__(self):

        if not os.path.exists(config_path):
            dat = {}
            dat["gamedir"] = ""
            self.cfg = dat
            with open(config_path, 'w') as f:
                json.dump(self.cfg, f)
        else:
            with open(config_path, 'r') as f:
                js = json.load(f)
                self.cfg = js

    def set(self,k,v):
        self.cfg[k] = v
        with open(config_path, 'w') as f:
            json.dump(self.cfg, f)



def change_default_dir():
    """Opens file explorer for user to choose new default elden ring directory. Writes changes to GameSaveDir.txt"""

    newdir = fd.askdirectory()
    if len(newdir) < 1:  # User presses cancel
        return

    folder = newdir.split("/")[-1]
    f_id = re.findall(r"\d{17}", folder)

    if len(f_id) == 0:
        popup("Please select the directory named after your 17 digit SteamID")
        return

    else:
        config.set("gamedir", newdir)
        dir_var.set(config.cfg["gamedir"])
        root.update()
        popup(f"Directory set to:\n {newdir}\n")


def popup(text, command=None, functions=False, buttons=False, button_names=("Yes", "No"), b_width=(6,6), title="Manager", parent_window=None):
    """text: Message to display on the popup window.
    command: Simply run the windows CMD command if you press yes.
    functions: Pass in external functions to be executed for yes/no"""
    def run_cmd():
        cmd_out = run_command(command)
        popupwin.destroy()
        if cmd_out[0] == "error":
            popupwin.destroy()

    def dontrun_cmd():
        popupwin.destroy()

    def run_func(arg):
        arg()
        popupwin.destroy()
    if parent_window is None:
        parent_window = root
    popupwin = Toplevel(parent_window)
    popupwin.title(title)

    lab = Label(popupwin, text=text)
    lab.grid(row=0, column=0, padx=5, pady=5, columnspan=2)
    # Places popup window at center of the root window
    x = parent_window.winfo_x()
    y = parent_window.winfo_y()
    popupwin.geometry("+%d+%d" % (x + 200, y + 200))

    # Runs for simple windows CMD execution
    if functions is False and buttons is True:
        but_yes = Button(
            popupwin, text=button_names[0], borderwidth=5, width=b_width[0], command=run_cmd
        ).grid(row=1, column=0, padx=(10, 0), pady=(0, 10))
        but_no = Button(
            popupwin, text=button_names[1], borderwidth=5, width=b_width[1], command=dontrun_cmd
        ).grid(row=1, column=1, padx=(10, 10), pady=(0, 10))

    elif functions is not False and buttons is True:
        but_yes = Button(
            popupwin,
            text=button_names[0],
            borderwidth=5,
            width=b_width[0],
            command=lambda: run_func(functions[0]),
        ).grid(row=1, column=0, padx=(10, 0), pady=(0, 10))
        but_no = Button(
            popupwin,
            text=button_names[1],
            borderwidth=5,
            width=b_width[1],
            command=lambda: run_func(functions[1]),
        ).grid(row=1, column=1, padx=(10, 10), pady=(0, 10))
    # if text is the only arguement passed in, it will simply be a popup window to display text


def validate(P):
    if len(P) == 0:
        return True
    elif len(P) < 3 and P.isdigit() and int(P) > 0:
        return True
    else:
        # Anything else, reject it
        return False


def change_main_value(file, new_value, index_location, length_in_bytes):

    with open(file, 'rb') as f:
        dat = f.read()

    data = (

        dat[:index_location]
        + new_value.to_bytes(length_in_bytes,"little")
        + dat[index_location + length_in_bytes :]

        )


    with open(file, 'wb') as f:
        f.write(data)
    recalc_checksum(file)


def l_endian(val):
    """Takes bytes and returns little endian int32/64"""
    l_hex = bytearray(val)
    l_hex.reverse()
    str_l = "".join(format(i, "02x") for i in l_hex)
    return int(str_l, 16)


def recalc_checksum(file):
    with open(file, "rb") as fh:
        dat = fh.read()
        slot_ls = []
        slot_len = 2621439
        cs_len = 15
        s_ind = 0x00000310
        c_ind = 0x00000300

        # Build nested list containing data and checksum related to each slot
        for i in range(10):
            # [ dat[0x00000310:0x0028030F +1], dat[ 0x00000300:0x0000030F + 1] ]
            d = dat[s_ind : s_ind + slot_len + 1]
            c = dat[c_ind : c_ind + cs_len + 1]
            slot_ls.append([d, c])
            s_ind += 2621456
            c_ind += 2621456

        # Do comparisons and recalculate checksums
        for ind, i in enumerate(slot_ls):
            new_cs = hashlib.md5(i[0]).hexdigest()
            cur_cs = binascii.hexlify(i[1]).decode("utf-8")

            if new_cs != cur_cs:
                slot_ls[ind][1] = binascii.unhexlify(new_cs)

        slot_len = 2621439
        cs_len = 15
        s_ind = 0x00000310
        c_ind = 0x00000300
        # Insert all checksums into data
        for i in slot_ls:
            dat = dat[:s_ind] + i[0] + dat[s_ind + slot_len + 1 :]
            dat = dat[:c_ind] + i[1] + dat[c_ind + cs_len + 1 :]
            s_ind += 2621456
            c_ind += 2621456

        # Manually doing General checksum
        general = dat[0x019003B0 : 0x019603AF + 1]
        new_cs = hashlib.md5(general).hexdigest()
        cur_cs = binascii.hexlify(dat[0x019003A0 : 0x019003AF + 1]).decode("utf-8")

        writeval = binascii.unhexlify(new_cs)
        dat = dat[:0x019003A0] + writeval + dat[0x019003AF + 1 :]

        with open(file, "wb") as fh1:
            fh1.write(dat)


def patch():
    if len(config.cfg["gamedir"]) < 1:
        popup("Please set your game save directory first")
        return
    if len(speed_ent.get()) < 1:
        popup("Please enter a speed value!")
        return

    speed_var = int(speed_ent.get())
    path = f"{config.cfg['gamedir']}/ER0000.sl2"
    if not os.path.exists(path):
        popup(f"Unable to find your save file!\nPATH: {path}")


    change_main_value(path, speed_var, speed_index, 1)
    popup("Success!")




config = Config()

# Main GUI
root = Tk()
root.title("EldenRing Mouse Sensitivity Patcher")
root.resizable(width=True, height=True)
root.geometry("510x300")

vcmd = (root.register(validate), "%P")

main_label = Label(root, text="Select your game save directory\n")
main_label.pack()

dir_var = StringVar()
dir_var.set(config.cfg["gamedir"])
dir_box = Entry(root, borderwidth=2, width=60, textvariable=dir_var, state=DISABLED)
dir_box.pack()


set_dir_but = Button( root, text="Change Directory", command=change_default_dir)
set_dir_but.pack()

padding_label = Label(root, text="\n\n")
padding_label.pack()

speed_lab = Label(root, text="Enter speed:")
speed_lab.pack()
speed_ent = Entry(root, borderwidth=5, width=3, validate="key", validatecommand=vcmd)
speed_ent.pack()

padding_label1 = Label(root, text="\n")
padding_label1.pack()

patch_but= Button( root, text="PATCH", command=patch)
patch_but.pack()

root.mainloop()
