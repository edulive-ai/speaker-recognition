from pyannote.audio import Pipeline
from dotenv import load_dotenv
import os
load_dotenv()
token = os.getenv("hugging_face")
pipeline = Pipeline.from_pretrained(
  "pyannote/speaker-diarization-3.1",
  use_auth_token=token)

# run the pipeline on an audio file
diarization = pipeline("meeting_voice/voice_meeting_v1.wav")

# dump the diarization output to disk using RTTM format
with open("meeting_voice/voice_meeting_v1.rttm", "w") as rttm:
    diarization.write_rttm(rttm)