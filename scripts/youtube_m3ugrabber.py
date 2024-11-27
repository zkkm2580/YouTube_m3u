import requests
import os
import sys
import platform
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)

# 输出的 Banner
banner = r'''
#########################################################################
#      ____            _           _   __  __                           #
#     |  _ \ _ __ ___ (_) ___  ___| |_|  \/  | ___   ___  ___  ___      #
#     | |_) | '__/ _ \| |/ _ \/ __| __| |\/| |/ _ \ / _ \/ __|/ _ \     #
#     |  __/| | | (_) | |  __/ (__| |_| |  | | (_) | (_) \__ \  __/     #
#     |_|   |_|  \___// |\___|\___|\__|_|  |_|\___/ \___/|___/\___|     #
#                   |__/                                                #
#                                  >> https://github.com/benmoose39     #
#########################################################################
'''

# 获取操作系统类型
def get_platform():
    system = platform.system().lower()
    if system == 'windows':
        return True
    elif system in ['linux', 'darwin']:
        return False
    return False

# 检查响应中是否包含 .m3u8
def contains_m3u8(response_text):
    return '.m3u8' in response_text

# 提取 .m3u8 链接
def extract_m3u8_link(response):
    end = response.find('.m3u8') + 5
    tuner = 100
    while True:
        if 'https://' in response[end-tuner : end]:
            link = response[end-tuner : end]
            start = link.find('https://')
            end = link.find('.m3u8') + 5
            return link[start : end]
        else:
            tuner += 5
    return None

# 从 URL 获取 .m3u8 链接
def grab(url, windows):
    try:
        response = requests.get(url, timeout=15).text
        if not contains_m3u8(response):
            if windows:
                logging.info("没有找到有效的 m3u8，使用默认备选链接")
                print('https://raw.githubusercontent.com/zkkm2580/YouTube_m3u/main/assets/moose_na.m3u')
                return
            # 使用 curl 命令下载内容并读取
            os.system(f'curl "{url}" > temp.txt')
            with open('temp.txt', 'r') as temp_file:
                response = temp_file.read()
            if not contains_m3u8(response):
                logging.info("没有找到有效的 m3u8，使用默认备选链接")
                print('https://raw.githubusercontent.com/zkkm2580/YouTube_m3u/main/assets/moose_na.m3u')
                return
        link = extract_m3u8_link(response)
        if link:
            print(link)
    except requests.exceptions.RequestException as e:
        logging.error(f"请求失败: {e}")

# 清理临时文件
def clean_up():
    if os.path.exists('temp.txt'):
        os.remove('temp.txt')
    if any(file.startswith('watch') for file in os.listdir()):
        for file in os.listdir():
            if file.startswith('watch'):
                os.remove(file)

# 主程序
def main():
    windows = get_platform()

    # 打印 M3U 头部
    print('#EXTM3U x-tvg-url="https://github.com/botallen/epg/releases/download/latest/epg.xml"')
    print(banner)

    # 读取频道信息文件
    file_path = os.path.join(os.path.dirname(__file__), 'youtube_channel_info.txt')
    try:
        with open(file_path) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('~~'):
                    continue
                if line.startswith('https:'):
                    grab(line, windows)
                else:
                    parts = line.split('|')
                    if len(parts) == 4:
                        ch_name, grp_title, tvg_logo, tvg_id = [part.strip() for part in parts]
                        print(f'\n#EXTINF:-1 group-title="{grp_title.title()}" tvg-logo="{tvg_logo}" tvg-id="{tvg_id}", {ch_name}')
    except FileNotFoundError:
        logging.error(f"文件 {file_path} 未找到！")
    
    # 清理临时文件
    clean_up()

if __name__ == "__main__":
    main()
