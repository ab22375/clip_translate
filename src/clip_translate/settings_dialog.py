"""Settings dialog for translation engine configuration."""

import asyncio
from typing import Optional
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox, 
    QComboBox, QLineEdit, QPushButton, QLabel, QTabWidget, QWidget,
    QTextEdit, QMessageBox, QProgressBar, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread, pyqtSlot
from PyQt6.QtGui import QFont
from loguru import logger

from clip_translate.config import Config
from clip_translate.engines import get_backend


class ConnectionTestWorker(QThread):
    """Worker thread for testing engine connections."""
    
    test_completed = pyqtSignal(str, bool, str)  # engine, success, message
    
    def __init__(self, engine: str, config: Config):
        super().__init__()
        self.engine = engine
        self.config = config
        
    def run(self):
        """Test the connection to the engine."""
        try:
            logger.info(f"Testing connection for {self.engine}")
            
            # Get engine configuration
            engine_config = self.config.get_engine_config(self.engine)
            logger.info(f"Engine config: {engine_config}")
            
            # Create backend
            backend = get_backend(self.engine, **engine_config)
            
            # Validate configuration
            if not backend.validate_config():
                logger.warning(f"Invalid config for {self.engine}")
                self.test_completed.emit(
                    self.engine, 
                    False, 
                    "Invalid configuration - check API key"
                )
                return
            
            # For Google Translate, just do a simple validation
            if self.engine == "google":
                self.test_completed.emit(
                    self.engine,
                    True,
                    "Google Translate is available (no API key needed)"
                )
                return
            
            # Try a simple translation test for other engines
            loop = None
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                logger.info(f"Starting translation test for {self.engine}")
                
                # Add timeout to prevent hanging
                result = loop.run_until_complete(
                    asyncio.wait_for(
                        backend.translate("Hello", "en", "es"),
                        timeout=30.0  # 30 second timeout
                    )
                )
                
                if result and result.strip():
                    logger.info(f"Test successful for {self.engine}: {result}")
                    self.test_completed.emit(
                        self.engine, 
                        True, 
                        f"Connection successful! Test translation: '{result[:50]}'"
                    )
                else:
                    logger.warning(f"Empty response for {self.engine}")
                    self.test_completed.emit(
                        self.engine, 
                        False, 
                        "Translation test failed - empty response"
                    )
                    
            except Exception as e:
                logger.error(f"Translation test failed for {self.engine}: {e}")
                self.test_completed.emit(
                    self.engine, 
                    False, 
                    f"Translation test failed: {str(e)}"
                )
            finally:
                if loop:
                    try:
                        loop.close()
                    except:
                        pass
                
        except Exception as e:
            logger.error(f"Connection test error for {self.engine}: {e}")
            self.test_completed.emit(
                self.engine, 
                False, 
                f"Connection failed: {str(e)}"
            )


