import usb.core
import usb.util
from time import sleep
from numpy import array

VENDOR_ID = 0x04D8
PRODUCT_ID = 0x003F #0x00DD # 00DD-MCP2221 
dev=usb.core.find(idVendor=VENDOR_ID, idProduct=PRODUCT_ID)

if dev is None:
    print('Device not found')
    exit()
print(f"Device descriptor:\n{dev}")
dev.set_configuration()
# ep = usb.util.find_descriptor(dev[0][(0,0)][0])
endpoint_in = dev[0][(0,0)][0]
endpoint_out = dev[0][(0,0)][1]
while True:
    try:
        send_list=[0]*64
        send_list[0]=0x80
        #print(f"Writing {len(send_list)} bytes to endpoint {hex(endpoint_out.bEndpointAddress)}")
        res=dev.write(endpoint_out.bEndpointAddress, send_list, 10)
    except Exception as e:
        print(e)
        pass

    try:
        send_list=[0]*64
        send_list[0]=0x81
        #print(f"Writing {len(send_list)} bytes to endpoint {hex(endpoint_out.bEndpointAddress)}")
        res=dev.write(endpoint_out.bEndpointAddress, send_list, 10)
    except Exception as e:
        print(e)
        pass

    try:
        # print(f"Reading {endpoint_in.wMaxPacketSize} bytes from endpoint {hex(endpoint_in.bEndpointAddress)}")
        res=(dev.read(endpoint_in.bEndpointAddress, 64, timeout=10))[0:2].tobytes()
        print(res)
    except Exception as e:
        print(e)
        pass
    sleep(0.1)
if __name__=="__main__":
    print("This is MAIN program\n")
