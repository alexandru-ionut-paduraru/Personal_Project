import usb.core
import usb.util
from time import sleep

def find_device (f_vid, f_pid):
    dev=usb.core.find(idVendor=f_vid, idProduct=f_pid)
    return dev

def get_register(dev, endpoint_in, endpoint_out, reg_no=0):
    try:
        send_list=[0]*64
        send_list[0]=0x10
        send_list[1]=reg_no
        res=dev.write(endpoint_out.bEndpointAddress, send_list, 10)
    except Exception as e:
        print(e)
        pass

    try:
        res=(dev.read(endpoint_in.bEndpointAddress, 64, timeout=10))[0:3].tobytes()
        return res
    except Exception as e:
        print(e)
        pass

    return None