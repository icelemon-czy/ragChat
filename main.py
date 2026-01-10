import sys
import os
import asyncio
from PyQt5.QtWidgets import QApplication, QInputDialog, QMessageBox
from qasync import QEventLoop

from services.rag_service import RagService
from ui.mainwindow import MainWindow

def main():
    app = QApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    
    # Default API Key (Replace 'sk-...' with your actual key if you want to skip input)
    DEFAULT_API_KEY = "。。。sk-..." 
    
    # Check API Key
    api_key = os.environ.get("DASHSCOPE_API_KEY") or DEFAULT_API_KEY
    
    if not api_key or api_key.startswith("sk-...") and len(api_key) < 10:
        key, ok = QInputDialog.getText(
            None, "API Key Required", 
            "Please enter your Alibaba DashScope API Key:\n(Starts with sk-...)", 
        )
        if ok and key:
            api_key = key.strip()
        else:
            QMessageBox.critical(None, "Error", "API Key is required to run this application.")
            sys.exit(1)
            
    # Initialize Service
    try:
        rag_service = RagService(api_key)
    except Exception as e:
        QMessageBox.critical(None, "Initialization Error", f"Failed to initialize services:\n{str(e)}")
        sys.exit(1)
        
    # Show Window
    window = MainWindow(rag_service)
    window.show()
    
    with loop:
        loop.run_forever()

if __name__ == "__main__":
    main()
