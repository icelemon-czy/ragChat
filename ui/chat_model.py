from PyQt5.QtCore import QAbstractListModel, Qt, QModelIndex, QSize, QRectF
from PyQt5.QtGui import QPainter, QColor, QFontMetrics, QTextDocument, QAbstractTextDocumentLayout, QPalette
from PyQt5.QtWidgets import QStyledItemDelegate, QStyleOptionViewItem, QStyle

class ChatMessage:
    def __init__(self, role, content):
        self.role = role  # "user" or "ai"
        self.content = content

class ChatModel(QAbstractListModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.messages = []

    def rowCount(self, parent=QModelIndex()):
        return len(self.messages)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or index.row() >= len(self.messages):
            return None
        
        msg = self.messages[index.row()]
        if role == Qt.DisplayRole:
            return msg.content
        if role == Qt.UserRole:
            return msg.role
        return None

    def add_message(self, role, content):
        self.beginInsertRows(QModelIndex(), len(self.messages), len(self.messages))
        self.messages.append(ChatMessage(role, content))
        self.endInsertRows()

    def update_last_message(self, content):
        if not self.messages:
            return
        idx = len(self.messages) - 1
        self.messages[idx].content = content
        self.dataChanged.emit(self.index(idx), self.index(idx))

class ChatDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.doc = QTextDocument()

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex):
        painter.save()
        
        # Get data
        text = index.data(Qt.DisplayRole)
        role = index.data(Qt.UserRole)
        
        # Setup Text Document for rich text / wrapping
        self.doc.setMarkdown(text if text else "")
        self.doc.setDefaultFont(option.font)
        self.doc.setTextWidth(option.rect.width() * 0.7) # Max width 70%

        # Calculate dimensions
        doc_height = self.doc.size().height()
        doc_width = self.doc.idealWidth()
        
        # Bubbles
        padding = 10
        bubble_rect = QRectF(0, 0, doc_width + padding * 2, doc_height + padding * 2)
        
        if role == "user":
            # Right aligned
            trans_x = option.rect.width() - bubble_rect.width() - 10
            trans_y = option.rect.y() + 5
            bg_color = QColor("#DCF8C6") # Light Green
        else:
            # Left aligned
            trans_x = 10
            trans_y = option.rect.y() + 5
            bg_color = QColor("#E0E0E0") # Light Gray

        painter.translate(trans_x, trans_y)

        # Draw Bubble Background
        painter.setBrush(bg_color)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(bubble_rect, 10, 10)

        # Draw Text
        painter.translate(padding, padding)
        # abstractTextDocumentLayout needs a paint context
        ctx = QAbstractTextDocumentLayout.PaintContext()
        ctx.palette.setColor(QPalette.Text, Qt.black)
        self.doc.documentLayout().draw(painter, ctx)

        painter.restore()

    def sizeHint(self, option: QStyleOptionViewItem, index: QModelIndex):
        text = index.data(Qt.DisplayRole)
        if not text:
            return QSize(0, 0)
        
        self.doc.setMarkdown(text)
        self.doc.setTextWidth(option.rect.width() * 0.7)
        
        height = self.doc.size().height() + 30 # + padding/margins
        return QSize(option.rect.width(), int(height))
