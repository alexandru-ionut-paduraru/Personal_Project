import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askopenfilename, asksaveasfilename
import xml.etree.ElementTree as ET
import os

from USB_Interface import *


'''Global Variables'''
device_connected=False
device_present=False
dev=None
in_ep=None
out_ep=None
dev_regs={}

'''END - Global Variables'''

def open_file():
    """Open a file for editing."""
    filepath = askopenfilename(
        filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
    )
    if not filepath:
        return
    with open(filepath, mode="r", encoding="utf-8") as input_file:
        text = input_file.read()
    window.title(f"Simple Text Editor - {filepath}")

def save_file():
    """Save the current file as a new file."""
    filepath = asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
    )
    if not filepath:
        return
    with open(filepath, mode="w", encoding="utf-8") as output_file:
        output_file.write(text)
    window.title(f"Simple Text Editor - {filepath}")

def open_children(parent):
    tree_view.item(parent, open=True)
    for child in tree_view.get_children(parent):
        open_children(child)

def close_children(parent):
    tree_view.item(parent, open=False)
    for child in tree_view.get_children(parent):
        close_children(child)

def usb_connect():
    global device_connected
    global dev
    global in_ep
    global out_ep
    dev.set_configuration()
    # ep = usb.util.find_descriptor(dev[0][(0,0)][0])
    in_ep = dev[0][(0,0)][0]
    out_ep = dev[0][(0,0)][1]
    device_connected=True

window = tk.Tk()
window.title("Simple Text Editor")

window.rowconfigure(0, minsize=800, weight=1)
window.columnconfigure(1, minsize=600, weight=1)
window.columnconfigure(2, minsize=500, weight=1)

frm_buttons = tk.Frame(window, relief=tk.RAISED, bd=2)
frm_buttons.grid(row=0, column=0, sticky="ns")
btn_open = tk.Button(frm_buttons, text="Open", command=open_file)
btn_save = tk.Button(frm_buttons, text="Save As...", command=save_file)

frm_middle = tk.Frame(window, relief=tk.RAISED, bd=2)
frm_middle.grid(row=0, column=1, sticky="nesw")
frm_middle.rowconfigure(0, weight=1)
frm_middle.columnconfigure(0, weight=1)

frm_work = tk.LabelFrame(frm_middle, text="Workplace")
frm_work.grid(row=0, column=0, sticky="nesw")
# frm_work.rowconfigure(0, weight=1)
frm_work.columnconfigure(0, weight=1)

btn_usb_connect = tk.Button(frm_work, text="Connect", command=usb_connect)
btn_usb_connect.grid(column=0, row=0, sticky="w", padx=5, pady=5)
btn_usb_disconnect = tk.Button(frm_work, text="Disconnect", command=usb_connect)
btn_usb_disconnect.grid(column=0, row=1, sticky="w", padx=5, pady=5)

# # STATUS FRAME
frm_status = tk.Frame(frm_middle, relief=tk.GROOVE, bd=2)
frm_status.grid(row=1, column=0, sticky="ew")


dev_stat_label = tk.Label(frm_status, text="Device Status:")
dev_stat_label.grid(row=0, column=0, sticky='esw')

dev_stat = tk.Label(frm_status, text="NONE", bg="#ffff00")
dev_stat.grid(row=0, column=1, sticky='esw')


frm_tree=tk.Frame(window, relief=tk.RAISED, bd=2, width=500)
frm_tree.grid(row=0, column=2, sticky="nsew")
frm_tree.rowconfigure(0, minsize=800, weight=1)
frm_tree.columnconfigure(0, minsize=300, weight=1)
frm_tree_btn=tk.Frame(frm_tree, relief=tk.RAISED, bd=2)

tree_view = ttk.Treeview(frm_tree, columns=("Value"))
tree_view.heading("#0", text="Node")
tree_view.heading("Value", text="Value")

btn_open.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
btn_save.grid(row=1, column=0, sticky="ew", padx=5)


frm_tree_btn.grid(row=1, column=0, sticky="ew")
tree_view.grid(row=0, column=0, sticky="nsew")
btn_expand=tk.Button(frm_tree_btn, text="Expand Element")
btn_expand.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
btn_collapse=tk.Button(frm_tree_btn, text="Collapse Element")
btn_collapse.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

