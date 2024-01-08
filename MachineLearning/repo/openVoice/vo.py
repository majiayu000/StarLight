import os
import torch
import se_extractor
from api import BaseSpeakerTTS, ToneColorConverter


    
reference_speaker = 'llm/openvoice/test.mp3'
target_se, audio_name = se_extractor.get_se(reference_speaker, tone_color_converter, target_dir='processed', vad=True)