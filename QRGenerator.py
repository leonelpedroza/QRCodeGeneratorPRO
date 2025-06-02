"""
Enhanced QR Code Generator Application - PySide6 Version
Author: @ LGP MIT License
Version: 2.0
"""

import sys
import os
import json
import csv
import logging
import tempfile
import traceback
from pathlib import Path
from datetime import datetime
from typing import Optional, Tuple, Dict, Any, List
from dataclasses import dataclass
from enum import Enum
from io import BytesIO

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QComboBox, QLineEdit, QTextEdit, QCheckBox,
    QSpinBox, QGroupBox, QTabWidget, QFileDialog, QMessageBox,
    QColorDialog, QProgressBar, QStatusBar, QToolBar, QSplitter,
    QScrollArea, QFrame, QGridLayout, QRadioButton, QButtonGroup,
    QStyle, QStyleFactory, QGraphicsDropShadowEffect, QMenu,
    QWidgetAction, QListWidget, QListWidgetItem, QStackedWidget,
    QSizePolicy, QToolButton
)
from PySide6.QtCore import (
    Qt, QTimer, QThread, Signal, Slot, QSize, QPropertyAnimation,
    QEasingCurve, QParallelAnimationGroup, QRect, QPoint,
    QEvent, QObject, QSettings
)
from PySide6.QtGui import (
    QPixmap, QImage, QPainter, QFont, QFontDatabase, QIcon,
    QPalette, QColor, QBrush, QLinearGradient, QRadialGradient,
    QAction, QKeySequence, QPen, QCursor, QGuiApplication
)

# QR Code and image processing imports
import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers.pil import (
    RoundedModuleDrawer, CircleModuleDrawer, GappedSquareModuleDrawer,
    SquareModuleDrawer, VerticalBarsDrawer
)
from qrcode.image.styles.colormasks import SolidFillColorMask, SquareGradiantColorMask
from PIL import Image, ImageDraw
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import material design icons as base64 strings (for embedded icons)
ICONS = {
    'qr': '🔲',
    'save': '💾',
    'pdf': '📄',
    'clear': '🔄',
    'settings': '⚙️',
    'batch': '📊',
    'help': '❓',
    'about': 'ℹ️',
    'folder': '📁',
    'color': '🎨',
    'style': '✨',
    'language': '🌐',
    'print': '🖨️',
    'copy': '📋',
    'paste': '📌',
    'image': '🖼️',
}

# Modern color palette with better contrast
COLORS = {
    'primary': '#1976D2',
    'primary_dark': '#0D47A1',
    'primary_light': '#42A5F5',
    'secondary': '#D32F2F',
    'accent': '#00ACC1',
    'success': '#388E3C',
    'warning': '#F57C00',
    'error': '#C62828',
    'background': '#F5F5F5',
    'surface': '#FFFFFF',
    'on_surface': '#000000',
    'text_primary': '#424242',  # Dark grey for all text
    'text_secondary': '#616161',  # Medium grey for secondary text
    'divider': '#E0E0E0',
    'input_background': '#FFFFFF',
    'input_border': '#BDBDBD',
    'input_border_focus': '#1976D2',
    'group_title': '#1976D2',
}

# Language translations (keeping original translations)
TRANSLATIONS = {
    'en': {
        'app_title': 'QR Generator Pro 2.0',
        'language': 'Language',
        'english': 'English',
        'spanish': 'Español',
        'file': 'File',
        'save_config': 'Save Configuration',
        'load_config': 'Load Configuration',
        'save_qr': 'Save QR Code',
        'save_as_pdf': 'Save as PDF',
        'save_as_png': 'Save as PNG',
        'print': 'Print',
        'exit': 'Exit',
        'help_menu': 'Help',
        'help': 'Help',
        'about': 'About',
        'generator_tab': 'QR Generator',
        'settings_tab': 'Settings',
        'batch_tab': 'Batch Processing',
        'preview': 'Preview',
        'qr_placeholder': 'QR code will appear here',
        'qr_type': 'QR Code Type',
        'data': 'Data',
        'text': 'Text',
        'text_label': 'Text:',
        'url': 'URL',
        'url_label': 'URL:',
        'email': 'Email',
        'email_label': 'Email:',
        'subject_label': 'Subject:',
        'message_label': 'Message:',
        'phone': 'Phone',
        'phone_label': 'Phone:',
        'wifi': 'WiFi',
        'ssid_label': 'Network Name (SSID):',
        'password_label': 'Password:',
        'security_label': 'Security:',
        'hidden_network': 'Hidden network',
        'sms': 'SMS',
        'vcard': 'vCard',
        'full_name_label': 'Full name:',
        'organization_label': 'Organization:',
        'website_label': 'Website:',
        'style': 'Style',
        'module_style': 'Module style:',
        'square': 'Square',
        'rounded': 'Rounded',
        'circle': 'Circle',
        'gapped': 'Gapped',
        'vertical': 'Vertical bars',
        'main_color': 'Main color:',
        'background_color': 'Background color:',
        'use_gradient': 'Use gradient',
        'pdf_options': 'PDF Options',
        'title': 'Title:',
        'format_letter': 'Format: Letter',
        'save_as_image': 'Save as Image',
        'save_as_pdf': 'Save as PDF',
        'clear_all': 'Clear All',
        'error_correction': 'Error Correction Level',
        'low_ec': 'L - Low (7%)',
        'medium_ec': 'M - Medium (15%)',
        'quartile_ec': 'Q - Quartile (25%)',
        'high_ec': 'H - High (30%)',
        'size_settings': 'Size Settings',
        'module_size': 'Module size:',
        'border': 'Border:',
        'auto_save': 'Auto Save',
        'enable_autosave': 'Enable auto save',
        'folder': 'Folder:',
        'save_settings': 'Save Settings',
        'batch_instructions': 'Process multiple QR codes from a CSV file.\nThe file must have columns: type, data, pdf_title',
        'select_csv': 'Select CSV',
        'output_folder': 'Output folder:',
        'process_batch': 'Process Batch',
        'processing': 'Processing {} of {}',
        'batch_complete': 'Complete! {} QR codes generated',
        'ready': 'Ready',
        'qr_generated': 'QR code generated successfully',
        'image_saved': 'Image saved: {}',
        'pdf_saved': 'PDF saved: {}',
        'fields_cleared': 'All fields have been cleared',
        'settings_saved': 'Settings saved successfully',
        'memory': 'Memory: {:.1f} MB',
        'printing': 'Sending to printer...',
        'error': 'Error',
        'no_qr_to_save': 'No QR code to save',
        'no_qr_to_print': 'No QR code to print',
        'error_generating_qr': 'Error generating QR code: {}',
        'error_saving_image': 'Error saving image: {}',
        'error_saving_pdf': 'Error saving PDF: {}',
        'error_saving_settings': 'Error saving settings: {}',
        'error_batch': 'Batch processing error: {}',
        'error_printing': 'Error printing: {}',
        'select_valid_csv': 'Please select a valid CSV file',
        'success': 'Success',
        'image_saved_success': 'Image saved successfully.\nDo you want to open the file location?',
        'pdf_saved_success': 'PDF saved successfully.\nDo you want to open the file?',
        'batch_success': 'Processing completed.\n{} files generated in:\n{}',
        'settings_loaded': 'Configuration loaded from: {}',
        'settings_saved_to': 'Configuration saved to: {}',
        'error_loading_config': 'Error loading configuration: {}',
        'help_text': '''QR Generator Pro 2.0

Keyboard shortcuts:
- Ctrl+S: Save as PDF
- Ctrl+I: Save as image
- Ctrl+R: Clear all
- F1: Show help

Supported QR types:
- Simple text
- URLs
- Email with subject and message
- Phone numbers
- WiFi networks
- SMS
- Contact cards (vCard)

Features:
- Multiple module styles
- Customizable colors
- Gradients
- Auto save
- Batch processing
- Export to PDF and images''',
        'about_title': 'About QR Generator Pro',
        'about_text': '''QR Generator Pro 2.0

A professional QR code generator with advanced features.

Features:
• Multiple QR code types support
• Customizable styles and colors
• PDF and image export
• Batch processing
• Multi-language support

Developed by LGP with much help from Claude/Anthropic LLM

Developed with Python and PySide6
© 2024 - All rights reserved''',
        'enter_data': 'Enter data to generate QR code',
        'generated_by': 'Generated by QR Generator Pro - {}',
        'images': 'Images',
        'all_files': 'All files',
        'save_as_pdf_title': 'Save as PDF',
        'select_autosave_folder': 'Select auto save folder',
        'select_csv_file': 'Select CSV file',
        'select_color': 'Select Color',
        'more_colors': 'More Colors...',
        'copy_qr': 'Copy QR Code',
        'qr_copied': 'QR code copied to clipboard',
        'theme': 'Theme',
        'light_theme': 'Light',
        'dark_theme': 'Dark',
        'auto_theme': 'Auto',
        'logo': 'Logo:',
        'no_logo': 'No hay logo seleccionado',
        'select_logo': 'Seleccionar Logo',
        'logo_loaded': 'Logo: {}',
        'error_loading_logo': 'Error al cargar logo: {}',
        'warning': 'Advertencia',
        'info': 'Información',
        'logo_too_large': 'El logo seleccionado es muy grande (>2000px). Esto puede afectar el rendimiento de generación del código QR. ¿Continuar de todos modos?',
        'error_correction_set_high': 'La corrección de errores se ha establecido automáticamente en Alta (30%) para garantizar la legibilidad del código QR con el logo.',
        'error_correction_warning': 'Al usar un logo, la corrección de errores debe permanecer en Alta (30%) para garantizar que el código QR siga siendo escaneable.',
        'logo_size_info': 'El tamaño del logo está limitado al 6.55% del área del código QR para un escaneo óptimo.',
        'logo': 'Logo:',
        'no_logo': 'No logo selected',
        'select_logo': 'Select Logo',
        'logo_loaded': 'Logo: {}',
        'error_loading_logo': 'Error loading logo: {}',
    },
    'es': {
        'app_title': 'QR Generator Pro 2.0',
        'language': 'Idioma',
        'english': 'English',
        'spanish': 'Español',
        'file': 'Archivo',
        'save_config': 'Guardar Configuración',
        'load_config': 'Cargar Configuración',
        'save_qr': 'Guardar Código QR',
        'save_as_pdf': 'Guardar como PDF',
        'save_as_png': 'Guardar como PNG',
        'print': 'Imprimir',
        'exit': 'Salir',
        'help_menu': 'Ayuda',
        'help': 'Ayuda',
        'about': 'Acerca de',
        'generator_tab': 'Generador QR',
        'settings_tab': 'Configuración',
        'batch_tab': 'Procesamiento por Lotes',
        'preview': 'Vista Previa',
        'qr_placeholder': 'El código QR aparecerá aquí',
        'qr_type': 'Tipo de Código QR',
        'data': 'Datos',
        'text': 'Texto',
        'text_label': 'Texto:',
        'url': 'URL',
        'url_label': 'URL:',
        'email': 'Email',
        'email_label': 'Email:',
        'subject_label': 'Asunto:',
        'message_label': 'Mensaje:',
        'phone': 'Teléfono',
        'phone_label': 'Teléfono:',
        'wifi': 'WiFi',
        'ssid_label': 'Nombre de Red (SSID):',
        'password_label': 'Contraseña:',
        'security_label': 'Seguridad:',
        'hidden_network': 'Red oculta',
        'sms': 'SMS',
        'vcard': 'vCard',
        'full_name_label': 'Nombre completo:',
        'organization_label': 'Organización:',
        'website_label': 'Sitio web:',
        'style': 'Estilo',
        'module_style': 'Estilo de módulos:',
        'square': 'Cuadrado',
        'rounded': 'Redondeado',
        'circle': 'Circular',
        'gapped': 'Con espacios',
        'vertical': 'Barras verticales',
        'main_color': 'Color principal:',
        'background_color': 'Color de fondo:',
        'use_gradient': 'Usar degradado',
        'pdf_options': 'Opciones de PDF',
        'title': 'Título:',
        'format_letter': 'Formato: Carta (Letter)',
        'save_as_image': 'Guardar como Imagen',
        'save_as_pdf': 'Guardar como PDF',
        'clear_all': 'Limpiar Todo',
        'error_correction': 'Nivel de Corrección de Errores',
        'low_ec': 'L - Bajo (7%)',
        'medium_ec': 'M - Medio (15%)',
        'quartile_ec': 'Q - Cuartil (25%)',
        'high_ec': 'H - Alto (30%)',
        'size_settings': 'Configuración de Tamaño',
        'module_size': 'Tamaño de módulo:',
        'border': 'Borde:',
        'auto_save': 'Guardado Automático',
        'enable_autosave': 'Habilitar guardado automático',
        'folder': 'Carpeta:',
        'save_settings': 'Guardar Configuración',
        'batch_instructions': 'Procese múltiples códigos QR desde un archivo CSV.\nEl archivo debe tener columnas: tipo, datos, titulo_pdf',
        'select_csv': 'Seleccionar CSV',
        'output_folder': 'Carpeta de salida:',
        'process_batch': 'Procesar Lote',
        'processing': 'Procesando {} de {}',
        'batch_complete': '¡Completado! {} códigos QR generados',
        'ready': 'Listo',
        'qr_generated': 'Código QR generado exitosamente',
        'image_saved': 'Imagen guardada: {}',
        'pdf_saved': 'PDF guardado: {}',
        'fields_cleared': 'Todos los campos han sido limpiados',
        'settings_saved': 'Configuración guardada exitosamente',
        'memory': 'Memoria: {:.1f} MB',
        'printing': 'Enviando a la impresora...',
        'error': 'Error',
        'no_qr_to_save': 'No hay código QR para guardar',
        'no_qr_to_print': 'No hay código QR para imprimir',
        'error_generating_qr': 'Error al generar código QR: {}',
        'error_saving_image': 'Error al guardar imagen: {}',
        'error_saving_pdf': 'Error al guardar PDF: {}',
        'error_saving_settings': 'Error al guardar configuración: {}',
        'error_batch': 'Error en procesamiento: {}',
        'error_printing': 'Error al imprimir: {}',
        'select_valid_csv': 'Por favor seleccione un archivo CSV válido',
        'success': 'Éxito',
        'image_saved_success': 'Imagen guardada exitosamente.\n¿Desea abrir la ubicación del archivo?',
        'pdf_saved_success': 'PDF guardado exitosamente.\n¿Desea abrir el archivo?',
        'batch_success': 'Procesamiento completado.\n{} archivos generados en:\n{}',
        'settings_loaded': 'Configuración cargada desde: {}',
        'settings_saved_to': 'Configuración guardada en: {}',
        'error_loading_config': 'Error al cargar configuración: {}',
        'help_text': '''QR Generator Pro 2.0

Atajos de teclado:
- Ctrl+S: Guardar como PDF
- Ctrl+I: Guardar como imagen
- Ctrl+R: Limpiar todo
- F1: Mostrar ayuda

Tipos de QR soportados:
- Texto simple
- URLs
- Email con asunto y mensaje
- Números de teléfono
- Redes WiFi
- SMS
- Tarjetas de contacto (vCard)

Características:
- Múltiples estilos de módulos
- Colores personalizables
- Degradados
- Guardado automático
- Procesamiento por lotes
- Exportación a PDF e imágenes''',
        'about_title': 'Acerca de QR Generator Pro',
        'about_text': '''QR Generator Pro 2.0

Un generador profesional de códigos QR con características avanzadas.

Características:
• Soporte para múltiples tipos de códigos QR
• Estilos y colores personalizables
• Exportación a PDF e imágenes
• Procesamiento por lotes
• Soporte multi-idioma

Desarrollado por LGP con mucha ayuda de Claude/Anthropic LLM

Desarrollado con Python y PySide6
© 2024 - Todos los derechos reservados''',
        'enter_data': 'Ingrese datos para generar el código QR',
        'generated_by': 'Generado por QR Generator Pro - {}',
        'images': 'Imágenes',
        'all_files': 'Todos los archivos',
        'save_as_pdf_title': 'Guardar como PDF',
        'select_autosave_folder': 'Seleccionar carpeta para guardado automático',
        'select_csv_file': 'Seleccionar archivo CSV',
        'select_color': 'Seleccionar Color',
        'more_colors': 'Más Colores...',
        'copy_qr': 'Copiar Código QR',
        'qr_copied': 'Código QR copiado al portapapeles',
        'theme': 'Tema',
        'light_theme': 'Claro',
        'dark_theme': 'Oscuro',
        'auto_theme': 'Auto',
    }
}


