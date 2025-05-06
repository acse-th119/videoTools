# Standard library imports
import os
import subprocess
# Related third-party imports
import gradio as gr

# Local application
from VideoFetcher import VideoFetcher
from VideoUtils import VideoUtils
# conda activate videoTools
# docker exec -it <container_id> bash
# docker run -p 7860:7860 -v $(pwd)/downloads:/app/downloads gr-video-tool
# docker tag gr-video-tool caesarhtx/gr-video-tool
# docker push caesarhtx/gr-video-tool

DOWNLOAD_DIR = "./downloads"
# DOWNLOAD_DIR = "/app/downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


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
    filename_no_ext = os.path.splitext(os.path.basename(path))[0]
    output_path = os.path.join(DOWNLOAD_DIR, f"{filename_no_ext}.mp3")
    subprocess.run(["ffmpeg","-y", "-i", input_path, output_path])
    return output_path

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