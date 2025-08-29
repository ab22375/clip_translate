"""GUI interface for clip_translate using PyQt6."""

import sys
import asyncio
from typing import Optional
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QLabel, QComboBox, QPushButton, QSlider, QCheckBox,
    QGroupBox, QSplitter
)
from PyQt6.QtCore import (
    Qt, QTimer, pyqtSignal, QThread, QPoint, QRect, 
    QPropertyAnimation, QEasingCurve, pyqtSlot
)
from PyQt6.QtGui import QFont, QClipboard, QPalette, QColor
import pyperclip
from loguru import logger

from clip_translate.core import TranslationEngine, get_supported_languages


class TranslationWorker(QThread):
    """Background worker thread for translations."""
    
    translation_ready = pyqtSignal(str, str, bool)  # translated, original, cached
    error_occurred = pyqtSignal(str)
    language_detected = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.engine = TranslationEngine()
        self.source_lang = "ja"
        self.target_lang = "en"
        self.text_to_translate = ""
        self.running = False
        self._loop = None
        
    def set_languages(self, source: str, target: str):
        """Set source and target languages."""
        self.source_lang = source
        self.target_lang = target
        
    def translate(self, text: str):
        """Queue text for translation."""
        self.text_to_translate = text
        if not self.isRunning():
            self.start()
    
    def run(self):
        """Run translation in background thread."""
        try:
            # Create a fresh event loop for this thread
            if self._loop is None or self._loop.is_closed():
                self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)
            
            # Detect language first
            detected = self._loop.run_until_complete(
                self.engine.detect_language(self.text_to_translate)
            )
            
            if detected:
                self.language_detected.emit(detected)
                logger.info(f"Detected language: {detected}, expected: {self.source_lang}")
                
                # Only translate if language matches OR if source is 'auto'
                if detected == self.source_lang or self.source_lang == 'auto':
                    try:
                        translated, original, cached = self._loop.run_until_complete(
                            self.engine.translate_text(
                                self.text_to_translate,
                                self.source_lang if self.source_lang != 'auto' else detected,
                                self.target_lang
                            )
                        )
                        logger.info(f"Translation completed: {translated[:50]}...")
                        self.translation_ready.emit(translated, original, cached)
                    except Exception as trans_error:
                        logger.error(f"Translation error: {trans_error}")
                        self.error_occurred.emit(f"Translation failed: {trans_error}")
                else:
                    skip_msg = f"Skipped: Detected '{detected}', expected '{self.source_lang}'"
                    logger.info(skip_msg)
                    self.error_occurred.emit(skip_msg)
            else:
                self.error_occurred.emit("Language detection failed")
                
        except Exception as e:
            logger.error(f"Translation worker error: {e}")
            self.error_occurred.emit(f"Worker error: {str(e)}")
        finally:
            # Don't close the loop, keep it for reuse
            pass


