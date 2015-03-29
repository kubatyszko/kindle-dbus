import dbus
import gobject
import dbus.decorators
import dbus.glib
import gobject
import time


gobject.threads_init()

from dbus import glib
glib.init_threads()

bus=dbus.SystemBus()

def add_device(*args, **keywords):
    print 'Device Added:', ' '.join([arg for arg in args])
    print "checking if it's kindle"
    time.sleep(2) ## Let is sleep for a while - this callback will run many times (for the whole device tree ) - if you query dbus too fast, you won't find kindle
    
    halObject = bus.get_object("org.freedesktop.Hal", "/org/freedesktop/Hal/Manager")
    halManager = dbus.Interface(halObject, "org.freedesktop.Hal.Manager")
    storageDevices = halManager.FindDeviceByCapability("storage")
    
    print storageDevices
    
    for device in storageDevices:
        dev_obj = bus.get_object('org.freedesktop.Hal', device)
        props=dev_obj.GetAllProperties(dbus_interface="org.freedesktop.Hal.Device")
#    print props
        
        if props["storage.bus"] == "usb" and props["storage.removable"]:
            #        print props
            children = halManager.FindDeviceStringMatch("info.parent", device)
        #        print children
            for child in children:
                deviceObject=bus.get_object("org.freedesktop.Hal", child)
                deviceVolumeInterface=dbus.Interface(deviceObject, "org.freedesktop.Hal.Device.Volume")
                deviceInterface=dbus.Interface(deviceObject, "org.freedesktop.Hal.Device")
                product= deviceInterface.GetProperty("info.product")
                mountpoint=deviceInterface.GetProperty("volume.mount_point")
                label=deviceInterface.GetProperty("volume.label")
                ismounted=deviceInterface.GetProperty("volume.is_mounted")
                
                if label=="Kindle" and ismounted==1:
                    print "Found Kindle at mountpoint: ",mountpoint," Now just need to run sync :P "

def remove_device(*args, **keywords):
    print 'Device Removed:', ' '.join([arg for arg in args])

bus.add_signal_receiver(add_device, 'DeviceAdded', 'org.freedesktop.Hal.Manager',
                        'org.freedesktop.Hal', '/org/freedesktop/Hal/Manager')
bus.add_signal_receiver(remove_device, 'DeviceRemoved', 'org.freedesktop.Hal.Manager',
                        'org.freedesktop.Hal', '/org/freedesktop/Hal/Manager')

loop = gobject.MainLoop()
loop.run()



