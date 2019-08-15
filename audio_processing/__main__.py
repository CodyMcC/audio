#! /usr/bin/env python

import aubio
import copy
import logging
import numpy as np
import os
import pyaudio
import threading
import time


class FPS:

    """
    Usage:
    fps = FPS(30)
    while True:
        fps.maintain()
    """

    def __init__(self, target_fps, name='FPS'):
        self.logger = logging.getLogger(f'audio_processor.{name}')
        self.logger.info('creating an instance of FPS')
        self.one_sec = 0 # moves every second
        self.sleep_fps = .005 # Guess!
        self.loop_count = 0 # to track FPS
        self.start_time = time.time()
        self.target_fps = target_fps
        self.true_fps = target_fps
        self.elapsed = 0

    def maintain(self):
        self.elapsed = time.time() - self.start_time
        self.loop_count += 1
        if self.one_sec < self.elapsed:
            self.logger.debug(f"FPS: {self.true_fps} - sleep: {self.sleep_fps}")
            self.one_sec += 1
            self.true_fps = self.loop_count
            # print options.fps
            # print ("Loops per sec: %i") % loopCount
                    
            if self.true_fps < self.target_fps - 2:
                self.sleep_fps *= .95
            elif self.true_fps > self.target_fps + 2:
                self.sleep_fps *= 1.05
            self.loop_count = 0
        time.sleep(self.sleep_fps)


