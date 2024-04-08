import os
import struct
import json
import math
import zipfile
import argparse

# 获取当前工作目录路径
current_dir = os.getcwd()

# 创建存放mcz文件的文件夹
mcz_folder = os.path.join(current_dir, "mczFile")
os.makedirs(mcz_folder, exist_ok=True)

# 解析命令行参数
parser = argparse.ArgumentParser()
parser.add_argument("refreshAll", help="Set to 'true' to refresh all .mcz files, default is 'false'", nargs='?', const='false')
args = parser.parse_args()

# 遍历文件夹
for foldername, subfolders, filenames in os.walk(current_dir):
    for filename in filenames:
        if filename.endswith(".imd"):
            print(f"Reading the folder: {foldername}")
            imd_file = os.path.join(foldername, filename)
            songinfo_file = os.path.join(foldername, "songinfo.txt")
            origin_file = os.path.join(current_dir, "origin.json")

            # 读取imd文件
            with open(imd_file, "rb") as file:
                imd_data = file.read()

            # 解析imd文件
            duration_time = struct.unpack("<I", imd_data[0:4])[0]
            bpm = struct.unpack("<d", imd_data[12:20])[0]

            # 读取songinfo.txt文件
            with open(songinfo_file, "r", encoding="utf-8") as file:
                songinfo_data = json.load(file)

            # 读取原始json文件
            with open(origin_file, "r", encoding="utf-8") as file:
                mc_info = json.load(file)

            # 更新歌曲信息中的值
            is_png_file = songinfo_data.get("isPngFile", False)
            if is_png_file:
                mc_info["meta"]["cover"] = f"{songinfo_data['id']}_title_ipad.png"
                mc_info["meta"]["background"] = f"{songinfo_data['id']}.png"
            else:
                mc_info["meta"]["cover"] = f"{songinfo_data['id']}.jpg"
                mc_info["meta"]["background"] = f"{songinfo_data['id']}.jpg"

            mc_info["meta"]["song"]["title"] = f"{songinfo_data['id']}"
            mc_info["meta"]["song"]["artist"] = songinfo_data["artist"]
            mc_info["meta"]["song"]["titleorg"] = songinfo_data["title"]
            mc_info["meta"]["song"]["file"] = f"{songinfo_data['id']}.mp3"
            mc_info["meta"]["song"]["bpm"] = bpm
            mc_info["note"][0]["beat"][0] = int(duration_time / (60000 / bpm))
            mc_info["note"][0]["beat"][1] = math.floor(((duration_time / (60000 / bpm)) % 1) * 4)
            mc_info["note"][0]["beat"][2] = 4
            mc_info["time"][0]["bpm"] = bpm
            mc_info["note"][2]["sound"] = f"{songinfo_data['id']}.mp3"

            for chartinfo in songinfo_data["charts"]:
                mc_info["meta"]["creator"] = chartinfo["chartDesigner"]
                mc_info["meta"]["version"] = f"{chartinfo['key']}K Hard Lv.{chartinfo['level']}"    

                # 保存更新后的歌曲信息为mc文件
                updated_file = os.path.join(foldername, f"{songinfo_data['id']}_{chartinfo['key']}k_{chartinfo['difficulty']}.mc")
                with open(updated_file, "w", encoding="utf-8") as file:
                    json.dump(mc_info, file, indent=4)
                print(f"    Create MC chart file: {songinfo_data['id']}_{chartinfo['key']}k_{chartinfo['difficulty']}")

            # 压缩文件夹中的相关文件为mcz文件
            zipped_file = os.path.join(mcz_folder, f"{songinfo_data['id']}.mcz")
            if args.refreshAll == 'true' or not os.path.exists(zipped_file):
                with zipfile.ZipFile(zipped_file, 'w') as zipf:
                    for root, dirs, files in os.walk(foldername):
                        for file in files:
                            if file.endswith(('.mp3', '.imd', '.png', '.jpg', '.mc')):
                                zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), foldername))
                print(f"    Create MCZ file: {songinfo_data['id']}")
            else:
                print(f"    Ignore: {songinfo_data['id']}")

print("Success.")