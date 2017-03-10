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
mail = 0
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

config = { 'cs': [ 'blink', (outp, bank, 4, 4, 31, 8), 0],
            'bot-otrs': [ 'blink', (outp, bank, 3, 1, 100, 14), 0],
            'general': [ 'blink', (outp, bank, 4, 3, 42, 14), 0],
            'Poolp Fiction': [ 'blink', (outp, bank, 4, 2, 40, 13), 0],
            'mechanicalkeyboards': [ 'blink', (outp, bank, 4, 1, 50, 127), 0],
            'Thunderbird': [ 'blink', (outp, bank, 1, 1, 50, 127), 0]}

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
        if notification['app_name'] == 'Thunderbird':
           a = notification['app_name']
        if a in config.keys():
            getattr(k2000, config[a][0])(*config[a][1])
            if config[a][2] < 123:
                config[a][2] += 10
                print config[a][2]
                outp = config[a][1][0]
                bank = config[a][1][1]
                line = config[a][1][2]
                col = config[a][1][3]
                k2000.dial(outp, bank, line, col, config[a][2])
            print a

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