class EngineConfigWidget(QWidget):
    """Widget for configuring a specific engine."""
    
    def __init__(self, engine: str, config: Config):
        super().__init__()
        self.engine = engine
        self.config = config
        self.test_worker = None
        self.init_ui()
        self.load_config()
        
    def __del__(self):
        """Cleanup when widget is destroyed."""
        try:
            if self.test_worker and self.test_worker.isRunning():
                self.test_worker.terminate()
                self.test_worker.wait(1000)
        except:
            pass
        
    def init_ui(self):
        """Initialize the UI for this engine."""
        layout = QVBoxLayout()
        
        # Engine info
        info_layout = QVBoxLayout()
        title = QLabel(f"{self.engine.title()} Translation Engine")
        title.setStyleSheet("font-weight: bold; font-size: 14px; color: #ffffff;")
        info_layout.addWidget(title)
        
        # Engine-specific description
        descriptions = {
            "google": "Free translation service. No API key required.",
            "openai": "High-quality AI translation using GPT models. Requires OpenAI API key.",
            "deepl": "Professional translation service with excellent quality. Requires DeepL API key.",
            "claude": "AI translation using Anthropic's Claude models. Requires Anthropic API key."
        }
        
        desc = QLabel(descriptions.get(self.engine, "Translation engine"))
        desc.setStyleSheet("color: #cccccc; font-style: italic;")
        desc.setWordWrap(True)
        info_layout.addWidget(desc)
        layout.addLayout(info_layout)
        
        # Configuration form
        if self.engine != "google":
            config_group = QGroupBox("Configuration")
            config_layout = QFormLayout()
            
            # API Key
            self.api_key_input = QLineEdit()
            self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.api_key_input.setPlaceholderText("Enter API key...")
            config_layout.addRow("API Key:", self.api_key_input)
            
            # Model selection for OpenAI and Claude
            if self.engine in ["openai", "claude"]:
                self.model_combo = QComboBox()
                if self.engine == "openai":
                    models = ["gpt-4o-mini", "gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"]
                else:  # claude
                    models = ["claude-3-haiku-20240307", "claude-3-sonnet-20240229", "claude-3-opus-20240229"]
                
                self.model_combo.addItems(models)
                config_layout.addRow("Model:", self.model_combo)
            else:
                self.model_combo = None
            
            config_group.setLayout(config_layout)
            layout.addWidget(config_group)
        else:
            self.api_key_input = None
            self.model_combo = None
        
        # Test connection section
        test_group = QGroupBox("Connection Test")
        test_layout = QVBoxLayout()
        
        # Test button and progress
        test_controls = QHBoxLayout()
        self.test_button = QPushButton("Test Connection")
        self.test_button.clicked.connect(self.test_connection)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        
        test_controls.addWidget(self.test_button)
        test_controls.addWidget(self.progress_bar)
        test_controls.addStretch()
        test_layout.addLayout(test_controls)
        
        # Test result
        self.test_result = QTextEdit()
        self.test_result.setMaximumHeight(80)
        self.test_result.setReadOnly(True)
        self.test_result.setPlaceholderText("Test results will appear here...")
        test_layout.addWidget(self.test_result)
        
        test_group.setLayout(test_layout)
        layout.addWidget(test_group)
        
        layout.addStretch()
        self.setLayout(layout)
        
    def load_config(self):
        """Load configuration for this engine."""
        if self.api_key_input:
            api_key = self.config.get_api_key(self.engine)
            if api_key:
                self.api_key_input.setText(api_key)
        
        if self.model_combo:
            engine_config = self.config.get_engine_config(self.engine)
            model = engine_config.get("model", "")
            if model:
                index = self.model_combo.findText(model)
                if index >= 0:
                    self.model_combo.setCurrentIndex(index)
    
    def save_config(self):
        """Save configuration for this engine."""
        if self.api_key_input:
            api_key = self.api_key_input.text().strip()
            self.config.set_api_key(self.engine, api_key)
        
        if self.model_combo:
            model = self.model_combo.currentText()
            self.config.set(f"{self.engine}.model", model)
    
    def test_connection(self):
        """Test connection to this engine."""
        try:
            # Save current configuration before testing
            self.save_config()
            
            # Clean up any existing worker
            if self.test_worker and self.test_worker.isRunning():
                logger.warning("Previous test still running, terminating...")
                self.test_worker.terminate()
                self.test_worker.wait(1000)
            
            # Start test
            self.test_button.setEnabled(False)
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)  # Indeterminate progress
            self.test_result.clear()
            self.test_result.setPlainText("Testing connection...")
            
            # Create and start worker thread
            logger.info(f"Starting connection test for {self.engine}")
            self.test_worker = ConnectionTestWorker(self.engine, self.config)
            self.test_worker.test_completed.connect(self.on_test_completed)
            self.test_worker.finished.connect(self.on_test_finished)
            self.test_worker.start()
            
        except Exception as e:
            logger.error(f"Failed to start connection test: {e}")
            self.test_button.setEnabled(True)
            self.progress_bar.setVisible(False)
            self.test_result.setStyleSheet("color: #FFB6C1;")  # Light red
            self.test_result.setPlainText(f"✗ Test failed to start: {str(e)}")
    
    @pyqtSlot(str, bool, str)
    def on_test_completed(self, engine, success, message):
        """Handle test completion."""
        logger.info(f"Test completed for {engine}: success={success}, message={message}")
        
        self.test_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        if success:
            self.test_result.setStyleSheet("color: #90EE90;")  # Light green
            self.test_result.setPlainText(f"✓ {message}")
        else:
            self.test_result.setStyleSheet("color: #FFB6C1;")  # Light red
            self.test_result.setPlainText(f"✗ {message}")
    
    @pyqtSlot()
    def on_test_finished(self):
        """Handle test thread finished."""
        logger.info(f"Test thread finished for {self.engine}")
        
        # Clean up worker
        if self.test_worker:
            self.test_worker.deleteLater()
            self.test_worker = None


