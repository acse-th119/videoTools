import os
import time
from tqdm import tqdm
import threading
from faster_whisper import WhisperModel
import srt
from datetime import timedelta
# 初始化模型（建议 medium 模型 + auto compute_type）

class AudioWhisper:
    def __init__(self):
        self.model = WhisperModel("medium", compute_type="auto")

    @staticmethod
    def fake_progress_bar(stop_event):
        with tqdm(total=100, desc="Transcribing", bar_format="{l_bar}{bar}| {elapsed}") as pbar:
            while not stop_event.is_set():
                time.sleep(0.1)
                pbar.update(1 if pbar.n < 99 else 0)
            pbar.n = 100
            pbar.refresh()

    def transcribe_with_progress(self, file):
        stop_event = threading.Event()
        progress_thread = threading.Thread(target=AudioWhisper.fake_progress_bar, args=(stop_event,))
        
        progress_thread.start()
        segments, info = self.model.transcribe(file, beam_size=5)
        stop_event.set()
        progress_thread.join()

        print("Loading complete, Transcribing:")
        return segments, info

    # 转写 + 生成字幕
    def transcribe_and_save(self, file, output_pure_text=False):
        print(f'Loading {file}...')
        segments, info = self.transcribe_with_progress(file)
        # 生成 .txt 和 .srt 文件
        base = os.path.splitext(os.path.basename(file))[0]
        # temp_dir = tempfile.mkdtemp()
        temp_dir = os.path.dirname(file)
        txt_path = os.path.join(temp_dir, base + ".txt")
        srt_path = os.path.join(temp_dir, base + ".srt")
        pure_text = ''
        
        # 创建字幕段
        srt_segments = []
        for i, seg in tqdm(enumerate(segments)):
            pure_text+=seg.text+'\n'
            srt_segments.append(srt.Subtitle(
                index=i+1,
                start=timedelta(seconds=seg.start),
                end=timedelta(seconds=seg.end),
                content=seg.text.strip()
            ))
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(pure_text)
        with open(srt_path, "w", encoding="utf-8") as f:
            f.write(srt.compose(srt_segments))

        print(f'Done for {file}...')
        result = {
            "音频文件": os.path.basename(file),
            "转写文本": pure_text[:100]+" | <truncate here for demo>.",
            "TXT下载": txt_path,
            "SRT下载": srt_path
        }
        self.result = result
        # print(result)
        if output_pure_text:
            return txt_path
        else:
            return srt_path