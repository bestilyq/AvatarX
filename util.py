import math
import ffmpeg
import subprocess
import os

def get_duration(path):
    """获取文件的时长（秒）"""
    """获取音视频文件时长（秒）"""
    probe = ffmpeg.probe(path)
    for stream in probe['streams']:
        if stream['codec_type'] in ('audio', 'video'):
            return float(stream['duration'])
    raise ValueError(f"Cannot determine duration of {path}")

def create_looped_video(video_path, target_duration, output_path):
    """创建循环视频（正放+倒放）以匹配音频时长"""
    try:
        # 获取视频时长
        video_duration = get_duration(video_path)
        
        # 计算需要循环的次数（正放+倒放算一次循环）
        loops_needed = math.ceil(target_duration / (2 * video_duration))
        
        # 步骤 1：生成中间文件
        file_dir = os.path.dirname(video_path)
        file_name = os.path.basename(video_path)
        file_base, file_ext = os.path.splitext(file_name)
        forward_file = os.path.join(file_dir, f"{file_base}_forward{file_ext}")
        reverse_file = os.path.join(file_dir, f"{file_base}_reverse{file_ext}")

        # 生成正放视频
        cmd_forward = [
            'ffmpeg', '-i', video_path,
            '-c:v', 'copy',
            '-an',
            '-y',
            forward_file
        ]
        subprocess.run(cmd_forward, capture_output=True, text=True, check=True)

        # 生成倒放视频
        cmd_reverse = [
            'ffmpeg', '-i', video_path,
            '-vf', 'reverse',
            '-c:v', 'libx264',
            '-preset', 'fast',
            '-an',
            '-y',
            reverse_file
        ]
        subprocess.run(cmd_reverse, capture_output=True, text=True, check=True)

        # 步骤 2：创建 concat 文本文件
        concat_list_file = 'concat_list.txt'
        with open(concat_list_file, 'w') as f:
            for _ in range(loops_needed):
                f.write(f"file '{forward_file}'\n")
                f.write(f"file '{reverse_file}'\n")

        # 步骤 3：拼接视频
        cmd_concat = [
            'ffmpeg', '-f', 'concat',
            '-safe', '0',  # 允许非标准路径
            '-i', concat_list_file,
            '-c:v', 'copy',
            '-an',
            '-map_metadata', '-1',
            '-y',
            output_path
        ]
        subprocess.run(cmd_concat, capture_output=True, text=True, check=True)

        # 步骤 4：清理临时文件
        os.remove(forward_file)
        os.remove(reverse_file)
        os.remove(concat_list_file)

        return output_path
    except ffmpeg.Error as e:
        print(f"An error occurred: {e.stderr.decode()}")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")

def loop_video(audio_path, video_path, output_path):
    """视频较短则将视频循环以达到音频长度"""
    try:
        # 获取音频和视频时长
        audio_duration = get_duration(audio_path)
        video_duration = get_duration(video_path)
        print(f"Audio duration: {audio_duration} seconds")
        print(f"Video duration: {video_duration} seconds")
        
        # 准备视频流
        if video_duration > audio_duration:
            # 视频较长，直接截断
            video_stream = ffmpeg.input(video_path, t=audio_duration).video
            output = ffmpeg.output(video_stream, output_path, vcodec='copy', format='mp4')
            output.run(overwrite_output=True)
        else:
            # 视频较短，创建循环视频
            create_looped_video(video_path, audio_duration, output_path)
        
        print(f"Successfully created {output_path}")
        
    except ffmpeg.Error as e:
        print(f"An error occurred: {e.stderr.decode()}")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")

def main():
    import argparse
    
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="Merge audio and video files with hardware acceleration")
    parser.add_argument('--video', required=True, help="Path to the input video file")
    parser.add_argument('--audio', required=True, help="Path to the input audio file")
    parser.add_argument('--output', required=True, help="Path to the output merged file")
    
    args = parser.parse_args()
    
    # 检查文件是否存在
    if not os.path.isfile(args.video):
        print(f"Error: Video file '{args.video}' does not exist")
        return
    if not os.path.isfile(args.audio):
        print(f"Error: Audio file '{args.audio}' does not exist")
        return
    
    loop_video(args.audio, args.video, args.output)

if __name__ == "__main__":
    main()