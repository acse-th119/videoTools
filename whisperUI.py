import gradio as gr
import os
import shutil
from AudioWhisper import AudioWhisper
from VideoFetcher import VideoFetcher

DOWNLOAD_DIR = "./downloads"
# DOWNLOAD_DIR = "/app/downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)
tmpWhisper = AudioWhisper()

def ui_download_audio(url_input,to_txt):
    fetcher = VideoFetcher(url_input,root_dir=DOWNLOAD_DIR)
    fetcher.download_video(audio_only=True)
    head, tail, subtitle_path = transcribe_audio(fetcher.tmp_output_path, to_txt)
    return fetcher.tmp_output_path, head, tail, subtitle_path

def transcribe_audio(audio_file,to_txt=False):
    # 保存上传文件
    input_path = './uploads/uploaded_audio.mp3'
    os.makedirs('./uploads', exist_ok=True)
    os.makedirs('./results', exist_ok=True)
    shutil.copy(audio_file, input_path)

    # 转字幕
    subtitle_path = tmpWhisper.transcribe_and_save(input_path, to_txt)  # 假设返回字幕路径列表

    # 提取前后几句显示
    with open(subtitle_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    preview_count = 10
    head = ''.join(lines[:preview_count])
    tail = ''.join(lines[-preview_count:])

    return head, tail, subtitle_path

# Gradio界面定义
with gr.Blocks() as demo:
    gr.Markdown("### 🎧 在线视频字幕识别")
    gr.Markdown("### ☕预计等待音频时长的1/3时间")

    url_input = gr.Textbox(label="Video URL")
    sub_convert_to_txt = gr.Checkbox(label="Convert subtitle to .txt format", value=False)
    run_button = gr.Button("开始提取音频并识别字幕")

    with gr.Row():
        audio_player = gr.Audio(label="提取后的音频", type="filepath")

    subtitle_file_output = gr.File(label="下载字幕文件")

    with gr.Row():
        head_output = gr.Textbox(label="字幕开头", lines=10)
        tail_output = gr.Textbox(label="字幕结尾", lines=10)

    run_button.click(
        fn=ui_download_audio,
        inputs=[url_input,sub_convert_to_txt],
        outputs=[audio_player, head_output, tail_output, subtitle_file_output]
    )

if __name__ == "__main__":
    demo.launch()

