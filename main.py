import sys
import argparse
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QSlider, QFileDialog, QSpinBox, QGroupBox, 
                             QFrame, QSizePolicy, QMessageBox)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QIcon
from pathlib import Path
from omegaconf import OmegaConf
from datetime import datetime

import inference

CONFIG_PATH = Path("configs/unet/stage2.yaml")
CHECKPOINT_PATH = Path("checkpoints/latentsync_unet.pt")

def create_args(
    video_path: str, audio_path: str, output_path: str, inference_steps: int, guidance_scale: float, seed: int
) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--inference_ckpt_path", type=str, required=True)
    parser.add_argument("--video_path", type=str, required=True)
    parser.add_argument("--audio_path", type=str, required=True)
    parser.add_argument("--video_out_path", type=str, required=True)
    parser.add_argument("--inference_steps", type=int, default=20)
    parser.add_argument("--guidance_scale", type=float, default=1.0)
    parser.add_argument("--seed", type=int, default=1247)

    return parser.parse_args(
        [
            "--inference_ckpt_path",
            CHECKPOINT_PATH.absolute().as_posix(),
            "--video_path",
            video_path,
            "--audio_path",
            audio_path,
            "--video_out_path",
            output_path,
            "--inference_steps",
            str(inference_steps),
            "--guidance_scale",
            str(guidance_scale),
            "--seed",
            str(seed),
        ]
    )

class LatentSyncApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(640, 480)
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f5f7;
                color: #333333;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QLabel {
                font-size: 12px;
                padding: 5px;
            }
            QPushButton {
                background-color: #4a86e8;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3a76d8;
            }
            QPushButton:pressed {
                background-color: #2a66c8;
            }
            QSlider {
                height: 30px;
            }
            QSlider::groove:horizontal {
                border: 1px solid #999999;
                height: 8px;
                background: #cccccc;
                margin: 2px 0;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #4a86e8;
                border: 1px solid #5c5c5c;
                width: 18px;
                margin: -8px 0;
                border-radius: 9px;
            }
            QSlider::handle:horizontal:hover {
                background: #3a76d8;
            }
            QGroupBox {
                border: 1px solid #cccccc;
                border-radius: 6px;
                margin-top: 12px;
                padding-top: 10px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 5px;
            }
            QSpinBox {
                padding: 5px;
                border: 1px solid #cccccc;
                border-radius: 4px;
                height: 30px;
                background-color: #ffffff;
                font-size: 12px;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                width: 20px;
                border: none;
                background-color: #e6e6e6;
                border-radius: 2px;
            }
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {
                background-color: #d9d9d9;
            }
            QSpinBox::up-button:pressed, QSpinBox::down-button:pressed {
                background-color: #cccccc;
            }
            QSpinBox::up-arrow {
                image: url(data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24"><path fill="#555555" d="M7 14l5-5 5 5z"/></svg>);
                width: 16px;
                height: 16px;
            }
            QSpinBox::down-arrow {
                image: url(data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24"><path fill="#555555" d="M7 10l5 5 5-5z"/></svg>);
                width: 16px;
                height: 16px;
            }
        """)
        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title_label = QLabel("LatentSync Video Processing")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #333333; margin-bottom: 10px;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Input section
        input_group = QGroupBox("Input Files")
        input_layout = QVBoxLayout()
        input_layout.setSpacing(10)
        
        # Video input
        video_layout = QHBoxLayout()
        self.video_label = QLabel("Input Video: Not selected")
        self.video_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.video_button = QPushButton("Select Video")
        video_layout.addWidget(self.video_label)
        video_layout.addWidget(self.video_button)
        self.video_button.clicked.connect(self.select_video)
        input_layout.addLayout(video_layout)
        
        # Audio input
        audio_layout = QHBoxLayout()
        self.audio_label = QLabel("Input Audio: Not selected")
        self.audio_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.audio_button = QPushButton("Select Audio")
        audio_layout.addWidget(self.audio_label)
        audio_layout.addWidget(self.audio_button)
        self.audio_button.clicked.connect(self.select_audio)
        input_layout.addLayout(audio_layout)
        
        input_group.setLayout(input_layout)
        main_layout.addWidget(input_group)
        
        # Parameters section
        params_group = QGroupBox("Processing Parameters")
        params_layout = QVBoxLayout()
        params_layout.setSpacing(10)
        
        # Guidance scale
        guidance_layout = QVBoxLayout()
        guidance_header = QHBoxLayout()
        guidance_label = QLabel("Guidance Scale:")
        guidance_value = QLabel("1.5")
        guidance_header.addWidget(guidance_label)
        guidance_header.addWidget(guidance_value)
        guidance_layout.addLayout(guidance_header)
        
        self.guidance_scale_slider = QSlider(Qt.Orientation.Horizontal)
        self.guidance_scale_slider.setMinimum(10)
        self.guidance_scale_slider.setMaximum(25)
        self.guidance_scale_slider.setValue(15)
        self.guidance_scale_slider.setTickInterval(5)
        self.guidance_scale_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.guidance_scale_slider.valueChanged.connect(lambda v: guidance_value.setText(str(v/10.0)))
        guidance_layout.addWidget(self.guidance_scale_slider)
        params_layout.addLayout(guidance_layout)
        
        # Inference steps
        inference_layout = QVBoxLayout()
        inference_header = QHBoxLayout()
        inference_label = QLabel("Inference Steps:")
        inference_value = QLabel("20")
        inference_header.addWidget(inference_label)
        inference_header.addWidget(inference_value)
        inference_layout.addLayout(inference_header)
        
        self.inference_steps_slider = QSlider(Qt.Orientation.Horizontal)
        self.inference_steps_slider.setMinimum(10)
        self.inference_steps_slider.setMaximum(50)
        self.inference_steps_slider.setValue(20)
        self.inference_steps_slider.setTickInterval(5)
        self.inference_steps_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.inference_steps_slider.valueChanged.connect(lambda v: inference_value.setText(str(v)))
        inference_layout.addWidget(self.inference_steps_slider)
        params_layout.addLayout(inference_layout)
        
        # Random seed
        seed_layout = QHBoxLayout()
        seed_label = QLabel("Random Seed:")
        self.seed_spinbox = QSpinBox()
        self.seed_spinbox.setMinimum(100)
        self.seed_spinbox.setMaximum(10000)
        self.seed_spinbox.setValue(1247)
        self.seed_spinbox.setFixedHeight(30)
        seed_layout.addWidget(seed_label)
        seed_layout.addWidget(self.seed_spinbox)
        params_layout.addLayout(seed_layout)
        
        params_group.setLayout(params_layout)
        main_layout.addWidget(params_group)
        
        # Process button
        self.process_button = QPushButton("Process Video")
        self.process_button.setFixedHeight(40)
        self.process_button.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                background-color: #4a86e8;
            }
        """)
        self.process_button.clicked.connect(self.process_video)
        main_layout.addWidget(self.process_button)
        
        # Status indicator
        self.status_label = QLabel("Ready")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: #666666; font-style: italic;")
        main_layout.addWidget(self.status_label)
        
        self.setLayout(main_layout)
        self.setWindowTitle("LatentSync Video Processing")

    def select_video(self):
        file_dialog = QFileDialog()
        video_path, _ = file_dialog.getOpenFileName(self, "Select Video File")
        if video_path:
            self.video_label.setText(f"Input Video: {video_path}")
            self.video_path = video_path

    def select_audio(self):
        file_dialog = QFileDialog()
        audio_path, _ = file_dialog.getOpenFileName(self, "Select Audio File")
        if audio_path:
            self.audio_label.setText(f"Input Audio: {audio_path}")
            self.audio_path = audio_path

    def process_video(self):
        video_path = getattr(self, 'video_path', None)
        audio_path = getattr(self, 'audio_path', None)
        guidance_scale = self.guidance_scale_slider.value() / 10.0
        inference_steps = self.inference_steps_slider.value()
        seed = self.seed_spinbox.value()

        if not video_path or not audio_path:
            self.status_label.setText("Error: Please select both video and audio files")
            self.status_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
            return
            
        self.status_label.setText("Processing... Please wait")
        self.status_label.setStyleSheet("color: #3498db; font-weight: bold;")
        QApplication.processEvents()

        output_dir = Path("./temp")
        output_dir.mkdir(parents=True, exist_ok=True)

        video_file_path = Path(video_path)
        video_path = video_file_path.absolute().as_posix()
        audio_path = Path(audio_path).absolute().as_posix()

        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = str(output_dir / f"{video_file_path.stem}_{current_time}.mp4")

        config = OmegaConf.load(CONFIG_PATH)

        config["run"].update(
            {
                "guidance_scale": guidance_scale,
                "inference_steps": inference_steps,
            }
        )

        args = create_args(video_path, audio_path, output_path, inference_steps, guidance_scale, seed)

        try:
            inference.main(
                config=config,
                args=args,
            )
            self.status_label.setText(f"Processing completed successfully. Output saved to: {output_path}")
            self.status_label.setStyleSheet("color: #27ae60; font-weight: bold;")
            QMessageBox.information(self, "Processing Complete", f"Video processed successfully!\nSaved to: {output_path}")
        except Exception as e:
            error_msg = str(e)
            self.status_label.setText(f"Error: {error_msg}")
            self.status_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
            QMessageBox.critical(self, "Processing Error", f"An error occurred during processing:\n{error_msg}")
            print(f"Error during processing: {error_msg}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = LatentSyncApp()
    ex.show()
    sys.exit(app.exec())
