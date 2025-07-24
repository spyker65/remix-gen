import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QFileDialog, QPushButton,
    QLabel, QSlider, QHBoxLayout, QLineEdit
)
from PyQt5.QtCore import Qt
from pydub import AudioSegment

class MusicRemixApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Music Remix Tool")
        self.setGeometry(100, 100, 600, 300)
        self.audio = None
        self.processed_audio = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Load Button
        self.load_button = QPushButton("Load Audio File")
        self.load_button.clicked.connect(self.load_audio)
        layout.addWidget(self.load_button)

        # Labels
        self.file_label = QLabel("No file loaded.")
        layout.addWidget(self.file_label)

        # Sliders for effects
        # Tempo (speed up / slow down)
        tempo_layout = QHBoxLayout()
        tempo_label = QLabel("Tempo (speed x):")
        self.tempo_slider = QSlider(Qt.Horizontal)
        self.tempo_slider.setMinimum(50)
        self.tempo_slider.setMaximum(150)
        self.tempo_slider.setValue(100)
        self.tempo_slider.valueChanged.connect(self.update_preview)
        tempo_layout.addWidget(tempo_label)
        tempo_layout.addWidget(self.tempo_slider)
        layout.addLayout(tempo_layout)

        # Pitch shift (semitones)
        pitch_layout = QHBoxLayout()
        pitch_label = QLabel("Pitch (semitones):")
        self.pitch_input = QLineEdit("0")
        self.pitch_input.textChanged.connect(self.update_preview)
        pitch_layout.addWidget(pitch_label)
        pitch_layout.addWidget(self.pitch_input)
        layout.addLayout(pitch_layout)

        # Volume Adjustment
        volume_layout = QHBoxLayout()
        volume_label = QLabel("Volume (dB):")
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setMinimum(-20)
        self.volume_slider.setMaximum(20)
        self.volume_slider.setValue(0)
        self.volume_slider.valueChanged.connect(self.update_preview)
        volume_layout.addWidget(volume_label)
        volume_layout.addWidget(self.volume_slider)
        layout.addLayout(volume_layout)

        # Buttons for actions
        buttons_layout = QHBoxLayout()
        self.preview_button = QPushButton("Preview Remix")
        self.preview_button.clicked.connect(self.apply_effects)
        self.save_button = QPushButton("Save Remix")
        self.save_button.clicked.connect(self.save_audio)
        buttons_layout.addWidget(self.preview_button)
        buttons_layout.addWidget(self.save_button)
        layout.addLayout(buttons_layout)

        self.setLayout(layout)

    def load_audio(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open Audio File", "", "Audio Files (*.mp3 *.wav *.flac)")
        if filename:
            self.audio = AudioSegment.from_file(filename)
            self.file_label.setText(f"Loaded: {filename}")
            self.processed_audio = self.audio
        else:
            self.file_label.setText("No file loaded.")

    def update_preview(self):
        if self.audio:
            self.apply_effects(preview=True)

    def apply_effects(self, preview=False):
        if not self.audio:
            return

        # Get effect parameters
        speed_change = self.tempo_slider.value() / 100.0
        try:
            pitch_semitones = float(self.pitch_input.text())
        except ValueError:
            pitch_semitones = 0
        volume_change = self.volume_slider.value()

        # Apply tempo change
        new_audio = self.audio.speedup(playback_speed=speed_change)

        # Apply pitch shift
        # pydub doesn't have built-in pitch shifting, but for simplicity, we can change frame rate
        new_sample_rate = int(new_audio.frame_rate * (2.0 ** (pitch_semitones / 12.0)))
        new_audio = new_audio._spawn(new_audio.raw_data, overrides={'frame_rate': new_sample_rate})
        new_audio = new_audio.set_frame_rate(self.audio.frame_rate)

        # Apply volume change
        new_audio = new_audio + volume_change

        self.processed_audio = new_audio

        if preview:
            # Play preview (requires simple playback)
            try:
                from pydub.playback import play
                play(self.processed_audio)
            except ImportError:
                pass  # Playback not available

    def save_audio(self):
        if self.processed_audio:
            filename, _ = QFileDialog.getSaveFileName(self, "Save Remix", "", "MP3 Files (*.mp3);;WAV Files (*.wav)")
            if filename:
                self.processed_audio.export(filename, format=filename.split('.')[-1])
                self.file_label.setText(f"Saved: {filename}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MusicRemixApp()
    window.show()
    sys.exit(app.exec_())
