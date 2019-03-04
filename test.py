import aubio
import numpy as num
import time
import logging
import operator
import os
import pyaudio
import sys




#CHUNK = 4096 # the number of frames to split the sample rate into
CHUNK = 256
#FORMAT = pyaudio.paFloat32 #paInt16 #paInt8
#CHANNELS = 1
RATE = 44100 #44100 #sample rate i.e. number of frames per second


def main():
    global pitch, volume

    # PyAudio object.
    p = pyaudio.PyAudio()

    # Open stream.
    stream = p.open(format=pyaudio.paFloat32,
                    channels=1,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    # Aubio's pitch detection.
    pDetection = aubio.pitch("default", CHUNK, CHUNK // 2, RATE)
    # Set unit.
    pDetection.set_unit("Hz")
    pDetection.set_silence(-40)

    while True:

        try:
            data = stream.read(CHUNK // 2)
            # except IOError as ex:
        except KeyboardInterrupt:
            print()
            print("Interup detected")
            try:
                sys.exit(0)
            except SystemExit:
                os._exit(0)
        except:
            # if ex[1] != pyaudio.paInputOverflowed:
            #    raise
            # data = '\x00' *  (CHUNK  * 2)  # or however you choose to handle it, e.g. return None
            logging.warning(file, "Errrrrrrror Overload, skipping...but it's okay")

        samples = num.fromstring(data,dtype=aubio.float_type)
        pitch = pDetection(samples)[0]
        pitchUse = pitch

        # Compute the energy (volume) of the
        # current frame.
        volume = num.sum(samples ** 2) / len(samples)

        # Format the volume output so that at most
        # it has six decimal numbers.
        volume = "{:.6f}".format(volume)
        volume = float(volume)
        volumeUse = volume * 1000000

        # save the volume and pitch to a list
        #pitchList.append(pitchUse)
        #volumeList.append(volumeUse)
        # volumePitch[volumeUse] = pitchUse
        #count += 1

if __name__ == "__main__":
        main()
