import threading
import time
import os

import yt_dlp
import pysrt
import webvtt


from StreamingLogger import StreamingLogger

class VideoFetcher:
    def __init__(self,url,root_dir=None):
        if root_dir:
            self.root_dir = root_dir
        else:
            self.root_dir = '.'
        self.video_url = url
        self.platform = VideoFetcher.get_platform(url)
        self.output_filename_format = os.path.join(self.root_dir,'%(title).50s-%(id)s.%(ext)s') # 'outtmpl': '%(title)s.%(ext)s',
        self.logger = StreamingLogger()
        self.cookie_path = './bili_cookies.txt'

    @staticmethod
    def get_platform(url):
        if "youtube.com" in url or "youtu.be" in url:
            return "YouTube"
        elif "bilibili.com" in url:
            return "Bilibili"
        else:
            return "Unknown"

    @staticmethod
    def create_hook(logger):
        def hook(d):
            if d['status'] == 'downloading':
                percent = d.get('_percent_str', '').strip()
                speed = d.get('_speed_str', '').strip()
                eta = d.get('_eta_str', '').strip()
                logger.push_line(f"Downloading: {percent} at {speed}, ETA: {eta}")
            elif d['status'] == 'finished':
                logger.push_line("✅ Download complete! Now post-processing...")
        return hook
    
    # Generator function for streaming
    def download_video_live(self):
        print('🟢 begin video download')
        hook = VideoFetcher.create_hook(self.logger)
        ydl_opts = {
            'outtmpl': self.output_filename_format,
            'logger': self.logger,
            'progress_hooks': [hook],
            'writesubtitles': False,
            'quiet': True,
        }

        finished = False

        def run_yt_dlp():
            nonlocal finished
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(self.video_url, download=False)
                    filename = ydl.prepare_filename(info)
                    mainname = os.path.splitext(os.path.basename(filename))[0]
                    self.logger.push_line(f"预计下载文件名为：{mainname}")
                    ydl.download([self.video_url])
                    print('🟢 finish video download')

            except Exception as e:
                self.logger.push_line(f"❌ Error: {str(e)}")
            finally:
                finished = True

        thread = threading.Thread(target=run_yt_dlp)
        thread.start()

        # Poll logger every 0.5 seconds
        while not finished or self.logger.pop_lines():
            time.sleep(0.5)
            for line in self.logger.pop_lines():
                yield line

        yield "🎉 Done!"
    
    def get_subtitles(self):
        ydl_opts = {
            'skip_download': True,
            'writesubtitles': True,
            'logger': self.logger,
            'quiet': True,
            'outtmpl': self.output_filename_format,
        }

        if self.platform == "YouTube":
            ydl_opts['writeautomaticsub'] = True
        else:
            print('bili sub downloading')
            ydl_opts['cookiefile'] = self.cookie_path
            
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.video_url, download=False)
                subtitles = info.get('subtitles', {})
                auto_subtitles = info.get('automatic_captions', {})
                available_subs = list(subtitles.keys()) + list(auto_subtitles.keys())
                return available_subs
        except Exception as e:
            return ["Error fetching subtitles"]
        
    @staticmethod
    def convert_sub_to_txt(sub_path):
        txt_path = os.path.splitext(sub_path)[0] + ".txt"
        if sub_path.endswith('.vtt'):
            lines = [caption.text for caption in webvtt.read(sub_path)]
        elif sub_path.endswith('.srt'):
            subs = pysrt.open(sub_path)
            lines = [sub.text for sub in subs]
        else:
            return None  # unsupported format
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        return txt_path

    def download_subtitles(self, lang,convert_txt=False):
        print('🟢 begin sub download')
        ydl_opts = {
            'writeautomaticsub': True if self.platform == "YouTube" else False,
            'writesubtitles': True,
            'subtitlesformat': 'srt',
            'subtitleslangs': [lang],
            'skip_download': True,
            'logger': self.logger,
            'quiet': True,
            'outtmpl': self.output_filename_format
        }
        if self.platform == "YouTube":
            pass
        else:
            ydl_opts['cookiefile'] = self.cookie_path

        finished = False

        def run_yt_sub():
            nonlocal finished
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(self.video_url, download=False)
                    # print(info)
                    filename = ydl.prepare_filename(info)
                    # print(filename)
                    mainname = os.path.splitext(os.path.basename(filename))[0]
                    self.logger.push_line(f"预计下载文件名为：{mainname}")

                    ydl.download([self.video_url])
                    download_dir = self.root_dir
                    find_target = False
                    target_file_name = ''

                    for fn in os.listdir(download_dir):
                        if fn.startswith(mainname) and (fn.endswith('.srt') or fn.endswith('.vtt')):
                            self.logger.push_line(f"✅ 字幕下载成功:{mainname}")
                            find_target = True
                            target_file_path = os.path.join(download_dir,fn)

                    if not find_target:
                        self.logger.push_line(f"⚠️ 下载命令执行了，但未找到文件: {mainname}")
                        raise Exception('❌ Subtitles Download have issue, please debug!')
                    else:
                        if convert_txt:
                            print('🟢 Convert Sub to txt!')
                            self.logger.push_line(f"☕️ Converting subtitle to .txt!")
                            VideoFetcher.convert_sub_to_txt(target_file_path)
                            self.logger.push_line(f"✅ Convert to .txt Successfully!")
                        print('🟢 finish Sub download')
                        self.logger.push_line(f"✅ Subtitles for '{lang}': <{mainname}> downloaded successfully!")
            except Exception as e:
                self.logger.push_line(f"❌ Error: {str(e)}")
            finally:
                finished = True

        thread = threading.Thread(target=run_yt_sub)
        thread.start()

        # Poll logger every 0.5 seconds
        while not finished or self.logger.pop_lines():
            time.sleep(0.5)
            for line in self.logger.pop_lines():
                yield line

        yield "🎉 Sub Done!"
        
