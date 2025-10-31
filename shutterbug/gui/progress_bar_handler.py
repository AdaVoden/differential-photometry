from PySide6.QtWidgets import QProgressBar, QLabel

class ProgressHandler:
    def __init__(self, progress_bar: QProgressBar, label: QLabel):
        self.progress_bar = progress_bar
        self.label = label
        self.processing_text = None

    def __call__(self, processing_text: str):
        self.processing_text = processing_text
        return self


    def __enter__(self):
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
        if self.processing_text:
            self.label.setText(self.processing_text)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.progress_bar.setValue(100)
        self.progress_bar.setVisible(False)
        self.label.setText("Ready")
        return False # Errors can propagate