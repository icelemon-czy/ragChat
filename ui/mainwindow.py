from PyQt5.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QSplitter
from PyQt5.QtCore import Qt

from .chat_widget import ChatWidget
from .knowledge_widget import KnowledgeWidget

class MainWindow(QMainWindow):
    def __init__(self, rag_service):
        super().__init__()
        self.rag_service = rag_service
        self.setWindowTitle("Tongyi RAG Desktop")
        self.resize(1200, 800)
        
        # Central Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Splitter
        splitter = QSplitter(Qt.Horizontal)
        
        # Left: Chat
        self.chat_widget = ChatWidget(self.rag_service)
        splitter.addWidget(self.chat_widget)
        
        # Right: Knowledge Base
        self.knowledge_widget = KnowledgeWidget(self.rag_service)
        splitter.addWidget(self.knowledge_widget)
        
        # Set initial sizes (60% Chat, 40% Knowledge)
        splitter.setSizes([700, 500])
        splitter.setCollapsible(0, False)
        splitter.setCollapsible(1, False)
        
        main_layout.addWidget(splitter)
        
        # Apply strict styling
        self.setStyleSheet("""
            QMainWindow { background-color: white; }
            QLabel { color: black; }
            QGroupBox { color: black; font-weight: bold; }
        """)
        
        # Trigger initial load of docs
        # We can trigger it now that the loop is running (after this returns)
        # But for safety, we rely on the manual refresh or button inside knowledge widget for now.