class AudioProcessor:
    """
    Usage:
    audio_obj = AudioProcessor()
    while True:
        can_save_data = audio_obj.update() -> returns self.data_dict
        audio_obj.data_dict
        audio_obj.print_bars()
    
    """
    
    def __init__(self, num_pitch_ranges=None, start=True, name='AudioProcessor'):
        # self.logger = logging.getLogger('audio_processing.AudioProcessor')
        self.logger = logging.getLogger(f'audio_processor.{name}')
        self.logger.info('creating an instance of AudioProcessor')

        self.volume_list = []
        self.pitch_list = []
        self.capture_error_count = 0
        self.run = True        
        self.pitch_map = self._setup_pitch_map(num_pitch_ranges)
        self.data_dict = self._setup_data_dict(len(self.pitch_map))
        self.capture_thread = threading.Thread(target=self._capture)
        if start:
            self.start_capturing()        
        self.max_calc_volume = 100
        self.max_volume_list = []

        self.start_time = 0

    def start_capturing(self):
        self.run = True
        if not self.capture_thread.isAlive():
            self.capture_thread = threading.Thread(target=self._capture)
            self.capture_thread.start()
        self.start_time = time.time()

    def stop_capturing(self):
        self.run = False

    @staticmethod
    def mapping(input_min, input_max, output_min, output_max, val):
        # TODO: This function is being replaced with scale()
        
        if val < input_min:
            val = input_min
        if val > input_max:
            val = input_max
        
        return (val - input_min) / (input_max - input_min) * (output_max - output_min) + output_min

    @staticmethod
    def scale(val, src, dst):
        """
        Scale the given value from the scale of src to the scale of dst.
        """
        return ((val - src[0]) / (src[1] - src[0])) * (dst[1] - dst[0]) + dst[0]
            
    def _setup_pitch_map(self, num):
        # TODO: This function needs simplification
        """
        #
        # Map
        # Everything lower than the number is included
        # minimum number of ranges is 11
        """

        # https://courses.physics.illinois.edu/phys406/sp2017/Lab_Handouts/Octave_Bands.pdf
        bands = [22, 44, 88, 176, 353, 707, 1414, 2828, 5656, 11313, 22627]
        extras_order = [5, 4, 6, 3, 7, 2, 8, 1, 9, 0]
        data = []

        if num is None:
            return bands
        if num < 11:
            num = 11

        # Number of freq groups per band
        per_band = int(num / len(bands))
        self.logger.debug(f'per_band: {per_band}')

        missing_count = num - (per_band * len(bands))
        self.logger.debug(f'missing_count: {missing_count}')

        freq_per_band = [per_band] * len(bands)

        # Add the missing count across the center of the bands
        for index in range(missing_count):
            freq_per_band[extras_order[index]] += 1
        self.logger.debug(f'freq_per_band: {freq_per_band}')

        for index in range(len(bands)):

            step = bands[index] / freq_per_band[index]
            for num_steps in range(freq_per_band[index]):
                data.append(int(bands[index] + step * num_steps))

        self.logger.debug(f"per_band: {per_band}")
        self.logger.debug(f'freq ranges: {data}')
        return data

    @staticmethod
    def _setup_data_dict(num):

        # current_volume: UNUSED
        # max_volume: The max volume for a given pitch in the range
        # pitch:
        # max_last: The max volume seen last time pitch_updater was ran
        # falling_max: slowly decreases to 0 unless max_volume is higher

        data_dict = {"current_volume": 0, "max_volume": 0, "pitch": 0, "max_last": 0, "falling_max": 0}
        data = []
        for i in range(num):
            data.append(copy.deepcopy(data_dict))
        return data
    
    def print_bars(self):
        print()
        print()
        os.system('clear')
        for index in range(len(self.pitch_map)):
            print(f'{self.pitch_map[index]:7d}|', end='')
    
            tmp_volume = self.data_dict[index]["max_volume"]
            diff_volume = self.data_dict[index]["falling_max"] - tmp_volume
    
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

    def _update_max_volume(self):
        """
        Keeps track of the max volume, updating it incrementally over time
        """       
        
        max_volume_found = max(self.max_volume_list)
        self.max_volume_list[:] = []
        if max_volume_found > self.max_calc_volume * 2:  # if the max is way off, help it get there faster
            self.max_calc_volume *= 1.9
        
        # Aim to be about a third higher than the average max
        if max_volume_found > 2:  # if no audio is playing, don't adjust
            if max_volume_found + (max_volume_found * .3) > self.max_calc_volume:
                self.max_calc_volume *= 1.1
            if max_volume_found + (max_volume_found * .3) < self.max_calc_volume:
                self.max_calc_volume *= .75

        self.logger.debug(f"The calc max volume is: {self.max_calc_volume}")
    
    def update(self) -> dict:
        """Takes a list of pitches and volumes and finds the max volume for each pitch range"""

        self.start_capturing()  # Just double check that it is running

        # Move all of the max_volume data to max_last and reset max_volume to 0
        for index in range(len(self.data_dict)):
            self.data_dict[index]["max_last"] = self.data_dict[index]["max_volume"]
            self.data_dict[index]["max_volume"] = 0
            
            # Calculate falling_max
            if self.data_dict[index]["max_last"] > self.data_dict[index]["falling_max"]:
                self.data_dict[index]["falling_max"] = self.data_dict[index]["max_last"]
            else:
                self.data_dict[index]['falling_max'] *= .7        
        
        # If the buffer overflows, it is possible for the lists not to be equal in length,
        # by using the shorter list there is no risk of index error
    
        # Loop through each of the gathered volume samples
        for position in range(len(min(self.pitch_list, self.volume_list))):
            for index in range(len(self.pitch_map)):
                try: 
                    if self.pitch_list[position] < self.pitch_map[index]:
                        if self.volume_list[position] > self.data_dict[index]["max_volume"]:
                            self.data_dict[index]["max_volume"] = self.volume_list[position]
                        break  # Only if a match is found in the pitch_map
                except IndexError:
                    pass 

        try:
            self.max_volume_list.append(max(self.volume_list))
        except ValueError:
            pass
        if len(self.max_volume_list) > 120: 
            self._update_max_volume()

        self.volume_list[:] = []  # empty the list
        self.pitch_list[:] = []  # empty the list
    
        return self.data_dict

    def _capture(self):
        """Constantly adds to pitch_list and volume_list until cleared by self.update()"""
        # TODO Add more optional paramaters
    
        # initialise pyaudio
        p = pyaudio.PyAudio()
        print(1)
    
        # open stream
        buffer_size = 32
        pyaudio_format = pyaudio.paFloat32
        print(2)
        n_channels = 1
        samplerate = 44100
        stream = p.open(format=pyaudio_format,
                        channels=n_channels,
                        rate=samplerate,
                        input=True,
                        frames_per_buffer=buffer_size)
        print(3)
    
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

            try:
                # try:
                audiobuffer = stream.read(buffer_size, exception_on_overflow=False)
    
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

                volume = (np.sum(signal ** 2) / len(signal)) * 100
    
                self.volume_list.append(volume)
                self.pitch_list.append(pitch)
    
            except KeyboardInterrupt:
                print("*** Ctrl+C pressed, exiting")
                break
    
        print("*** done recording")
        stream.stop_stream()
        stream.close()
        p.terminate()


def main():
    audio_o = AudioProcessor()
    fps = FPS(30)

    while True:
        try:
            fps.maintain()
            audio_o.update()
            audio_o.print_bars()
        except KeyboardInterrupt:
            break


if __name__ == "__main__":
    main()
