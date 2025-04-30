# ruff: noqa: E402
# Above allows ruff to ignore E402: module level import not at top of file

import gradio as gr
import torch

from inference_audio import gpu_decorator, infer2


with gr.Blocks() as app_tts:
    ref_audio_input = gr.Audio(label="Reference Audio", type="filepath")
    gen_text_input = gr.Textbox(label="Text to Generate", lines=10)
    generate_btn = gr.Button("Synthesize", variant="primary")
    with gr.Accordion("Advanced Settings", open=False):
        ref_text_input = gr.Textbox(
            label="Reference Text",
            info="Leave blank to automatically transcribe the reference audio. If you enter text it will override automatic transcription.",
            lines=2,
        )
        remove_silence = gr.Checkbox(
            label="Remove Silences",
            info="The model tends to produce silences, especially on longer audio. We can manually remove silences if needed. Note that this is an experimental feature and may produce strange results. This will also increase generation time.",
            value=False,
        )
        speed_slider = gr.Slider(
            label="Speed",
            minimum=0.3,
            maximum=2.0,
            value=1.0,
            step=0.1,
            info="Adjust the speed of the audio.",
        )
        nfe_slider = gr.Slider(
            label="NFE Steps",
            minimum=4,
            maximum=64,
            value=32,
            step=2,
            info="Set the number of denoising steps.",
        )
        cross_fade_duration_slider = gr.Slider(
            label="Cross-Fade Duration (s)",
            minimum=0.0,
            maximum=1.0,
            value=0.15,
            step=0.01,
            info="Set the duration of the cross-fade between audio clips.",
        )

    audio_output = gr.Audio(label="Synthesized Audio")
    spectrogram_output = gr.Image(label="Spectrogram")

    @gpu_decorator
    def basic_tts(
        ref_audio_input,
        ref_text_input,
        gen_text_input,
        remove_silence,
        cross_fade_duration_slider,
        nfe_slider,
        speed_slider,
    ):
        if not ref_audio_input:
            gr.Warning("Please provide reference audio.")
            return gr.update(), gr.update(), ref_text_input

        if not gen_text_input.strip():
            gr.Warning("Please enter text to generate.")
            return gr.update(), gr.update(), ref_text_input
    
        try:
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
                progress=gr.Progress()
            )
            return audio_out, spectrogram_path, ref_text_out
        except Exception as e:
            print(f"Error during processing: {str(e)}")
            raise gr.Error(f"Error during processing: {str(e)}")
        finally:
            torch.cuda.empty_cache()

    generate_btn.click(
        basic_tts,
        inputs=[
            ref_audio_input,
            ref_text_input,
            gen_text_input,
            remove_silence,
            cross_fade_duration_slider,
            nfe_slider,
            speed_slider,
        ],
        outputs=[audio_output, spectrogram_output, ref_text_input],
    )

if __name__ == "__main__":
    app_tts.launch(inbrowser=True, share=True)