class FloatingTranslator(QMainWindow):
    """Main floating window for translation."""
    
    def __init__(self, source_lang: str = "ja", target_lang: str = "en", show_romaji: bool = False, show_hiragana: bool = False):
        super().__init__()
        self.source_lang = source_lang
        self.target_lang = target_lang
        self.show_romaji = show_romaji
        self.show_hiragana = show_hiragana
        self.translation_worker = TranslationWorker()
        self.clipboard_timer = QTimer()
        self.last_clipboard_text = ""
        self.is_monitoring = False
        self.is_closing = False  # Flag to prevent operations during shutdown
        self.init_ui()
        self.setup_connections()
        
        # Set initial language selections
        self.set_language_selection()
        
        # Setup Japanese converter if needed
        if self.source_lang == "ja" and (self.show_romaji or self.show_hiragana):
            self.translation_worker.engine.setup_japanese_converter()
        
    def init_ui(self):
        """Initialize the user interface."""
        # Window properties
        self.setWindowTitle("Clip Translate")
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setFixedSize(1050, 910)  # Double width (525 * 2), 40% higher (650 * 1.4)
        
        # Central widget with styling
        central_widget = QWidget()
        central_widget.setObjectName("centralWidget")
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Title bar
        title_bar = self.create_title_bar()
        main_layout.addWidget(title_bar)
        
        # Language selector
        lang_group = QGroupBox("Languages")
        lang_layout = QHBoxLayout()
        
        self.source_combo = QComboBox()
        self.target_combo = QComboBox()
        self.swap_btn = QPushButton("⇄")
        self.swap_btn.setMaximumWidth(30)
        
        # Populate language combos
        languages = get_supported_languages()
        for code, name in sorted(languages.items()):
            display = f"{name} ({code})"
            self.source_combo.addItem(display, code)
            self.target_combo.addItem(display, code)
        
        # Defaults will be set in set_language_selection()
        
        lang_layout.addWidget(QLabel("From:"))
        lang_layout.addWidget(self.source_combo)
        lang_layout.addWidget(self.swap_btn)
        lang_layout.addWidget(QLabel("To:"))
        lang_layout.addWidget(self.target_combo)
        
        lang_group.setLayout(lang_layout)
        main_layout.addWidget(lang_group)
        
        # Text areas
        splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Original text
        original_group = QGroupBox("Original")
        original_layout = QVBoxLayout()
        self.original_text = QTextEdit()
        self.original_text.setReadOnly(True)
        self.original_text.setMinimumHeight(150)
        self.original_text.setMaximumHeight(200)
        original_layout.addWidget(self.original_text)
        
        # Add reading text area if Japanese readings are enabled
        if self.source_lang == "ja" and (self.show_romaji or self.show_hiragana):
            reading_label = "Romaji" if self.show_romaji else "Hiragana"
            self.reading_text = QTextEdit()
            self.reading_text.setReadOnly(True)
            self.reading_text.setMinimumHeight(60)
            self.reading_text.setMaximumHeight(100)
            self.reading_text.setStyleSheet("""
                QTextEdit {
                    background-color: rgba(60, 45, 45, 200);
                    color: #DDA0DD;
                    font-style: italic;
                }
            """)
            original_layout.addWidget(QLabel(f"{reading_label} Reading:"))
            original_layout.addWidget(self.reading_text)
        else:
            self.reading_text = None
            
        original_group.setLayout(original_layout)
        
        # Translation
        translation_group = QGroupBox("Translation")
        translation_layout = QVBoxLayout()
        self.translation_text = QTextEdit()
        self.translation_text.setReadOnly(True)
        self.translation_text.setMinimumHeight(150)
        self.copy_translation_btn = QPushButton("Copy Translation")
        translation_layout.addWidget(self.translation_text)
        translation_layout.addWidget(self.copy_translation_btn)
        translation_group.setLayout(translation_layout)
        
        splitter.addWidget(original_group)
        splitter.addWidget(translation_group)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        
        main_layout.addWidget(splitter)
        
        # Status and controls
        controls_layout = QHBoxLayout()
        
        self.monitor_checkbox = QCheckBox("Monitor Clipboard")
        self.monitor_checkbox.setChecked(True)
        
        self.status_label = QLabel("Ready")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        controls_layout.addWidget(self.monitor_checkbox)
        controls_layout.addStretch()
        controls_layout.addWidget(self.status_label)
        
        main_layout.addLayout(controls_layout)
        
        # Opacity slider
        opacity_layout = QHBoxLayout()
        opacity_layout.addWidget(QLabel("Opacity:"))
        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setRange(30, 100)
        self.opacity_slider.setValue(95)
        self.opacity_slider.setMaximumWidth(100)
        opacity_layout.addWidget(self.opacity_slider)
        self.opacity_label = QLabel("95%")
        opacity_layout.addWidget(self.opacity_label)
        opacity_layout.addStretch()
        
        main_layout.addLayout(opacity_layout)
        
        # Apply styles
        self.setStyleSheet("""
            #centralWidget {
                background-color: rgba(30, 30, 30, 240);
                border-radius: 12px;
                border: 1px solid rgba(60, 60, 60, 200);
            }
            
            QGroupBox {
                color: #ffffff;
                font-weight: bold;
                border: 1px solid rgba(80, 80, 80, 150);
                border-radius: 6px;
                margin-top: 6px;
                padding-top: 10px;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            
            QTextEdit {
                background-color: rgba(45, 45, 45, 200);
                color: #ffffff;
                border: 1px solid rgba(70, 70, 70, 150);
                border-radius: 4px;
                padding: 5px;
                font-family: 'Menlo', 'Monaco', 'Consolas', monospace;
                font-size: 14px;
            }
            
            QComboBox {
                background-color: rgba(50, 50, 50, 200);
                color: #ffffff;
                border: 1px solid rgba(70, 70, 70, 150);
                border-radius: 4px;
                padding: 4px;
                min-width: 100px;
            }
            
            QComboBox::drop-down {
                border: none;
            }
            
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #ffffff;
                margin-right: 5px;
            }
            
            QComboBox QAbstractItemView {
                background-color: rgba(240, 240, 240, 250);
                color: #000000;
                selection-background-color: rgba(70, 130, 180, 200);
                selection-color: #ffffff;
                border: 1px solid rgba(70, 70, 70, 150);
                border-radius: 4px;
                padding: 2px;
            }
            
            QPushButton {
                background-color: rgba(70, 130, 180, 200);
                color: #ffffff;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
            }
            
            QPushButton:hover {
                background-color: rgba(100, 149, 237, 200);
            }
            
            QPushButton:pressed {
                background-color: rgba(65, 105, 225, 200);
            }
            
            QLabel {
                color: #ffffff;
            }
            
            QCheckBox {
                color: #ffffff;
            }
            
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border-radius: 3px;
                border: 1px solid rgba(70, 70, 70, 150);
                background-color: rgba(45, 45, 45, 200);
            }
            
            QCheckBox::indicator:checked {
                background-color: rgba(70, 130, 180, 200);
            }
            
            QSlider::groove:horizontal {
                height: 4px;
                background: rgba(70, 70, 70, 150);
                border-radius: 2px;
            }
            
            QSlider::handle:horizontal {
                background: rgba(70, 130, 180, 200);
                width: 12px;
                height: 12px;
                border-radius: 6px;
                margin: -4px 0;
            }
            
            #titleBar {
                background-color: rgba(40, 40, 40, 200);
                border-top-left-radius: 12px;
                border-top-right-radius: 12px;
            }
        """)
        
    def create_title_bar(self) -> QWidget:
        """Create custom title bar for dragging."""
        title_bar = QWidget()
        title_bar.setObjectName("titleBar")
        title_bar.setFixedHeight(30)
        
        layout = QHBoxLayout(title_bar)
        layout.setContentsMargins(10, 0, 10, 0)
        
        title = QLabel("Clip Translate")
        title.setStyleSheet("color: #ffffff; font-weight: bold;")
        
        minimize_btn = QPushButton("−")
        minimize_btn.setMaximumSize(20, 20)
        minimize_btn.clicked.connect(self.showMinimized)
        
        close_btn = QPushButton("×")
        close_btn.setMaximumSize(20, 20)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 59, 48, 200);
            }
            QPushButton:hover {
                background-color: rgba(255, 69, 58, 250);
            }
        """)
        close_btn.clicked.connect(self.close)  # This will trigger closeEvent
        
        layout.addWidget(title)
        layout.addStretch()
        layout.addWidget(minimize_btn)
        layout.addWidget(close_btn)
        
        return title_bar
    
    def set_language_selection(self):
        """Set the language combo boxes to the specified languages."""
        languages = get_supported_languages()
        
        # Find and set source language
        for i in range(self.source_combo.count()):
            if self.source_combo.itemData(i) == self.source_lang:
                self.source_combo.setCurrentIndex(i)
                break
        
        # Find and set target language  
        for i in range(self.target_combo.count()):
            if self.target_combo.itemData(i) == self.target_lang:
                self.target_combo.setCurrentIndex(i)
                break
        
        # Update the worker with the languages
        self.translation_worker.set_languages(self.source_lang, self.target_lang)
        
    def setup_connections(self):
        """Setup signal/slot connections."""
        # Translation worker signals
        self.translation_worker.translation_ready.connect(self.on_translation_ready)
        self.translation_worker.error_occurred.connect(self.on_translation_error)
        self.translation_worker.language_detected.connect(self.on_language_detected)
        
        # UI signals
        self.monitor_checkbox.stateChanged.connect(self.toggle_monitoring)
        self.opacity_slider.valueChanged.connect(self.update_opacity)
        self.copy_translation_btn.clicked.connect(self.copy_translation)
        self.swap_btn.clicked.connect(self.swap_languages)
        self.source_combo.currentIndexChanged.connect(self.update_languages)
        self.target_combo.currentIndexChanged.connect(self.update_languages)
        
        # Clipboard timer
        self.clipboard_timer.timeout.connect(self.check_clipboard)
        self.clipboard_timer.start(500)  # Check every 500ms
        
        # Start monitoring
        self.toggle_monitoring(Qt.CheckState.Checked.value)
        
    @pyqtSlot(int)
    def toggle_monitoring(self, state):
        """Toggle clipboard monitoring."""
        self.is_monitoring = state == Qt.CheckState.Checked.value
        if self.is_monitoring:
            self.status_label.setText("Monitoring...")
            self.status_label.setStyleSheet("color: #90EE90;")
        else:
            self.status_label.setText("Paused")
            self.status_label.setStyleSheet("color: #FFD700;")
    
    @pyqtSlot(int)
    def update_opacity(self, value):
        """Update window opacity."""
        self.setWindowOpacity(value / 100.0)
        self.opacity_label.setText(f"{value}%")
    
    @pyqtSlot()
    def copy_translation(self):
        """Copy translation to clipboard."""
        text = self.translation_text.toPlainText()
        if text:
            pyperclip.copy(text)
            # Temporarily change button text
            self.copy_translation_btn.setText("Copied!")
            QTimer.singleShot(1000, lambda: self.copy_translation_btn.setText("Copy Translation"))
    
    @pyqtSlot()
    def swap_languages(self):
        """Swap source and target languages."""
        source_idx = self.source_combo.currentIndex()
        target_idx = self.target_combo.currentIndex()
        self.source_combo.setCurrentIndex(target_idx)
        self.target_combo.setCurrentIndex(source_idx)
    
    @pyqtSlot()
    def update_languages(self):
        """Update translation worker languages."""
        source = self.source_combo.currentData()
        target = self.target_combo.currentData()
        if source and target:
            self.translation_worker.set_languages(source, target)
    
    def check_clipboard(self):
        """Check clipboard for new content."""
        if not self.is_monitoring or self.is_closing:
            return
            
        try:
            current_text = pyperclip.paste()
            if current_text and current_text != self.last_clipboard_text:
                logger.info(f"New clipboard content detected: {current_text[:50]}...")
                self.last_clipboard_text = current_text
                
                # Don't show text in original area yet - wait for language detection
                self.original_text.clear()
                self.translation_text.clear()
                if self.reading_text:
                    self.reading_text.clear()
                self.status_label.setText("Detecting language...")
                self.status_label.setStyleSheet("color: #87CEEB;")
                
                # Update languages before translating
                self.update_languages()
                
                # Trigger translation (which includes language detection)
                logger.info(f"Starting translation with source={self.translation_worker.source_lang}, target={self.translation_worker.target_lang}")
                self.translation_worker.translate(current_text)
        except Exception as e:
            if not self.is_closing:
                logger.error(f"Clipboard check error: {e}")
                self.status_label.setText("Clipboard error")
                self.status_label.setStyleSheet("color: #FF6B6B;")
    
    @pyqtSlot(str, str, bool)
    def on_translation_ready(self, translated, original, cached):
        """Handle translation result."""
        # Now show both original and translated text
        self.original_text.setPlainText(original)
        self.translation_text.setPlainText(translated)
        
        # Show Japanese reading if enabled and available
        if (self.reading_text is not None and self.source_lang == "ja" and 
            (self.show_romaji or self.show_hiragana)):
            try:
                reading = self.translation_worker.engine.get_japanese_reading(
                    original, 
                    romaji=self.show_romaji, 
                    hiragana=self.show_hiragana
                )
                if reading:
                    self.reading_text.setPlainText(reading)
                else:
                    self.reading_text.setPlainText("(No Japanese text found)")
            except Exception as e:
                logger.error(f"Failed to generate reading: {e}")
                self.reading_text.setPlainText("(Reading generation failed)")
        
        status = "Cached" if cached else "Translated"
        self.status_label.setText(status)
        self.status_label.setStyleSheet("color: #90EE90;")
        
        # Don't automatically update clipboard to avoid loops
        # User can manually copy using the Copy button
        logger.info(f"Translation ready: {translated[:100]}...")
    
    @pyqtSlot(str)
    def on_translation_error(self, error):
        """Handle translation error."""
        self.status_label.setText(f"Error: {error[:30]}...")
        self.status_label.setStyleSheet("color: #FF6B6B;")
        logger.error(f"Translation error: {error}")
    
    @pyqtSlot(str)
    def on_language_detected(self, language):
        """Handle language detection result."""
        logger.info(f"Detected language: {language}")
    
    # Window dragging
    def mousePressEvent(self, event):
        """Handle mouse press for dragging."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
    
    def mouseMoveEvent(self, event):
        """Handle mouse move for dragging."""
        if event.buttons() == Qt.MouseButton.LeftButton and hasattr(self, 'drag_position'):
            self.move(event.globalPosition().toPoint() - self.drag_position)
    
    def closeEvent(self, event):
        """Handle window close event - clean shutdown."""
        logger.info("Closing application...")
        self.is_closing = True
        
        # Stop clipboard monitoring
        self.is_monitoring = False
        self.clipboard_timer.stop()
        
        # Stop and clean up translation worker
        if self.translation_worker.isRunning():
            self.translation_worker.terminate()
            self.translation_worker.wait(1000)  # Wait max 1 second
        
        # Close event loop if exists
        if hasattr(self.translation_worker, '_loop') and self.translation_worker._loop:
            try:
                self.translation_worker._loop.close()
            except:
                pass
        
        # Accept the close event
        event.accept()
        
        # Ensure the application quits
        QApplication.quit()


