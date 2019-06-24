# audio

This package was created to simplify the process of audio processing in LED related projects. 

```python
from audio_processing import *

audio_obj = AudioProcessor()  # Create instance
while True:
    can_save_data = audio_obj.update()  # Returns self.data_dict
    audio_obj.data_dict  # Or can just access it directly 
    audio_obj.print_bars()  # An option to print a graphical representation of the audio
```

