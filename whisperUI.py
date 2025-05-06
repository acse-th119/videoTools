import gradio as gr
import os
import shutil
from AudioWhisper import AudioWhisper
tmpWhisper = AudioWhisper()

def transcribe_audio(audio_file):
    # 保存上传文件
    input_path = './uploads/uploaded_audio.mp3'
    os.makedirs('./uploads', exist_ok=True)
    os.makedirs('./results', exist_ok=True)
    shutil.copy(audio_file, input_path)

    # 转字幕
    subtitle_path = tmpWhisper.transcribe_and_save(input_path)  # 假设返回字幕路径列表

    # 提取前后几句显示
    with open(subtitle_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    preview_count = 10
    head = ''.join(lines[:preview_count])
    tail = ''.join(lines[-preview_count:])

    return head, tail, subtitle_path

# Gradio界面定义
with gr.Blocks() as demo:
    gr.Markdown("# 🎧 音频字幕识别工具")

    with gr.Row():
        audio_input = gr.Audio(type="filepath", label="上传音频文件")
    
    transcribe_btn = gr.Button("识别字幕")
    subtitle_file_output = gr.File(label="下载字幕文件")

    with gr.Row():
        head_output = gr.Textbox(label="字幕开头", lines=10)
        tail_output = gr.Textbox(label="字幕结尾", lines=10)

    

    transcribe_btn.click(fn=transcribe_audio,
                         inputs=audio_input,
                         outputs=[head_output, tail_output, subtitle_file_output])

if __name__ == "__main__":
    demo.launch()

