import gradio as gr
import torch
from pathlib import Path
from omegaconf import OmegaConf
from datetime import datetime
import time
import argparse

from inference_audio import gpu_decorator, infer2
from inference_video import main as inference_video_main
from util import loop_video

# Paths for video processing
SUBMODULES_PATH = Path("submodules")
CONFIGS_PATH = Path(SUBMODULES_PATH, "LatentSync/configs")
UNET_CONFIG_PATH = Path(CONFIGS_PATH, "unet/stage2.yaml")
CHECKPOINT_PATH = Path("checkpoints/latentsync_unet.pt")
MASK_IMAGE_PATH = Path(SUBMODULES_PATH, "LatentSync/latentsync/utils/mask.png")

def measure_time(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"处理时间: {end_time - start_time:.2f} 秒")
        return result
    return wrapper

# Audio processing function
@gpu_decorator
def basic_tts(
    ref_audio_input,
    ref_text_input,
    gen_text_input,
    remove_silence,
    cross_fade_duration_slider,
    nfe_slider,
    speed_slider,
    progress=gr.Progress()
):
    if not ref_audio_input:
        gr.Warning("请提供参考音频。")
        return gr.update(), gr.update(), ref_text_input

    if not gen_text_input.strip():
        gr.Warning("请输入要生成的文本。")
        return gr.update(), gr.update(), ref_text_input
    
    try:
        progress(0.1, desc="开始生成音频...")
        audio_out, spectrogram_path, ref_text_out = infer2(
            ref_audio_input,
            ref_text_input,
            gen_text_input,
            "F5-TTS",
            remove_silence,
            cross_fade_duration=cross_fade_duration_slider,
            nfe_step=nfe_slider,
            speed=speed_slider,
            show_info=gr.Info,
            progress=progress
        )
        progress(1.0, desc="音频生成完成")
        print(f"音频已保存至: {audio_out}")
        return audio_out, ref_text_out
    except Exception as e:
        print(f"处理音频时出错: {str(e)}")
        raise gr.Error(f"处理音频时出错: {str(e)}")
    finally:
        torch.cuda.empty_cache()

# Video processing function
@measure_time
def process_video(
    video_path,
    audio_path,
    guidance_scale,
    inference_steps,
    seed,
    progress=gr.Progress()
):
    output_dir = Path("output")
    output_dir.mkdir(parents=True, exist_ok=True)

    video_file_path = Path(video_path)
    video_path = video_file_path.absolute().as_posix()
    audio_path = Path(audio_path).absolute().as_posix()

    prepared_video_path = video_file_path.with_stem(video_file_path.stem + "_prepared").absolute().as_posix()
    loop_video(audio_path, video_path, prepared_video_path)

    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = str(output_dir / f"{video_file_path.stem}_{current_time}.mp4")

    config = OmegaConf.load(UNET_CONFIG_PATH)
    config["run"].update(
        {
            "guidance_scale": guidance_scale,
            "inference_steps": inference_steps,
        }
    )

    args = create_args(prepared_video_path, audio_path, output_path, inference_steps, guidance_scale, seed)

    try:
        progress(0.4, desc="开始处理视频...")
        inference_video_main(config=config, args=args)
        progress(1.0, desc="视频处理完成")
        print("视频处理完成。")
        return output_path
    except Exception as e:
        print(f"处理视频时出错: {str(e)}")
        raise gr.Error(f"处理视频时出错: {str(e)}")
    finally:
        torch.cuda.empty_cache()

