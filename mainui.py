# Standard library imports
import os
import subprocess
import shutil
# Related third-party imports
import gradio as gr

# Local application
from VideoFetcher import VideoFetcher
from VideoUtils import VideoUtils
from AudioWhisper import AudioWhisper
# conda activate videoTools
# docker exec -it <container_id> bash
# docker run -p 7860:7860 -v $(pwd)/downloads:/app/downloads gr-video-tool
# docker tag gr-video-tool caesarhtx/gr-video-tool
# docker push caesarhtx/gr-video-tool

DOWNLOAD_DIR = "./downloads"
# DOWNLOAD_DIR = "/app/downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)
tmpWhisper = AudioWhisper()

def download_video_with_logs(url_input):
    log = ""
    def add_log(line):
        nonlocal log
        log = f"{line}\n" + log
        yield f"<pre><code>{log}</code></pre>"

    yield from add_log("🚀 视频📥下载初始化...")
    fetcher = VideoFetcher(url_input,root_dir=DOWNLOAD_DIR)
    yield from add_log(f"🔗 输入链接: {url_input}")
    yield from add_log(f"🛰️ 平台识别中...")
    yield from add_log(f"✅ 平台为{fetcher.platform}")
    for line in fetcher.download_video_live():
        yield from add_log(line)

def download_subtitles_with_logs(url_input,lang_input,convert_to_txt):
    log = ""
    def add_log(line):
        nonlocal log
        log = f"{line}\n" + log
        yield f"<pre><code>{log}</code></pre>"

    yield from add_log("🚀 字幕💬下载初始化...")
    fetcher = VideoFetcher(url_input,root_dir=DOWNLOAD_DIR)
    yield from add_log(f"🔗 输入链接: {url_input}")
    yield from add_log(f"🛰️ 平台识别中...")
    yield from add_log(f"✅ 平台为{fetcher.platform}")
    available_subs = fetcher.get_subtitles()
    print(available_subs)

    if lang_input not in available_subs:
        yield from add_log(f"❌ Subtitle language '{lang_input}' not available for this video.")
        yield from add_log(f"pls select from:{available_subs}")

    else:
        yield from add_log(f"☕️ {lang_input} 字幕下载中...")
        for line in fetcher.download_subtitles(lang_input,convert_to_txt):
            yield from add_log(line)

def process_video_to_audio(file):
    input_path = file.name
    filename_no_ext = os.path.splitext(os.path.basename(input_path))[0]
    # print(filename_no_ext)
    output_path = os.path.join(DOWNLOAD_DIR, f"{filename_no_ext}.mp3")
    # print(output_path)

    subprocess.run(["ffmpeg","-y", "-i", input_path, output_path])
    return output_path


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
# Gradio interface
with gr.Blocks() as demo:
    gr.Markdown("## 🎥 视频处理工具：支持视频下载 + 字幕下载")
    with gr.Tabs():
        with gr.Tab("📥 视频下载"):
            gr.Markdown("### 🙋下载完成后可以刷新一下最新文件，点击蓝色链接存到本地")
            url_input = gr.Textbox(label="Video URL")
            run_button = gr.Button("开始下载视频")
            with gr.Row():
                refresh_button = gr.Button("🔁 刷新最新文件")
                file_frame = gr.File(label="点击蓝色链接下载")
                latest_time = gr.Textbox(label="文件修改时间", interactive=False, lines=1)


            output_md = gr.Markdown(elem_id="console-log")
            run_button.click(
                fn=download_video_with_logs,
                inputs=[url_input],
                outputs=output_md
            )
            refresh_button.click(
                fn=lambda: VideoUtils.get_latest_video_file(DOWNLOAD_DIR),
                inputs=[],
                outputs=[file_frame,latest_time]
            )
            demo.load(None, None, None, js="""
                const observer = new MutationObserver(() => {
                    const el = document.getElementById("console-log");
                    if (el) el.scrollTop = el.scrollHeight;
                });
                const target = document.getElementById("console-log");
                if (target) observer.observe(target, { childList: true, subtree: true });
            """)
        with gr.Tab("💬 字幕下载"):
            gr.Markdown("### ⚠️不确定字幕语言，可以先不填运行一次，输出窗口会给出可选字幕语言。")
            with gr.Row():
                video_url = gr.Textbox(label="Video URL")
                lang_select = gr.Textbox(
                    label="Select or Input Subtitle Language",
                    placeholder="e.g. <zh> for YouTube or <ai-zh> for Bili",
                    lines=1
                )
            
            convert_to_txt = gr.Checkbox(label="Convert subtitle to .txt format", value=False)
            download_button = gr.Button("Download Subtitles")
            # output_box = gr.Textbox(label="Download Progress", interactive=False, lines=10)
            output_box = gr.Markdown(elem_id="console-log-sub")
            download_button.click(download_subtitles_with_logs, 
                                  inputs=[video_url, lang_select,convert_to_txt], 
                                  outputs=output_box)

        with gr.Tab("🔁 格式转换"):
            gr.Markdown("### 目前支持：视频➡️音频转换")
            gr.Interface(fn=process_video_to_audio, inputs=gr.File(), outputs=gr.File())

        with gr.Tab("🎧 字幕识别"):
            gr.Markdown("### 目前支持：音频➡️srt格式字幕")
            gr.Markdown("### ☕预计等待音频时长的1/3时间")

            with gr.Row():
                audio_input = gr.Audio(type="filepath", label="上传音频文件")
            sub_convert_to_txt = gr.Checkbox(label="Convert subtitle to .txt format", value=False)
            
            transcribe_btn = gr.Button("识别字幕")
            subtitle_file_output = gr.File(label="下载字幕文件")

            with gr.Row():
                head_output = gr.Textbox(label="字幕开头", lines=10)
                tail_output = gr.Textbox(label="字幕结尾", lines=10)

            

            transcribe_btn.click(fn=transcribe_audio,
                                inputs=[audio_input,sub_convert_to_txt],
                                outputs=[head_output, tail_output, subtitle_file_output])


demo.stylesheets.append("""
#console-log {
    height: 300px;
    overflow-y: auto;
    background-color: #111;
    color: #0f0;
    padding: 1em;
    border-radius: 6px;
    font-family: monospace;
    font-size: 14px;
}
""")
if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7861)