from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox
)
from PySide6.QtCore import Qt


class ReplaceTagDialog(QDialog):
    """Dialog for collecting the replacement tag name in a bulk replace operation."""

    def __init__(self, parent, source_tag_name):
        """Initialize the dialog.

        Args:
            parent: Parent widget
            source_tag_name (str): The tag being replaced (stored with underscores)
        """
        super().__init__(parent)
        self.source_tag_name = source_tag_name
        self._target_tag = None

        self._setup_ui()
        self.setModal(True)

    def _setup_ui(self):
        self.setWindowTitle("Replace Tag in All Images")
        self.setMinimumWidth(380)

        layout = QVBoxLayout()
        layout.setSpacing(8)

        source_display = self.source_tag_name.replace('_', ' ')

        # Main prompt label
        prompt_label = QLabel(f"Replace <b>'{source_display}'</b> with:")
        prompt_label.setWordWrap(True)
        layout.addWidget(prompt_label)

        # Input field
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Enter replacement tag name...")
        self.input_field.setStyleSheet("color: white;")
        self.input_field.returnPressed.connect(self._on_accept)
        layout.addWidget(self.input_field)

        # Note text
        note_label = QLabel(
            "Replaces the tag in-place across all images in the current folder. "
            "A backup will be created automatically."
        )
        note_label.setWordWrap(True)
        note_label.setStyleSheet("color: #888888; font-style: italic; font-size: 11px;")
        layout.addWidget(note_label)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        ok_button = QPushButton("Replace")
        ok_button.setDefault(True)
        ok_button.clicked.connect(self._on_accept)
        button_layout.addWidget(ok_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

        self.input_field.setFocus()

    def _on_accept(self):
        raw = self.input_field.text()
        normalized = raw.strip().lower().replace(' ', '_')

        if not normalized:
            QMessageBox.warning(self, "Invalid Input", "Please enter a replacement tag name.")
            return

        if normalized == self.source_tag_name.lower():
            QMessageBox.warning(
                self,
                "Invalid Input",
                "The replacement tag is the same as the source tag."
            )
            return

        self._target_tag = normalized
        self.accept()

    def get_target_tag(self):
        """Returns the normalized replacement tag name, or None if cancelled."""
        return self._target_tag
