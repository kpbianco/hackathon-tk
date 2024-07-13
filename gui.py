import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel, QFileDialog, QMessageBox
from PyQt5.QtCore import Qt, QFile, QTextStream
import pandas as pd
from Classes.Tire import Tire

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Formula 1 Tire Wear Simulator")
        self.setGeometry(100, 100, 600, 400)
        self.load_stylesheet()
        self.start_page()

    def start_page(self):
        title_label = QLabel("Formula 1 Tire Wear Simulator", self)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        title_label.setAlignment(Qt.AlignCenter)
        
        start_button = QPushButton("Start", self)
        start_button.clicked.connect(self.open_file_selection_window)

        layout = QVBoxLayout()
        layout.addWidget(title_label)
        layout.addStretch(1)
        layout.addWidget(start_button)
        
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def open_file_selection_window(self):
        self.file_selection_window = FileSelectionWindow(self)
        self.setCentralWidget(self.file_selection_window)

    def back_to_start_page(self):
        self.start_page()

    def load_stylesheet(self):
        style_file = QFile("./gpt4.css")
        style_file.open(QFile.ReadOnly | QFile.Text)
        stream = QTextStream(style_file)
        stylesheet = stream.readAll()
        self.setStyleSheet(stylesheet)

class FileSelectionWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Select CSV File")
        self.setGeometry(200, 200, 600, 400)

        self.main_window = parent
        
        title_label = QLabel("Select CSV File", self)
        title_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        title_label.setAlignment(Qt.AlignCenter)
        
        select_button = QPushButton("Browse", self)
        select_button.clicked.connect(self.select_file)

        back_button = QPushButton("Back", self)
        back_button.clicked.connect(self.go_back)

        layout = QVBoxLayout()
        layout.addWidget(title_label)
        layout.addStretch(1)
        layout.addWidget(select_button)
        layout.addWidget(back_button)
        
        self.setLayout(layout)

    def select_file(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_name, _ = QFileDialog.getOpenFileName(self, "Select CSV File", "", "CSV Files (*.csv);;All Files (*)", options=options)
        if file_name:
            # Read CSV file skipping first few rows (assuming metadata)
            df = pd.read_csv(file_name, skiprows=9, header=[0,1])  # Adjust skiprows as needed based on your file structure

            # LF Headers
            LF_headers = [
                'LFwearL', 'LFpressure', 'LFtempM', 'LFtempL', 'LFTiresUsed', 
                'LFtempCL', 'LFbrakeLinePress', 'LFshockDefl', 'LFtempCR', 'LFtempCM', 
                'LFtempR', 'LFcoldPressure', 'LFrideHeight', 
                'LFshockVel', 'LFspeed', 'LFwearM', 'LFwearR', 'TireLF_RumblePitch'
            ]

            # RF Headers
            RF_headers = [
                'RFwearL', 'RFpressure', 'RFtempM', 'RFtempL', 'RFTiresUsed', 
                'RFtempCL', 'RFbrakeLinePress', 'RFshockDefl', 'RFtempCR', 'RFtempCM', 
                'RFtempR', 'RFcoldPressure', 'RFrideHeight', 
                'RFshockVel', 'RFspeed', 'RFwearM', 'RFwearR', 'TireRF_RumblePitch'
            ]

            # RR Headers
            RR_headers = [
                'RRwearL', 'RRpressure', 'RRtempM', 'RRtempL', 'RRTiresUsed', 
                'RRtempCL', 'RRbrakeLinePress', 'RRshockDefl', 'RRtempCR', 'RRtempCM', 
                'RRtempR', 'RRcoldPressure', 'RRrideHeight', 
                'RRshockVel', 'RRspeed', 'RRwearM', 'RRwearR', 'TireRR_RumblePitch'
            ]

            # LR Headers
            LR_headers = [
                'LRwearL', 'LRpressure', 'LRtempM', 'LRtempL', 'LRTiresUsed', 
                'LRtempCL', 'LRbrakeLinePress', 'LRshockDefl', 'LRtempCR', 'LRtempCM', 
                'LRtempR', 'LRcoldPressure', 'LRrideHeight', 
                'LRshockVel', 'LRspeed', 'LRwearM', 'LRwearR', 'TireLR_RumblePitch'
            ]

            header_list = [
                LF_headers, LR_headers, RF_headers, RR_headers
            ]

            LFtire = Tire()
            LRtire = Tire()
            RFtire = Tire()
            RRtire = Tire()

            LFtire.assign_df(df, LF_headers)
            LRtire.assign_df(df, LR_headers)
            RFtire.assign_df(df, RF_headers)
            RRtire.assign_df(df, RR_headers)

    def go_back(self):
        self.main_window.back_to_start_page()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
