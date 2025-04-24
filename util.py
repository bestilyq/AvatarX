import ffmpeg

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
    # 获取视频时长
    video_duration = get_duration(video_path)
    
    # 计算需要循环的次数（正放+倒放算一次循环）
    loops_needed = int(target_duration / (2 * video_duration)) + 1
    
    # 创建正放和倒放的视频流
    stream = ffmpeg.input(video_path)
    forward = stream
    reverse = stream.filter('reverse')
    
    # 交替正放和倒放
    concat_streams = []
    for _ in range(loops_needed):
        concat_streams.extend([forward, reverse])
    
    # 拼接视频流
    concat = ffmpeg.concat(*concat_streams, v=1, a=0)
    
    # 裁剪到音频时长
    concat = concat.filter('trim', duration=target_duration)
    
    # 输出临时循环视频
    ffmpeg.output(concat, output_path).run(overwrite_output=True)
    return output_path

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
    import os
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