import torch
from speechbrain.pretrained import SpeakerRecognition

# Tải mô hình pre-trained ECAPA-TDNN (mô hình tốt nhất cho speaker recognition)
verification = SpeakerRecognition.from_hparams(
    source="speechbrain/spkrec-ecapa-voxceleb",
    savedir="pretrained_models/spkrec-ecapa-voxceleb"
)

# So sánh hai file âm thanh để xác định có phải cùng một người nói không
score, prediction = verification.verify_files(
    "mp3/Seren1.wav",
    "mp3/Seren2.wav"
)

print(f"Similarity score: {score}")
print(f"Same speaker: {prediction}")