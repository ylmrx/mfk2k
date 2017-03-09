import re, sys, time
import pygame.midi as midi
import threading
import k2000

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

runnings = []

def main():
    runnings.append(threading.Thread(target=k2000.kit, args=(outp, 4, 3, 112, lambda: stop_threads)))
    runnings.append(threading.Thread(target=k2000.kit, args=(outp, 4, 1, 78, lambda: stop_threads)))
    runnings.append(threading.Thread(target=k2000.auto, args=(outp, 4, 1, 3, lambda: stop_threads)))
    for i in runnings:
        i.start()

    threading.Thread(target=k2000.rainbow, args=(outp, 4, 2, 2)).start()


stop_threads = False

main()
time.sleep(2)
print threading.enumerate()
time.sleep(6)
stop_threads = True
for i in runnings:
    i.join()
print threading.enumerate()

k2000.blink(outp, 4, 2, 3, 64, 6)
time.sleep(7)
k2000.cut(outp, 4, 2, 3)
k2000.cut(outp, 4, 2, 2)
outp.close
