from audio_processing import AudioProcessor, FPS
import logging

logging.basicConfig(level=logging.DEBUG, format=f'%(asctime)s %(levelname)s %(name)s %(message)s')
audio_obj = AudioProcessor(num_pitch_ranges=10)
while True:
    try:
        audio_obj.update()

        # audio_obj.print_bars()
    except KeyboardInterrupt:
        break
