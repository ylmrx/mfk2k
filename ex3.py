import re, sys, time
import pygame.midi as midi
import threading
import k2000
import glib
import dbus
from dbus.mainloop.glib import DBusGMainLoop
from multiprocessing import Process

midi.init()
device = "Midi Fighter Twister MIDI 1"

bank = 4

for i in range(midi.get_count()):
    devInfo = midi.get_device_info(i)
    if(re.compile(device).search(devInfo[1]) and
                devInfo[3] == 1):
        print devInfo[1]
        outp = midi.Output(i)
        inp = midi.Input(i + 1)
        k2000.initialize_mf(outp, bank)
        break

config = { 'app1': [ 'kit', (bank, 1, 78)],
            'app2': [ 'auto', (bank, 1, 2)],
            'app3': [ 'dial', (outp, bank, 3, 3, 100)],
            'app4': [ 'blink', (outp, bank, 4, 1, 50, 13)] }

def listen(inp, outp):
    while True:
        if inp.poll():
            polled = inp.read(100)
            for p in polled:
                if p[0][2] == 127 and p[0][0] == 177:
                    outp.write_short(0xb0, p[0][1], 0)
                    outp.write_short(0xb2, p[0][1], 0)
                    outp.write_short(0xb1, p[0][1], k2000.default_color)

        time.sleep(0.5)



def print_notification(bus, message):
    keys = ["app_name", "replaces_id", "app_icon", "summary",
            "body", "actions", "hints", "expire_timeout"]
    args = message.get_args_list()
    if len(args) == 8:
        notification = dict([(keys[i], args[i]) for i in range(8)])
        a = notification['summary']
        if a in config.keys():
            print a
            conf = (outp,)
            conf += config[a][1]
            #t = threading.Thread(target=k2000.kit, args=(outp, 4, 3, 112, lambda: stop_threads))
            if a == 'app1':
                t = threading.Thread(target=k2000.kit, args=conf)
                t.setDaemon = True
                t.start()
            if a == 'app2':
                t = threading.Thread(target=k2000.auto, args=(outp, bank, 2, 2))
                t.setDaemon = True
                t.start()
            if a == 'app3' or a == 'app4':
                getattr(k2000, config[a][0])(*config[a][1])

if __name__ == '__main__':
    p = Process(target=listen, args=(inp,outp))
    p.start()
    loop = DBusGMainLoop(set_as_default=True)
    session_bus = dbus.SessionBus()
    session_bus.add_match_string("type='method_call',interface='org.freedesktop.Notifications',member='Notify',eavesdrop=true")
    session_bus.add_message_filter(print_notification)
    glib.threads_init()
    glib.MainLoop().run()
    outp.close
    inp.close
    p.join()

#g = threading.Thread(target=glib.MainLoop().run())
#g.start()

# main()
# time.sleep(2)
# print threading.enumerate()
# time.sleep(6)
# stop_threads = True
# for i in runnings:
#     i.join()
# print threading.enumerate()
# 
# k2000.blink(outp, 4, 2, 3, 64, 6)
# time.sleep(7)
# k2000.cut(outp, 4, 2, 3)
# k2000.cut(outp, 4, 2, 2)
# outp.close
