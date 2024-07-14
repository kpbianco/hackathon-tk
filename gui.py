import sys
import subprocess
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
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

    def show_sim_window(self, df, tires):
        self.sim_window = SimWindow(df, tires, self)
        self.setCentralWidget(self.sim_window)

    def back_to_start_page(self):
        self.start_page()

    def load_stylesheet(self):
        style_file = QFile("./darkmode.css")
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
            df = pd.read_csv(file_name, skiprows=9, header=[0,1])

            LF_headers = [
                'LFwearL', 'LFpressure', 'LFtempM', 'LFtempL', 'LFTiresUsed', 
                'LFtempCL', 'LFbrakeLinePress', 'LFshockDefl', 'LFtempCR', 'LFtempCM', 
                'LFtempR', 'LFcoldPressure', 'LFrideHeight', 
                'LFshockVel', 'LFspeed', 'LFwearM', 'LFwearR', 'TireLF_RumblePitch'
            ]

            RF_headers = [
                'RFwearL', 'RFpressure', 'RFtempM', 'RFtempL', 'RFTiresUsed', 
                'RFtempCL', 'RFbrakeLinePress', 'RFshockDefl', 'RFtempCR', 'RFtempCM', 
                'RFtempR', 'RFcoldPressure', 'RFrideHeight', 
                'RFshockVel', 'RFspeed', 'RFwearM', 'RFwearR', 'TireRF_RumblePitch'
            ]

            RR_headers = [
                'RRwearL', 'RRpressure', 'RRtempM', 'RRtempL', 'RRTiresUsed', 
                'RRtempCL', 'RRbrakeLinePress', 'RRshockDefl', 'RRtempCR', 'RRtempCM', 
                'RRtempR', 'RRcoldPressure', 'RRrideHeight', 
                'RRshockVel', 'RRspeed', 'RRwearM', 'RRwearR', 'TireRR_RumblePitch'
            ]

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

            tires = {
                'LFtire': LFtire,
                'LRtire': LRtire,
                'RFtire': RFtire,
                'RRtire': RRtire
            }

            self.main_window.show_sim_window(df, [LFtire, LRtire, RFtire, RRtire])

    def go_back(self):
        self.main_window.back_to_start_page()

