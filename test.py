from audio_processing import AudioProcessor, FPS

audio_obj = AudioProcessor()
while True:
    audio_obj.update()

    audio_obj.print_bars()