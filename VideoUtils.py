import time
import os
import glob

class VideoUtils:
    def __init__(self):
        pass

    @staticmethod
    def format_time_ago(timestamp):
        now = time.time()
        diff = int(now - timestamp)
        if diff < 60:
            return f"{diff} 秒前"
        elif diff < 3600:
            return f"{diff // 60} 分钟前"
        elif diff < 86400:
            return f"{diff // 3600} 小时前"
        else:
            return f"{diff // 86400} 天前"
        
    @staticmethod
    def get_latest_video_file(root_dir=None):
        if root_dir:
            tmp_root = root_dir
        else:
            tmp_root = None
        video_extensions = ['*.mp4', '*.mov', '*.avi', '*.mkv','*.webm']
        files = []
        for ext in video_extensions:
            files.extend(glob.glob(ext,root_dir=tmp_root))  # 查找所有匹配的扩展名
        if not files:
            return None, None
        
        if root_dir:
            files = [os.path.join(tmp_root,i) for i in files]
        latest_file = ''
        latest_file_time = ''

        latest_file = max(files, key=os.path.getmtime)
        latest_file_time =  VideoUtils.format_time_ago(os.path.getmtime(latest_file))
        print(tmp_root)
        print(latest_file)
        print(latest_file_time)
        return latest_file,latest_file_time