class Language(Enum):
    """Supported languages"""
    ENGLISH = "en"
    SPANISH = "es"


class QRType(Enum):
    """Enumeration for QR code types"""
    TEXT = "Text"
    URL = "URL"
    EMAIL = "Email"
    PHONE = "Phone"
    WIFI = "WiFi"
    SMS = "SMS"
    VCARD = "vCard"


class ModuleStyle(Enum):
    """Enumeration for QR module styles"""
    SQUARE = "Square"
    ROUNDED = "Rounded"
    CIRCLE = "Circle"
    GAPPED = "Gapped"
    VERTICAL = "Vertical"


class Theme(Enum):
    """Application themes"""
    LIGHT = "Light"
    DARK = "Dark"
    AUTO = "Auto"


@dataclass
class QRConfig:
    """Configuration for QR code generation"""
    error_correction: int = qrcode.constants.ERROR_CORRECT_H
    box_size: int = 10
    border: int = 4
    fill_color: str = "black"
    back_color: str = "white"
    module_style: ModuleStyle = ModuleStyle.SQUARE
    use_gradient: bool = False
    logo_path: Optional[str] = None
    logo_size_ratio: float = 0.0655  # Maximum 6.55% of QR code area


@dataclass
class AppConfig:
    """Application configuration"""
    window_width: int = 1200
    window_height: int = 800
    preview_size: int = 400
    autosave_enabled: bool = False
    autosave_path: str = "autosave"
    theme: Theme = Theme.LIGHT  # Default to light theme
    language: Language = Language.ENGLISH


class StyledButton(QPushButton):
    """Custom styled button with hover effects"""
    
    def __init__(self, text="", icon=None, primary=False, parent=None):
        super().__init__(text, parent)
        self.primary = primary
        self.setIcon(icon) if icon else None
        self._setup_style()
        
    def _setup_style(self):
        """Setup button style"""
        if self.primary:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLORS['primary']};
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 6px;
                    font-weight: bold;
                    font-size: 14px;
                    min-height: 20px;
                }}
                QPushButton:hover {{
                    background-color: {COLORS['primary_dark']};
                }}
                QPushButton:pressed {{
                    background-color: {COLORS['primary_light']};
                }}
                QPushButton:disabled {{
                    background-color: {COLORS['divider']};
                    color: {COLORS['text_secondary']};
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLORS['surface']};
                    color: {COLORS['text_primary']};
                    border: 2px solid {COLORS['divider']};
                    padding: 8px 16px;
                    border-radius: 6px;
                    font-size: 14px;
                    font-weight: 500;
                    min-height: 20px;
                }}
                QPushButton:hover {{
                    background-color: {COLORS['background']};
                    border-color: {COLORS['primary']};
                    color: {COLORS['primary']};
                }}
                QPushButton:pressed {{
                    background-color: {COLORS['divider']};
                }}
                QPushButton:disabled {{
                    background-color: {COLORS['background']};
                    color: {COLORS['text_secondary']};
                    border-color: {COLORS['divider']};
                }}
            """)
        
        # Add drop shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(8)
        shadow.setXOffset(0)
        shadow.setYOffset(2)
        shadow.setColor(QColor(0, 0, 0, 20))
        self.setGraphicsEffect(shadow)


class StyledLineEdit(QLineEdit):
    """Custom styled line edit with animations"""
    
    def __init__(self, placeholder="", parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self._setup_style()
        
    def _setup_style(self):
        """Setup line edit style"""
        self.setStyleSheet(f"""
            QLineEdit {{
                background-color: {COLORS['input_background']};
                color: {COLORS['text_primary']};
                border: 2px solid {COLORS['input_border']};
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
            }}
            QLineEdit:focus {{
                border-color: {COLORS['input_border_focus']};
            }}
            QLineEdit:disabled {{
                background-color: {COLORS['background']};
                color: {COLORS['text_secondary']};
            }}
        """)


class ColorButton(QPushButton):
    """Custom color picker button"""
    
    colorChanged = Signal(str)
    
    def __init__(self, color="#000000", parent=None):
        super().__init__(parent)
        self._color = color
        self._setup_ui()
        
    def _setup_ui(self):
        """Setup button UI"""
        self.setFixedSize(60, 30)
        self.setCursor(Qt.PointingHandCursor)
        self._update_style()
        self.clicked.connect(self._pick_color)
        
    def _update_style(self):
        """Update button style based on color"""
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {self._color};
                border: 2px solid {COLORS['divider']};
                border-radius: 5px;
            }}
            QPushButton:hover {{
                border-color: {COLORS['primary']};
            }}
        """)
        
    def _pick_color(self):
        """Open color picker dialog"""
        dialog = QColorDialog(QColor(self._color), self)
        
        # Apply light theme to color dialog
        dialog.setStyleSheet(f"""
            QColorDialog {{
                background-color: {COLORS['background']};
                color: {COLORS['text_primary']};
            }}
            QWidget {{
                background-color: {COLORS['background']};
                color: {COLORS['text_primary']};
            }}
            QLabel {{
                color: {COLORS['text_primary']};
                background-color: transparent;
            }}
            QLineEdit {{
                background-color: {COLORS['input_background']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['input_border']};
                padding: 5px;
            }}
            QSpinBox {{
                background-color: {COLORS['input_background']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['input_border']};
                padding: 5px;
            }}
            QPushButton {{
                background-color: {COLORS['surface']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['divider']};
                padding: 5px 15px;
                border-radius: 3px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['background']};
                border-color: {COLORS['primary']};
            }}
            QDialogButtonBox {{
                background-color: {COLORS['background']};
            }}
        """)
        
        dialog.setOption(QColorDialog.DontUseNativeDialog, True)  # Use Qt dialog instead of native
        
        if dialog.exec() == QColorDialog.Accepted:
            color = dialog.currentColor()
            self._color = color.name()
            self._update_style()
            self.colorChanged.emit(self._color)
            
    def color(self):
        """Get current color"""
        return self._color
        
    def setColor(self, color):
        """Set color"""
        self._color = color
        self._update_style()


class QRDataFormatter:
    """Handles formatting of different QR code data types"""
    
    @staticmethod
    def format_data(qr_type: QRType, data: Dict[str, str]) -> str:
        """Format data according to QR code type"""
        formatters = {
            QRType.TEXT: lambda d: d.get('text', ''),
            QRType.URL: lambda d: d.get('url', ''),
            QRType.EMAIL: lambda d: f"mailto:{d.get('email', '')}?subject={d.get('subject', '')}&body={d.get('body', '')}",
            QRType.PHONE: lambda d: f"tel:{d.get('phone', '')}",
            QRType.WIFI: lambda d: f"WIFI:T:{d.get('security', 'WPA')};S:{d.get('ssid', '')};P:{d.get('password', '')};H:{d.get('hidden', 'false')};;",
            QRType.SMS: lambda d: f"sms:{d.get('phone', '')}?body={d.get('message', '')}",
            QRType.VCARD: QRDataFormatter._format_vcard
        }
        
        formatter = formatters.get(qr_type, lambda d: d.get('text', ''))
        return formatter(data)
    
    @staticmethod
    def _format_vcard(data: Dict[str, str]) -> str:
        """Format vCard data"""
        vcard = ["BEGIN:VCARD", "VERSION:3.0"]
        
        if data.get('name'):
            vcard.append(f"FN:{data['name']}")
        if data.get('phone'):
            vcard.append(f"TEL:{data['phone']}")
        if data.get('email'):
            vcard.append(f"EMAIL:{data['email']}")
        if data.get('org'):
            vcard.append(f"ORG:{data['org']}")
        if data.get('url'):
            vcard.append(f"URL:{data['url']}")
        
        vcard.append("END:VCARD")
        return "\n".join(vcard)


