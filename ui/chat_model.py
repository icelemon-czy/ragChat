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
        
        # Layout Constants
        avatar_size = 36
        margin_h = 10
        margin_v = 5
        bubble_padding = 10
        max_bubble_width = option.rect.width() * 0.7
        
        # Setup Text Document
        self.doc.setMarkdown(text if text else "")
        self.doc.setDefaultFont(option.font)
        self.doc.setTextWidth(max_bubble_width - bubble_padding * 2) 

        # Calculate Text Dimensions
        doc_height = self.doc.size().height()
        doc_width = self.doc.idealWidth()
        
        # Bubble Rect size
        bubble_w = doc_width + bubble_padding * 2
        bubble_h = doc_height + bubble_padding * 2
        bubble_rect = QRectF(0, 0, bubble_w, bubble_h)
        
        # Determine Positions
        if role == "user":
            # --- User Style (Right) ---
            bg_color = QColor("#95EC69") # WeChat Green
            # Avatar Position
            avatar_rect = QRectF(
                option.rect.width() - margin_h - avatar_size,
                option.rect.y() + margin_v,
                avatar_size,
                avatar_size
            )
            # Bubble Position
            bubble_rect.moveTopLeft(
                QRectF(
                    avatar_rect.left() - margin_h - bubble_w,
                    option.rect.y() + margin_v,
                    bubble_w,
                    bubble_h
                ).topLeft()
            )
            avatar_color = QColor("#007AFF") # Blue
            avatar_text = "Me"
        else:
            # --- AI Style (Left) ---
            bg_color = QColor("white") 
            # Avatar Position
            avatar_rect = QRectF(
                margin_h,
                option.rect.y() + margin_v,
                avatar_size,
                avatar_size
            )
            # Bubble Position
            bubble_rect.moveTopLeft(
                QRectF(
                    avatar_rect.right() + margin_h,
                    option.rect.y() + margin_v,
                    bubble_w,
                    bubble_h
                ).topLeft()
            )
            avatar_color = QColor("#5c6bc0") # Primary Purple
            avatar_text = "AI"

        # --- Draw Avatar ---
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)
        painter.setBrush(avatar_color)
        painter.drawEllipse(avatar_rect)
        
        # Draw Avatar Text (Initials)
        painter.setPen(Qt.white)
        font = painter.font()
        font.setBold(True)
        font.setPixelSize(12)
        painter.setFont(font)
        painter.drawText(avatar_rect, Qt.AlignCenter, avatar_text)

        # --- Draw Bubble ---
        painter.setPen(Qt.NoPen)
        painter.setBrush(bg_color)
        painter.drawRoundedRect(bubble_rect, 10, 10)

        # --- Draw Text Content ---
        # Translate painter to inside the bubble for text rendering
        painter.translate(bubble_rect.x() + bubble_padding, bubble_rect.y() + bubble_padding)
        ctx = QAbstractTextDocumentLayout.PaintContext()
        ctx.palette.setColor(QPalette.Text, Qt.black)
        
        # Restore font for content
        painter.setFont(option.font)
        self.doc.documentLayout().draw(painter, ctx)

        painter.restore()

    def sizeHint(self, option: QStyleOptionViewItem, index: QModelIndex):
        text = index.data(Qt.DisplayRole)
        if not text:
            return QSize(0, 0)
        
        # Padding constants must match paint()
        avatar_size = 36
        margin_v = 5
        bubble_padding = 10
        max_bubble_width = option.rect.width() * 0.7
        
        self.doc.setMarkdown(text)
        self.doc.setTextWidth(max_bubble_width - bubble_padding * 2)
        
        text_height = self.doc.size().height() + bubble_padding * 2
        total_height = max(text_height, avatar_size) + margin_v * 2 + 10 # +10 extra buffer
        
        return QSize(option.rect.width(), int(total_height))
