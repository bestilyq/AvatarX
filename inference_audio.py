# ruff: noqa: E402
# Above allows ruff to ignore E402: module level import not at top of file

import json
from pathlib import Path
import re
import tempfile

import librosa
import numpy as np
import soundfile as sf
import torch
import torchaudio
from cached_path import cached_path
from pydub import AudioSegment
import tqdm

try:
    import spaces

    USING_SPACES = True
except ImportError:
    USING_SPACES = False


def gpu_decorator(func):
    if USING_SPACES:
        return spaces.GPU(func)
    else:
        return func


from f5_tts.model import DiT, UNetT
from f5_tts.infer.utils_infer import (
    load_vocoder,
    load_model,
    preprocess_ref_audio_text,
    infer_process,
    remove_silence_for_generated_wav,
    save_spectrogram,
)


DEFAULT_TTS_MODEL = "F5-TTS_v1"
tts_model_choice = DEFAULT_TTS_MODEL

DEFAULT_TTS_MODEL_CFG = [
    "hf://SWivid/F5-TTS/F5TTS_v1_Base/model_1250000.safetensors",
    "hf://SWivid/F5-TTS/F5TTS_v1_Base/vocab.txt",
    json.dumps(dict(dim=1024, depth=22, heads=16, ff_mult=2, text_dim=512, conv_layers=4)),
]


# load models
def load_f5tts():
    ckpt_path = str(cached_path(DEFAULT_TTS_MODEL_CFG[0]))
    F5TTS_model_cfg = json.loads(DEFAULT_TTS_MODEL_CFG[2])
    return load_model(DiT, F5TTS_model_cfg, ckpt_path)

# 文本分段函数
def split_text(text, max_len=150):
    sentences = re.split(r'[。！？.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    segments = []
    current_segment = ""
    for sentence in sentences:
        if len(current_segment) + len(sentence) <= max_len:
            current_segment += sentence + "。"
        else:
            if current_segment:
                segments.append(current_segment)
            current_segment = sentence + "。"
    if current_segment:
        segments.append(current_segment)
    return segments

# 合并音频函数
def merge_audio_with_crossfade(audio_files, crossfade_ms=50):
    merged = AudioSegment.from_wav(audio_files[0])
    for audio_file in audio_files[1:]:
        next_audio = AudioSegment.from_wav(audio_file)
        merged = merged.append(next_audio, crossfade=crossfade_ms)
    return merged

@gpu_decorator
def infer(
    ref_audio_orig,
    ref_text,
    gen_text,
    model,
    remove_silence,
    cross_fade_duration=0.15,
    nfe_step=32,
    speed=1,
    show_info=print,
    progress=tqdm
):
    ref_audio, ref_text = preprocess_ref_audio_text(ref_audio_orig, ref_text, show_info=show_info)

    vocoder = load_vocoder()
    ema_model = load_f5tts()
    final_wave, final_sample_rate, combined_spectrogram = infer_process(
        ref_audio,
        ref_text,
        gen_text,
        ema_model,
        vocoder,
        cross_fade_duration=cross_fade_duration,
        nfe_step=nfe_step,
        speed=speed,
        show_info=show_info,
        progress=progress,
    )

    # Remove silence
    if remove_silence:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
            sf.write(f.name, final_wave, final_sample_rate)
            remove_silence_for_generated_wav(f.name)
            final_wave, _ = torchaudio.load(f.name)
        final_wave = final_wave.squeeze().cpu().numpy()

    # Save the spectrogram
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_spectrogram:
        spectrogram_path = tmp_spectrogram.name
        save_spectrogram(combined_spectrogram, spectrogram_path)

    return (final_sample_rate, final_wave), spectrogram_path, ref_text

@gpu_decorator
def infer2(
    ref_audio_orig,
    ref_text,
    gen_text,
    model,
    remove_silence,
    cross_fade_duration=0.15,
    nfe_step=32,
    speed=1,
    show_info=print,
    progress=tqdm
):
    # Create the temp directory if it doesn't exist
    output_dir = Path("output")
    output_dir.mkdir(parents=True, exist_ok=True)
    temp_dir = Path(output_dir, "temp")
    temp_dir.mkdir(parents=True, exist_ok=True)

    ref_audio, ref_text = preprocess_ref_audio_text(ref_audio_orig, ref_text, show_info=show_info)

    vocoder = load_vocoder()
    ema_model = load_f5tts()

    # 分段
    segments = split_text(gen_text)

    # 生成音频片段
    audio_files = []
    spectrograms = []
    for i, text_segment in enumerate(segments):
        with torch.no_grad():
            wave, sampling_rate, spectrogram = infer_process(
                ref_audio,
                ref_text,
                text_segment,
                ema_model,
                vocoder,
                cross_fade_duration=cross_fade_duration,
                nfe_step=nfe_step,
                speed=speed,
                show_info=show_info,
                progress=progress,
            )
        temp_file = Path(temp_dir, f"temp_{i}.wav").absolute().as_posix()
        sf.write(temp_file, wave, sampling_rate)
        audio_files.append(temp_file)
        spectrograms.append(spectrogram)
        print(f"生成第 {i+1} 段音频")

    # 合并音频
    merged_audio_path = Path(temp_dir, "output_long_crossfade.wav").absolute().as_posix()
    merged_audio = merge_audio_with_crossfade(audio_files)
    merged_audio.export(merged_audio_path, format="wav")

    # 音量归一化
    final_audio, _ = librosa.load(merged_audio_path, sr=sampling_rate)
    final_audio = librosa.util.normalize(final_audio)
    final_audio_path = Path(temp_dir, "output_long_final.wav").absolute().as_posix()
    sf.write(final_audio_path, final_audio, sampling_rate)

    final_wave = final_audio
    final_sample_rate = sampling_rate
    combined_spectrogram = np.concatenate(spectrograms, axis=1)
    # Remove silence
    if remove_silence:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
            sf.write(f.name, final_wave, final_sample_rate)
            remove_silence_for_generated_wav(f.name)
            final_wave, _ = torchaudio.load(f.name)
        final_wave = final_wave.squeeze().cpu().numpy()

    # Save the spectrogram
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_spectrogram:
        spectrogram_path = tmp_spectrogram.name
        save_spectrogram(combined_spectrogram, spectrogram_path)

    return (final_sample_rate, final_wave), spectrogram_path, ref_text
