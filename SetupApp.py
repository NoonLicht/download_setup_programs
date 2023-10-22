import os
import requests
import subprocess
import shutil
import threading
from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QVBoxLayout, QWidget, QPushButton, QCheckBox, QFrame, QFileDialog, QMessageBox, QHBoxLayout, QGridLayout
from PyQt5.QtCore import Qt, QDir
from PyQt5.QtGui import QPainter, QColor, QIcon, QPixmap
import urllib.request
import gettext


app = QApplication([])

def download_file(url_or_path, destination):
    try:
        if url_or_path.startswith("https://"):
            response = requests.get(url_or_path)
            response.raise_for_status()
            with open(destination, "wb") as file:
                file.write(response.content)
        else:
            # Это локальный путь к файлу, просто копируем его
            shutil.copy(url_or_path, destination)
        return True
    except Exception as e:
        QMessageBox.critical(None, "Ошибка", f"Ошибка скачивания файлов: {str(e)}")
        return False

class ProgramDownloader(QMainWindow):
    def __init__(self):
        super().__init__()
        
        app_icon = QIcon(':/icon/tab.ico')
        taskbar_icon = QIcon(':/icon/tab.ico')
        
        self.setWindowIcon(app_icon)
        self.setWindowIcon(taskbar_icon)  # Установка иконки на панели задач
        self.download_completed_event = threading.Event()

        self.setWindowTitle("Program Downloader")
        self.setGeometry(100, 100, 1200, 550)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        self.category_frames = {}

        self.setFixedSize(1200, 550)

        self.programs = {
            "Браузер": {
                "Opera": "https://get.geo.opera.com/ftp/pub/opera/desktop/102.0.4880.46/win/Opera_102.0.4880.46_Setup_x64.exe",
                "Yandex": "https://download.yandex.ru/downloadable_soft/browser/11069/Yandex.exe",
                "Google": "https://dl.google.com/chrome/install/chrome_installer.exe",},
            "Утилиты": {
                "SophiaApp": "https://github.com/Sophia-Community/SophiApp/releases/download/1.0.97/SophiApp.zip",
                "Driver Booster": "https://cdn.iobit.com/dl/driver_booster_setup.exe",
                "AIDA64": "https://download.aida64.com/aida64extreme692.exe",
                "WinDirStat": "https://www.windirstat.org/media/download/windirstat1_1_2_setup.exe",
                "MSI Afterburner": "https://dl.comss.org/download/MSIAfterburnerSetup465.exe",
                "AMD Software": "https://dl.comss.org/download/whql-amd-software-adrenalin-edition-23.9.1-win10-win11-sep6.exe",
                "NVidia Driver": "https://dl.comss.org/download/GeForce_Experience_v3.27.0.112.exe",
                "OpenVPN(!)": "",
            },
            "Клиент": {
                "Steam": "https://cdn.akamai.steamstatic.com/client/installer/SteamSetup.exe",
                "Epic Games Store": "https://launcher-public-service-prod06.ol.epicgames.com/launcher/api/installer/download/EpicGamesLauncherInstaller.msi",
                "RockStar Launcher": "https://gamedownloads.rockstargames.com/public/installer/Rockstar-Games-Launcher.exe",
                "Riot Games": "https://www.valorantpcdownload.com/dl/RiotClientServices.exe",
                "GOG Galaxy": "https://webinstallers.gog-statics.com/download/GOG_Galaxy_2.0.exe",
                "qBittorrent": "https://dl.comss.org/download/qbittorrent_4.5.5_x64_setup.exe",
            },
            "Общение": {
                "Discord(!)": "./exe/DiscordSetup.exe",
                "Telegram": "https://telegram.org/dl/desktop/win64",
            },
            "Программирование": {
                "VS Code(!)": "./exe/VSCodeUserSetup-x64-1.82.1.exe",
                "Visual Studio(!)": "./exe/VisualStudioSetup.exe",
                "Git": "https://github.com/git-for-windows/git/releases/download/v2.42.0.windows.2/Git-2.42.0.2-64-bit.exe",
                "PyCharm": "https://download.jetbrains.com/python/pycharm-professional-2023.2.1.exe",
                "Github Desktop(!)": "./exe/GithubDesktop.exe",
                "PostgreSQL": "https://repo.postgrespro.ru/win/64/PostgreSQL_15.4_64bit_Setup.exe",
                "DBeaver": "https://dbeaver.io/files/dbeaver-ce-latest-x86_64-setup.exe",
            },
            "Прочее": {
                "7-Zip": "https://www.7-zip.org/a/7z2301-x64.exe",
                "WinRAR": "https://www.rarlab.com/rar/winrar-x64-623ru.exe",
                "PowerToys": "https://github.com/microsoft/PowerToys/releases/download/v0.73.0/PowerToysUserSetup-0.73.0-x64.exe",
                "NotePad++": "https://github.com/notepad-plus-plus/notepad-plus-plus/releases/download/v8.5.7/npp.8.5.7.Installer.x64.exe",
                "FileZilla": "https://www.filezilla.ru/download/FileZilla_3.65.0_win64-setup.exe",
                "PuTTY": "https://github.com/putty-org-ru/PuTTY/releases/download/PuTTY-0.73-RU-17/putty-0.73-ru-17.zip",
                "Microsoft Office(!)": "./exe/MicrosoftOffice.torrent",
                "StartAllBack": "https://dl.comss.org/download/StartAllBack_3.6.13_setup.exe"
            },
            "Зависимости": {
                "DirectX": "https://download.microsoft.com/download/1/7/1/1718CCC4-6315-4D8E-9543-8E28A4E18C4C/dxwebsetup.exe",
                "Node.js": "https://nodejs.org/dist/v18.17.1/node-v18.17.1-x64.msi",
                "Python 3.11.5": "https://www.python.org/ftp/python/3.11.5/python-3.11.5-amd64.exe",
                "Visual C++ x64": "https://aka.ms/vs/17/release/vc_redist.x64.exe",
                "Visual C++ x86": "https://aka.ms/vs/17/release/vc_redist.x86.exe",
                ".NET Desktop Runtime 5": "https://download.visualstudio.microsoft.com/download/pr/3aa4e942-42cd-4bf5-afe7-fc23bd9c69c5/64da54c8864e473c19a7d3de15790418/windowsdesktop-runtime-5.0.17-win-x64.exe",
                ".NET Desktop Runtime 6": "https://download.visualstudio.microsoft.com/download/pr/66a7c4c6-8401-4799-864f-9afddf5a7733/4052f458f0266e25ab1b9c7959ca245f/windowsdesktop-runtime-6.0.22-win-x64.exe",
                ".NET Desktop Runtime 7": "https://download.visualstudio.microsoft.com/download/pr/2ce1cbbe-71d1-44e7-8e80-d9ae336b9b17/a2706bca3474eef8ef95e10a12ecc2a4/windowsdesktop-runtime-7.0.11-win-x64.exe",
            },
            "Антивирус": {
                "Kaspersky Free": "https://dl.comss.org/download/kaspersky4win202121.14.5.462ru_42131.exe",
                "Dr.Web SS": "https://download.geo.drweb.com/pub/drweb/windows/workstation/12.0/drweb-12.0-ss-win.exe",
                "Kaspersky(!)": "./exe/Kaspersky.exe",
            },
            "Эмуляторы": {
                "PCSX2": "https://github.com/PCSX2/pcsx2/releases/download/v1.7.5004/pcsx2-v1.7.5004-windows-x64-Qt.7z",
                "RPCS3": "https://github.com/RPCS3/rpcs3-binaries-win/releases/download/build-c7c81ed95d3d23b37d78aad49dab6beddac200bc/rpcs3-v0.0.29-15617-c7c81ed9_win64.7z",
                "Xenia": "https://github.com/xenia-project/release-builds-windows/releases/latest/download/xenia_master.zip",
                "Yuzu": "https://github.com/yuzu-emu/liftinstall/releases/download/1.9/yuzu_install.exe",
                "Ryujinx": "https://github.com/Ryujinx/release-channel-master/releases/download/1.1.1011/ryujinx-1.1.1011-win_x64.zip",
            },
            "Мультимедия": {
                "iTunes": "https://secure-appldnld.apple.com/itunes12/001-97787-20210421-F0E5A3C2-A2C9-11EB-A40B-A128318AD179/iTunes64Setup.exe",
                "VLC": "https://mirror.yandex.ru/mirrors/ftp.videolan.org/vlc/3.0.18/win64/vlc-3.0.18-win64.exe",
                "Spotify": "https://download.scdn.co/SpotifySetup.exe",
                "KMPlayer": "https://dl.comss.org/download/KMP64_2023.8.22.7.exe",
            },
            "Диск": {
                "Yandex Disk": "https://webdav.yandex.ru/share/dist/YandexDisk30SetupPack.exe",
                "Google Drive": "https://dl.google.com/drive-file-stream/GoogleDriveSetup.exe",
                "DropBox": "https://clientupdates.dropboxstatic.com/dbx-releng/client/Dropbox%20181.4.5678%20Offline%20Installer.exe",
            },
            "Творчество": {
                "Blender": "https://www.blender.org/download/release/Blender3.6/blender-3.6.2-windows-x64.msi",
                "Krita": "https://download.kde.org/stable/krita/5.1.5/krita-x64-5.1.5-setup.exe",
                "GIMP": "https://download.gimp.org/gimp/v2.10/windows/gimp-2.10.34-setup-2.exe",
                "Photoshop(!)": "./exe/Photoshop.torrent",
                "Illustrator(!)": "./exe/Illustrator.torrent",
            },
        }

        self.create_category_frames()
        self.organize_programs_into_frames()

        self.download_button = QPushButton("Загрузка")
        self.download_button.clicked.connect(self.download_selected_programs)

        self.select_all_button = QPushButton("Выбрать всё")
        self.select_all_button.clicked.connect(self.select_all_programs)      

        self.setup_button = QPushButton("Установка")
        self.enable_sandbox_button = QPushButton("Песочница")
        self.enable_hyperv_button = QPushButton("Hyper-V")
        self.install_wsl_button = QPushButton("WSL Ubuntu")

        self.setup_button.clicked.connect(self.setup_exe)
        self.enable_sandbox_button.clicked.connect(self.sandbox_windows)
        self.enable_hyperv_button.clicked.connect(self.enable_hyperv)
        self.install_wsl_button.clicked.connect(self.install_wsl)

        additional_buttons_layout = QHBoxLayout()
        additional_buttons_layout.addWidget(self.download_button)
        additional_buttons_layout.addWidget(self.select_all_button)
        additional_buttons_layout.addWidget(self.setup_button)
        additional_buttons_layout.addWidget(self.enable_sandbox_button)
        additional_buttons_layout.addWidget(self.enable_hyperv_button)
        additional_buttons_layout.addWidget(self.install_wsl_button)

        self.layout.addLayout(additional_buttons_layout)

        self.central_widget.setLayout(self.layout)
            
        app.setStyleSheet('''
            QTitle {
                background-color: #333333;
                color: red;
                padding: 6px;
            }
            
            QWidget {
                background: #2b2b2b;
            }
            
            QPushButton {
                background-color: #333333;
                color: white;
                font-size: 12px;
                font-family: Calibri;
                font-weight: 600;
                margin: 5px;
                height: 30%;
                border-radius: 5px;
            }
            
            QPushButton:pressed {
                background-color: #0175bd;
                color: white;
            }
            
            QPushButton:hover {
                background-color: #0175bd;
                color: white;
            }
            
            QFrame {
                background-color: #333333;
                border-radius: 10px;
            }
            
            QCheckBox {
                background-color: #333333;
                font-size: 12px;
                height: 15px;    
                color: white;
            }
            
            QCheckBox:checked {
                color: #666666;
            }
            
            QCheckBox::indicator {
                width: 15px;
                height: 15px;
                background-color: #666666;
                border: 1px solid white;
                border-radius: 8px;
                background-position: center;
            }
            
            QCheckBox::indicator:checked {
                background-color: #029afb;
                background-position: 100%;
            }
            
            QLabel{
                background-color: #2b2b2b;
                color: white;
                font-size: 17px;
                font-family: Calibri;
                font-weight: 600;
                text-align: center;
            }
            QMessageBox {
                background-color: #2b2b2b;
            }

            QMessageBox QLabel#qt_msgbox_label {
                color: #029afb;
                min-width: 240px;
                min-height: 40px;
            }

            QMessageBox QLabel#qt_msgboxex_icon_label {
                width: 40px;
                height: 40px;
            }

            QMessageBox QPushButton {
                border: 1px solid #298DFF;
                border-radius: 3px;
                background-color: #029afb;
                color: white;
                font-size: 10pt;
                min-width: 70px;
                min-height: 25px;
            }

            QMessageBox QPushButton:hover {
                background-color: #029afb;
                color: #F2F2F2;
            }

            QMessageBox QPushButton:pressed {
                background-color: #257FE6;
            }

            QMessageBox QDialogButtonBox#qt_msgbox_buttonbox {
                button-layout: 0;
            }
        ''')

    def run_download_thread(self, program_name, download_link_or_path, download_folder):
        if download_link_or_path:
            file_extension = os.path.splitext(download_link_or_path)[1]  # Получаем расширение файла из ссылки
            file_name = os.path.join(download_folder, f"{program_name}{file_extension}")

            try:
                urllib.request.urlretrieve(download_link_or_path, file_name)
                self.downloaded_programs += 1
                progress_value = int((self.downloaded_programs / self.selected_programs) * 100)
                with open('downloaded_programs.txt', 'a') as file:
                    file.write(f"{program_name}: Да\n")
            except Exception as e:
                with open('downloaded_programs.txt', 'a') as file:
                    file.write(f"{program_name}: Нет (Скачивание не удалось: {str(e)})\n")
        else:
            with open('downloaded_programs.txt', 'a') as file:
                file.write(f"{program_name}: Нет (Ссылка не найдена)\n")

    def download_selected_programs(self):
        download_folder = QFileDialog.getExistingDirectory(self, "Выберите папку для загрузки", QDir.currentPath())

        if not download_folder:
            QMessageBox.critical(self, "Ошибка", "Пожалуйста, выберите папку для загрузки.")
            return

        self.selected_programs = 0
        self.downloaded_programs = 0

        with open('downloaded_programs.txt', 'w') as file:
            file.write("Список скачанных программ:\n\n")

        for category, frame in self.category_frames.items():
            for i in range(frame.layout().count()):
                widget = frame.layout().itemAt(i).widget()
                if isinstance(widget, QCheckBox):
                    checkbox = widget
                    if checkbox.isChecked():
                        self.selected_programs += 1

        for category, frame in self.category_frames.items():
            for i in range(frame.layout().count()):
                widget = frame.layout().itemAt(i).widget()
                if isinstance(widget, QCheckBox):
                    checkbox = widget
                    if checkbox.isChecked():
                        program_name = checkbox.text()
                        download_link_or_path = self.programs[category][program_name]
                        download_thread = threading.Thread(target=self.run_download_thread, args=(program_name, download_link_or_path, download_folder))
                        download_thread.start()

        # Ждем завершения всех потоков
        for thread in threading.enumerate():
            if thread != threading.current_thread():
                thread.join()

        # Создаем и открываем файл после завершения всех потоков
        QMessageBox.information(self, "Загрузка завершена", "Загрузка завершена.")
        os.system("notepad.exe downloaded_programs.txt")

    def select_all_programs(self):
        for category, frame in self.category_frames.items():
            for i in range(frame.layout().count()):
                widget = frame.layout().itemAt(i).widget()
                if isinstance(widget, QCheckBox):
                    checkbox = widget
                    checkbox.setChecked(not checkbox.isChecked())

    def create_category_frames(self):
        for i, category in enumerate(self.programs.keys()):
            frame = QFrame()
            frame.setFrameShape(QFrame.Box)
            frame.setFrameShadow(QFrame.Sunken)
            layout = QVBoxLayout()

            for program in self.programs[category]:
                checkbox = QCheckBox(program)
                layout.addWidget(checkbox)

            for i in range(8 - len(self.programs[category])):
                spacer_label = QLabel()
                spacer_label.setFixedHeight(20)
                spacer_label.setStyleSheet("background-color: transparent; border: none;")
                layout.addWidget(spacer_label)

            frame.setLayout(layout)
            self.category_frames[category] = frame

    def organize_programs_into_frames(self):
        grid_layout = QGridLayout()
        column_count = 6

        row = 0
        col = 0
        for category, frame in self.category_frames.items():
            grid_layout.addWidget(frame, row, col)
            col += 1
            if col >= column_count:
                col = 0
                row += 1

        self.layout.addLayout(grid_layout)

    def install_wsl(self):
        wsl_install_command = "wsl --install -d Ubuntu-22.04"

        try:

            subprocess.Popen(wsl_install_command, shell=True)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось установить WSL: {str(e)}")

    def sandbox_windows(self):
        sandbox_windows_command = 'Dism /online /Enable-Feature /FeatureName:"Containers-DisposableClientVM" /NoRestart'

        try:
            subprocess.Popen(sandbox_windows_command, shell=True)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось запустить изолированную среду Windows: {str(e)}")

    def enable_hyperv(self):
        enable_hyperv_command = 'DISM /Online /Enable-Feature /All /FeatureName:Microsoft-Hyper-V /NoRestart'

        try:
            subprocess.Popen(enable_hyperv_command, shell=True)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось включить Hyper-V: {str(e)}")

    def setup_exe(self):
        installation_folder = QFileDialog.getExistingDirectory(self, "Выберите папку загрузки", QDir.currentPath())

        exe_files = [filename for filename in os.listdir(installation_folder) if filename.endswith(".exe")]

        try:
            for exe_file in exe_files:
                exe_path = os.path.join(installation_folder, exe_file)

                try:
                    subprocess.Popen(f'"{exe_path}"', shell=True).wait()

                except Exception as e:
                    QMessageBox.critical(self, "Ошибка", f"Не удалось установить {exe_file}: {str(e)}")

            QMessageBox.information(self, "Установка завершена", "Все программы установлены.")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось установить программы: {str(e)}")

if __name__ == "__main__":
    window = ProgramDownloader()
    window.show()
    app.exec_()