class SimWindow(QWidget):
    def __init__(self, df, tires, parent=None):
        super().__init__()
        self.initUI()

        self.setWindowTitle("Simulation Window")
        self.setGeometry(100, 100, 600, 400)

        self.df = df
        self.tires = tires
        self.current_index = 0
        self.playback_speeds = [1, 100, 1000, 10000]
        self.current_speed_index = 0

        self.slider_values = [0.0, 0.0, 0.0, 0.0]

        parameters_button = QPushButton("Parameters", self)
        parameters_button.clicked.connect(self.open_parameters_window)

        go_back_button = QPushButton("Back", self)
        go_back_button.clicked.connect(self.go_back_to_browse)

        self.play_button = QPushButton("Play", self)
        self.play_button.clicked.connect(self.play)

        self.pause_button = QPushButton("Pause", self)
        self.pause_button.clicked.connect(self.pause)

        self.rewind_button = QPushButton("Rewind", self)
        self.rewind_button.clicked.connect(self.rewind)

        self.speed_button = QPushButton(f"Speed: {self.playback_speeds[self.current_speed_index]}x", self)
        self.speed_button.clicked.connect(self.change_speed)

        self.runtime_label = QLabel("Runtime: 00:00", self)

        self.data_label = QLabel("Data: ", self)

        self.tire_table = QTableWidget(4, 4, self)
        self.setup_table()

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.rewind_button)
        button_layout.addWidget(self.pause_button)
        button_layout.addWidget(self.play_button)
        button_layout.addWidget(self.speed_button)

        top_layout = QHBoxLayout()
        top_layout.addWidget(go_back_button, alignment=Qt.AlignLeft)
        top_layout.addWidget(parameters_button, alignment=Qt.AlignRight)

        data_layout = QHBoxLayout()
        data_layout.addWidget(self.runtime_label, alignment=Qt.AlignLeft)
        data_layout.addWidget(self.data_label)

        main_layout = QVBoxLayout()
        main_layout.addLayout(top_layout)
        main_layout.addWidget(self.tire_table)
        main_layout.addLayout(data_layout)
        main_layout.addStretch(1)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_data)

        self.play()

    def setup_table(self):
        headers = ["Tire", "Wear L", "Wear M", "Wear R"]
        self.tire_table.setHorizontalHeaderLabels(headers)

        tire_names = ["LF Tire", "LR Tire", "RF Tire", "RR Tire"]
        for row, tire_name in enumerate(tire_names):
            item_tire = QTableWidgetItem(tire_name)
            self.tire_table.setItem(row, 0, item_tire)

        self.tire_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tire_table.horizontalHeader().setStretchLastSection(True)
        self.tire_table.verticalHeader().setVisible(False)
        self.tire_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tire_table.setSelectionMode(QTableWidget.NoSelection)

        self.update_table()

    def update_table(self):
        for row, tire_instance in enumerate(self.tires):
            wear_data = tire_instance.get_wear(self.current_index)
            
            # Ensure wear_data items are converted to float before formatting
            wearL_value = float(wear_data['wearL'][0]) if isinstance(wear_data['wearL'], list) else float(wear_data['wearL'])
            wearM_value = float(wear_data['wearM'][0]) if isinstance(wear_data['wearM'], list) else float(wear_data['wearM'])
            wearR_value = float(wear_data['wearR'][0]) if isinstance(wear_data['wearR'], list) else float(wear_data['wearR'])
            
            self.tire_table.setItem(row, 1, QTableWidgetItem(f"{wearL_value:.2f}"))
            self.tire_table.setItem(row, 2, QTableWidgetItem(f"{wearM_value:.2f}"))
            self.tire_table.setItem(row, 3, QTableWidgetItem(f"{wearR_value:.2f}"))

    def open_tkinter_popup(self):
        subprocess.Popen(['python', 'omni6.py'])

    def play(self):
        self.playback_direction = 1
        self.timer.start(int(1000 / (360 * self.playback_speeds[self.current_speed_index])))

    def pause(self):
        self.timer.stop()

    def rewind(self):
        self.playback_direction = -1
        self.timer.start(int(1000 / (360 * self.playback_speeds[self.current_speed_index])))

    def change_speed(self):
        self.current_speed_index = (self.current_speed_index + 1) % len(self.playback_speeds)
        speed = self.playback_speeds[self.current_speed_index]
        self.speed_button.setText(f"Speed: {speed}x")
        if self.timer.isActive():
            self.timer.start(int(1000 / (360 * speed)))

    def open_parameters_window(self):
        parameters_window = ParametersWindow(self)
        parameters_window.slider_value_changed.connect(self.update_slider_values)
        parameters_window.exec_()

    def initUI(self):
        self.setGeometry(100, 100, 400, 300)
        self.setWindowTitle('Sim Window')
        self.open_tkinter_popup()

    @pyqtSlot(int, float)
    def update_slider_values(self, slider_index, value):
        self.slider_values[slider_index] = value
        print(f"Slider {slider_index + 1} value updated to: {value}")

    def update_data(self):
        if self.current_index >= 0 and self.current_index < len(self.df):
            data_row = self.df.iloc[self.current_index]
            lap_dist = data_row.get(('LapDist', 'm'), 'N/A')
            speed = data_row.get(('Speed', 'm/s'), 'N/A')
            yaw = data_row.get(('Yaw', 'rad'), 'N/A')
            lat = data_row.get(('Lat', 'deg'), 'N/A')
            lon = data_row.get(('Lon', 'deg'), 'N/A')

            self.update_table()

            self.data_label.setText(f"Lap Dist: {lap_dist:.0f}, Speed: {speed:.0f}, Yaw: {yaw:.2f}, Lat: {lat:.2f}, Lon: {lon:.2f}")
            self.current_index += self.playback_direction
            self.update_runtime_label()
        else:
            self.timer.stop()

    def update_runtime_label(self):
        minutes = self.current_index // (360 * 60)
        seconds = (self.current_index // 360) % 60
        self.runtime_label.setText(f"Runtime: {minutes:02}:{seconds:02}")

    def go_back_to_browse(self):
        confirm = QMessageBox.question(self, "Confirmation", "Are you sure you want to go back to file selection?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if confirm == QMessageBox.Yes:
            parent_main_window = self.parent()
            if isinstance(parent_main_window, MainWindow):
                parent_main_window.open_file_selection_window()

class SliderWithLabel(QWidget):
    value_changed = pyqtSignal(int, float)

    def __init__(self, label_text, index, parent=None):
        super().__init__(parent)
        
        self.index = index

        layout = QHBoxLayout()
        
        self.label = QLabel(label_text, self)
        self.slider = QSlider(Qt.Horizontal, self)
        self.slider.setMinimum(0)
        self.slider.setMaximum(100)
        self.slider.setSingleStep(1)
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.setTickInterval(10)
        self.slider.valueChanged.connect(self.update_label)

        self.value_label = QLabel("0.0", self)
        
        layout.addWidget(self.label)
        layout.addWidget(self.slider)
        layout.addWidget(self.value_label)

        self.checkbox = QCheckBox("Use", self)
        layout.addWidget(self.checkbox)
        
        self.setLayout(layout)

    def update_label(self, value):
        float_value = value / 10.0
        self.value_label.setText(f"{float_value:.1f}")
        self.value_changed.emit(self.index, float_value)

    def update_label(self, value):
        float_value = value / 10.0
        self.value_label.setText(f"{float_value:.1f}")

class ParametersWindow(QDialog):
    slider_value_changed = pyqtSignal(int, float)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Parameters")
        self.setGeometry(200, 200, 400, 300)

        label = QLabel("This is the parameters window.", self)
        label.setAlignment(Qt.AlignCenter)

        slider_labels = ["Slider 1", "Slider 2", "Slider 3", "Slider 4"]

        layout = QVBoxLayout()
        layout.addWidget(label)

        for index, label_text in enumerate(slider_labels):
            slider_with_label = SliderWithLabel(label_text, index, self)
            slider_with_label.value_changed.connect(self.emit_slider_value_changed)
            layout.addWidget(slider_with_label)

        self.setLayout(layout)

    def emit_slider_value_changed(self, index, value):
        self.slider_value_changed.emit(index, value)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
