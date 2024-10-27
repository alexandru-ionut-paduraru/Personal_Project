import usb.core
import usb.util
from time import sleep

def find_device (f_vid, f_pid):
    dev=usb.core.find(idVendor=f_vid, idProduct=f_pid)
    return dev