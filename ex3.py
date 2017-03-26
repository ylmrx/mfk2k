import re, sys, time
import pygame.midi as midi
import threading
import k2000
import glib
import dbus
from dbus.mainloop.glib import DBusGMainLoop
from multiprocessing import Process
from multiprocessing import Value

import json

midi.init()
device = "Midi Fighter Twister MIDI 1"
conf_file = "./config.json"
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

if len(sys.argv) > 1:
    fp = open(sys.argv[1])
else:
    fp = open(conf_file, 'r')

js = json.load(fp)

config = {}

for j in js.keys():
    config[j] = ['blink', (outp, bank, js[j]['line'], js[j]['column'], js[j]['color'], js[j]['mode']), 0 ]

def listen(inp, outp, conf, r):
    while True:
        if inp.poll():
            polled = inp.read(100)
            for p in polled:
                if p[0][2] == 127 and p[0][0] == 177:
                    outp.write_short(0xb0, p[0][1], 0)
                    outp.write_short(0xb2, p[0][1], 0)
                    outp.write_short(0xb1, p[0][1], k2000.default_color)
                    for c in conf.keys():
                        if len(conf[c]) == 3:
                            knob = 0
                            knob += (conf[c][1][1] - 1) * 16
                            knob += (conf[c][1][2] - 1) * 4
                            knob += conf[c][1][3] - 1
                            if knob == p[0][1]:
                                r.value = knob
        time.sleep(0.5)

def print_notification(bus, message):
    keys = ["app_name", "replaces_id", "app_icon", "summary",
            "body", "actions", "hints", "expire_timeout"]
    args = message.get_args_list()
    if len(args) == 8:
        notification = dict([(keys[i], args[i]) for i in range(8)])
        print notification['summary']
        print notification['app_name']
        a = notification['summary']
        if notification['app_name'] == 'Thunderbird':
           a = notification['app_name']
        if a in config.keys():
            getattr(k2000, config[a][0])(*config[a][1])
            print config[a][1]
            print config[a][2]
            if len(config[a]) == 3:
                if r.value == ((config[a][1][1] - 1) * 16) + ((config[a][1][2] - 1) * 4) + config[a][1][3] - 1:
                    config[a][2] = 0
                    r.value = 0
                config[a][2] += 10
                outp = config[a][1][0]
                bank = config[a][1][1]
                line = config[a][1][2]
                col = config[a][1][3]
                if config[a][2] < 127:
                    k2000.dial(outp, bank, line, col, config[a][2])
                else:
                    k2000.dial(outp, bank, line, col, 127)
            print a

if __name__ == '__main__':
    r = Value('i', 0)
    p = Process(target=listen, args=(inp, outp, config, r))
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
