from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox
)


class FindReplaceDialog(QDialog):
    """Dialog for collecting find/replace strings for folder-wide tag text replacement."""

    def __init__(self, parent):
        super().__init__(parent)
        self._find_text = None
        self._replace_text = None

        self._setup_ui()
        self.setModal(True)

    def _setup_ui(self):
        self.setWindowTitle("Find/Replace Tag Text in All Images")
        self.setMinimumWidth(420)

        layout = QVBoxLayout()
        layout.setSpacing(8)

        prompt = QLabel(
            "Replace text inside tags across all images in the current folder. "
            "Example: find <code>blue</code>, replace with <code>azure</code>."
        )
        prompt.setWordWrap(True)
        layout.addWidget(prompt)

        self.find_field = QLineEdit()
        self.find_field.setPlaceholderText("Find text (required)...")
        layout.addWidget(self.find_field)

        self.replace_field = QLineEdit()
        self.replace_field.setPlaceholderText("Replace with text (can be empty)...")
        self.replace_field.returnPressed.connect(self._on_accept)
        layout.addWidget(self.replace_field)

        note = QLabel("A workfile backup will be created automatically before changes are saved.")
        note.setWordWrap(True)
        note.setStyleSheet("color: #888888; font-style: italic; font-size: 11px;")
        layout.addWidget(note)

        button_layout = QHBoxLayout()
        button_layout.addStretch()

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        apply_button = QPushButton("Apply")
        apply_button.setDefault(True)
        apply_button.clicked.connect(self._on_accept)
        button_layout.addWidget(apply_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

        self.find_field.setFocus()

    def _on_accept(self):
        find_text = self.find_field.text().strip()
        replace_text = self.replace_field.text().strip()

        if not find_text:
            QMessageBox.warning(self, "Invalid Input", "Please enter text to find.")
            return

        if find_text == replace_text:
            QMessageBox.warning(self, "Invalid Input", "Find and replace text are identical.")
            return

        self._find_text = find_text
        self._replace_text = replace_text
        self.accept()

    def get_values(self):
        return self._find_text, self._replace_text