class QRGenerator:
    """Core QR code generation logic"""
    
    def __init__(self, config: QRConfig):
        self.config = config
        self._qr = None
        self._current_data = None
    
    def _parse_color(self, color_str: str) -> Tuple[int, int, int]:
        """Parse color string to RGB tuple"""
        color_map = {
            'black': (0, 0, 0),
            'white': (255, 255, 255),
            'red': (255, 0, 0),
            'green': (0, 255, 0),
            'blue': (0, 0, 255),
            'yellow': (255, 255, 0),
            'cyan': (0, 255, 255),
            'magenta': (255, 0, 255),
            'gray': (128, 128, 128),
            'grey': (128, 128, 128),
        }
        
        color_lower = color_str.lower().strip()
        if color_lower in color_map:
            return color_map[color_lower]
        
        if color_str.startswith('#'):
            try:
                hex_color = color_str.lstrip('#')
                if len(hex_color) == 3:
                    hex_color = ''.join([c*2 for c in hex_color])
                if len(hex_color) == 6:
                    r = int(hex_color[0:2], 16)
                    g = int(hex_color[2:4], 16)
                    b = int(hex_color[4:6], 16)
                    return (r, g, b)
            except ValueError:
                pass
        
        logger.warning(f"Could not parse color '{color_str}', defaulting to black")
        return (0, 0, 0)
    
    def generate(self, data: str) -> Optional[Image.Image]:
        """Generate QR code image"""
        if not data:
            return None
        
        try:
            self._qr = qrcode.QRCode(
                error_correction=self.config.error_correction,
                box_size=self.config.box_size,
                border=self.config.border
            )
            self._qr.add_data(data)
            self._qr.make(fit=True)
            self._current_data = data
            
            module_drawer = self._get_module_drawer()
            
            if self.config.module_style == ModuleStyle.SQUARE and not self.config.use_gradient:
                img = self._qr.make_image(
                    fill_color=self.config.fill_color,
                    back_color=self.config.back_color
                )
            else:
                fill_rgb = self._parse_color(self.config.fill_color)
                back_rgb = self._parse_color(self.config.back_color)
                
                kwargs = {
                    'image_factory': StyledPilImage,
                    'module_drawer': module_drawer
                }
                
                if self.config.use_gradient:
                    kwargs['color_mask'] = SquareGradiantColorMask()
                else:
                    kwargs['color_mask'] = SolidFillColorMask(
                        front_color=fill_rgb,
                        back_color=back_rgb
                    )
                    
                img = self._qr.make_image(**kwargs)
            
            # Add logo if specified
            if self.config.logo_path and os.path.exists(self.config.logo_path):
                img = self._add_logo(img, self.config.logo_path)
            
            return img
            
        except Exception as e:
            logger.error(f"Error generating QR code: {e}")
            raise
    
    def _add_logo(self, qr_img: Image.Image, logo_path: str) -> Image.Image:
        """Add logo to QR code center with size validation (max 6.55% of area)"""
        try:
            # Open logo
            logo = Image.open(logo_path)
            
            # Convert to RGBA if needed
            if logo.mode != 'RGBA':
                logo = logo.convert('RGBA')
            
            # Calculate QR code dimensions
            qr_width, qr_height = qr_img.size
            qr_area = qr_width * qr_height
            
            # Calculate maximum allowed logo area (6.55% of QR code area)
            max_logo_area = qr_area * self.config.logo_size_ratio
            
            # Calculate maximum logo dimensions while maintaining aspect ratio
            logo_aspect = logo.width / logo.height
            
            # Start with current logo dimensions
            logo_width = logo.width
            logo_height = logo.height
            logo_area = logo_width * logo_height
            
            # Scale down if necessary to fit within 6.55% area constraint
            if logo_area > max_logo_area:
                scale_factor = (max_logo_area / logo_area) ** 0.5
                logo_width = int(logo.width * scale_factor)
                logo_height = int(logo.height * scale_factor)
            
            # Also ensure logo doesn't exceed 6.55% in any linear dimension
            # This means the logo shouldn't be larger than ~25.6% of the QR code's width/height
            max_dimension = int(min(qr_width, qr_height) * 0.256)
            
            if logo_width > max_dimension or logo_height > max_dimension:
                # Scale to fit within dimension constraint
                if logo_width > logo_height:
                    logo_width = max_dimension
                    logo_height = int(logo_width / logo_aspect)
                else:
                    logo_height = max_dimension
                    logo_width = int(logo_height * logo_aspect)
            
            # Resize logo
            logo = logo.resize((logo_width, logo_height), Image.Resampling.LANCZOS)
            
            # Final verification - ensure area is within 6.55%
            actual_logo_area = logo.width * logo.height
            if actual_logo_area > max_logo_area:
                # Extra safety - scale down by 10% more
                scale_factor = 0.9 * ((max_logo_area / actual_logo_area) ** 0.5)
                new_width = int(logo.width * scale_factor)
                new_height = int(logo.height * scale_factor)
                logo = logo.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Create a white background for the logo (with minimal padding)
            padding = 5  # Reduced padding to stay within 6.55%
            bg_size = (logo.size[0] + padding * 2, logo.size[1] + padding * 2)
            logo_bg = Image.new('RGBA', bg_size, 'white')
            
            # Paste logo on white background
            logo_bg.paste(logo, (padding, padding), logo)
            
            # Convert QR to RGBA
            if qr_img.mode != 'RGBA':
                qr_img = qr_img.convert('RGBA')
            
            # Calculate position (center)
            pos_x = (qr_width - logo_bg.size[0]) // 2
            pos_y = (qr_height - logo_bg.size[1]) // 2
            
            # Create a copy and paste logo
            result = qr_img.copy()
            result.paste(logo_bg, (pos_x, pos_y), logo_bg)
            
            # Log the actual coverage percentage for debugging
            final_logo_area = logo_bg.size[0] * logo_bg.size[1]
            coverage_percentage = (final_logo_area / qr_area) * 100
            logger.info(f"Logo coverage: {coverage_percentage:.2f}% of QR code (max allowed: 6.55%)")
            
            return result
            
        except Exception as e:
            logger.error(f"Error adding logo: {e}")
            return qr_img
    
    def _get_module_drawer(self):
        """Get the appropriate module drawer based on style"""
        drawers = {
            ModuleStyle.SQUARE: SquareModuleDrawer(),
            ModuleStyle.ROUNDED: RoundedModuleDrawer(),
            ModuleStyle.CIRCLE: CircleModuleDrawer(),
            ModuleStyle.GAPPED: GappedSquareModuleDrawer(),
            ModuleStyle.VERTICAL: VerticalBarsDrawer()
        }
        return drawers.get(self.config.module_style, SquareModuleDrawer())


