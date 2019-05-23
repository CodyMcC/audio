#! /usr/bin/env python

import aubio
import copy
import numpy as np
import os
import pyaudio
import sys
import threading
import time


def print_ranges():
    for key in pitch_map.keys():
        print(f"{pitch_map[key]}: {data_dict[key]['max_volume']:.2f} {data_dict[key]['max_last']:.2f}")
    print()



class AudioProcessor():
    """
    Usage:
    audio_obj = audioProcessor()
    while True:
        can_save_data = audio_obj.update() -> returns self.data_dict
        audio_obj.data_dict
        audio_obj.print_bars()
    
    """
    
    def __init__():
        self.volume_list = []
        self.pitch_list = []
        self.capture_error_count
        
        self.pitch_map = setup_pitch_map()
        self.data_dict = setup_data_dict()
        
        capture_thread = threading.Thread(target=self.capture)
        capture_thread.start()
        self.start_time = time.time()
        
    def setup_pitch_map():
        # TODO make this flexible
        """
        #     Frequency (Hz)	Octave	Description
        16 to 32	1st	The lower human threshold of hearing, and the lowest pedal notes of a pipe organ.
        32 to 512	2nd to 5th	Rhythm frequencies, where the lower and upper bass notes lie.
        512 to 2048	6th to 7th	Defines human speech intelligibility, gives a horn-like or tinny quality to sound.
        2048 to 8192	8th to 9th	Gives presence to speech, where labial and fricative sounds puss.
        8192 to 16384	10th	Brilliance, the sounds of bells and the ringing of cymbals and sibilance in speech.
        16384 to 32768 11th Beyond brilliance, nebulous sounds approaching and just passing the upper human threshold of hearing
        #
        # Map
        # Everything lower than the number is included
        """
        
        return {
            "p1": 32,
            "p2": 64,  # 2nd to 5th	Rhythm frequencies, where the lower and upper bass notes lie.
            "p3": 256,  # 2nd to 5th	Rhythm frequencies, where the lower and upper bass notes lie.
            "p4": 512,  # 2nd to 5th	Rhythm frequencies, where the lower and upper bass notes lie.
            "p5": 1024,  # 6th to 7th	Defines human speech intelligibility, gives a horn-like or tinny quality to sound.
            "p6": 2048,  # 6th to 7th	Defines human speech intelligibility, gives a horn-like or tinny quality to sound.
            "p7": 4096,  # 6th to 7th	Defines human speech intelligibility, gives a horn-like or tinny quality to sound.
            "p8": 8192,  # 6th to 7th	Defines human speech intelligibility, gives a horn-like or tinny quality to sound.
            "p9": 12000,  # 10th	Brilliance, the sounds of bells and the ringing of cymbals and sibilance in speech.
            "p10": 16384,  # 10th	Brilliance, the sounds of bells and the ringing of cymbals and sibilance in speech.
            "p11": 32768  # 11th Beyond brilliance, nebulous sounds approaching and just passing the upper human threshold of hearing
        }
        
    def setup_data_dict():
        # TODO make flexible: dict_copy = copy.deepcopy(my_dict)
        # TODO define each of the dict keys
        # current_volume: UNUSED
        # max_volume: The max volume for a given pitch in the range
        # pitch:
        # max_last: The max volume seen last time pitch_updater was ran
        # floating_max: slowly decreases to 0 unless max_volume is higher
        return {
        'p1': {"current_volume": 0, "max_volume": 0, "pitch": 0, "max_last": 0, "floating_max": 0},
        'p2': {"current_volume": 0, "max_volume": 0, "pitch": 0, "max_last": 0, "floating_max": 0},
        'p3': {"current_volume": 0, "max_volume": 0, "pitch": 0, "max_last": 0, "floating_max": 0},
        'p4': {"current_volume": 0, "max_volume": 0, "pitch": 0, "max_last": 0, "floating_max": 0},
        'p5': {"current_volume": 0, "max_volume": 0, "pitch": 0, "max_last": 0, "floating_max": 0},
        'p6': {"current_volume": 0, "max_volume": 0, "pitch": 0, "max_last": 0, "floating_max": 0},
        'p7': {"current_volume": 0, "max_volume": 0, "pitch": 0, "max_last": 0, "floating_max": 0},
        'p8': {"current_volume": 0, "max_volume": 0, "pitch": 0, "max_last": 0, "floating_max": 0},
        'p9': {"current_volume": 0, "max_volume": 0, "pitch": 0, "max_last": 0, "floating_max": 0},
        'p10': {"current_volume": 0, "max_volume": 0, "pitch": 0, "max_last": 0, "floating_max": 0},
        'p11': {"current_volume": 0, "max_volume": 0, "pitch": 0, "max_last": 0, "floating_max": 0}
        }
    
    def print_bars():
        print()
        print()
        os.system('clear')
        for key in self.pitch_map.keys():
            print(f'{pitch_map[key]:7d}|', end='')
    
            tmp_volume = self.data_dict[key]["max_volume"]
            diff_volume = self.data_dict[key]["floating_max"] - tmp_volume
    
            if tmp_volume > 750:
                tmp_volume = 750
                diff_volume = 0
    
            if tmp_volume + diff_volume > 750:
                diff_volume = 750 - tmp_volume
    
            while tmp_volume > 0:
                print("-", end="")
                tmp_volume -= 10
            while diff_volume > 0:
                print(" ", end="")
                diff_volume -= 10
    
            print("|")
    
    def update(self) -> dict:
        """Takes a list of pitches and volumes and finds the max volume for each pitch range"""
    
        # Move all of the max_volume data to max_last and reset max_volume to 0
        for key in self.data_dict.keys():
            self.data_dict[key]["max_last"] = self.data_dict[key]["max_volume"]
            self.data_dict[key]["max_volume"] = 0
    
            if self.data_dict[key]["max_last"] > self.data_dict[key]["floating_max"]:
                self.data_dict[key]["floating_max"] = self.data_dict[key]["max_last"]
            else:
                if (self.data_dict[key]["floating_max"] / 6) > self.data_dict[key]["max_last"]:
                    self.data_dict[key]["floating_max"] -= 25
                elif (self.data_dict[key]["floating_max"] / 2) > self.data_dict[key]["max_last"]:
                    self.data_dict[key]["floating_max"] -= 5
                else:
                    self.data_dict[key]["floating_max"] -= 2.5
    
                # position = 0  # Keep track of position in volume_list and pitch_list
        #
        # If the buffer overflows, it is possible for the lists not to be equal in length,
        # by using the shorter list there is no risk of index error
    
        # Loop through each of the gathered volume samples
        for position in range(len(min(self.pitch_list, self.volume_list))):
            for key in self.pitch_map.keys():
    
                if self.pitch_list[position] < self.pitch_map[key]:
                    if self.volume_list[position] > self.data_dict[key]["max_volume"]:
                        self.data_dict[key]["max_volume"] = self.volume_list[position]
                    break  # Only if a match is found in the pitch_map
    
        self.volume_list[:] = []  # empty the list
        self.pitch_list[:] = []  # empty the list
    
        return self.data_dict

    def capture(self):
        """Constantly adds to pitch_list and volume_list untill cleared by update"""
        # TODO Add more optional paramaters
        
        start_time = time.time()
    
        # initialise pyaudio
        p = pyaudio.PyAudio()
    
        # open stream
        buffer_size = 32
        pyaudio_format = pyaudio.paFloat32
        n_channels = 1
        samplerate = 44100
        stream = p.open(format=pyaudio_format,
                        channels=n_channels,
                        rate=samplerate,
                        input=True,
                        frames_per_buffer=buffer_size)
    
        # setup pitch
        tolerance = 0.8
        win_s = 4096  # fft size
        hop_s = buffer_size  # hop size
        pitch_o = aubio.pitch("default", win_s, hop_s, samplerate)
        pitch_o.set_unit("Hz")
        pitch_o.set_tolerance(tolerance)
    
        print("*** starting recording")
    
        self.capture_error_count = 0
        while self.run:
    
            # TODO is this even used?
            run_time = time.time() - start_time
    
            try:
                # try:
                audiobuffer = stream.read(buffer_size, exception_on_overflow = False)
    
                # except OSError:
                #     # if ex[1] != pyaudio.paInputOverflowed:
                #     error_count += 1
                #     print("OSError", error_count)
                #     audiobuffer = ('\x00' * buffer_size * 4).encode()  # or however you choose to handle it, e.g. return None
    
                # except OSError as e:
    
                    # print("Got the OSError, here is the full thing:")
                    # print(e)
    
                signal = np.frombuffer(audiobuffer, dtype=np.float32)
    
                pitch = pitch_o(signal)[0]
                # confidence = pitch_o.get_confidence()
    
                volume = (np.sum(signal ** 2) / len(signal)) * 10000
    
                volume_list.append(volume)
                pitch_list.append(pitch)
    
            except KeyboardInterrupt:
                print("*** Ctrl+C pressed, exiting")
                break
    
        print("*** done recording")
        stream.stop_stream()
        stream.close()
        p.terminate()


def main():
    
    five_sec = 0
    one_sec = 0
    tenth_sec = 0.0

    small_list_count = 0
    
    audio_obj = AudioProcessor()

    try:
        while True:
            run_time = time.time() - start_time

            # 0.1 seconds
            if run_time + 0.05 > tenth_sec:
                tenth_sec += 0.05
                # print(len(pitch_list))
                # print_ranges()
                if len(volume_list) < 20:
                    small_list_count += 1
                print(len(volume_list), small_list_count)
                audio_obj.update()
                audio_obj.data_dict # to use it 
                audio_obj.print_bars()



            # 1 Second
            if run_time + 1 > one_sec:
                one_sec += 1

            # 5 Seconds
            if run_time + 5 > five_sec:
                five_sec += 5
            #run = False
            #sys.exit()
    except KeyboardInterrupt:
        run = False
        sys.exit()


if __name__ == "__main__":
    main()
