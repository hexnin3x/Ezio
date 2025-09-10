import sys
import os
import time
from dotenv import dotenv_values
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTextEdit, QStackedWidget,
                             QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QFrame, QSizePolicy)
from PyQt5.QtGui import (QIcon, QPainter, QMovie, QColor,
                         QTextCharFormat, QFont, QPixmap, QTextBlockFormat)
from PyQt5.QtCore import Qt, QSize, QTimer

# --- 1. SETUP & HELPER FUNCTIONS ---

env_vars = dotenv_values(".env")
ASSISTANT_NAME = env_vars.get("Assistantname", "Jarvis")
CURRENT_DIR = os.getcwd()
TempDirPath = os.path.join(CURRENT_DIR, "Frontend", "Files")
GraphicsDirPath = os.path.join(CURRENT_DIR, "Frontend", "Graphics")
old_chat_message = ""

os.makedirs(TempDirPath, exist_ok=True)
os.makedirs(GraphicsDirPath, exist_ok=True)

def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    modified_answer = '\n'.join(non_empty_lines)
    return modified_answer

def QueryModifier(Query):
    new_query = Query.lower().strip()
    query_words = new_query.split()
    question_words = ["how", "what", "who", "where", "when", "why", "which", "whose", "whom", "can you", "what's", "where's", "how's"]

    if any(word + " " in new_query for word in question_words):
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + "?"
        else:
            new_query += "?"
    else:
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + "."
        else:
            new_query += "."

    return new_query.capitalize()

def SetMicrophoneStatus(Command):
    with open(rf'{TempDirPath}\Mic.data', "w", encoding='utf-8') as file:
        file.write(Command)

def GetMicrophoneStatus():
    with open(rf'{TempDirPath}\Mic.data', "r", encoding='utf-8') as file:
        Status = file.read()
    return Status

def SetAssistantStatus(Status):
    with open(rf'{TempDirPath}\Status.data', "w", encoding='utf-8') as file:
        file.write(Status)

def GetAssistantStatus():
    with open(rf'{TempDirPath}\Status.data', "r", encoding='utf-8') as file:
        Status = file.read()
    return Status

def MicButtonInitialed():
    SetMicrophoneStatus("False")

def MicButtonClosed():
    SetMicrophoneStatus("True")

def GraphicsDirectoryPath(Filename):
    Path = rf'{GraphicsDirPath}\{Filename}'
    return Path

def TempDirectoryPath(Filename):
    Path = rf'{TempDirPath}\{Filename}'
    return Path

def ShowTextToScreen(Text):
    with open(rf'{TempDirPath}\Responses.data', "w", encoding='utf-8') as file:
        file.write(Text)

# --- 2. WIDGET CLASSES ---

class ChatSection(QWidget):
    def __init__(self):
        super().__init__()
        self.old_chat_message = ""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        self.chat_text_edit = QTextEdit()
        self.chat_text_edit.setReadOnly(True)
        self.chat_text_edit.setFrameStyle(QFrame.NoFrame)
        font = QFont("Arial", 12)
        self.chat_text_edit.setFont(font)
        layout.addWidget(self.chat_text_edit)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.loadMessages)
        self.timer.start(100)

        self.setStyleSheet("""
            background-color: black;
            QTextEdit { color: white; }
            QScrollBar:vertical {
                border: none; background: black; width: 10px; margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #555555; min-height: 20px; border-radius: 5px;
            }
        """)

    def loadMessages(self):
        try:
            with open(TempDirectoryPath('Responses.data'), "r", encoding='utf-8') as file:
                message = file.read().strip()
            if message and message != self.old_chat_message:
                self.addMessage(f"{ASSISTANT_NAME}: {message}", '#50C878')
                self.old_chat_message = message
        except FileNotFoundError:
            pass

    def addMessage(self, message, color):
        cursor = self.chat_text_edit.textCursor()
        cursor.movePosition(cursor.End)
        text_format = QTextCharFormat()
        text_format.setForeground(QColor(color))
        cursor.setCharFormat(text_format)
        cursor.insertText(message + "\n\n")
        self.chat_text_edit.ensureCursorVisible()

class InitialScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        content_layout = QVBoxLayout(self)
        content_layout.setSpacing(20)

        # GIF Setup
        gif_label = QLabel(self)
        movie = QMovie(GraphicsDirectoryPath('Jarvis.gif'))
        gif_width = 960
        gif_height = 540
        gif_label.setFixedSize(gif_width, gif_height)
        movie.setScaledSize(QSize(gif_width, gif_height))
        gif_label.setMovie(movie)
        movie.start()
        
        # Icon Label Setup
        self.icon_label = QLabel(self)
        self.icon_label.setFixedSize(120, 120)
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.icon_label.setStyleSheet("background-color: #222; border-radius: 60px;")
        
        # Status Label Setup
        self.label = QLabel(self)
        self.label.setStyleSheet("color: white; font-size:16px;")
        self.label.setAlignment(Qt.AlignCenter)

        # Layout Assembly
        content_layout.addStretch(1)
        content_layout.addWidget(gif_label, 0, Qt.AlignCenter)
        content_layout.addWidget(self.label, 0, Qt.AlignCenter)
        content_layout.addWidget(self.icon_label, 0, Qt.AlignCenter)
        content_layout.addStretch(1)

        self.setStyleSheet("background-color: black;")
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.SpeechRecogText)
        self.timer.start(100)
        
        self.toggled = False
        self.toggle_icon()
        self.icon_label.mousePressEvent = self.toggle_icon

    def SpeechRecogText(self):
        try:
            with open(TempDirectoryPath('Status.data'), "r", encoding='utf-8') as file:
                self.label.setText(file.read().strip())
        except FileNotFoundError:
            self.label.setText("Click the mic to start")

    def load_icon(self, path, width=50, height=50):
        pixmap = QPixmap(path)
        self.icon_label.setPixmap(pixmap.scaled(width, height, Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def toggle_icon(self, event=None):
        self.toggled = not self.toggled
        if self.toggled:
            self.load_icon(GraphicsDirectoryPath('Mic_on.png'), 50, 50)
            MicButtonClosed()
        else:
            self.load_icon(GraphicsDirectoryPath('Mic_off.png'), 50, 50)
            MicButtonInitialed()

class MessageScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        chat_section = ChatSection()
        layout.addWidget(chat_section)

class CustomTopBar(QWidget):
    def __init__(self, parent, stacked_widget):
        super().__init__(parent)
        self.parent_window = parent
        self.stacked_widget = stacked_widget
        self.initUI()
        self.draggable = True
        self.offset = None

    def initUI(self):
        self.setFixedHeight(50)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 0, 5, 0)
        layout.setSpacing(10)
        
        title_label = QLabel(ASSISTANT_NAME)
        # REVERTED: Title color is now white to be visible on the black background.
        title_label.setStyleSheet("color: white; font-size: 18px; font-weight: bold;")
        
        home_button = QPushButton(" Home")
        home_button.setIcon(QIcon(GraphicsDirectoryPath("Home.png")))
        message_button = QPushButton(" Chat")
        message_button.setIcon(QIcon(GraphicsDirectoryPath("Chats.png")))
        
        # REVERTED: Button text color is now white.
        for btn in [home_button, message_button]:
            btn.setStyleSheet("color: white; border:none; text-align: left; padding-left: 10px;")

        home_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        message_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        
        minimize_button = QPushButton()
        minimize_button.setIcon(QIcon(GraphicsDirectoryPath('Minimize2.png')))
        self.maximize_button = QPushButton()
        self.maximize_icon = QIcon(GraphicsDirectoryPath('Maximize.png'))
        self.restore_icon = QIcon(GraphicsDirectoryPath('Minimize.png'))
        self.maximize_button.setIcon(self.maximize_icon)
        close_button = QPushButton()
        close_button.setIcon(QIcon(GraphicsDirectoryPath('close.png')))
        
        for btn in [minimize_button, self.maximize_button, close_button]:
            btn.setStyleSheet("background-color:transparent; border:none;")
            btn.setFixedSize(40, 40)
            btn.setIconSize(QSize(18, 18))

        minimize_button.clicked.connect(self.minimizeWindow)
        self.maximize_button.clicked.connect(self.maximizeWindow)
        close_button.clicked.connect(self.closeWindow)
        
        layout.addWidget(title_label)
        layout.addStretch()
        layout.addWidget(home_button)
        layout.addWidget(message_button)
        layout.addSpacing(20)
        layout.addWidget(minimize_button)
        layout.addWidget(self.maximize_button)
        layout.addWidget(close_button)

    def minimizeWindow(self): self.parent_window.showMinimized()
    def closeWindow(self): self.parent_window.close()

    def maximizeWindow(self):
        if self.parent_window.isMaximized():
            self.parent_window.showNormal()
            self.maximize_button.setIcon(self.maximize_icon)
        else:
            self.parent_window.showMaximized()
            self.maximize_button.setIcon(self.restore_icon)
    
    def mousePressEvent(self, event):
        if self.draggable and event.button() == Qt.LeftButton:
            self.offset = event.pos()

    def mouseMoveEvent(self, event):
        if self.draggable and self.offset is not None and event.buttons() == Qt.LeftButton:
            self.parent_window.move(self.parent_window.pos() + event.pos() - self.offset)
            
    # REVERTED: The paintEvent was removed so the top bar will inherit the main window's black background.

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setStyleSheet("background-color: black;")
        self.initUI()

    def initUI(self):
        stacked_widget = QStackedWidget()
        initial_screen = InitialScreen()
        message_screen = MessageScreen()
        stacked_widget.addWidget(initial_screen)
        stacked_widget.addWidget(message_screen)
        
        top_bar = CustomTopBar(self, stacked_widget)
        
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0,0,0,0)
        main_layout.setSpacing(0)
        main_layout.addWidget(top_bar)
        main_layout.addWidget(stacked_widget)
        
        self.setCentralWidget(central_widget)

# --- 3. MAIN EXECUTION ---
def GraphicalUserInterface():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.showMaximized()
    sys.exit(app.exec_())

if __name__ == "__main__":
    GraphicalUserInterface()