class SettingsDialog(QDialog):
    """Settings dialog for translation engine configuration."""
    
    # Signal emitted when engine is changed
    engine_changed = pyqtSignal(str)
    
    def __init__(self, config: Config, parent=None):
        super().__init__(parent)
        self.config = config
        self.engine_widgets = {}
        self.init_ui()
        self.load_settings()
        
    def init_ui(self):
        """Initialize the dialog UI."""
        self.setWindowTitle("Translation Engine Settings")
        self.setFixedSize(600, 500)
        self.setModal(True)
        
        # Apply dark theme
        self.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
                color: #ffffff;
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
            
            QTabWidget::pane {
                border: 1px solid rgba(70, 70, 70, 150);
                background-color: rgba(45, 45, 45, 200);
            }
            
            QTabWidget::tab-bar {
                left: 5px;
            }
            
            QTabBar::tab {
                background-color: rgba(60, 60, 60, 200);
                color: #ffffff;
                padding: 8px 12px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            
            QTabBar::tab:selected {
                background-color: rgba(70, 130, 180, 200);
            }
            
            QTabBar::tab:hover {
                background-color: rgba(80, 80, 80, 200);
            }
            
            QComboBox {
                background-color: rgba(50, 50, 50, 200);
                color: #ffffff;
                border: 1px solid rgba(70, 70, 70, 150);
                border-radius: 4px;
                padding: 4px;
                min-width: 150px;
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
                background-color: rgba(255, 248, 220, 250);
                color: #000000;
                selection-background-color: rgba(70, 130, 180, 200);
                selection-color: #ffffff;
                border: 1px solid rgba(70, 70, 70, 150);
                border-radius: 4px;
                padding: 2px;
            }
            
            QComboBox QAbstractItemView::item {
                color: #000000;
                background-color: transparent;
                padding: 4px;
            }
            
            QComboBox QAbstractItemView::item:selected {
                background-color: rgba(70, 130, 180, 200);
                color: #ffffff;
            }
            
            QLineEdit {
                background-color: rgba(45, 45, 45, 200);
                color: #ffffff;
                border: 1px solid rgba(70, 70, 70, 150);
                border-radius: 4px;
                padding: 6px;
            }
            
            QLineEdit:focus {
                border-color: rgba(70, 130, 180, 200);
            }
            
            QTextEdit {
                background-color: rgba(45, 45, 45, 200);
                color: #ffffff;
                border: 1px solid rgba(70, 70, 70, 150);
                border-radius: 4px;
                padding: 5px;
            }
            
            QPushButton {
                background-color: rgba(70, 130, 180, 200);
                color: #ffffff;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            
            QPushButton:hover {
                background-color: rgba(100, 149, 237, 200);
            }
            
            QPushButton:pressed {
                background-color: rgba(65, 105, 225, 200);
            }
            
            QPushButton:disabled {
                background-color: rgba(60, 60, 60, 200);
                color: #888888;
            }
            
            QProgressBar {
                border: 1px solid rgba(70, 70, 70, 150);
                border-radius: 4px;
                background-color: rgba(45, 45, 45, 200);
                color: #ffffff;
                text-align: center;
            }
            
            QProgressBar::chunk {
                background-color: rgba(70, 130, 180, 200);
                border-radius: 3px;
            }
            
            QLabel {
                color: #ffffff;
            }
        """)
        
        layout = QVBoxLayout()
        
        # Header
        header = QLabel("Configure Translation Engines")
        header.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px;")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        # Default engine selection
        default_group = QGroupBox("Default Translation Engine")
        default_layout = QFormLayout()
        
        self.default_engine_combo = QComboBox()
        engines = ["google", "openai", "deepl", "claude"]
        for engine in engines:
            display_name = f"{engine.title()}"
            if not self.config.validate_engine_config(engine) and engine != "google":
                display_name += " (Not Configured)"
            self.default_engine_combo.addItem(display_name, engine)
        
        default_layout.addRow("Default Engine:", self.default_engine_combo)
        default_group.setLayout(default_layout)
        layout.addWidget(default_group)
        
        # Engine configuration tabs
        self.tab_widget = QTabWidget()
        
        for engine in engines:
            widget = EngineConfigWidget(engine, self.config)
            self.engine_widgets[engine] = widget
            self.tab_widget.addTab(widget, engine.title())
        
        layout.addWidget(self.tab_widget)
        
        # Dialog buttons
        button_layout = QHBoxLayout()
        
        self.save_button = QPushButton("Save & Apply")
        self.save_button.clicked.connect(self.save_and_apply)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.close_dialog)
        
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.save_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def closeEvent(self, event):
        """Handle dialog close event."""
        try:
            # Stop any running tests
            for widget in self.engine_widgets.values():
                if widget.test_worker and widget.test_worker.isRunning():
                    logger.info(f"Terminating test worker for {widget.engine}")
                    widget.test_worker.terminate()
                    widget.test_worker.wait(1000)
            
            event.accept()
        except Exception as e:
            logger.error(f"Error closing settings dialog: {e}")
            event.accept()
    
    def close_dialog(self):
        """Close the dialog safely."""
        self.close()
    
    def load_settings(self):
        """Load current settings."""
        current_engine = self.config.get_engine()
        
        # Set default engine combo
        for i in range(self.default_engine_combo.count()):
            if self.default_engine_combo.itemData(i) == current_engine:
                self.default_engine_combo.setCurrentIndex(i)
                break
    
    def save_and_apply(self):
        """Save settings and apply changes."""
        try:
            # Save configurations for all engines
            for engine, widget in self.engine_widgets.items():
                widget.save_config()
            
            # Set default engine
            selected_engine = self.default_engine_combo.currentData()
            self.config.set_engine(selected_engine)
            
            # Save config file
            if self.config.save_config():
                # Emit signal that engine changed
                self.engine_changed.emit(selected_engine)
                
                QMessageBox.information(
                    self,
                    "Settings Saved",
                    f"Settings saved successfully!\nDefault engine: {selected_engine}"
                )
                self.accept()
            else:
                QMessageBox.warning(
                    self,
                    "Save Failed",
                    "Failed to save configuration file."
                )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to save settings: {str(e)}"
            )
            logger.error(f"Settings save error: {e}")