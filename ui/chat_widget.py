from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListView, QLineEdit, QPushButton, QLabel
)
from PyQt5.QtCore import Qt
from qasync import asyncSlot
from .chat_model import ChatModel, ChatDelegate

class ChatWidget(QWidget):
    def __init__(self, rag_service, parent=None):
        super().__init__(parent)
        self.rag_service = rag_service
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("AI Assistant")
        header.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px;")
        layout.addWidget(header)
        
        # Chat List
        self.chat_view = QListView()
        self.chat_model = ChatModel()
        self.delegate = ChatDelegate()
        
        self.chat_view.setModel(self.chat_model)
        self.chat_view.setItemDelegate(self.delegate)
        self.chat_view.setSelectionMode(QListView.NoSelection)
        self.chat_view.setSpacing(10)
        
        # Styling for the list view
        self.chat_view.setStyleSheet("""
            QListView {
                background-color: #f0f2f5;
                border: none;
                padding: 10px;
            }
        """)
        
        layout.addWidget(self.chat_view)
        
        # Input Area
        input_layout = QHBoxLayout()
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Ask me anything about our policies...")
        self.input_field.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 2px solid #5c6bc0;
                border-radius: 20px;
                font-size: 14px;
                color: black;
                background-color: white;
            }
        """)
        self.input_field.returnPressed.connect(self.send_message)
        
        self.send_btn = QPushButton("Send")
        self.send_btn.setStyleSheet("""
            QPushButton {
                background-color: #283593;
                color: white;
                border-radius: 20px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1a237e;
            }
        """)
        self.send_btn.clicked.connect(self.send_message)
        
        input_layout.addWidget(self.input_field)
        input_layout.addWidget(self.send_btn)
        
        layout.addLayout(input_layout)
        
        # Welcome message
        self.chat_model.add_message("ai", "Welcome! I am your RAG Assistant powered by Tongyi (Qwen). Ask away!")

    @asyncSlot()
    async def send_message(self):
        text = self.input_field.text().strip()
        if not text:
            return
            
        # Add User Message
        self.chat_model.add_message("user", text)
        self.input_field.clear()
        self.chat_view.scrollToBottom()
        
        # Disable input while processing
        self.send_btn.setEnabled(False)
        self.input_field.setEnabled(False)
        
        # Add Empty AI Message placeholder
        self.chat_model.add_message("ai", "Thinking...")
        self.chat_view.scrollToBottom()
        
        try:
            # Stream response
            full_response = ""
            # We'll rely on update_last_message to animate
            first_chunk = True
            
            async for chunk in self.rag_service.stream_query(text):
                if first_chunk:
                    full_response = "" # Clear "Thinking..."
                    first_chunk = False
                
                full_response += chunk
                self.chat_model.update_last_message(full_response)
                self.chat_view.scrollToBottom()
                
        except Exception as e:
            self.chat_model.update_last_message(f"Error: {str(e)}")
        finally:
            self.send_btn.setEnabled(True)
            self.input_field.setEnabled(True)
            self.input_field.setFocus()