def create_args(video_path, audio_path, output_path, inference_steps, guidance_scale, seed):
    parser = argparse.ArgumentParser()
    parser.add_argument("--configs_path", type=str, required=True)
    parser.add_argument("--inference_ckpt_path", type=str, required=True)
    parser.add_argument("--video_path", type=str, required=True)
    parser.add_argument("--audio_path", type=str, required=True)
    parser.add_argument("--mask_image_path", type=str, required=True)
    parser.add_argument("--video_out_path", type=str, required=True)
    parser.add_argument("--inference_steps", type=int, default=20)
    parser.add_argument("--guidance_scale", type=float, default=1.0)
    parser.add_argument("--seed", type=int, default=1247)

    return parser.parse_args(
        [
            "--configs_path", CONFIGS_PATH.absolute().as_posix(),
            "--inference_ckpt_path", CHECKPOINT_PATH.absolute().as_posix(),
            "--video_path", video_path,
            "--audio_path", audio_path,
            "--mask_image_path", MASK_IMAGE_PATH.absolute().as_posix(),
            "--video_out_path", output_path,
            "--inference_steps", str(inference_steps),
            "--guidance_scale", str(guidance_scale),
            "--seed", str(seed),
        ]
    )

# Create Gradio interface
with gr.Blocks(title="AvatarX", fill_width=True) as app:
    gr.Markdown(
    """
    <h1 align="center">AvatarX</h1>
    <div style="display:flex;justify-content:center;column-gap:4px;">
        <a href="https://github.com/bestilyq/AvatarX">
            <img src='https://img.shields.io/badge/GitHub-Repo-blue'>
        </a> 
        <a href="https://arxiv.org/abs/2412.09262">
            <img src='https://img.shields.io/badge/arXiv-Paper-red'>
        </a>
    </div>
    <h2 align="center">A digital human built with LatentSync and F5-TTS</h2>
    """
    )
    
    with gr.Row():            
        # Video processing column
        with gr.Column():
            video_input = gr.Video(label="输入视频", height="74vh")
            
            with gr.Accordion("生成视频设置", open=False):
                guidance_scale = gr.Slider(
                    label="引导尺度",
                    minimum=1.0,
                    maximum=3.0,
                    value=2.0,
                    step=0.5,
                )
                inference_steps = gr.Slider(
                    label="推理步数",
                    minimum=10,
                    maximum=50,
                    value=20,
                    step=1,
                )
                seed = gr.Number(
                    label="随机种子",
                    value=1247,
                    precision=0,
                )

        # Audio processing column
        with gr.Column():
            ref_audio_input = gr.Audio(label="参考音频", type="filepath")
            gen_text_input = gr.Textbox(label="输入文本", lines=30)
            
            with gr.Accordion("生成音频设置", open=False):
                ref_text_input = gr.Textbox(
                    label="参考文本",
                    info="留空以自动转录参考音频。输入文本将覆盖自动转录。",
                    lines=2,
                )
                remove_silence = gr.Checkbox(
                    label="移除静音",
                    info="模型可能在较长音频中产生静音。如需移除静音可启用此选项。注意：此为实验性功能，可能产生意外结果，且会增加生成时间。",
                    value=False,
                )
                speed_slider = gr.Slider(
                    label="音频速度",
                    minimum=0.3,
                    maximum=2.0,
                    value=1.0,
                    step=0.1,
                )
                nfe_slider = gr.Slider(
                    label="降噪步数",
                    minimum=4,
                    maximum=64,
                    value=32,
                    step=2,
                )
                cross_fade_duration_slider = gr.Slider(
                    label="交叉淡化时长 (秒)",
                    minimum=0.0,
                    maximum=1.0,
                    value=0.15,
                    step=0.01,
                )

            generated_audio = gr.Audio(label="合成的音频", type="filepath", visible=False)

        with gr.Column():
            video_output = gr.Video(label="输出视频", height="74vh")
            generate_Video_btn = gr.Button("生成视频", variant="primary")

    # Configure queue
    app.queue(
        default_concurrency_limit=1,
        max_size=10
    )

    # Bind video generation button
    generate_Video_btn.click(
        fn=basic_tts,
        inputs=[
            ref_audio_input,
            ref_text_input,
            gen_text_input,
            remove_silence,
            cross_fade_duration_slider,
            nfe_slider,
            speed_slider,
        ],
        outputs=[generated_audio, ref_text_input],
        queue=True
    ).success(
        fn=process_video,
        inputs=[
            video_input,
            generated_audio,
            guidance_scale,
            inference_steps,
            seed,
        ],
        outputs=video_output,
        queue=True
    )

if __name__ == "__main__":
    app.launch(inbrowser=True, share=True)