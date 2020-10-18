# Audio Processing

This package was created to simplify the process of audio processing in LED related projects. 

This package samples live audio and gives the max volume in each of the given pitch ranges. 

## Instalation
First install portaudio

Mac
`brew install portaudio`

```python
from audioprocessing import *

audio_obj = AudioProcessor(num_pitch_ranges=None)  # Create instance

while True:
    try:
        can_save_data = audio_obj.update()  # Returns self.data_dict
        audio_obj.data_dict  # Or can just access it directly 
        audio_obj.print_bars()  # An option to print a graphical representation of the audio
    except KeyboardInterrupt:
        break
    
```

