from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem, 
    QLabel, QLineEdit, QTextEdit, QPushButton, QGroupBox, QMessageBox, QProgressBar,
    QFileDialog, QFrame
)
from PyQt5.QtCore import Qt, QTimer, QFileInfo
from qasync import asyncSlot
import asyncio

class DocumentCard(QWidget):
    def __init__(self, title, source, content_preview, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Title
        title_lbl = QLabel(title)
        # 修改3: Title 使用淡紫色 (#9B59B6)
        title_lbl.setStyleSheet("font-weight: bold; font-size: 14px; color: #9B59B6;")
        layout.addWidget(title_lbl)
        
        # Source
        if source:
            src_lbl = QLabel(source)
            src_lbl.setStyleSheet("color: #666; font-size: 10px; font-style: italic;")
            layout.addWidget(src_lbl)
            
        # Preview
        # 修改2: Preview 内容限定约5行 (Approx 200-300 chars, max-height 90px)
        limit = 300
        preview_text = content_preview[:limit] + "..." if len(content_preview) > limit else content_preview
        prev_lbl = QLabel(preview_text)
        prev_lbl.setWordWrap(True)
        # Max height ~ 5 lines * 18px line-height
        prev_lbl.setMaximumHeight(90)
        prev_lbl.setStyleSheet("color: #444; margin-top: 5px; margin-bottom: 10px;")
        layout.addWidget(prev_lbl)
        
        # Add Separator Line
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("background-color: #ddd;")
        layout.addWidget(line)
        
        # Style the card (Remove box border to make it look like a list with separators)
        self.setStyleSheet("""
            DocumentCard {
                background-color: transparent;
            }
        """)

class KnowledgeWidget(QWidget):
    def __init__(self, rag_service, parent=None):
        super().__init__(parent)
        self.rag_service = rag_service
        self.init_ui()
        
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        
        # 1. Header
        header = QLabel("Knowledge Base")
        header.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        main_layout.addWidget(header)
        
        # 2. Document List Area
        self.doc_list = QListWidget()
        
        # 修改: 彻底禁用选中和焦点框，解决视觉错位问题
        self.doc_list.setSelectionMode(QListWidget.NoSelection)
        self.doc_list.setFocusPolicy(Qt.NoFocus)

        # Style: 仅保留 Hover 效果
        self.doc_list.setStyleSheet("""
            QListWidget {
                background-color: white;
                border: none;
            }
            QListWidget::item {
                border: none;
                padding: 0px;
            }
            QListWidget::item:hover {
                background-color: #fafafa; /* 鼠标悬停时的极淡灰色 */
            }
        """)
        # Enable smooth scrolling (pixel-based instead of item-based)
        self.doc_list.setVerticalScrollMode(QListWidget.ScrollPerPixel)
        self.doc_list.verticalScrollBar().setSingleStep(10) # Adjust scrolling speed
        # 修改1: 增加 Document 之间的间隔 (10 -> 20) -> Adjusted to 0 for separator line style
        self.doc_list.setSpacing(0)
        main_layout.addWidget(self.doc_list)
        
        # Separator Line
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setFrameShadow(QFrame.Sunken)
        sep.setStyleSheet("background-color: #ddd; margin-top: 10px; margin-bottom: 10px;")
        main_layout.addWidget(sep)

        # 3. Add Document Form (Removed GroupBox wrapper)
        
        # Styles for inputs
        input_style = "color: black; background-color: white; border: 1px solid #ccc; padding: 5px;"
        
        # File Upload Button
        self.upload_btn = QPushButton("📂 Upload Local File (PDF, Docx, etc)")
        self.upload_btn.setStyleSheet("""
            QPushButton {
                background-color: #eee; color: #333; border: 1px solid #ccc; 
                padding: 8px; border-radius: 4px;
            }
            QPushButton:hover { background-color: #e0e0e0; }
        """)
        self.upload_btn.clicked.connect(self.browse_file)
        main_layout.addWidget(self.upload_btn)
        
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Document Title")
        self.title_input.setStyleSheet(input_style)
        main_layout.addWidget(self.title_input)
        
        self.content_input = QTextEdit()
        self.content_input.setPlaceholderText("Paste document content here or upload file...")
        self.content_input.setMaximumHeight(150)
        self.content_input.setStyleSheet(input_style)
        main_layout.addWidget(self.content_input)
        
        self.add_btn = QPushButton("Save")
        self.add_btn.setStyleSheet("background-color: #5c6bc0; color: white; padding: 8px;")
        self.add_btn.clicked.connect(self.add_document)
        main_layout.addWidget(self.add_btn)
        
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        main_layout.addWidget(self.progress)
        
        # form_group.setLayout(form_layout)
        # main_layout.addWidget(form_group)

        # Initial Load: Trigger after UI is ready
        QTimer.singleShot(100, self.load_documents)
        
    @asyncSlot()
    async def load_documents(self):
        self.doc_list.clear()
        try:
            docs = await self.rag_service.get_all_documents()
            for doc in docs:
                item = QListWidgetItem(self.doc_list)
                # Use 'summary' instead of 'content'
                card = DocumentCard(doc['title'], doc['source'], doc['summary'])
                item.setSizeHint(card.sizeHint())
                self.doc_list.setItemWidget(item, card)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load documents: {str(e)}")

    @asyncSlot()
    async def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Document", "", 
            "Documents (*.pdf *.docx *.txt *.md);;All Files (*)"
        )
        
        if not file_path:
            return
            
        self.upload_btn.setEnabled(False)
        self.upload_btn.setText("Parsing file...")
        self.progress.setRange(0, 0)
        self.progress.setVisible(True)
        
        try:
            # Parse file content
            content = await self.rag_service.extract_text_from_file(file_path)
            
            # Auto-fill fields
            file_info = QFileInfo(file_path)
            self.title_input.setText(file_info.fileName())
            # self.source_input.setText(file_path) # Removed
            self.content_input.setPlainText(content)
            
        except Exception as e:
            QMessageBox.critical(self, "Parsing Error", f"Failed to parse file:\n{str(e)}")
        finally:
            self.upload_btn.setEnabled(True)
            self.upload_btn.setText("📂 Upload Local File (PDF, Docx, etc)")
            self.progress.setVisible(False)

    @asyncSlot()
    async def add_document(self):
        title = self.title_input.text().strip()
        content = self.content_input.toPlainText().strip()
        
        if not title or not content:
            QMessageBox.warning(self, "Invalid Input", "Title and Content are required.")
            return
            
        self.add_btn.setEnabled(False)
        self.progress.setRange(0, 0) # Indeterminate
        self.progress.setVisible(True)
        
        try:
            # Let the service summarize if needed, or we just pass content as before.
            # But the user asked for "summary" in preview. 
            # We can generate a quick summary here OR just truncate.
            # For true summary, we'd need an LLM call. Assuming simple truncation or service-side logic.
            # We'll pass empty source as it was removed from UI but API might need it.
            count = await self.rag_service.add_document(title, content, source="Local/Manual")
            QMessageBox.information(self, "Success", f"Added document with {count} chunks.")
            
            # Clear inputs
            self.title_input.clear()
            self.content_input.clear()
            
            # Refresh list
            await self.load_documents()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add document: {str(e)}")
        finally:
            self.add_btn.setEnabled(True)
            self.progress.setVisible(False)
