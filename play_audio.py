import sys
from pydub import AudioSegment
from pydub.playback import play

def play_audio_file(file_path):
    """
    Phát file âm thanh sử dụng pydub.
    
    Parameters:
    - file_path: Đường dẫn đến file âm thanh
    """
    try:
        print(f"Đang tải file âm thanh: {file_path}")
        audio = AudioSegment.from_file(file_path)
        print(f"Đang phát file âm thanh (thời lượng: {len(audio)/1000:.2f} giây)")
        play(audio)
        print("Phát hoàn tất")
    except Exception as e:
        print(f"Lỗi khi phát file âm thanh: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Cách sử dụng: python play_audio.py <đường_dẫn_file_âm_thanh>")
        sys.exit(1)
    
    audio_file = sys.argv[1]
    play_audio_file(audio_file) 