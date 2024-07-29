from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QVBoxLayout, QFrame, QPushButton

import qtawesome as qta
from ..signals import all_signals


class SidebarMenus(QFrame):
    def __init__(self) -> None:
        super().__init__()
        self.setFixedWidth(55)
        self.setMinimumHeight(670)
        self.setMaximumHeight(2160)
        self.setStyleSheet("background-color: #333333; border-radius: 0px")

        main_layout = QVBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setAlignment(Qt.AlignLeft)
        menu_layout = QVBoxLayout()
        menu_layout.setSpacing(0)
        menu_layout.setContentsMargins(0, 0, 0, 0)
        menu_layout.setAlignment(Qt.AlignTop | Qt.AlignCenter)

        self.btn_recorder_menu = self.make_icons(
            qta.icon("fa.video-camera", color="#d7d7d7"), 
            "Recording Viewer"
        )
        self.btn_explorer_menu = self.make_icons(
            qta.icon("ph.monitor-play-fill", color="#777777"), 
            "Explorer & Playback"
        )
        # self.btn_deeplearning_menu = self.make_icons(
        #     qta.icon("fa.crosshairs", color="#777777"), 
        #     "Deep Learning Solution"
        # )

        menu_layout.addWidget(self.btn_recorder_menu)
        menu_layout.addWidget(self.btn_explorer_menu)
        # menu_layout.addWidget(self.btn_deeplearning_menu)
        main_layout.addLayout(menu_layout)

        # option_layout = QVBoxLayout()
        # btn_option = self.make_icons(qta.icon("fa.gear"), "Pykinect Recorder Option")
        # option_layout.addWidget(btn_option)
        # main_layout.addLayout(option_layout)
        self.setLayout(main_layout)

        self.btn_recorder_menu.clicked.connect(self.clicked_recorder)
        self.btn_explorer_menu.clicked.connect(self.clicked_explorer)
        # self.btn_deeplearning_menu.clicked.connect(self.clicked_solution)

    def make_icons(self, icon: qta, tooltip: str, scale: float = 0.8) -> QPushButton:
        w, h = int(45 * scale), int(45 * scale)
        _btn = QPushButton(icon, "")
        _btn.setFixedSize(55, 55)
        _btn.setIconSize(QSize(w, h))
        _btn.setToolTip(f"<b>{tooltip}<b>")
        _btn.setStyleSheet(
            """
            QPushButton {
                border: 0px solid #ffffff;
            }
            QPushButton:hover {
                background-color: #252526;
            }
            QToolTip {
                font:"Arial"; font-size: 15px; color: #ffffff; border: 1px solid #ffffff; 
            }
        """
        )
        return _btn

    def clicked_recorder(self):
        self.btn_recorder_menu.setIcon(qta.icon("fa.video-camera", color="#d7d7d7"))
        self.btn_explorer_menu.setIcon(qta.icon("ph.monitor-play-fill", color="#777777"))
        # self.btn_deeplearning_menu.setIcon(qta.icon("fa.crosshairs", color="#777777"))
        all_signals.option_signals.stacked_sidebar_status.emit("recorder")

    def clicked_explorer(self):
        self.btn_recorder_menu.setIcon(qta.icon("fa.video-camera", color="#777777"))
        self.btn_explorer_menu.setIcon(qta.icon("ph.monitor-play-fill", color="#d7d7d7"))
        # self.btn_deeplearning_menu.setIcon(qta.icon("fa.crosshairs", color="#777777"))
        all_signals.option_signals.stacked_sidebar_status.emit("explorer")

    def clicked_solution(self):
        self.btn_recorder_menu.setIcon(qta.icon("fa.video-camera", color="#777777"))
        self.btn_explorer_menu.setIcon(qta.icon("ph.monitor-play-fill", color="#777777"))
        # self.btn_deeplearning_menu.setIcon(qta.icon("fa.crosshairs", color="#d7d7d7"))
        all_signals.option_signals.stacked_sidebar_status.emit("solution")