class PDFGenerator:
    """Handles PDF generation with Letter size format"""
    
    def __init__(self, app=None):
        self.app = app
    
    def save_to_pdf(self, qr_img: Image.Image, output_path: str, 
                    title: str = "", metadata: Dict[str, str] = None) -> None:
        """Save QR code to PDF with metadata"""
        try:
            width, height = letter
            
            c = canvas.Canvas(output_path, pagesize=letter)
            
            if metadata:
                c.setAuthor(metadata.get('author', 'QR Generator Pro'))
                c.setTitle(metadata.get('title', 'QR Code'))
                c.setSubject(metadata.get('subject', 'Generated QR Code'))
            
            if title:
                c.setFont("Helvetica-Bold", 16)
                c.drawCentredString(width / 2, height - 1*inch, title)
            
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                qr_img.save(tmp.name, 'PNG')
                tmp_path = tmp.name
            
            try:
                img_size = min(width - 2*inch, height - 3*inch)
                x = (width - img_size) / 2
                y = (height - img_size) / 2
                
                c.drawImage(tmp_path, x, y, width=img_size, height=img_size)
                
                self._add_footer(c, width)
                
                c.save()
                
            finally:
                os.unlink(tmp_path)
                
        except Exception as e:
            logger.error(f"Error generating PDF: {e}")
            raise
    
    def _add_footer(self, c: canvas.Canvas, page_width: float) -> None:
        """Add footer to PDF"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        c.setFont("Helvetica", 8)
        c.setFillColor(colors.grey)
        
        footer_text = f"Generated by QR Generator Pro - {timestamp}"
            
        c.drawCentredString(
            page_width / 2, 
            0.5 * inch, 
            footer_text
        )


class BatchWorker(QThread):
    """Worker thread for batch processing"""
    
    progress = Signal(int, int)
    status = Signal(str)
    finished = Signal(int)
    error = Signal(str)
    
    def __init__(self, csv_path, output_dir, qr_generator, pdf_generator):
        super().__init__()
        self.csv_path = csv_path
        self.output_dir = output_dir
        self.qr_generator = qr_generator
        self.pdf_generator = pdf_generator
        
    def run(self):
        """Process batch QR codes"""
        try:
            # Create output directory
            Path(self.output_dir).mkdir(exist_ok=True)
            
            # Read CSV
            with open(self.csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
            
            total = len(rows)
            
            for i, row in enumerate(rows):
                # Update progress
                self.progress.emit(i + 1, total)
                
                # Generate QR
                qr_type = row.get('type', 'TEXT')
                data = row.get('data', '')
                title = row.get('pdf_title', f'QR_{i+1}')
                
                # Create QR
                qr_img = self.qr_generator.generate(data)
                
                if qr_img:
                    # Save as PDF
                    pdf_path = Path(self.output_dir) / f"{title}.pdf"
                    self.pdf_generator.save_to_pdf(
                        qr_img,
                        str(pdf_path),
                        title=title
                    )
            
            # Complete
            self.finished.emit(total)
            
        except Exception as e:
            logger.error(f"Batch processing error: {e}")
            self.error.emit(str(e))


class QRGeneratorApp(QMainWindow):
    """Main application class with enhanced features"""
    
    def __init__(self):
        super().__init__()
        self.app_config = AppConfig()
        self.qr_config = QRConfig()
        self.qr_generator = QRGenerator(self.qr_config)
        self.pdf_generator = PDFGenerator(self)
        
        # State variables
        self.qr_img: Optional[Image.Image] = None
        self.current_qr_type = QRType.TEXT
        self.current_language = Language.ENGLISH
        self._last_autosave_data = None
        self._autosave_timer = QTimer()
        self._autosave_timer.timeout.connect(self._auto_save)
        
        # Initialize variables for settings
        self.ec_var = None
        self.ec_button_group = None
        
        # Initialize UI
        self._setup_window()
        self._create_actions()
        self._create_menu_bar()
        self._create_toolbar()
        self._create_central_widget()
        self._create_status_bar()
        
        # Load saved configuration
        self._load_config()
        
        # Apply theme after all widgets are created
        QTimer.singleShot(50, self._apply_theme)
        
        # Generate initial QR code
        QTimer.singleShot(100, self._update_qr)
    
    def tr(self, key: str, *args) -> str:
        """Get translated string for current language"""
        text = TRANSLATIONS[self.current_language.value].get(key, key)
        if args:
            return text.format(*args)
        return text
    
    def _setup_window(self) -> None:
        """Setup main window"""
        self.setWindowTitle(self.tr('app_title'))
        self.resize(self.app_config.window_width, self.app_config.window_height)
        self.setMinimumSize(800, 600)
        
        # Set background color
        self.setStyleSheet(f"background-color: {COLORS['background']};")
        
        # Center window
        screen = QGuiApplication.primaryScreen().geometry()
        x = (screen.width() - self.app_config.window_width) // 2
        y = (screen.height() - self.app_config.window_height) // 2
        self.move(x, y)
        
        # Set window icon
        self.setWindowIcon(self.style().standardIcon(QStyle.SP_ComputerIcon))
    
    def _create_actions(self):
        """Create application actions"""
        # File actions
        self.save_config_action = QAction(self.tr('save_config'), self)
        self.save_config_action.setShortcut(QKeySequence("Ctrl+Shift+S"))
        self.save_config_action.triggered.connect(lambda: self._save_config(save_to_file=True))
        
        self.load_config_action = QAction(self.tr('load_config'), self)
        self.load_config_action.setShortcut(QKeySequence("Ctrl+O"))
        self.load_config_action.triggered.connect(self._load_config_dialog)
        
        self.save_pdf_action = QAction(self.tr('save_as_pdf'), self)
        self.save_pdf_action.setShortcut(QKeySequence("Ctrl+S"))
        self.save_pdf_action.triggered.connect(self._save_pdf)
        
        self.save_image_action = QAction(self.tr('save_as_png'), self)
        self.save_image_action.setShortcut(QKeySequence("Ctrl+I"))
        self.save_image_action.triggered.connect(self._save_image)
        
        self.print_action = QAction(self.tr('print'), self)
        self.print_action.setShortcut(QKeySequence("Ctrl+P"))
        self.print_action.triggered.connect(self._print_qr)
        
        self.exit_action = QAction(self.tr('exit'), self)
        self.exit_action.setShortcut(QKeySequence("Alt+F4"))
        self.exit_action.triggered.connect(self.close)
        
        # Edit actions
        self.clear_action = QAction(self.tr('clear_all'), self)
        self.clear_action.setShortcut(QKeySequence("Ctrl+R"))
        self.clear_action.triggered.connect(self._reset_all)
        
        self.copy_action = QAction(self.tr('copy_qr'), self)
        self.copy_action.setShortcut(QKeySequence("Ctrl+C"))
        self.copy_action.triggered.connect(self._copy_qr)
        
        # Help actions
        self.help_action = QAction(self.tr('help'), self)
        self.help_action.setShortcut(QKeySequence("F1"))
        self.help_action.triggered.connect(self._show_help)
        
        self.about_action = QAction(self.tr('about'), self)
        self.about_action.triggered.connect(self._show_about)
    
    def _create_menu_bar(self):
        """Create application menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu(self.tr('file'))
        file_menu.addAction(self.save_config_action)
        file_menu.addAction(self.load_config_action)
        file_menu.addSeparator()
        file_menu.addAction(self.save_pdf_action)
        file_menu.addAction(self.save_image_action)
        file_menu.addSeparator()
        file_menu.addAction(self.print_action)
        file_menu.addSeparator()
        file_menu.addAction(self.exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu("Edit")
        edit_menu.addAction(self.clear_action)
        edit_menu.addAction(self.copy_action)
        
        # Language menu
        language_menu = menubar.addMenu(self.tr('language'))
        
        english_action = QAction(self.tr('english'), self)
        english_action.triggered.connect(lambda: self._change_language(Language.ENGLISH))
        language_menu.addAction(english_action)
        
        spanish_action = QAction(self.tr('spanish'), self)
        spanish_action.triggered.connect(lambda: self._change_language(Language.SPANISH))
        language_menu.addAction(spanish_action)
        
        # Theme menu
        theme_menu = menubar.addMenu(self.tr('theme'))
        
        light_action = QAction(self.tr('light_theme'), self)
        light_action.triggered.connect(lambda: self._change_theme(Theme.LIGHT))
        theme_menu.addAction(light_action)
        
        dark_action = QAction(self.tr('dark_theme'), self)
        dark_action.triggered.connect(lambda: self._change_theme(Theme.DARK))
        theme_menu.addAction(dark_action)
        
        # Help menu
        help_menu = menubar.addMenu(self.tr('help_menu'))
        help_menu.addAction(self.help_action)
        help_menu.addSeparator()
        help_menu.addAction(self.about_action)
    
    def _create_toolbar(self):
        """Create application toolbar"""
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(32, 32))  # Larger, consistent icon size
        toolbar.setStyleSheet(f"""
            QToolBar {{
                spacing: 10px;
                padding: 8px;
            }}
        """)
        self.addToolBar(toolbar)
        
        # Common button style
        button_style = f"""
            QToolButton {{
                font-size: 28px;  /* Larger, consistent font size */
                padding: 10px;
                min-width: 50px;
                min-height: 50px;
                border-radius: 8px;
            }}
        """
        
        # Add toolbar actions with icons
        save_btn = QToolButton()
        save_btn.setText(ICONS['save'])
        save_btn.setToolTip(self.tr('save_as_image'))
        save_btn.clicked.connect(self._save_image)
        save_btn.setStyleSheet(button_style)
        toolbar.addWidget(save_btn)
        
        pdf_btn = QToolButton()
        pdf_btn.setText(ICONS['pdf'])
        pdf_btn.setToolTip(self.tr('save_as_pdf'))
        pdf_btn.clicked.connect(self._save_pdf)
        pdf_btn.setStyleSheet(button_style)
        toolbar.addWidget(pdf_btn)
        
        toolbar.addSeparator()
        
        copy_btn = QToolButton()
        copy_btn.setText(ICONS['copy'])
        copy_btn.setToolTip(self.tr('copy_qr'))
        copy_btn.clicked.connect(self._copy_qr)
        copy_btn.setStyleSheet(button_style)
        toolbar.addWidget(copy_btn)
        
        clear_btn = QToolButton()
        clear_btn.setText(ICONS['clear'])
        clear_btn.setToolTip(self.tr('clear_all'))
        clear_btn.clicked.connect(self._reset_all)
        clear_btn.setStyleSheet(button_style)
        toolbar.addWidget(clear_btn)
        
        toolbar.addSeparator()
        
        print_btn = QToolButton()
        print_btn.setText(ICONS['print'])
        print_btn.setToolTip(self.tr('print'))
        print_btn.clicked.connect(self._print_qr)
        print_btn.setStyleSheet(button_style)
        toolbar.addWidget(print_btn)
    
    def _create_central_widget(self):
        """Create the central widget with tabs"""
        central_widget = QWidget()
        central_widget.setStyleSheet(f"background-color: {COLORS['background']}; color: {COLORS['text_primary']};")
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setDocumentMode(True)
        self.tab_widget.setStyleSheet(f"""
            QTabWidget {{
                background-color: {COLORS['background']};
                color: {COLORS['text_primary']};
            }}
            QTabWidget::pane {{
                border: 1px solid {COLORS['divider']};
                background-color: {COLORS['surface']};
                border-radius: 4px;
                color: {COLORS['text_primary']};
            }}
            QTabBar::tab {{
                background-color: {COLORS['background']};
                color: {COLORS['text_secondary']};
                padding: 12px 24px;
                margin-right: 4px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                font-size: 14px;
                font-weight: 500;
                min-width: 100px;
            }}
            QTabBar::tab:selected {{
                background-color: {COLORS['surface']};
                color: {COLORS['primary']};
                border-bottom: 3px solid {COLORS['primary']};
                font-weight: bold;
            }}
            QTabBar::tab:hover {{
                background-color: {COLORS['surface']};
                color: {COLORS['text_primary']};
            }}
        """)
        layout.addWidget(self.tab_widget)
        
        # Create tabs
        self._create_generator_tab()
        self._create_settings_tab()
        self._create_batch_tab()
    
    def _create_generator_tab(self):
        """Create the main QR generator tab"""
        generator_widget = QWidget()
        # Ensure proper background and text color
        generator_widget.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['background']};
                color: {COLORS['text_primary']};
            }}
        """)
        self.tab_widget.addTab(generator_widget, self.tr('generator_tab'))
        
        layout = QHBoxLayout(generator_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Horizontal)
        splitter.setStyleSheet(f"""
            QSplitter {{
                background-color: {COLORS['background']};
            }}
            QSplitter::handle {{
                background-color: {COLORS['divider']};
                width: 4px;
            }}
        """)
        layout.addWidget(splitter)
        
        # Left panel - QR Preview
        preview_widget = self._create_preview_panel()
        splitter.addWidget(preview_widget)
        
        # Right panel - Controls
        controls_widget = self._create_controls_panel()
        splitter.addWidget(controls_widget)
        
        # Set initial splitter sizes
        splitter.setSizes([450, 550])
    
    def _create_preview_panel(self):
        """Create QR preview panel"""
        widget = QWidget()
        widget.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['surface']};
                color: {COLORS['text_primary']};
                border-radius: 8px;
            }}
            QLabel {{
                color: {COLORS['text_primary']};
                background-color: transparent;
            }}
        """)
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel(self.tr('preview'))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(f"""
            font-size: 20px;
            font-weight: bold;
            color: {COLORS['text_primary']};
            padding: 10px;
            background-color: transparent;
        """)
        layout.addWidget(title)
        
        # Preview container with white background
        preview_container = QFrame()
        preview_container.setStyleSheet(f"""
            QFrame {{
                background-color: #FFFFFF;
                border: 3px solid {COLORS['divider']};
                border-radius: 10px;
            }}
        """)
        preview_layout = QVBoxLayout(preview_container)
        preview_layout.setContentsMargins(20, 20, 20, 20)
        
        # QR preview label
        self.qr_preview = QLabel(self.tr('qr_placeholder'))
        self.qr_preview.setAlignment(Qt.AlignCenter)
        self.qr_preview.setMinimumSize(350, 350)
        self.qr_preview.setStyleSheet(f"""
            color: {COLORS['text_secondary']};
            font-size: 16px;
            background-color: transparent;
        """)
        preview_layout.addWidget(self.qr_preview)
        
        layout.addWidget(preview_container)
        
        # Action buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        self.save_image_btn = StyledButton(
            self.tr('save_as_image'),
            primary=True
        )
        self.save_image_btn.clicked.connect(self._save_image)
        button_layout.addWidget(self.save_image_btn)
        
        self.save_pdf_btn = StyledButton(
            self.tr('save_as_pdf'),
            primary=True
        )
        self.save_pdf_btn.clicked.connect(self._save_pdf)
        button_layout.addWidget(self.save_pdf_btn)
        
        layout.addLayout(button_layout)
        layout.addStretch()
        
        return widget
    
    def _create_controls_panel(self):
        """Create controls panel"""
        widget = QWidget()
        widget.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['surface']};
                color: {COLORS['text_primary']};
                border-radius: 8px;
            }}
            QLabel {{
                color: {COLORS['text_primary']};
                background-color: transparent;
            }}
        """)
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Create scroll area for controls
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setStyleSheet(f"""
            QScrollArea {{
                background-color: transparent;
                border: none;
            }}
            QScrollArea > QWidget > QWidget {{
                background-color: transparent;
            }}
            QScrollBar:vertical {{
                background-color: {COLORS['background']};
                width: 12px;
                border: none;
            }}
            QScrollBar::handle:vertical {{
                background-color: {COLORS['divider']};
                border-radius: 6px;
                min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {COLORS['text_secondary']};
            }}
        """)
        layout.addWidget(scroll_area)
        
        # Controls container
        controls_widget = QWidget()
        controls_widget.setStyleSheet("background-color: transparent;")
        controls_layout = QVBoxLayout(controls_widget)
        controls_layout.setSpacing(15)
        scroll_area.setWidget(controls_widget)
        
        # QR Type selection
        type_group = QGroupBox(self.tr('qr_type'))
        type_group.setStyleSheet(f"""
            QGroupBox {{
                font-weight: bold;
                font-size: 14px;
                color: {COLORS['text_primary']};
                border: 2px solid {COLORS['divider']};
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 15px;
                padding-bottom: 10px;
                background-color: {COLORS['background']};  /* Changed to F5F5F5 */
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
                color: {COLORS['group_title']};
                background-color: {COLORS['background']};  /* Changed to match */
            }}
        """)
        type_layout = QVBoxLayout(type_group)
        
        self.qr_type_combo = QComboBox()
        self.qr_type_combo.addItems([t.value for t in QRType])
        self.qr_type_combo.setStyleSheet(f"""
            QComboBox {{
                min-height: 35px;
                font-size: 14px;
                color: {COLORS['text_primary']};
                background-color: {COLORS['input_background']};
                border: 2px solid {COLORS['input_border']};
                border-radius: 5px;
                padding: 8px;
            }}
            QComboBox::drop-down {{
                border: none;
                width: 30px;
            }}
            QComboBox::down-arrow {{
                image: none;
                width: 0;
                height: 0;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid {COLORS['text_primary']};
                margin-right: 8px;
            }}
            QComboBox QAbstractItemView {{
                border: 1px solid {COLORS['divider']};
                background-color: white;  /* White background for dropdown */
                selection-background-color: {COLORS['primary']};  /* Blue selection */
                outline: none;
            }}
            QComboBox QAbstractItemView::item {{
                padding: 8px 12px;
                background-color: white;  /* White background */
                color: {COLORS['text_primary']};  /* Dark grey text */
                min-height: 30px;
            }}
            QComboBox QAbstractItemView::item:hover {{
                background-color: #E3F2FD;  /* Very light blue on hover */
                color: {COLORS['text_primary']};  /* Keep dark grey text */
            }}
            QComboBox QAbstractItemView::item:selected {{
                background-color: {COLORS['primary']};  /* Blue when clicked */
                color: white;  /* White text when selected */
            }}
        """)
        self.qr_type_combo.currentTextChanged.connect(self._on_qr_type_changed)
        type_layout.addWidget(self.qr_type_combo)
        
        controls_layout.addWidget(type_group)
        
        # Data input
        self.data_group = QGroupBox(self.tr('data'))
        self.data_group.setStyleSheet(f"""
            QGroupBox {{
                font-weight: bold;
                font-size: 14px;
                color: {COLORS['text_primary']};
                border: 2px solid {COLORS['divider']};
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 15px;
                padding-bottom: 10px;
                background-color: {COLORS['background']};  /* Changed to F5F5F5 */
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
                color: {COLORS['group_title']};
                background-color: {COLORS['background']};  /* Changed to match */
            }}
        """)
        self.data_layout = QVBoxLayout(self.data_group)
        controls_layout.addWidget(self.data_group)
        
        # Create stacked widget for different input types
        self.input_stack = QStackedWidget()
        self.input_stack.setStyleSheet("background-color: transparent;")
        self.data_layout.addWidget(self.input_stack)
        
        # Create input widgets for each type
        self.input_widgets = {}
        self._create_all_input_widgets()
        
        # Style options
        style_group = QGroupBox(self.tr('style'))
        style_group.setStyleSheet(f"""
            QGroupBox {{
                font-weight: bold;
                font-size: 14px;
                color: {COLORS['text_primary']};
                border: 2px solid {COLORS['divider']};
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 15px;
                padding-bottom: 10px;
                background-color: {COLORS['background']};  /* Changed to F5F5F5 */
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
                color: {COLORS['group_title']};
                background-color: {COLORS['background']};  /* Changed to match */
            }}
        """)
        style_layout = QGridLayout(style_group)
        style_layout.setSpacing(10)
        
        # Module style
        style_label = QLabel(self.tr('module_style'))
        style_label.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: 14px; font-weight: normal;")
        style_layout.addWidget(style_label, 0, 0)
        self.module_style_combo = QComboBox()
        self.module_style_combo.addItems([s.value for s in ModuleStyle])
        self.module_style_combo.setStyleSheet(f"""
            QComboBox {{
                min-height: 30px;
                color: {COLORS['text_primary']};
                background-color: {COLORS['input_background']};
                border: 2px solid {COLORS['input_border']};
                border-radius: 5px;
                padding: 5px;
                font-size: 14px;
            }}
            QComboBox::drop-down {{
                border: none;
                width: 30px;
            }}
            QComboBox::down-arrow {{
                image: none;
                width: 0;
                height: 0;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid {COLORS['text_primary']};
                margin-right: 8px;
            }}
            QComboBox QAbstractItemView {{
                border: 1px solid {COLORS['divider']};
                background-color: white;
                selection-background-color: {COLORS['primary']};
                outline: none;
            }}
            QComboBox QAbstractItemView::item {{
                padding: 8px 12px;
                background-color: white;
                color: {COLORS['text_primary']};
                min-height: 25px;
            }}
            QComboBox QAbstractItemView::item:hover {{
                background-color: #E3F2FD;  /* Very light blue on hover */
                color: {COLORS['text_primary']};
            }}
            QComboBox QAbstractItemView::item:selected {{
                background-color: {COLORS['primary']};
                color: white;
            }}
        """)
        self.module_style_combo.currentTextChanged.connect(lambda: self._update_qr())
        style_layout.addWidget(self.module_style_combo, 0, 1)
        
        # Colors
        color_label = QLabel(self.tr('main_color'))
        color_label.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: 14px; font-weight: normal;")
        style_layout.addWidget(color_label, 1, 0)
        self.color_button = ColorButton("#000000")
        self.color_button.colorChanged.connect(lambda: self._update_qr())
        style_layout.addWidget(self.color_button, 1, 1)
        
        bg_label = QLabel(self.tr('background_color'))
        bg_label.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: 14px; font-weight: normal;")
        style_layout.addWidget(bg_label, 2, 0)
        self.bg_color_button = ColorButton("#FFFFFF")
        self.bg_color_button.colorChanged.connect(lambda: self._update_qr())
        style_layout.addWidget(self.bg_color_button, 2, 1)
        
        # Gradient option
        self.gradient_check = QCheckBox(self.tr('use_gradient'))
        self.gradient_check.setStyleSheet(f"""
            QCheckBox {{
                color: {COLORS['text_primary']}; 
                font-size: 14px;
                font-weight: normal;
            }}
            QCheckBox::indicator {{
                width: 20px;
                height: 20px;
                border: 2px solid {COLORS['input_border']};
                border-radius: 4px;
                background-color: {COLORS['input_background']};
            }}
            QCheckBox::indicator:checked {{
                background-color: {COLORS['primary']};
                border-color: {COLORS['primary']};
            }}
        """)
        self.gradient_check.stateChanged.connect(lambda: self._update_qr())
        style_layout.addWidget(self.gradient_check, 3, 0, 1, 2)
        
        # Logo section
        style_layout.addWidget(QLabel(""), 4, 0)  # Spacer
        
        logo_label = QLabel(self.tr('logo'))
        logo_label.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: 14px; font-weight: normal;")
        style_layout.addWidget(logo_label, 5, 0)
        
        logo_frame = QFrame()
        logo_layout = QHBoxLayout(logo_frame)
        logo_layout.setContentsMargins(0, 0, 0, 0)
        
        self.logo_path_label = QLabel(self.tr('no_logo'))
        self.logo_path_label.setStyleSheet(f"""
            color: {COLORS['text_secondary']}; 
            font-size: 13px;
            padding: 5px;
            background-color: {COLORS['background']};
            border: 1px solid {COLORS['divider']};
            border-radius: 4px;
        """)
        self.logo_path_label.setWordWrap(True)
        logo_layout.addWidget(self.logo_path_label, 1)
        
        self.logo_btn = QPushButton("📁")
        self.logo_btn.setFixedSize(35, 35)
        self.logo_btn.setStyleSheet(f"""
            QPushButton {{
                font-size: 18px;
                background-color: {COLORS['surface']};
                border: 1px solid {COLORS['divider']};
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['background']};
                border-color: {COLORS['primary']};
            }}
        """)
        self.logo_btn.clicked.connect(self._load_logo)
        logo_layout.addWidget(self.logo_btn)
        
        self.remove_logo_btn = QPushButton("❌")
        self.remove_logo_btn.setFixedSize(35, 35)
        self.remove_logo_btn.setStyleSheet(f"""
            QPushButton {{
                font-size: 16px;
                background-color: {COLORS['surface']};
                border: 1px solid {COLORS['divider']};
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: #ffebee;
                border-color: #f44336;
            }}
        """)
        self.remove_logo_btn.clicked.connect(self._remove_logo)
        self.remove_logo_btn.setEnabled(False)
        logo_layout.addWidget(self.remove_logo_btn)
        
        style_layout.addWidget(logo_frame, 5, 1)
        
        controls_layout.addWidget(style_group)
        
        # PDF options
        pdf_group = QGroupBox(self.tr('pdf_options'))
        pdf_group.setStyleSheet(f"""
            QGroupBox {{
                font-weight: bold;
                font-size: 14px;
                color: {COLORS['text_primary']};
                border: 2px solid {COLORS['divider']};
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 15px;
                padding-bottom: 10px;
                background-color: {COLORS['background']};  /* Changed to F5F5F5 */
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
                color: {COLORS['group_title']};
                background-color: {COLORS['background']};  /* Changed to match */
            }}
        """)
        pdf_layout = QVBoxLayout(pdf_group)
        
        pdf_title_label = QLabel(self.tr('title'))
        pdf_title_label.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: 14px; font-weight: normal;")
        pdf_layout.addWidget(pdf_title_label)
        self.pdf_title_edit = StyledLineEdit()
        pdf_layout.addWidget(self.pdf_title_edit)
        
        controls_layout.addWidget(pdf_group)
        
        # Clear button
        self.clear_btn = StyledButton(self.tr('clear_all'))
        self.clear_btn.clicked.connect(self._reset_all)
        controls_layout.addWidget(self.clear_btn)
        
        # Add stretch at the end
        controls_layout.addStretch()
        
        return widget
    
    def _create_all_input_widgets(self):
        """Create input widgets for all QR types"""
        # Common label style
        label_style = f"color: {COLORS['text_primary']}; font-size: 14px; font-weight: 500; padding: 5px 0;"
        
        # Text input
        text_widget = QWidget()
        text_widget.setStyleSheet("background-color: transparent;")
        text_layout = QVBoxLayout(text_widget)
        text_layout.setContentsMargins(10, 5, 10, 10)  # Add margins for centering
        
        # Add some space at the top
        text_layout.addSpacing(10)
        
        text_label = QLabel(self.tr('text_label'))
        text_label.setStyleSheet(label_style)
        text_label.setAlignment(Qt.AlignCenter)  # Center the label
        text_layout.addWidget(text_label)
        
        self.text_input = QTextEdit()
        self.text_input.setMinimumHeight(150)  # Increased from 120
        self.text_input.setMaximumHeight(200)  # Increased max height
        self.text_input.setStyleSheet(f"""
            QTextEdit {{
                background-color: {COLORS['input_background']};
                color: {COLORS['text_primary']};
                font-size: 15px;  /* Slightly larger font */
                border: 2px solid {COLORS['input_border']};
                border-radius: 8px;
                padding: 12px;
            }}
            QTextEdit:focus {{
                border-color: {COLORS['input_border_focus']};
            }}
        """)
        self.text_input.setPlaceholderText("Enter your text here...")
        self.text_input.textChanged.connect(self._update_qr)
        text_layout.addWidget(self.text_input)
        
        # Add stretch at the bottom to center vertically
        text_layout.addStretch()
        
        self.input_widgets[QRType.TEXT] = text_widget
        self.input_stack.addWidget(text_widget)
        
        # URL input
        url_widget = QWidget()
        url_widget.setStyleSheet("background-color: transparent;")
        url_layout = QVBoxLayout(url_widget)
        url_layout.setContentsMargins(10, 5, 10, 10)  # Add margins for centering
        
        # Add space at the top
        url_layout.addSpacing(20)
        
        url_label = QLabel(self.tr('url_label'))
        url_label.setStyleSheet(label_style)
        url_label.setAlignment(Qt.AlignCenter)  # Center the label
        url_layout.addWidget(url_label)
        
        self.url_input = StyledLineEdit()
        self.url_input.setMinimumHeight(45)  # Make it taller
        self.url_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {COLORS['input_background']};
                color: {COLORS['text_primary']};
                border: 2px solid {COLORS['input_border']};
                border-radius: 8px;
                padding: 12px;
                font-size: 15px;
            }}
            QLineEdit:focus {{
                border-color: {COLORS['input_border_focus']};
            }}
        """)
        self.url_input.setPlaceholderText("https://example.com")
        self.url_input.textChanged.connect(self._update_qr)
        url_layout.addWidget(self.url_input)
        
        # Add stretch at the bottom to center vertically
        url_layout.addStretch()
        
        self.input_widgets[QRType.URL] = url_widget
        self.input_stack.addWidget(url_widget)
        
        # Email input
        email_widget = QWidget()
        email_widget.setStyleSheet("background-color: transparent;")
        email_layout = QVBoxLayout(email_widget)
        
        email_label = QLabel(self.tr('email_label'))
        email_label.setStyleSheet(label_style)
        email_layout.addWidget(email_label)
        self.email_input = StyledLineEdit()
        self.email_input.textChanged.connect(self._update_qr)
        email_layout.addWidget(self.email_input)
        
        subject_label = QLabel(self.tr('subject_label'))
        subject_label.setStyleSheet(label_style)
        email_layout.addWidget(subject_label)
        self.email_subject = StyledLineEdit()
        self.email_subject.textChanged.connect(self._update_qr)
        email_layout.addWidget(self.email_subject)
        
        message_label = QLabel(self.tr('message_label'))
        message_label.setStyleSheet(label_style)
        email_layout.addWidget(message_label)
        self.email_body = QTextEdit()
        self.email_body.setMaximumHeight(80)
        self.email_body.setStyleSheet(f"""
            QTextEdit {{
                background-color: {COLORS['input_background']};
                color: {COLORS['text_primary']};
                font-size: 14px;
            }}
        """)
        self.email_body.textChanged.connect(self._update_qr)
        email_layout.addWidget(self.email_body)
        
        self.input_widgets[QRType.EMAIL] = email_widget
        self.input_stack.addWidget(email_widget)
        
        # Phone input
        phone_widget = QWidget()
        phone_widget.setStyleSheet("background-color: transparent;")
        phone_layout = QVBoxLayout(phone_widget)
        phone_layout.setContentsMargins(10, 5, 10, 10)  # Add margins for centering
        
        # Add space at the top
        phone_layout.addSpacing(20)
        
        phone_label = QLabel(self.tr('phone_label'))
        phone_label.setStyleSheet(label_style)
        phone_label.setAlignment(Qt.AlignCenter)  # Center the label
        phone_layout.addWidget(phone_label)
        
        self.phone_input = StyledLineEdit()
        self.phone_input.setMinimumHeight(45)  # Make it taller
        self.phone_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {COLORS['input_background']};
                color: {COLORS['text_primary']};
                border: 2px solid {COLORS['input_border']};
                border-radius: 8px;
                padding: 12px;
                font-size: 15px;
            }}
            QLineEdit:focus {{
                border-color: {COLORS['input_border_focus']};
            }}
        """)
        self.phone_input.setPlaceholderText("+1 234 567 8900")
        self.phone_input.textChanged.connect(self._update_qr)
        phone_layout.addWidget(self.phone_input)
        
        # Add stretch at the bottom to center vertically
        phone_layout.addStretch()
        
        self.input_widgets[QRType.PHONE] = phone_widget
        self.input_stack.addWidget(phone_widget)
        
        # WiFi input
        wifi_widget = QWidget()
        wifi_widget.setStyleSheet("background-color: transparent;")
        wifi_layout = QVBoxLayout(wifi_widget)
        
        ssid_label = QLabel(self.tr('ssid_label'))
        ssid_label.setStyleSheet(label_style)
        wifi_layout.addWidget(ssid_label)
        self.wifi_ssid = StyledLineEdit()
        self.wifi_ssid.textChanged.connect(self._update_qr)
        wifi_layout.addWidget(self.wifi_ssid)
        
        pass_label = QLabel(self.tr('password_label'))
        pass_label.setStyleSheet(label_style)
        wifi_layout.addWidget(pass_label)
        self.wifi_password = StyledLineEdit()
        self.wifi_password.setEchoMode(QLineEdit.Password)
        self.wifi_password.textChanged.connect(self._update_qr)
        wifi_layout.addWidget(self.wifi_password)
        
        sec_label = QLabel(self.tr('security_label'))
        sec_label.setStyleSheet(label_style)
        wifi_layout.addWidget(sec_label)
        self.wifi_security = QComboBox()
        self.wifi_security.addItems(["WPA", "WEP", "nopass"])
        self.wifi_security.setStyleSheet("min-height: 30px;")
        self.wifi_security.currentTextChanged.connect(self._update_qr)
        wifi_layout.addWidget(self.wifi_security)
        
        self.wifi_hidden = QCheckBox(self.tr('hidden_network'))
        self.wifi_hidden.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: 14px;")
        self.wifi_hidden.stateChanged.connect(self._update_qr)
        wifi_layout.addWidget(self.wifi_hidden)
        
        self.input_widgets[QRType.WIFI] = wifi_widget
        self.input_stack.addWidget(wifi_widget)
        
        # SMS input
        sms_widget = QWidget()
        sms_widget.setStyleSheet("background-color: transparent;")
        sms_layout = QVBoxLayout(sms_widget)
        
        sms_phone_label = QLabel(self.tr('phone_label'))
        sms_phone_label.setStyleSheet(label_style)
        sms_layout.addWidget(sms_phone_label)
        self.sms_phone = StyledLineEdit()
        self.sms_phone.textChanged.connect(self._update_qr)
        sms_layout.addWidget(self.sms_phone)
        
        sms_msg_label = QLabel(self.tr('message_label'))
        sms_msg_label.setStyleSheet(label_style)
        sms_layout.addWidget(sms_msg_label)
        self.sms_message = QTextEdit()
        self.sms_message.setMaximumHeight(80)
        self.sms_message.setStyleSheet(f"""
            QTextEdit {{
                background-color: {COLORS['input_background']};
                color: {COLORS['text_primary']};
                font-size: 14px;
            }}
        """)
        self.sms_message.textChanged.connect(self._update_qr)
        sms_layout.addWidget(self.sms_message)
        
        self.input_widgets[QRType.SMS] = sms_widget
        self.input_stack.addWidget(sms_widget)
        
        # vCard input
        vcard_widget = QWidget()
        vcard_widget.setStyleSheet("background-color: transparent;")
        vcard_layout = QVBoxLayout(vcard_widget)
        
        name_label = QLabel(self.tr('full_name_label'))
        name_label.setStyleSheet(label_style)
        vcard_layout.addWidget(name_label)
        self.vcard_name = StyledLineEdit()
        self.vcard_name.textChanged.connect(self._update_qr)
        vcard_layout.addWidget(self.vcard_name)
        
        vcard_phone_label = QLabel(self.tr('phone_label'))
        vcard_phone_label.setStyleSheet(label_style)
        vcard_layout.addWidget(vcard_phone_label)
        self.vcard_phone = StyledLineEdit()
        self.vcard_phone.textChanged.connect(self._update_qr)
        vcard_layout.addWidget(self.vcard_phone)
        
        vcard_email_label = QLabel(self.tr('email_label'))
        vcard_email_label.setStyleSheet(label_style)
        vcard_layout.addWidget(vcard_email_label)
        self.vcard_email = StyledLineEdit()
        self.vcard_email.textChanged.connect(self._update_qr)
        vcard_layout.addWidget(self.vcard_email)
        
        org_label = QLabel(self.tr('organization_label'))
        org_label.setStyleSheet(label_style)
        vcard_layout.addWidget(org_label)
        self.vcard_org = StyledLineEdit()
        self.vcard_org.textChanged.connect(self._update_qr)
        vcard_layout.addWidget(self.vcard_org)
        
        web_label = QLabel(self.tr('website_label'))
        web_label.setStyleSheet(label_style)
        vcard_layout.addWidget(web_label)
        self.vcard_url = StyledLineEdit()
        self.vcard_url.textChanged.connect(self._update_qr)
        vcard_layout.addWidget(self.vcard_url)
        
        self.input_widgets[QRType.VCARD] = vcard_widget
        self.input_stack.addWidget(vcard_widget)
    
    def _create_settings_tab(self):
        """Create settings tab"""
        settings_widget = QWidget()
        self.tab_widget.addTab(settings_widget, self.tr('settings_tab'))
        
        layout = QVBoxLayout(settings_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Error correction level
        ec_group = QGroupBox(self.tr('error_correction'))
        ec_layout = QVBoxLayout(ec_group)
        
        self.ec_var = "H"  # Initialize as string for current selection
        self.ec_button_group = QButtonGroup()
        ec_levels = [
            (self.tr('low_ec'), qrcode.constants.ERROR_CORRECT_L, "L"),
            (self.tr('medium_ec'), qrcode.constants.ERROR_CORRECT_M, "M"),
            (self.tr('quartile_ec'), qrcode.constants.ERROR_CORRECT_Q, "Q"),
            (self.tr('high_ec'), qrcode.constants.ERROR_CORRECT_H, "H")
        ]
        
        for i, (text, level, code) in enumerate(ec_levels):
            radio = QRadioButton(text)
            radio.clicked.connect(lambda checked, c=code: self._on_ec_changed_radio(c))
            self.ec_button_group.addButton(radio, level)
            ec_layout.addWidget(radio)
            if level == qrcode.constants.ERROR_CORRECT_H:
                radio.setChecked(True)
        
        layout.addWidget(ec_group)
        
        # Size settings
        size_group = QGroupBox(self.tr('size_settings'))
        size_layout = QHBoxLayout(size_group)  # Changed to horizontal layout
        size_layout.setSpacing(20)  # Add spacing between the two controls
        size_layout.setContentsMargins(20, 10, 20, 10)  # Add margins for centering
        
        # Module size container
        module_container = QVBoxLayout()
        module_container.setAlignment(Qt.AlignCenter)
        
        self.module_size_label = QLabel(self.tr('module_size'))
        self.module_size_label.setAlignment(Qt.AlignCenter)
        module_container.addWidget(self.module_size_label)
        
        self.module_size_spin = QSpinBox()
        self.module_size_spin.setRange(1, 50)
        self.module_size_spin.setValue(10)
        self.module_size_spin.valueChanged.connect(self._update_qr)
        self.module_size_spin.setFixedWidth(60)  # Fixed width for 3 characters
        self.module_size_spin.setAlignment(Qt.AlignCenter)
        self.module_size_spin.setStyleSheet(f"""
            QSpinBox {{
                font-size: 14px;
                height: 35px;
            }}
        """)
        module_container.addWidget(self.module_size_spin, alignment=Qt.AlignCenter)
        
        size_layout.addLayout(module_container)
        
        # Border container
        border_container = QVBoxLayout()
        border_container.setAlignment(Qt.AlignCenter)
        
        self.border_label = QLabel(self.tr('border'))
        self.border_label.setAlignment(Qt.AlignCenter)
        border_container.addWidget(self.border_label)
        
        self.border_spin = QSpinBox()
        self.border_spin.setRange(0, 10)
        self.border_spin.setValue(4)
        self.border_spin.valueChanged.connect(self._update_qr)
        self.border_spin.setFixedWidth(60)  # Fixed width for 3 characters
        self.border_spin.setAlignment(Qt.AlignCenter)
        self.border_spin.setStyleSheet(f"""
            QSpinBox {{
                font-size: 14px;
                height: 35px;
            }}
        """)
        border_container.addWidget(self.border_spin, alignment=Qt.AlignCenter)
        
        size_layout.addLayout(border_container)
        
        layout.addWidget(size_group)
        
        # Auto save settings
        autosave_group = QGroupBox(self.tr('auto_save'))
        autosave_layout = QVBoxLayout(autosave_group)
        
        self.autosave_check = QCheckBox(self.tr('enable_autosave'))
        self.autosave_check.stateChanged.connect(self._on_autosave_changed)
        autosave_layout.addWidget(self.autosave_check)
        
        folder_layout = QHBoxLayout()
        folder_layout.addWidget(QLabel(self.tr('folder')))
        self.autosave_path_edit = StyledLineEdit()
        self.autosave_path_edit.setText("autosave")
        folder_layout.addWidget(self.autosave_path_edit)
        
        browse_btn = StyledButton(ICONS['folder'])
        browse_btn.clicked.connect(self._select_autosave_folder)
        folder_layout.addWidget(browse_btn)
        
        autosave_layout.addLayout(folder_layout)
        layout.addWidget(autosave_group)
        
        # Save settings button
        save_settings_btn = StyledButton(self.tr('save_settings'), primary=True)
        save_settings_btn.clicked.connect(self._save_config)
        layout.addWidget(save_settings_btn)
        
        # Add stretch
        layout.addStretch()
    
    def _create_batch_tab(self):
        """Create batch processing tab"""
        batch_widget = QWidget()
        self.tab_widget.addTab(batch_widget, self.tr('batch_tab'))
        
        layout = QVBoxLayout(batch_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Instructions
        instructions = QLabel(self.tr('batch_instructions'))
        instructions.setAlignment(Qt.AlignCenter)
        instructions.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['text_secondary']};
                font-size: 14px;
                padding: 20px;
                background-color: {COLORS['background']};
                border-radius: 5px;
            }}
        """)
        layout.addWidget(instructions)
        
        # File selection
        file_group = QGroupBox("CSV File")
        file_layout = QHBoxLayout(file_group)
        
        self.batch_file_edit = StyledLineEdit()
        self.batch_file_edit.setReadOnly(True)
        file_layout.addWidget(self.batch_file_edit)
        
        select_csv_btn = StyledButton(self.tr('select_csv'))
        select_csv_btn.clicked.connect(self._select_batch_file)
        file_layout.addWidget(select_csv_btn)
        
        layout.addWidget(file_group)
        
        # Output folder
        output_group = QGroupBox(self.tr('output_folder'))
        output_layout = QHBoxLayout(output_group)
        
        self.batch_output_edit = StyledLineEdit()
        self.batch_output_edit.setText("batch_output")
        output_layout.addWidget(self.batch_output_edit)
        
        browse_output_btn = StyledButton(ICONS['folder'])
        browse_output_btn.clicked.connect(self._select_batch_output)
        output_layout.addWidget(browse_output_btn)
        
        layout.addWidget(output_group)
        
        # Progress
        self.batch_progress = QProgressBar()
        self.batch_progress.setTextVisible(True)
        self.batch_progress.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid {COLORS['divider']};
                border-radius: 5px;
                text-align: center;
                height: 25px;
            }}
            QProgressBar::chunk {{
                background-color: {COLORS['primary']};
                border-radius: 4px;
            }}
        """)
        layout.addWidget(self.batch_progress)
        
        self.batch_status = QLabel("")
        self.batch_status.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.batch_status)
        
        # Process button
        self.batch_process_btn = StyledButton(self.tr('process_batch'), primary=True)
        self.batch_process_btn.clicked.connect(self._process_batch)
        layout.addWidget(self.batch_process_btn)
        
        # Add stretch
        layout.addStretch()
    
    def _create_status_bar(self):
        """Create status bar"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Status message
        self.status_label = QLabel(self.tr('ready'))
        self.status_bar.addWidget(self.status_label)
        
        # Memory usage
        self.memory_label = QLabel()
        self.status_bar.addPermanentWidget(self.memory_label)
        
        # Start memory timer
        self.memory_timer = QTimer()
        self.memory_timer.timeout.connect(self._update_memory_usage)
        self.memory_timer.start(2000)
        self._update_memory_usage()
    
    def _apply_theme(self):
        """Apply application theme"""
        if self.app_config.theme == Theme.LIGHT:
            self._apply_light_theme()
        elif self.app_config.theme == Theme.DARK:
            self._apply_dark_theme()
        
        # Force refresh all widgets
        self.update()
        self.repaint()
        
        # Update all child widgets safely
        for widget in self.findChildren(QWidget):
            try:
                # Skip QListView and other widgets that need special handling
                if not isinstance(widget, (QListWidget, QComboBox)):
                    widget.update()
                widget.style().unpolish(widget)
                widget.style().polish(widget)
            except:
                pass  # Skip any widgets that can't be updated
    
    def _apply_light_theme(self):
        """Apply light theme"""
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {COLORS['background']};
            }}
            QGroupBox {{
                font-weight: bold;
                border: 2px solid {COLORS['divider']};
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }}
            QTabWidget::pane {{
                border: 1px solid {COLORS['divider']};
                background-color: {COLORS['surface']};
            }}
            QTabBar::tab {{
                background-color: {COLORS['background']};
                padding: 10px 20px;
                margin-right: 2px;
            }}
            QTabBar::tab:selected {{
                background-color: {COLORS['surface']};
                border-bottom: 2px solid {COLORS['primary']};
            }}
            QTextEdit {{
                border: 2px solid {COLORS['divider']};
                border-radius: 5px;
                padding: 5px;
                background-color: {COLORS['surface']};
            }}
            QTextEdit:focus {{
                border-color: {COLORS['primary']};
            }}
            QComboBox {{
                border: 2px solid {COLORS['divider']};
                border-radius: 5px;
                padding: 8px;
                background-color: {COLORS['surface']};
            }}
            QComboBox:focus {{
                border-color: {COLORS['primary']};
            }}
            QComboBox::drop-down {{
                border: none;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid {COLORS['text_primary']};
                margin-right: 5px;
            }}
            QSpinBox {{
                border: 2px solid {COLORS['divider']};
                border-radius: 5px;
                padding: 5px;
                background-color: {COLORS['surface']};
            }}
            QSpinBox:focus {{
                border-color: {COLORS['primary']};
            }}
            QCheckBox {{
                spacing: 10px;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border: 2px solid {COLORS['divider']};
                border-radius: 3px;
                background-color: {COLORS['surface']};
            }}
            QCheckBox::indicator:checked {{
                background-color: {COLORS['primary']};
                border-color: {COLORS['primary']};
            }}
            QRadioButton {{
                spacing: 10px;
            }}
            QRadioButton::indicator {{
                width: 18px;
                height: 18px;
                border: 2px solid {COLORS['divider']};
                border-radius: 9px;
                background-color: {COLORS['surface']};
            }}
            QRadioButton::indicator:checked {{
                background-color: {COLORS['primary']};
                border-color: {COLORS['primary']};
            }}
            QStatusBar {{
                background-color: {COLORS['background']};
                border-top: 1px solid {COLORS['divider']};
            }}
            QToolBar {{
                background-color: {COLORS['surface']};
                border-bottom: 1px solid {COLORS['divider']};
                spacing: 5px;
                padding: 5px;
            }}
            QToolButton {{
                background-color: transparent;
                border: none;
                padding: 5px;
                border-radius: 5px;
                font-size: 20px;
            }}
            QToolButton:hover {{
                background-color: {COLORS['background']};
            }}
            QToolButton:pressed {{
                background-color: {COLORS['divider']};
            }}
            QScrollBar:vertical {{
                background-color: {COLORS['background']};
                width: 12px;
                border: none;
            }}
            QScrollBar::handle:vertical {{
                background-color: {COLORS['divider']};
                border-radius: 6px;
                min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {COLORS['text_secondary']};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
        """)
    
    def _apply_dark_theme(self):
        """Apply dark theme"""
        # Dark theme colors
        dark_colors = {
            'primary': '#2196F3',
            'primary_dark': '#1565C0',
            'primary_light': '#64B5F6',
            'secondary': '#FF4081',
            'accent': '#00BCD4',
            'success': '#4CAF50',
            'warning': '#FF9800',
            'error': '#F44336',
            'background': '#121212',
            'surface': '#1E1E1E',
            'on_surface': '#FFFFFF',
            'text_primary': '#FFFFFF',
            'text_secondary': '#B0B0B0',
            'divider': '#333333',
        }
        
        # Apply dark theme stylesheet
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {dark_colors['background']};
                color: {dark_colors['text_primary']};
            }}
            /* ... (similar to light theme but with dark colors) ... */
        """)
    
    def _change_language(self, language: Language):
        """Change application language"""
        self.current_language = language
        self.app_config.language = language
        self._update_ui_texts()
        self._save_config()
    
    def _change_theme(self, theme: Theme):
        """Change application theme"""
        self.app_config.theme = theme
        self._apply_theme()
        self._save_config()
    
    def _update_ui_texts(self):
        """Update all UI texts with current language"""
        # Update window title
        self.setWindowTitle(self.tr('app_title'))
        
        # Update menus
        self.menuBar().clear()
        self._create_menu_bar()
        
        # Update tab names
        self.tab_widget.setTabText(0, self.tr('generator_tab'))
        self.tab_widget.setTabText(1, self.tr('settings_tab'))
        self.tab_widget.setTabText(2, self.tr('batch_tab'))
        
        # Update all labels and buttons
        # This would need to be implemented for all UI elements
        # For brevity, showing just a few examples:
        self.save_image_btn.setText(self.tr('save_as_image'))
        self.save_pdf_btn.setText(self.tr('save_as_pdf'))
        self.clear_btn.setText(self.tr('clear_all'))
    
    def _on_qr_type_changed(self, text):
        """Handle QR type change"""
        self.current_qr_type = QRType(text)
        
        # Switch to appropriate input widget
        index = list(self.input_widgets.keys()).index(self.current_qr_type)
        self.input_stack.setCurrentIndex(index)
        
        # Update QR code
        self._update_qr()
    
    def _on_ec_changed(self):
        """Handle error correction level change"""
        self.qr_config.error_correction = self.ec_button_group.checkedId()
        self._update_qr()
    
    def _on_autosave_changed(self, state):
        """Handle autosave toggle"""
        self.app_config.autosave_enabled = state == Qt.Checked
        if self.app_config.autosave_enabled:
            self._autosave_timer.start(2000)  # Check every 2 seconds
        else:
            self._autosave_timer.stop()
    
    def _get_input_data(self) -> Dict[str, str]:
        """Get input data based on current QR type"""
        data = {}
        
        if self.current_qr_type == QRType.TEXT:
            data['text'] = self.text_input.toPlainText()
        elif self.current_qr_type == QRType.URL:
            data['url'] = self.url_input.text()
        elif self.current_qr_type == QRType.EMAIL:
            data['email'] = self.email_input.text()
            data['subject'] = self.email_subject.text()
            data['body'] = self.email_body.toPlainText()
        elif self.current_qr_type == QRType.PHONE:
            data['phone'] = self.phone_input.text()
        elif self.current_qr_type == QRType.WIFI:
            data['ssid'] = self.wifi_ssid.text()
            data['password'] = self.wifi_password.text()
            data['security'] = self.wifi_security.currentText()
            data['hidden'] = 'true' if self.wifi_hidden.isChecked() else 'false'
        elif self.current_qr_type == QRType.SMS:
            data['phone'] = self.sms_phone.text()
            data['message'] = self.sms_message.toPlainText()
        elif self.current_qr_type == QRType.VCARD:
            data['name'] = self.vcard_name.text()
            data['phone'] = self.vcard_phone.text()
            data['email'] = self.vcard_email.text()
            data['org'] = self.vcard_org.text()
            data['url'] = self.vcard_url.text()
        
        return data
    
    def _load_logo(self):
        """Load logo file with validation"""
        file_filter = f"{self.tr('images')} (*.png *.jpg *.jpeg *.gif *.bmp);;{self.tr('all_files')} (*.*)"
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            self.tr('select_logo'),
            "",
            file_filter
        )
        
        if file_path:
            try:
                # Open and validate image
                with Image.open(file_path) as img:
                    # Get image info without closing the file
                    img_format = img.format
                    img_mode = img.mode
                    img_width = img.width
                    img_height = img.height
                
                # Check if it's a valid image format
                if img_format not in ['PNG', 'JPEG', 'GIF', 'BMP', 'WEBP']:
                    self._show_error(self.tr('error_loading_logo', 'Unsupported image format'))
                    return
                
                # Check image dimensions
                if img_width > 2000 or img_height > 2000:
                    reply = QMessageBox.warning(
                        self,
                        self.tr('warning'),
                        self.tr('logo_too_large'),
                        QMessageBox.Ok | QMessageBox.Cancel
                    )
                    if reply == QMessageBox.Cancel:
                        return
                
                # Set logo path
                self.qr_config.logo_path = file_path
                self.logo_path_label.setText(self.tr('logo_loaded', Path(file_path).name))
                self.logo_path_label.setStyleSheet(f"""
                    color: {COLORS['text_primary']}; 
                    font-size: 13px;
                    padding: 5px;
                    background-color: {COLORS['background']};
                    border: 1px solid {COLORS['primary']};
                    border-radius: 4px;
                """)
                self.remove_logo_btn.setEnabled(True)
                
                # Automatically set error correction to High (30%) when logo is added - silently
                self.ec_var = "H"
                self.qr_config.error_correction = qrcode.constants.ERROR_CORRECT_H
                # Update the radio button
                for button in self.ec_button_group.buttons():
                    if self.ec_button_group.id(button) == qrcode.constants.ERROR_CORRECT_H:
                        button.setChecked(True)
                        break
                
                self._update_qr()
                
            except Exception as e:
                logger.error(f"Error loading logo: {e}")
                self._show_error(self.tr('error_loading_logo', str(e)))
    
    def _remove_logo(self):
        """Remove logo"""
        self.qr_config.logo_path = None
        self.logo_path_label.setText(self.tr('no_logo'))
        self.logo_path_label.setStyleSheet(f"""
            color: {COLORS['text_secondary']}; 
            font-size: 13px;
            padding: 5px;
            background-color: {COLORS['background']};
            border: 1px solid {COLORS['divider']};
            border-radius: 4px;
        """)
        self.remove_logo_btn.setEnabled(False)
        self._update_qr()
    
    def _update_qr(self):
        """Update QR code preview"""
        try:
            # Get input data
            data = self._get_input_data()
            
            # Format data according to type
            formatted_data = QRDataFormatter.format_data(self.current_qr_type, data)
            
            if not formatted_data:
                self.qr_preview.setText(self.tr('enter_data'))
                self.qr_preview.setPixmap(QPixmap())
                self.qr_img = None
                return
            
            # Update QR configuration
            self.qr_config.box_size = self.module_size_spin.value()
            self.qr_config.border = self.border_spin.value()
            self.qr_config.fill_color = self.color_button.color()
            self.qr_config.back_color = self.bg_color_button.color()
            self.qr_config.use_gradient = self.gradient_check.isChecked()
            
            # Find selected module style
            selected_style = self.module_style_combo.currentText()
            self.qr_config.module_style = ModuleStyle(selected_style)
            
            # Recreate generator with new config
            self.qr_generator = QRGenerator(self.qr_config)
            
            # Generate QR code
            self.qr_img = self.qr_generator.generate(formatted_data)
            
            # Update preview
            if self.qr_img:
                # Convert PIL image to QPixmap
                qr_bytes = BytesIO()
                self.qr_img.save(qr_bytes, format='PNG')
                qr_bytes.seek(0)
                
                pixmap = QPixmap()
                pixmap.loadFromData(qr_bytes.read())
                
                # Scale to fit preview
                scaled_pixmap = pixmap.scaled(
                    self.app_config.preview_size,
                    self.app_config.preview_size,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                
                self.qr_preview.setPixmap(scaled_pixmap)
                self._update_status(self.tr('qr_generated'))
                
                # Check for autosave
                if self.app_config.autosave_enabled:
                    self._check_autosave(formatted_data)
                    
        except Exception as e:
            logger.error(f"Error updating QR: {e}")
            self._show_error(self.tr('error_generating_qr', str(e)))
    
    def _check_autosave(self, data: str):
        """Check if data has changed for autosave"""
        if data != self._last_autosave_data:
            self._last_autosave_data = data
            # Autosave will be triggered by timer
    
    def _auto_save(self):
        """Auto-save QR code if enabled and data has changed"""
        if not self.app_config.autosave_enabled or not self.qr_img:
            return
        
        try:
            # Create autosave directory
            save_dir = Path(self.autosave_path_edit.text())
            save_dir.mkdir(exist_ok=True)
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"qr_{self.current_qr_type.name.lower()}_{timestamp}.png"
            save_path = save_dir / filename
            
            # Save image
            self.qr_img.save(str(save_path))
            logger.info(f"Auto-saved to: {save_path}")
            
        except Exception as e:
            logger.error(f"Auto-save failed: {e}")
    
    def _save_image(self):
        """Save QR code as image"""
        if not self.qr_img:
            self._show_error(self.tr('no_qr_to_save'))
            return
        
        file_filter = f"{self.tr('images')} (*.png *.jpg *.jpeg *.bmp *.gif);;{self.tr('all_files')} (*.*)"
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            self.tr('save_qr'),
            "",
            file_filter
        )
        
        if file_path:
            try:
                # Determine format from extension
                ext = Path(file_path).suffix.lower()
                format_map = {
                    '.jpg': 'JPEG',
                    '.jpeg': 'JPEG',
                    '.png': 'PNG',
                    '.bmp': 'BMP',
                    '.gif': 'GIF'
                }
                
                save_format = format_map.get(ext, 'PNG')
                
                # Convert RGBA to RGB for JPEG
                save_img = self.qr_img
                if save_format == 'JPEG' and save_img.mode == 'RGBA':
                    rgb_img = Image.new('RGB', save_img.size, 'white')
                    rgb_img.paste(save_img, mask=save_img.split()[3])
                    save_img = rgb_img
                
                save_img.save(file_path, save_format)
                self._update_status(self.tr('image_saved', Path(file_path).name))
                
                # Ask to open file location
                reply = QMessageBox.question(
                    self,
                    self.tr('success'),
                    self.tr('image_saved_success'),
                    QMessageBox.Yes | QMessageBox.No
                )
                
                if reply == QMessageBox.Yes:
                    self._open_file_location(file_path)
                    
            except Exception as e:
                logger.error(f"Error saving image: {e}")
                self._show_error(self.tr('error_saving_image', str(e)))
    
    def _save_pdf(self):
        """Save QR code as PDF"""
        if not self.qr_img:
            self._show_error(self.tr('no_qr_to_save'))
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            self.tr('save_as_pdf_title'),
            "",
            "PDF (*.pdf)"
        )
        
        if file_path:
            try:
                metadata = {
                    'author': 'QR Generator Pro',
                    'title': self.pdf_title_edit.text() or self.tr('qr_type'),
                    'subject': f'QR Code - {self.current_qr_type.value}'
                }
                
                self.pdf_generator.save_to_pdf(
                    self.qr_img,
                    file_path,
                    title=self.pdf_title_edit.text(),
                    metadata=metadata
                )
                
                self._update_status(self.tr('pdf_saved', Path(file_path).name))
                
                reply = QMessageBox.question(
                    self,
                    self.tr('success'),
                    self.tr('pdf_saved_success'),
                    QMessageBox.Yes | QMessageBox.No
                )
                
                if reply == QMessageBox.Yes:
                    self._open_file(file_path)
                    
            except Exception as e:
                logger.error(f"Error saving PDF: {e}")
                self._show_error(self.tr('error_saving_pdf', str(e)))
    
    def _copy_qr(self):
        """Copy QR code to clipboard"""
        if not self.qr_img:
            self._show_error(self.tr('no_qr_to_save'))
            return
        
        try:
            # Convert PIL image to QPixmap
            qr_bytes = BytesIO()
            self.qr_img.save(qr_bytes, format='PNG')
            qr_bytes.seek(0)
            
            pixmap = QPixmap()
            pixmap.loadFromData(qr_bytes.read())
            
            # Copy to clipboard
            clipboard = QGuiApplication.clipboard()
            clipboard.setPixmap(pixmap)
            
            self._update_status(self.tr('qr_copied'))
            
        except Exception as e:
            logger.error(f"Error copying QR: {e}")
    
    def _print_qr(self):
        """Print QR code"""
        if not self.qr_img:
            self._show_error(self.tr('no_qr_to_print'))
            return
        
        try:
            # Create a temporary PDF for printing
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
                tmp_path = tmp.name
            
            # Generate PDF with current settings
            metadata = {
                'author': 'QR Generator Pro',
                'title': self.pdf_title_edit.text() or self.tr('qr_type'),
                'subject': f'QR Code - {self.current_qr_type.value}'
            }
            
            self.pdf_generator.save_to_pdf(
                self.qr_img,
                tmp_path,
                title=self.pdf_title_edit.text(),
                metadata=metadata
            )
            
            # Print the PDF using the default system method
            if sys.platform == "win32":
                os.startfile(tmp_path, "print")
            elif sys.platform == "darwin":
                os.system(f'lpr "{tmp_path}"')
            else:
                os.system(f'lp "{tmp_path}"')
            
            # Clean up temporary file after a delay
            QTimer.singleShot(10000, lambda: self._cleanup_temp_file(tmp_path))
            
            self._update_status(self.tr('printing'))
            
        except Exception as e:
            logger.error(f"Error printing: {e}")
            self._show_error(self.tr('error_printing', str(e)))
    
    def _cleanup_temp_file(self, filepath: str):
        """Clean up temporary file"""
        try:
            if os.path.exists(filepath):
                os.unlink(filepath)
        except Exception as e:
            logger.error(f"Error cleaning up temp file: {e}")
    
    def _reset_all(self):
        """Reset all fields"""
        # Clear all input fields
        self.text_input.clear()
        self.url_input.clear()
        self.email_input.clear()
        self.email_subject.clear()
        self.email_body.clear()
        self.phone_input.clear()
        self.wifi_ssid.clear()
        self.wifi_password.clear()
        self.wifi_hidden.setChecked(False)
        self.sms_phone.clear()
        self.sms_message.clear()
        self.vcard_name.clear()
        self.vcard_phone.clear()
        self.vcard_email.clear()
        self.vcard_org.clear()
        self.vcard_url.clear()
        self.pdf_title_edit.clear()
        
        # Clear logo
        self._remove_logo()
        
        # Clear QR preview
        self.qr_img = None
        self.qr_preview.setText(self.tr('qr_placeholder'))
        self.qr_preview.setPixmap(QPixmap())
        
        self._update_status(self.tr('fields_cleared'))
    
    def _select_autosave_folder(self):
        """Select autosave folder"""
        folder = QFileDialog.getExistingDirectory(
            self,
            self.tr('select_autosave_folder'),
            self.autosave_path_edit.text()
        )
        if folder:
            self.autosave_path_edit.setText(folder)
            self.app_config.autosave_path = folder
    
    def _select_batch_file(self):
        """Select CSV file for batch processing"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            self.tr('select_csv_file'),
            "",
            "CSV (*.csv)"
        )
        if file_path:
            self.batch_file_edit.setText(file_path)
    
    def _select_batch_output(self):
        """Select batch output folder"""
        folder = QFileDialog.getExistingDirectory(
            self,
            self.tr('output_folder'),
            self.batch_output_edit.text()
        )
        if folder:
            self.batch_output_edit.setText(folder)
    
    def _process_batch(self):
        """Process batch QR codes"""
        csv_path = self.batch_file_edit.text()
        if not csv_path or not Path(csv_path).exists():
            self._show_error(self.tr('select_valid_csv'))
            return
        
        output_dir = self.batch_output_edit.text()
        
        # Disable button during processing
        self.batch_process_btn.setEnabled(False)
        self.batch_progress.setValue(0)
        
        # Create worker thread
        self.batch_worker = BatchWorker(
            csv_path,
            output_dir,
            self.qr_generator,
            self.pdf_generator
        )
        
        # Connect signals
        self.batch_worker.progress.connect(self._update_batch_progress)
        self.batch_worker.status.connect(self._update_batch_status)
        self.batch_worker.finished.connect(self._batch_finished)
        self.batch_worker.error.connect(self._batch_error)
        
        # Start processing
        self.batch_worker.start()
    
    @Slot(int, int)
    def _update_batch_progress(self, current, total):
        """Update batch progress"""
        progress = int((current / total) * 100)
        self.batch_progress.setValue(progress)
        self.batch_status.setText(self.tr('processing', current, total))
    
    @Slot(str)
    def _update_batch_status(self, status):
        """Update batch status"""
        self.batch_status.setText(status)
    
    @Slot(int)
    def _batch_finished(self, total):
        """Handle batch processing completion"""
        self.batch_process_btn.setEnabled(True)
        self.batch_status.setText(self.tr('batch_complete', total))
        
        QMessageBox.information(
            self,
            self.tr('success'),
            self.tr('batch_success', total, self.batch_output_edit.text())
        )
    
    @Slot(str)
    def _batch_error(self, error):
        """Handle batch processing error"""
        self.batch_process_btn.setEnabled(True)
        self._show_error(self.tr('error_batch', error))
    
    def _save_config(self, save_to_file: bool = False):
        """Save application configuration"""
        try:
            config = {
                'autosave_enabled': self.app_config.autosave_enabled,
                'autosave_path': self.app_config.autosave_path,
                'error_correction': self.qr_config.error_correction,
                'box_size': self.module_size_spin.value(),
                'border': self.border_spin.value(),
                'module_style': self.module_style_combo.currentText(),
                'language': self.current_language.value,
                'theme': self.app_config.theme.value,
                'logo_path': self.qr_config.logo_path
            }
            
            if save_to_file:
                file_path, _ = QFileDialog.getSaveFileName(
                    self,
                    self.tr('save_config'),
                    "",
                    "JSON (*.json)"
                )
                
                if file_path:
                    with open(file_path, 'w') as f:
                        json.dump(config, f, indent=2)
                    self._update_status(self.tr('settings_saved_to', Path(file_path).name))
            else:
                # Save to default location
                settings = QSettings('QRGeneratorPro', 'Settings')
                for key, value in config.items():
                    settings.setValue(key, value)
                self._update_status(self.tr('settings_saved'))
                
        except Exception as e:
            logger.error(f"Error saving config: {e}")
            self._show_error(self.tr('error_saving_settings', str(e)))
    
    def _load_config(self):
        """Load saved configuration"""
        try:
            settings = QSettings('QRGeneratorPro', 'Settings')
            
            # Load settings
            self.app_config.autosave_enabled = settings.value('autosave_enabled', False, type=bool)
            self.app_config.autosave_path = settings.value('autosave_path', 'autosave', type=str)
            
            ec_level = settings.value('error_correction', qrcode.constants.ERROR_CORRECT_H, type=int)
            for button in self.ec_button_group.buttons():
                if self.ec_button_group.id(button) == ec_level:
                    button.setChecked(True)
                    break
            
            self.module_size_spin.setValue(settings.value('box_size', 10, type=int))
            self.border_spin.setValue(settings.value('border', 4, type=int))
            
            module_style = settings.value('module_style', ModuleStyle.SQUARE.value, type=str)
            self.module_style_combo.setCurrentText(module_style)
            
            # Load language preference
            saved_lang = settings.value('language', 'en', type=str)
            self.current_language = Language.ENGLISH if saved_lang == 'en' else Language.SPANISH
            self.app_config.language = self.current_language
            
            # Load theme
            saved_theme = settings.value('theme', Theme.LIGHT.value, type=str)
            self.app_config.theme = Theme(saved_theme)
            
            # Load logo path
            logo_path = settings.value('logo_path', None, type=str)
            if logo_path and os.path.exists(logo_path):
                try:
                    # Validate the logo still exists and is valid
                    with Image.open(logo_path) as img:
                        # Just check if it's valid
                        img_format = img.format
                    
                    self.qr_config.logo_path = logo_path
                    self.logo_path_label.setText(self.tr('logo_loaded', Path(logo_path).name))
                    self.logo_path_label.setStyleSheet(f"""
                        color: {COLORS['text_primary']}; 
                        font-size: 13px;
                        padding: 5px;
                        background-color: {COLORS['background']};
                        border: 1px solid {COLORS['primary']};
                        border-radius: 4px;
                    """)
                    self.remove_logo_btn.setEnabled(True)
                except Exception as e:
                    logger.warning(f"Could not load saved logo: {e}")
                    self.qr_config.logo_path = None
            
            # Apply loaded settings
            self.autosave_check.setChecked(self.app_config.autosave_enabled)
            self.autosave_path_edit.setText(self.app_config.autosave_path)
            self._on_ec_changed()
            
        except Exception as e:
            logger.error(f"Error loading config: {e}")
    
    def _load_config_dialog(self):
        """Load configuration from file dialog"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            self.tr('load_config'),
            "",
            "JSON (*.json)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    config = json.load(f)
                
                # Apply configuration
                self.app_config.autosave_enabled = config.get('autosave_enabled', False)
                self.app_config.autosave_path = config.get('autosave_path', 'autosave')
                
                ec_level = config.get('error_correction', qrcode.constants.ERROR_CORRECT_H)
                for button in self.ec_button_group.buttons():
                    if self.ec_button_group.id(button) == ec_level:
                        button.setChecked(True)
                        break
                
                self.module_size_spin.setValue(config.get('box_size', 10))
                self.border_spin.setValue(config.get('border', 4))
                self.module_style_combo.setCurrentText(config.get('module_style', ModuleStyle.SQUARE.value))
                
                # Load language preference
                saved_lang = config.get('language', 'en')
                new_language = Language.ENGLISH if saved_lang == 'en' else Language.SPANISH
                if new_language != self.current_language:
                    self._change_language(new_language)
                
                # Load theme
                saved_theme = config.get('theme', Theme.LIGHT.value)
                self._change_theme(Theme(saved_theme))
                
                # Update UI
                self.autosave_check.setChecked(self.app_config.autosave_enabled)
                self.autosave_path_edit.setText(self.app_config.autosave_path)
                self._on_ec_changed()
                self._update_qr()
                
                self._update_status(self.tr('settings_loaded', Path(file_path).name))
                
            except Exception as e:
                logger.error(f"Error loading config: {e}")
                self._show_error(self.tr('error_loading_config', str(e)))
    
    def _show_help(self):
        """Show help dialog"""
        QMessageBox.information(
            self,
            self.tr('help'),
            self.tr('help_text')
        )
    
    def _show_about(self):
        """Show about dialog"""
        QMessageBox.information(
            self,
            self.tr('about_title'),
            self.tr('about_text')
        )
    
    def _update_status(self, message: str):
        """Update status bar"""
        self.status_label.setText(message)
        QTimer.singleShot(5000, lambda: self.status_label.setText(self.tr('ready')))
    
    def _update_memory_usage(self):
        """Update memory usage display"""
        try:
            import psutil
            process = psutil.Process(os.getpid())
            memory_mb = process.memory_info().rss / 1024 / 1024
            self.memory_label.setText(self.tr('memory', memory_mb))
        except:
            pass
    
    def _show_error(self, message: str):
        """Show error message"""
        QMessageBox.critical(self, self.tr('error'), message)
        self._update_status(f"{self.tr('error')}: {message}")
    
    def _open_file(self, path: str):
        """Open file with default application"""
        try:
            if sys.platform == "win32":
                os.startfile(path)
            elif sys.platform == "darwin":
                os.system(f'open "{path}"')
            else:
                os.system(f'xdg-open "{path}"')
        except Exception as e:
            logger.error(f"Error opening file: {e}")
    
    def _open_file_location(self, path: str):
        """Open file location in explorer"""
        try:
            folder = str(Path(path).parent)
            if sys.platform == "win32":
                os.startfile(folder)
            elif sys.platform == "darwin":
                os.system(f'open "{folder}"')
            else:
                os.system(f'xdg-open "{folder}"')
        except Exception as e:
            logger.error(f"Error opening folder: {e}")


def main():
    """Main entry point"""
    try:
        app = QApplication(sys.argv)
        
        # Set application info
        app.setApplicationName("QR Generator Pro")
        app.setOrganizationName("QRGeneratorPro")
        
        # Set application style
        app.setStyle(QStyleFactory.create('Fusion'))
        
        # Set default font
        default_font = QFont("Arial", 10)
        app.setFont(default_font)
        
        # Create and show main window
        window = QRGeneratorApp()
        
        # Force light theme and proper styling
        window.app_config.theme = Theme.LIGHT
        QTimer.singleShot(100, window._apply_theme)  # Apply theme after window is shown
        
        window.show()
        
        sys.exit(app.exec())
        
    except Exception as e:
        logger.critical(f"Fatal error: {e}")
        traceback.print_exc()
        try:
            QMessageBox.critical(None, "Fatal Error", f"The application encountered a critical error:\n{str(e)}")
        except:
            print(f"Fatal Error: {e}")


if __name__ == '__main__':
    main()