def insertTreeNode(node, level, tree_node):
    nodes=0
    for child in node:
        nodes+=1
        
        if (child.tag=="register"):
            new_node = tree_view.insert(tree_node, tk.END, text=child[0].text)
        elif (child.tag=="bit"):
            new_node = tree_view.insert(tree_node, tk.END, text=child[1].text)
        elif (child.tag=="option"):
            new_node = tree_view.insert(tree_node, tk.END, text=child[0].text+ " - ("+child[1].text+")")
        else:
            new_node = tree_view.insert(tree_node, tk.END, text=child.tag)
        val = insertTreeNode(child, level+1, new_node)
        if val==0:
            tree_view.set(new_node, "Value", child.text)
            
    if nodes==0:
        return 0
    else:
        return 1

tree = ET.parse(os.path.join('DescriptorFile1.xml'))
root = tree.getroot()
root_node=tree_view.insert("", tk.END, text=root.tag)
insertTreeNode(root, 1, root_node)

btn_expand.configure(command=lambda: open_children(tree_view.focus()))
btn_collapse.configure(command=lambda: close_children(tree_view.focus()))

def generate_workspace_content(root):
    # global frm_work
    reg_struct=[]
    place_row=2
    if(root):
        for child in root:
            if child.tag=="registers":
                for regs in child:
                    reg_dict={}
                    reg_dict["name"]=regs[0].text #register name
                    reg_dict["type"]=regs[2].text
                    reg_dict["frame"]=tk.LabelFrame(frm_work, text=reg_dict["name"])
                    reg_dict["frame"].grid(row=place_row, column=0, sticky="ew", padx=5, pady=5)
                    for reg_child in regs:
                        if reg_child.tag=="reg_structure":
                            col_number=0
                            reg_dict["elements"]=[]
                            for element in reg_child:
                                dict_element={element[1].text:{}}
                                options=element.findall('.//option')
                                for option in options:
                                    dict_element[element[1].text][option[1].text]=option[0].text
                                reg_dict["elements"].append(dict_element)
                                # print(option[1][1].text)
                                if element.tag=="bit":
                                    tk.Label(reg_dict["frame"], text=element[1].text).grid(row=0, column=col_number, padx=5)
                                    key=list(reg_dict["elements"][-1])[0]
                                    value_list=list(reg_dict["elements"][-1][key].keys())
                                    if reg_dict["type"]=="IN":
                                        combo_box=ttk.Combobox(reg_dict["frame"], values=value_list, width=max(len(item) for item in value_list))
                                        combo_box.grid(row=1, column=col_number, padx=5, pady=5)
                                        combo_box.set(value_list[0])
                                    elif reg_dict["type"]=="OUT":
                                        text_box=tk.Label(reg_dict["frame"], width=max(len(item) for item in value_list))
                                        text_box.grid(row=1, column=col_number, padx=5, pady=5)
                                        text_box.configure(text=value_list[0])
                                        if reg_dict["elements"][-1][key][value_list[0]]=="0":
                                            text_box.configure(bg="#FF8888")
                                        else:
                                            text_box.configure(bg="#88FF88")
                                    else:
                                        pass
                                col_number+=1

                    place_row+=1
                    reg_struct.append(reg_dict)
    return reg_struct

def USB_Script():
    global device_connected
    global device_present
    global dev
    global in_ep
    global out_ep

    dev=find_device(0x04D8, 0x003F)
    if not device_present:
        #look for device
        if dev:
            device_present=True
        dev_stat.config(text="NOT DETECTED")
        dev_stat.config(bg="#ff8888")
        pass
    elif not device_connected:
        # wait for device to be connected
        if not dev:
            device_present=False
        dev_stat.config(text="NOT CONNECTED")
        dev_stat.config(bg="#ffff55")
    else:
        # device is connected
        if not dev:
            device_present=False
            device_connected=False
        dev_stat.config(text="CONNECTED") 
        dev_stat.config(bg="#55ff55")

    window.after(100, USB_Script)

USB_Script()
dev_regs=generate_workspace_content(root)
print(dev_regs)
window.mainloop()