def main():
    """Main entry point for GUI."""
    import argparse
    import signal
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Clip Translate GUI')
    parser.add_argument('--source', '-s', default='ja', help='Source language code (default: ja)')
    parser.add_argument('--target', '-t', default='en', help='Target language code (default: en)')
    parser.add_argument('--romaji', '-r', action='store_true', help='Show romaji reading for Japanese text')
    parser.add_argument('--hiragana', '--hira', action='store_true', help='Show hiragana reading for Japanese text')
    
    # Only parse known args to avoid issues with Qt args
    args, remaining = parser.parse_known_args()
    
    # Create QApplication with remaining args
    app = QApplication([sys.argv[0]] + remaining)
    app.setApplicationName("Clip Translate")
    
    # Set application style
    app.setStyle("Fusion")
    
    # Create main window
    window = FloatingTranslator(
        source_lang=args.source, 
        target_lang=args.target,
        show_romaji=args.romaji,
        show_hiragana=args.hiragana
    )
    
    # Setup signal handler for clean exit on Ctrl+C
    def signal_handler(sig, frame):
        logger.info("Received interrupt signal, closing...")
        window.close()
    
    signal.signal(signal.SIGINT, signal_handler)
    
    # Make app handle Ctrl+C properly
    timer = QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)  # Let Python handle signals
    
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()