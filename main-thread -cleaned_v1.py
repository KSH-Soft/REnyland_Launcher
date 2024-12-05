from discord_webhook import DiscordWebhook, DiscordEmbed
from PyQt5.QtWidgets import QLineEdit, QToolButton, QTextEdit, QCheckBox, QApplication, QProgressBar, QRadioButton, QPushButton, QMainWindow, QLabel, QGroupBox, QMessageBox, QFileDialog, QDialog, QVBoxLayout, QHBoxLayout, QFrame, QWidget, QTabWidget, QComboBox
from PyQt5.QtCore import Qt, QRect, QResource, QThread, pyqtSignal, QSize, QMetaObject
from PyQt5 import QtGui
from  configparser import ConfigParser
import os
import sys
from shutil import rmtree, copytree, move
from io import BytesIO
from time import sleep
import requests
import socket
from zipfile import ZipFile, BadZipFile
from random import choice
import webbrowser

version = '1.0.0.0'
serverIP = ''
appdata_path = os.getenv('APPDATA')
KSHDIR = os.path.join(appdata_path, 'KSH-Soft')
KSHRPDIR = os.path.join(appdata_path, 'KSH-Soft', 'RenylandLauncher')
KSHRPTMPDIR = os.path.join(appdata_path, 'KSH-Soft', 'RenylandLauncher', "TMP")
KSHRPTMPDIRDLL = os.path.join(appdata_path, 'KSH-Soft', 'RenylandLauncher', "TMP", "BepInEx", "plugins")
KSHRLFile = os.path.join(appdata_path, 'KSH-Soft', 'RenylandLauncher', 'config.ini')
KSHRLVERSIONFile = os.path.join(appdata_path, 'KSH-Soft', 'RenylandLauncher', "VERSIONS.ini")
GameLoc = ''
webhook_url = ''
webhook = DiscordWebhook(url=webhook_url)

class SliderIMG(QThread):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        
    def run(self):
        def download_file(url, local_filename):
            try:
                response = requests.get(url)
                response.raise_for_status()

                with open(local_filename, 'wb') as f:
                    f.write(response.content)
                # print(f"Fichier téléchargé avec succès: {local_filename}")
            except requests.exceptions.RequestException as e:
                print(f"Erreur lors du téléchargement: {e}")
                
        def display_image_from_url_Main(url):
            response = requests.get(url)
            if response.status_code == 200:
                image_data = BytesIO(response.content)
                pixmap = QtGui.QPixmap()
                pixmap.loadFromData(image_data.read())
                scaled_pixmap = pixmap.scaled(self.main_window.ArtworkIMG.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
                self.main_window.ArtworkIMG.setPixmap(scaled_pixmap)
            else:
                pass
        
        def read_random_line(data):
            if data:
                random_item = choice(data)
                image_url = random_item['url']
                display_image_from_url_Main(image_url)
                self.main_window.ArtworkDesc.setText(f"   Artwork by : {random_item['name']}")
                # print(f"Ligne aléatoire: URL = {random_item['url']}, NAME = {random_item['name']}")
            else:
                print("Aucune donnée disponible.")
        
        def read_file_and_store_variables(file_path):
            data = []
            try:
                with open(file_path, 'r') as f:
                    lines = f.readlines()
                    for line in lines:
                        line = line.strip()
                        if line and '"' in line:
                            try:
                                url, name = line.split('","')
                                url = url.replace('"', '')
                                name = name.replace('"', '') 
                                data.append({"url": url, "name": name})
                            except ValueError:
                                print(f"Format de ligne incorrect: {line}")
                return data
            except FileNotFoundError:
                print(f"Le fichier {file_path} n'a pas été trouvé.")
            except Exception as e:
                print(f"Erreur lors de la lecture du fichier: {e}")
            return data

        url = ""
        local_filename = "ArtworkList"
        local_filename = os.path.join(appdata_path, 'KSH-Soft', 'RenylandLauncher', local_filename)
        download_file(url, local_filename)
        data = read_file_and_store_variables(local_filename)
        
        read_random_line(data)
        try:
            while True:
                sleep(10)
                try:
                    read_random_line(data)
                except:
                    pass
        except Exception as e:
            pass
        finally:
            pass
    
class ApplyPatchWorker(QThread):
    progress = pyqtSignal(str)  # Signal pour mettre à jour l'interface
    error = pyqtSignal(str)     # Signal pour les erreurs
    finished = pyqtSignal()     # Signal quand le thread est terminé

    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent  # Pour accéder à la fenêtre principale

    def run(self):
        try:
            self.progress.emit("0")
            self.main_window.PatchResult.append("Clear WORKDIR/TMP Folder...")
            self.scrollDown()
            self.clear_folder()
            self.progress.emit("10")
            
            VAR_BIE = self.read_value_from_ini('Version', 'bepinexversion', KSHRLVERSIONFile)
            VAR_REM = self.main_window.read_value_from_ini('Version', 'versionrenylandmod', KSHRLVERSIONFile)
            ToggleBIE = 0
            ToggleREM = 0

            self.main_window.PatchResult.append("Download and Extract Files...")
            self.scrollDown()
            
            if self.main_window.rdo_Steam.isChecked():
                # print("steam : Coché")
                if self.main_window.rdo_SteamInstall.isChecked():
                    self.progress.emit("20")
                    self.main_window.PatchResult.append("Download the BepInEx archive...")
                    self.scrollDown()
                    url = "" 
                    self.download_and_extract_zip(url)
                    ToggleBIE = 1
                # self.main_window.progressBar.setValue(75)
                self.progress.emit("40")
                self.main_window.PatchResult.append("Configure/Installing Renyland Mods...")
                self.scrollDown()
                if self.main_window.chk_SteamModRedirect.isChecked():
                    # print("steam : Add mod Coché")
                    url = ""
                    self.downloadDLL(url, "Renyland_DNS.dll")
                    ToggleREM = 1
            elif self.main_window.rdo_Crack.isChecked():
                # print("Github : coché")
                if self.main_window.rdo_CrackInstall.isChecked():
                    self.progress.emit("20")
                    self.main_window.PatchResult.append("Download the BepInEx archive...")
                    self.scrollDown()
                    url = ""
                    self.download_and_extract_zip(url)
                    ToggleBIE = 1
                self.progress.emit("30")
                self.main_window.PatchResult.append("Configure/Installing Bypass Mods...")
                self.scrollDown()
                if self.main_window.chk_CrackAddCrack.isChecked():
                    # print("Github : Add crack Coché")
                    url = ""
                    self.downloadDLL(url, "steam_api64.dll")
                self.progress.emit("40")
                self.main_window.PatchResult.append("Configure/Installing Renyland Mods...")
                self.scrollDown()
                if self.main_window.chk_CrackModRedirect.isChecked():
                    # print("Github : Add mod Coché")
                    url = ""
                    self.downloadDLL(url, "Renyland_DNS.dll")
                    ToggleREM = 1
            else:
                self.main_window.show_critical('WTF !!!!')
                self.main_window.PatchResult.setStyleSheet("background-color: rgb(125, 0, 0);")
                self.main_window.PatchResult.append('ERROR WTF !!!!')
                self.scrollDown()
                return
            
            self.progress.emit("50")
            self.main_window.PatchResult.append("Copy all File into Anyland...")
            self.scrollDown()
            self.copy_all()
            self.progress.emit("60")
    
            
            self.main_window.save_to_ini(KSHRLFile, 'Config', 'patched', "Patched")
            if ToggleBIE == 1:
                self.main_window.save_to_ini(KSHRLFile, 'Config', 'bepinexversion', VAR_BIE)
                self.main_window.BepInExVersionVAR.setText(VAR_BIE)
            if ToggleREM == 1:
                self.main_window.save_to_ini(KSHRLFile, 'Config', 'versionrenylandmod', VAR_REM)
                self.main_window.VersionREnylandModVAR.setText(VAR_REM)
        
            self.progress.emit("70")
            self.main_window.PatchResult.append("Clear WORKDIR/TMP Folder...")
            self.scrollDown()
            self.clear_folder()
            self.progress.emit("80")
            self.main_window.save_to_ini(KSHRLFile, 'Config', 'patched', "Patched")
            self.main_window.PatchResult.append("Anyland is Patched for Renyland...")
            self.main_window.PatchResult.append("")
            self.main_window.PatchResult.append(" /!\\  Ready to start  /!\\")
            self.main_window.PatchResult.setStyleSheet("background-color: rgb(0, 125, 0);")
            self.progress.emit("90")
            self.main_window.RunCheckAll()
            self.progress.emit("100")
            self.scrollDown()
            self.main_window.btn_Apply.setText("Already patched")
            
            # self.main_window.progress.emit(" /!\\  Ready to start  /!\\")
        except Exception as e:
            self.error.emit(str(e))
        finally:
            self.finished.emit()
    
    def scrollDown(self):
            try:
                cursor = self.main_window.PatchResult.textCursor()
                cursor.movePosition(cursor.End)
                self.main_window.PatchResult.setTextCursor(cursor)
            except:
                pass
    
    def clear_folder(self):
        try:
            if os.path.exists(KSHRPTMPDIR) and os.path.isdir(KSHRPTMPDIR):
                for filename in os.listdir(KSHRPTMPDIR):
                    file_path = os.path.join(KSHRPTMPDIR, filename)
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        rmtree(file_path)
            else:
                pass
                # print("Le dossier n'existe pas ou n'est pas un dossier valide.")
        except Exception as e:
            self.main_window.PatchResult.setStyleSheet("background-color: rgb(125, 0, 0);")
            # print(f"Erreur lors du nettoyage du dossier : {e}")
            self.main_window.PatchResult.append(f"Folder cleanup error : {e}")

    def download_and_extract_zip(self, url):
        
        extract_to = KSHRPTMPDIR
        zip_filename = ""
    
        try:
            # print(f"Téléchargement depuis {url}...")
            response = requests.get(url, stream=True)
            response.raise_for_status()
    
            KSHRPTMPDIRZIP = os.path.join(appdata_path, 'KSH-Soft', 'RenylandLauncher', "TMP", zip_filename)
            with open(KSHRPTMPDIRZIP, "wb") as zip_file:
                for chunk in response.iter_content(chunk_size=8192):
                    zip_file.write(chunk)
            # print(f"Fichier téléchargé : {KSHRPTMPDIRZIP}")
            
            # self.progressBar.setValue(20)
            self.main_window.PatchResult.append("Extract the BepInEx archive...")
            
            if not os.path.exists(extract_to):
                os.makedirs(extract_to)

            # print(f"Décompression dans le répertoire : {extract_to}")
            with ZipFile(KSHRPTMPDIRZIP, "r") as zip_ref:
                zip_ref.extractall(extract_to)
            # print("Décompression terminée.")
            
            # self.progressBar.setValue(40)
            self.main_window.PatchResult.append("Remove the BepInEx archive...")
            
            if os.path.exists(KSHRPTMPDIRZIP):
                os.remove(KSHRPTMPDIRZIP)
                # print("Fichier ZIP supprimé après extraction.")

        
        except requests.exceptions.RequestException as e:
            # print(f"Erreur lors du téléchargement : {e}")
            self.main_window.PatchResult.setStyleSheet("background-color: rgb(125, 0, 0);")
            self.main_window.PatchResult.append(f"Error while downloading : {e}")
        except BadZipFile:
            # print("Le fichier téléchargé n'est pas un fichier ZIP valide.")
            self.main_window.PatchResult.setStyleSheet("background-color: rgb(125, 0, 0);")
            self.main_window.PatchResult.append("The downloaded file is not a valid ZIP file.")
            
    def downloadDLL(self, url, name):
        zip_filename = name
        if not os.path.exists(KSHRPTMPDIRDLL):
            try:
                os.makedirs(KSHRPTMPDIRDLL, exist_ok=True)
            except:
                self.main_window.PatchResult.setStyleSheet("background-color: rgb(125, 0, 0);")
                self.main_window.PatchResult.append("ERROR")
        try:
            # print(f"Téléchargement depuis {url}...")
            response = requests.get(url, stream=True)
            response.raise_for_status()
            if name == "steam_api64.dll":
                KSHRPTMPDIRDLLL = os.path.join(KSHRPTMPDIR, zip_filename)
            else:
                KSHRPTMPDIRDLLL = os.path.join(KSHRPTMPDIRDLL, zip_filename)
                
            with open(KSHRPTMPDIRDLLL, "wb") as zip_file:
                for chunk in response.iter_content(chunk_size=8192):
                    zip_file.write(chunk)
            # print(f"Fichier téléchargé : {KSHRPTMPDIRDLLL}")
                        
        except requests.exceptions.RequestException as e:
            self.main_window.PatchResult.setStyleSheet("background-color: rgb(125, 0, 0);")
            # print(f"Erreur lors du téléchargement : {e}")
            self.main_window.PatchResult.append(f"Error while downloading : {e}")
        except BadZipFile:
            self.main_window.PatchResult.setStyleSheet("background-color: rgb(125, 0, 0);")
            # print("Le fichier téléchargé n'est pas un fichier ZIP valide.")
            self.main_window.PatchResult.append("The downloaded file is not a valid ZIP file.")
    
    def read_value_from_ini(self, section, key, filename):
        config = ConfigParser()
        config.read(filename)
        if config.has_section(section) and config.has_option(section, key):
            value = config.get(section, key)
            return value
        else:
            return None
    
    def copy_all(self):
        src = KSHRPTMPDIR
        GameLoc = self.read_value_from_ini('Config', 'exeloc', KSHRLFile)
        directory = os.path.dirname(GameLoc)
        dst = directory
        try:
            copytree(src, dst, dirs_exist_ok=True)
            # print(f"Le contenu du dossier {src} a été copié avec succès vers {dst}.")
        except Exception as e:
            # print(f"Erreur lors de la copie du dossier : {e}")
            self.main_window.PatchResult.setStyleSheet("background-color: rgb(125, 0, 0);")
            self.main_window.PatchResult.append(f"Error copying folder : {e}")
    
    
# class Ui_MainWindow(object):
class Ui_MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
    
    def showEvent(self, event):
        super().showEvent(event)
        self.raise_()
        self.activateWindow()

    def start_Slide(self):
        self.patch_workerr = SliderIMG(parent=self)
        self.patch_workerr.start()

    def start_patch_thread(self):
        self.patch_worker = ApplyPatchWorker(parent=self)
        self.patch_worker.progress.connect(self.update_patch_status)
        self.patch_worker.error.connect(self.show_error)
        self.patch_worker.finished.connect(self.patch_finished)
        self.patch_worker.start()

    def update_patch_status(self, message):
        integer_number = int(message)
        self.progressBar.setValue(integer_number)
        # self.PatchResult.append(message)
        
    def show_error(self, error_message):
        QMessageBox.critical(self, "Error", f"An error has occurred: {error_message}")

    def patch_finished(self):
        self.patch_worker.terminate
        QMessageBox.information(self, "Completed", "The patch has been successfully applied!")
    
    def setupUi(self, MainWindow):
        self.MainWindow = MainWindow
        self.MainWindow.setWindowTitle("Renyland_Launcher")
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1000, 600)
        MainWindow.setFixedSize(1000, 600)
        MainWindow.setWindowFlags(Qt.FramelessWindowHint)
                
        app_icon = QtGui.QIcon()
        app_icon.addFile(':/Asset/logo.ico', QSize(48, 48))
        self.MainWindow.setWindowIcon(app_icon)
        
        fontSegoeBlack = QtGui.QFont()
        fontSegoeBlack.setFamily("Segoe UI Black")
        fontSegoeBlack.setBold(True)
        fontSegoeBlack.setPointSize(8)
        
        fontSegoeBlack_under = QtGui.QFont()
        fontSegoeBlack_under.setFamily("Segoe UI Black")
        fontSegoeBlack_under.setBold(True)
        fontSegoeBlack_under.setUnderline(True)
        fontSegoeBlack_under.setPointSize(8)
        
        fontSegoe_under = QtGui.QFont()
        fontSegoe_under.setFamily("Segoe UI")
        fontSegoe_under.setBold(True)
        fontSegoe_under.setUnderline(True)
        fontSegoe_under.setPointSize(8)
        
        fontSegoe = QtGui.QFont()
        fontSegoe.setFamily("Segoe UI")
        fontSegoe.setPointSize(8)
        
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setGeometry(QRect(40, 90, 921, 491))
        self.tabWidget.setMaximumSize(QSize(16777215, 16777215))
        self.tabWidget.setFont(fontSegoeBlack)
        
        
        
        self.tabWidget.setAutoFillBackground(False)
        self.tabWidget.setStyleSheet("QTabBar::tab {\n"
"    min-width: 230%; \n"
"    background: #BCD2EA;\n"
"    color: #2A373F;\n"
"    font-family: \'Arimo\', sans-serif;\n"
"    border-top: 4px solid #A9B9C6;\n"
"    border-bottom: 6px solid #B0C6DD;\n"
"    border-right: 5px solid #CFEBFF;\n"
"    border-left: 5px solid #899EB3;\n"
"    border-radius: 4px;\n"
"    padding: 10px 20px;\n"
"    margin: 10px; \n"
# "    box-shadow: 0px 6px 0px #627082;\n"
# "    transform: translate(0px, -6px);\n"
"}\n"
"\n"
"QTabBar::tab:selected {\n"
"    background: #CFEBFF;\n"
"    color: #1B2631;\n"
# "    box-shadow: 0px 4px 0px #627082;\n"
# "    transform: translate(0px, -4px);\n"
"}\n"
"\n"
"QTabBar::tab:hover {\n"
"    background: #E0F5FF;\n"
# "    box-shadow: 0px 4px 0px #627082;\n"
# "    transform: translate(0px, -4px);\n"
"}\n"
"\n"
"QTabBar::tab:pressed {\n"
# "    transform: translate(0px, -3px);\n"
# "    box-shadow: 0px 3px 0px #627082;\n"
"    width: 200%\n"
"}\n"
"\n"
"QTabWidget::pane {\n"
"    background: #BCD2EA;\n"
"    border-radius: 4px;\n"
"    padding: 10px;\n"
"    border-top: 4px solid #A9B9C6;\n"
"    border-bottom: 6px solid #B0C6DD;\n"
"    border-right: 5px solid #CFEBFF;\n"
"    border-left: 5px solid #899EB3;\n"
# "    box-shadow: 0px 0px 20px #8E9AA8, 0px 10px 0px #627082, 0px 0px 80px #33BEFF;\n"
"}")
        self.tabWidget.setObjectName("tabWidget")
        self.HOME_TAB = QWidget()
        self.HOME_TAB.setObjectName("HOME_TAB")
        self.PLAYOFFLINE = QPushButton(self.HOME_TAB)
        self.PLAYOFFLINE.setGeometry(QRect(550, 340, 161, 51))
        self.PLAYOFFLINE.setFont(fontSegoeBlack)
        self.PLAYOFFLINE.setStyleSheet("QPushButton {\n"
"    background: #BCD2EA;\n"
"    color: #2A373F;\n"
# "    font-family: \'Arimo\', sans-serif;\n"
"    border-top: 4px solid #A9B9C6;\n"
"    border-bottom: 6px solid #B0C6DD;\n"
"    border-right: 5px solid #CFEBFF;\n"
"    border-left: 5px solid #899EB3;\n"
"    border-radius: 4px;\n"
"    padding: 10px 20px;\n"
"    margin: 4px;\n"
# "    box-shadow: 0px 6px 0px #627082;\n"
# "    transform: translate(0px, -6px);\n"
"    min-width: 100px;\n"
# "    transition: all 0.2s ease; \n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background: #E0F5FF;\n"
# "    box-shadow: 0px 4px 0px #627082;\n"
# "    transform: translate(0px, -4px);\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"    background: #CFEBFF;\n"
# "    transform: translate(0px, -3px);\n"
# "    box-shadow: 0px 3px 0px #627082;\n"
"}")
        self.PLAYOFFLINE.setObjectName("PLAYOFFLINE")
        self.PLAYOFFLINE.mouseReleaseEvent = self.RUN_OFFLINE
        
        self.PLAYONLINE = QPushButton(self.HOME_TAB)
        self.PLAYONLINE.setGeometry(QRect(720, 340, 161, 51))
        self.PLAYONLINE.setFont(fontSegoeBlack)
        self.PLAYONLINE.setStyleSheet("QPushButton {\n"
"    background: #BCD2EA;\n"
"    color: #2A373F;\n"
# "    font-family: \'Arimo\', sans-serif;\n"
"    border-top: 4px solid #A9B9C6;\n"
"    border-bottom: 6px solid #B0C6DD;\n"
"    border-right: 5px solid #CFEBFF;\n"
"    border-left: 5px solid #899EB3;\n"
"    border-radius: 4px;\n"
"    padding: 10px 20px;\n"
"    margin: 4px;\n"
# "    box-shadow: 0px 6px 0px #627082;\n"
# "    transform: translate(0px, -6px);\n"
"    min-width: 100px;\n"
# "    transition: all 0.2s ease; \n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background: #E0F5FF;\n"
# "    box-shadow: 0px 4px 0px #627082;\n"
# "    transform: translate(0px, -4px);\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"    background: #CFEBFF;\n"
# "    transform: translate(0px, -3px);\n"
# "    box-shadow: 0px 3px 0px #627082;\n"
"}")
        self.PLAYONLINE.setObjectName("PLAYONLINE")
        self.PLAYONLINE.mouseReleaseEvent = self.RUN_ONLINE
        
        self.OnlinePayer = QLabel(self.HOME_TAB)
        self.OnlinePayer.setGeometry(QRect(587, 316, 111, 21))
        self.OnlinePayer.setAlignment(Qt.AlignCenter)
        self.OnlinePayer.setObjectName("OnlinePayer")
        self.OnlinePayer.setFont(fontSegoe)
        
        self.PUNServerChoice = QComboBox(self.HOME_TAB)
        self.PUNServerChoice.setGeometry(QRect(718, 315, 165, 22))
        self.PUNServerChoice.setObjectName("PUNServerChoice")
        self.PUNServerChoice.addItem("")
        self.PUNServerChoice.addItem("")
        self.PUNServerChoice.addItem("")
        self.PUNServerChoice.setFont(fontSegoe)
        
        self.WebsiteView = QLabel(self.HOME_TAB)
        self.WebsiteView.setGeometry(QRect(10, 10, 521, 321))
        self.WebsiteView.setStyleSheet("background-color: rgb(137, 158, 179);")
        self.WebsiteView.setText("")
        self.WebsiteView.setObjectName("WebsiteView")
        self.WebsiteView.mouseReleaseEvent = self.OpenWebsite
        
        self.Status = QLabel(self.HOME_TAB)
        self.Status.setGeometry(QRect(50, 340, 481, 51))
        self.Status.setStyleSheet("QLabel {\n"
"    background-color: #BCD2EA;\n"
"    background: #BCD2EA;\n"
"    color: #2A373F;\n"
"    border-top: 4px solid #A9B9C6;\n"
"    border-bottom: 6px solid #B0C6DD;\n"
"    border-right: 5px solid #CFEBFF;\n"
"    border-left: 5px solid #899EB3;\n"
"    border-radius: 4px;\n"
"    padding: 10px 20px;\n"
"    margin: 2px;\n"
# "    box-shadow: 0px 6px 0px #627082;\n"
# "    transform: translate(0px, -6px);\n"
# "    min-width: 100px;\n"
# "    transition: all 0.2s ease; \n"
"}")
        self.Status.setObjectName("Status")
        self.Status.setFont(fontSegoe)
        
        self.ArtworkIMG = QLabel(self.HOME_TAB)
        self.ArtworkIMG.setGeometry(QRect(550, 10, 330, 232))
        # self.ArtworkIMG.setStyleSheet("background-color: rgb(255, 170, 255);")
        self.ArtworkIMG.setStyleSheet("background-color: rgb(169, 185, 198);")
        self.ArtworkIMG.setText("")
        self.ArtworkIMG.setObjectName("ArtworkIMG")
        # self.ArtworkIMG.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        self.ArtworkIMG.setAlignment(Qt.AlignCenter)
        
        self.LedStatus = QLabel(self.HOME_TAB)
        self.LedStatus.setGeometry(QRect(-10, 336, 61, 61))
        self.LedStatus.setStyleSheet("image: url(:/Asset/led-r.png);")
        self.LedStatus.setText("")
        self.LedStatus.setObjectName("LedStatus")
        
        # self.Reload = QLabel(self.HOME_TAB)
        # self.Reload.setGeometry(QRect(560, 316, 21, 21))
        # self.Reload.setStyleSheet("image: url(:/Asset/reload.png);")
        # self.Reload.setText("")
        # self.Reload.setObjectName("Reload")
        self.Reload = QLabel(self.HOME_TAB)
        self.Reload.setObjectName(u"Reload")
        self.Reload.setGeometry(QRect(560, 316, 21, 21))
        pixmap = QtGui.QPixmap(":/Asset/reload.png")
        self.Reload.setPixmap(pixmap)
        self.Reload.setAlignment(Qt.AlignCenter)
        self.Reload.mouseReleaseEvent = self.launch_tests_thread
        
        self.TotalNewPlayers = QLabel(self.HOME_TAB)
        self.TotalNewPlayers.setGeometry(QRect(550, 260, 331, 21))
        self.TotalNewPlayers.setAlignment(Qt.AlignCenter)
        self.TotalNewPlayers.setObjectName("TotalNewPlayers")
        self.TotalNewPlayers.setFont(fontSegoe)
        
        self.TotalArea = QLabel(self.HOME_TAB)
        self.TotalArea.setGeometry(QRect(550, 280, 151, 21))
        self.TotalArea.setAlignment(Qt.AlignCenter)
        self.TotalArea.setObjectName("TotalArea")
        self.TotalArea.setFont(fontSegoe)
        
        self.TotalThings = QLabel(self.HOME_TAB)
        self.TotalThings.setGeometry(QRect(710, 280, 171, 21))
        self.TotalThings.setAlignment(Qt.AlignCenter)
        self.TotalThings.setObjectName("TotalThings")
        self.TotalThings.setFont(fontSegoe)
        
        self.ULineServerInfos = QFrame(self.HOME_TAB)
        self.ULineServerInfos.setGeometry(QRect(630, 250, 251, 20))
        self.ULineServerInfos.setFrameShape(QFrame.HLine)
        self.ULineServerInfos.setFrameShadow(QFrame.Sunken)
        self.ULineServerInfos.setObjectName("ULineServerInfos")
        
        self.ServerInfos = QLabel(self.HOME_TAB)
        self.ServerInfos.setGeometry(QRect(555, 250, 71, 16))
        self.ServerInfos.setAlignment(Qt.AlignCenter)
        self.ServerInfos.setObjectName("ServerInfos")
        self.ServerInfos.setFont(fontSegoe)
        
        self.BLineServerInfos = QFrame(self.HOME_TAB)
        self.BLineServerInfos.setGeometry(QRect(550, 292, 331, 20))
        self.BLineServerInfos.setFrameShape(QFrame.HLine)
        self.BLineServerInfos.setFrameShadow(QFrame.Sunken)
        self.BLineServerInfos.setObjectName("BLineServerInfos")
        
        self.RLineServerInfos = QFrame(self.HOME_TAB)
        self.RLineServerInfos.setGeometry(QRect(870, 264, 20, 33))
        self.RLineServerInfos.setFrameShape(QFrame.VLine)
        self.RLineServerInfos.setFrameShadow(QFrame.Sunken)
        self.RLineServerInfos.setObjectName("RLineServerInfos")
        
        self.LLineServerInfos = QFrame(self.HOME_TAB)
        self.LLineServerInfos.setGeometry(QRect(540, 260, 20, 38))
        self.LLineServerInfos.setFrameShape(QFrame.VLine)
        self.LLineServerInfos.setFrameShadow(QFrame.Sunken)
        self.LLineServerInfos.setObjectName("LLineServerInfos")
        
        self.ArtworkDesc = QLabel(self.HOME_TAB)
        self.ArtworkDesc.setObjectName(u"ArtworkDesc")
        self.ArtworkDesc.setGeometry(QRect(550, 221, 191, 21))
        self.ArtworkDesc.setStyleSheet(u"background-color: rgba(161, 161, 161, 175);")
        self.ArtworkDesc.setFont(fontSegoe)
        
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/Asset/25694-100px.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.tabWidget.addTab(self.HOME_TAB, icon, "")
        self.PATCH_TAB = QWidget()
        self.PATCH_TAB.setObjectName("PATCH_TAB")
        
        self.GroupPatch = QGroupBox(self.PATCH_TAB)
        self.GroupPatch.setGeometry(QRect(-10, -6, 911, 421))
        self.GroupPatch.setTitle("")
        self.GroupPatch.setObjectName("GroupPatch")
        
        self.Allbox = QGroupBox(self.GroupPatch)
        self.Allbox.setObjectName(u"Allbox")
        self.Allbox.setTitle("")
        self.Allbox.setGeometry(QRect(440, 50, 451, 21))
        self.Allbox.setStyleSheet(u"QGroupBox {\n"
        "            border: none;\n"
        "            margin: 0;\n"
        "            padding: 0;\n"
        "        }")
        self.Allbox.setFlat(False)
        self.Allbox.setCheckable(False)
        
        self.rdo_Steam = QRadioButton(self.Allbox)
        self.rdo_Steam.setObjectName(u"rdo_Steam")
        self.rdo_Steam.setGeometry(QRect(10, 0, 201, 20))
        self.rdo_Steam.setFont(fontSegoe_under)
        self.rdo_Steam.setChecked(False)
        self.rdo_Steam.toggled.connect(self.SteamToggled)
        
        self.rdo_Crack = QRadioButton(self.Allbox)
        self.rdo_Crack.setObjectName(u"rdo_Crack")
        self.rdo_Crack.setGeometry(QRect(240, 0, 201, 20))
        self.rdo_Crack.setChecked(False)
        self.rdo_Crack.setFont(fontSegoe_under)
        
        self.groupBoxSteam = QGroupBox(self.GroupPatch)
        self.groupBoxSteam.setGeometry(QRect(447, 74, 201, 101))
        self.groupBoxSteam.setTitle("")
        self.groupBoxSteam.setObjectName("groupBoxSteam")        
        
        self.rdo_SteamInstall = QRadioButton(self.groupBoxSteam)
        self.rdo_SteamInstall.setGeometry(QRect(10, 40, 171, 20))
        self.rdo_SteamInstall.setChecked(True)
        self.rdo_SteamInstall.setFont(fontSegoe)
        self.rdo_SteamInstall.setObjectName("rdo_SteamInstall")
        # self.rdo_SteamInstall.toggled.connect(self.BepInExSteamToggled)
        
        
        self.chk_SteamModRedirect = QCheckBox(self.groupBoxSteam)
        self.chk_SteamModRedirect.setGeometry(QRect(10, 70, 181, 20))
        self.chk_SteamModRedirect.setChecked(True)
        self.chk_SteamModRedirect.setFont(fontSegoe)
        
        self.chk_SteamModRedirect.setObjectName("chk_SteamModRedirect")
        self.rdo_SteamNoInstall = QRadioButton(self.groupBoxSteam)
        self.rdo_SteamNoInstall.setGeometry(QRect(10, 10, 171, 20))
        self.rdo_SteamNoInstall.setObjectName("rdo_SteamNoInstall")
        self.rdo_SteamNoInstall.setFont(fontSegoe)
        
        self.groupBoxCrack = QGroupBox(self.GroupPatch)
        self.groupBoxCrack.setGeometry(QRect(677, 74, 201, 131))
        self.groupBoxCrack.setTitle("")
        self.groupBoxCrack.setObjectName("groupBoxCrack")
        
        self.rdo_CrackInstall = QRadioButton(self.groupBoxCrack)
        self.rdo_CrackInstall.setGeometry(QRect(10, 40, 171, 20))
        self.rdo_CrackInstall.setChecked(True)
        self.rdo_CrackInstall.setObjectName("rdo_CrackInstall")
        self.rdo_CrackInstall.setFont(fontSegoe)
        # self.rdo_CrackInstall.toggled.connect(self.BepInExCrackToggled)
        
        self.chk_CrackAddCrack = QCheckBox(self.groupBoxCrack)
        self.chk_CrackAddCrack.setGeometry(QRect(10, 70, 151, 20))
        self.chk_CrackAddCrack.setChecked(True)
        self.chk_CrackAddCrack.setObjectName("chk_CrackAddCrack")
        self.chk_CrackAddCrack.setFont(fontSegoe)
        
        self.rdo_CrackNoInstall = QRadioButton(self.groupBoxCrack)
        self.rdo_CrackNoInstall.setGeometry(QRect(10, 10, 171, 20))
        self.rdo_CrackNoInstall.setObjectName("rdo_CrackNoInstall")
        self.rdo_CrackNoInstall.setFont(fontSegoe)
        
        self.chk_CrackModRedirect = QCheckBox(self.groupBoxCrack)
        self.chk_CrackModRedirect.setGeometry(QRect(10, 100, 181, 20))
        self.chk_CrackModRedirect.setChecked(True)
        self.chk_CrackModRedirect.setObjectName("chk_CrackModRedirect")
        self.chk_CrackModRedirect.setFont(fontSegoe)
        
        self.btn_Apply = QPushButton(self.GroupPatch)
        self.btn_Apply.setGeometry(QRect(570, 224, 181, 51))
        self.btn_Apply.setFont(fontSegoeBlack)
        self.btn_Apply.setStyleSheet("QPushButton {\n"
"    background: #BCD2EA;\n"
"    color: #2A373F;\n"
"    font-family: \'Arimo\', sans-serif;\n"
"    border-top: 4px solid #A9B9C6;\n"
"    border-bottom: 6px solid #B0C6DD;\n"
"    border-right: 5px solid #CFEBFF;\n"
"    border-left: 5px solid #899EB3;\n"
"    border-radius: 4px;\n"
"    padding: 10px 20px;\n"
"    margin: 4px;\n"
# "    box-shadow: 0px 6px 0px #627082;\n"
# "    transform: translate(0px, -6px);\n"
"    min-width: 100px;\n"
# "    transition: all 0.2s ease; \n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background: #E0F5FF;\n"
# "    box-shadow: 0px 4px 0px #627082;\n"
# "    transform: translate(0px, -4px);\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"    background: #CFEBFF;\n"
# "    transform: translate(0px, -3px);\n"
# "    box-shadow: 0px 3px 0px #627082;\n"
"}")
        self.btn_Apply.setObjectName("btn_Apply")
        self.btn_Apply.mouseReleaseEvent = self.ApplyPatch
        
        self.line = QFrame(self.GroupPatch)
        self.line.setGeometry(QRect(650, 44, 20, 171))
        self.line.setFrameShape(QFrame.VLine)
        self.line.setFrameShadow(QFrame.Sunken)
        self.line.setObjectName("line")
        self.line_2 = QFrame(self.GroupPatch)
        self.line_2.setGeometry(QRect(436, 204, 451, 20))
        self.line_2.setFrameShape(QFrame.HLine)
        self.line_2.setFrameShadow(QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.line_3 = QFrame(self.GroupPatch)
        self.line_3.setGeometry(QRect(429, 14, 16, 381))
        self.line_3.setFrameShape(QFrame.VLine)
        self.line_3.setFrameShadow(QFrame.Sunken)
        self.line_3.setObjectName("line_3")
        self.line_4 = QFrame(self.GroupPatch)
        self.line_4.setGeometry(QRect(880, 14, 16, 381))
        self.line_4.setFrameShape(QFrame.VLine)
        self.line_4.setFrameShadow(QFrame.Sunken)
        self.line_4.setObjectName("line_4")
        self.line_5 = QFrame(self.GroupPatch)
        self.line_5.setGeometry(QRect(437, 4, 451, 20))
        self.line_5.setFrameShape(QFrame.HLine)
        self.line_5.setFrameShadow(QFrame.Sunken)
        self.line_5.setObjectName("line_5")
        
        self.questiongame = QLabel(self.GroupPatch)
        self.questiongame.setGeometry(QRect(447, 18, 431, 20))
        self.questiongame.setFont(fontSegoeBlack_under)
        self.questiongame.setObjectName("questiongame")
        self.questiongame.setFont(fontSegoeBlack_under)
        
        self.PatchResult = QTextEdit(self.GroupPatch)
        self.PatchResult.setGeometry(QRect(447, 284, 431, 71))
        # self.PatchResult.setGeometry(QRect(447, 284, 431, 101))
        # self.PatchResult.setStyleSheet("background-color:#899EB3;")
        self.PatchResult.setStyleSheet("background-color: rgb(137, 158, 179);")
        self.PatchResult.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.PatchResult.setObjectName("PatchResult")
        self.PatchResult.setReadOnly(True)
        self.PatchResult.setFont(fontSegoe)
        
        self.progressBar = QProgressBar(self.GroupPatch)
        self.progressBar.setGeometry(QRect(450, 364, 425, 20))
        self.progressBar.setProperty("value", 100)
        self.progressBar.setObjectName("progressBar")
        self.IMGPatch = QLabel(self.GroupPatch)
        self.IMGPatch.setGeometry(QRect(10, 10, 411, 391))
        # self.IMGPatch.setStyleSheet("background-image: url(:/Asset/bg.png);")
        self.IMGPatch.setFrameShape(QFrame.NoFrame)
        self.IMGPatch.setFrameShadow(QFrame.Plain)
        self.IMGPatch.setText("")
        self.IMGPatch.setObjectName("IMGPatch")
        
        self.line_6 = QFrame(self.GroupPatch)
        self.line_6.setGeometry(QRect(437, 386, 451, 20))
        self.line_6.setFrameShape(QFrame.HLine)
        self.line_6.setFrameShadow(QFrame.Sunken)
        self.line_6.setObjectName("line_6")
        
        self.AutoDetect = QLabel(self.GroupPatch)
        self.AutoDetect.setGeometry(QRect(720, 20, 161, 21))
        self.AutoDetect.setAlignment(Qt.AlignCenter)
        self.AutoDetect.setObjectName("AutoDetect")
        self.AutoDetect.setFont(fontSegoe)
        
        # self.Allbox.raise_()
        self.rdo_Crack.raise_()
        self.rdo_Steam.raise_()
        self.groupBoxSteam.raise_()
        self.groupBoxCrack.raise_()
        self.btn_Apply.raise_()
        self.line.raise_()
        self.line_2.raise_()
        self.line_3.raise_()
        self.line_4.raise_()
        self.line_5.raise_()
        self.questiongame.raise_()
        self.PatchResult.raise_()
        self.progressBar.raise_()
        self.IMGPatch.raise_()
        self.line_6.raise_()
        self.AutoDetect.raise_()
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/Asset/2150689-100px.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.tabWidget.addTab(self.PATCH_TAB, icon1, "")
        self.SETTINGS_TAB = QWidget()
        self.SETTINGS_TAB.setObjectName("SETTINGS_TAB")
        
        self.pushButton_3 = QPushButton(self.SETTINGS_TAB)
        self.pushButton_3.setGeometry(QRect(600, 310, 231, 41))
        self.pushButton_3.setObjectName("pushButton_3")
        self.pushButton_3.mouseReleaseEvent = self.ClearAllBepInEx
        self.pushButton_3.setFont(fontSegoe)
        
        self.VersionLauncher = QLabel(self.SETTINGS_TAB)
        self.VersionLauncher.setGeometry(QRect(490, 50, 131, 16))
        self.VersionLauncher.setObjectName("VersionLauncher")
        self.VersionLauncher.setFont(fontSegoe)
        
        self.VersionPUNMod = QLabel(self.SETTINGS_TAB)
        self.VersionPUNMod.setGeometry(QRect(490, 130, 131, 16))
        self.VersionPUNMod.setObjectName("VersionPUNMod")
        self.VersionPUNMod.setFont(fontSegoe)
        
        self.VersionREnylandMod = QLabel(self.SETTINGS_TAB)
        self.VersionREnylandMod.setGeometry(QRect(490, 90, 131, 16))
        self.VersionREnylandMod.setObjectName("VersionREnylandMod")
        self.VersionREnylandMod.setFont(fontSegoe)
        
        self.line_14 = QFrame(self.SETTINGS_TAB)
        self.line_14.setGeometry(QRect(430, 24, 20, 181))
        self.line_14.setFrameShape(QFrame.VLine)
        self.line_14.setFrameShadow(QFrame.Sunken)
        self.line_14.setObjectName("line_14")
        
        self.TitleArtWork = QLabel(self.SETTINGS_TAB)
        self.TitleArtWork.setGeometry(QRect(15, 10, 101, 16))
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        self.TitleArtWork.setFont(font)
        self.TitleArtWork.setAlignment(Qt.AlignCenter)
        self.TitleArtWork.setObjectName("TitleArtWork")
        self.TitleArtWork.setFont(fontSegoe)
        
        self.line_12 = QFrame(self.SETTINGS_TAB)
        self.line_12.setGeometry(QRect(10, 200, 431, 20))
        self.line_12.setFrameShape(QFrame.HLine)
        self.line_12.setFrameShadow(QFrame.Sunken)
        self.line_12.setObjectName("line_12")
        self.line_13 = QFrame(self.SETTINGS_TAB)
        self.line_13.setGeometry(QRect(0, 20, 20, 181))
        self.line_13.setFrameShape(QFrame.VLine)
        self.line_13.setFrameShadow(QFrame.Sunken)
        self.line_13.setObjectName("line_13")
        self.line_11 = QFrame(self.SETTINGS_TAB)
        self.line_11.setGeometry(QRect(120, 10, 321, 20))
        self.line_11.setFrameShape(QFrame.HLine)
        self.line_11.setFrameShadow(QFrame.Sunken)
        self.line_11.setObjectName("line_11")
        
        self.toolButton = QToolButton(self.SETTINGS_TAB)
        self.toolButton.setGeometry(QRect(400, 130, 25, 19))
        self.toolButton.setFont(fontSegoeBlack)
        self.toolButton.setObjectName("toolButton")
        self.toolButton.mouseReleaseEvent = self.BrowseIMGArtwork
        
        self.ArtWorkText = QLabel(self.SETTINGS_TAB)
        self.ArtWorkText.setGeometry(QRect(20, 30, 411, 61))
        self.ArtWorkText.setFont(fontSegoe)
        self.ArtWorkText.setAlignment(Qt.AlignCenter)
        self.ArtWorkText.setObjectName("ArtWorkText")
        
        self.IMGPathEdit = QLineEdit(self.SETTINGS_TAB)
        self.IMGPathEdit.setGeometry(QRect(92, 130, 301, 20))
        self.IMGPathEdit.setObjectName("IMGPathEdit")
        
        self.btn_sendDiscord = QPushButton(self.SETTINGS_TAB)
        self.btn_sendDiscord.setGeometry(QRect(320, 162, 111, 31))
        self.btn_sendDiscord.setFont(fontSegoe)
        self.btn_sendDiscord.setObjectName("btn_sendDiscord")
        self.btn_sendDiscord.mouseReleaseEvent = (self.SendToDiscord)
        
        self.StatusSendIMG = QLabel(self.SETTINGS_TAB)
        self.StatusSendIMG.setGeometry(QRect(28, 170, 281, 16))
        self.StatusSendIMG.setFont(fontSegoe)
        self.StatusSendIMG.setObjectName("StatusSendIMG")
        
        self.YourPicture = QLabel(self.SETTINGS_TAB)
        self.YourPicture.setGeometry(QRect(20, 132, 71, 16))
        self.YourPicture.setFont(fontSegoe_under)
        self.YourPicture.setObjectName("YourPicture")
        
        self.UsernameEdit = QLineEdit(self.SETTINGS_TAB)
        self.UsernameEdit.setGeometry(QRect(112, 100, 281, 20))
        self.UsernameEdit.setAlignment(Qt.AlignCenter)
        self.UsernameEdit.setObjectName("UsernameEdit")
        self.UsernameEdit.setFont(fontSegoe)
        
        self.YourUsername = QLabel(self.SETTINGS_TAB)
        self.YourUsername.setGeometry(QRect(20, 102, 81, 16))
        self.YourUsername.setFont(fontSegoe_under)
        self.YourUsername.setObjectName("YourUsername")
        
        self.TitleProgramInfo = QLabel(self.SETTINGS_TAB)
        self.TitleProgramInfo.setGeometry(QRect(480, 20, 71, 16))
        self.TitleProgramInfo.setFont(fontSegoe)
        self.TitleProgramInfo.setAlignment(Qt.AlignCenter)
        self.TitleProgramInfo.setObjectName("TitleProgramInfo")
        
        self.line_15 = QFrame(self.SETTINGS_TAB)
        self.line_15.setGeometry(QRect(870, 34, 20, 161))
        self.line_15.setFrameShape(QFrame.VLine)
        self.line_15.setFrameShadow(QFrame.Sunken)
        self.line_15.setObjectName("line_15")
        self.line_16 = QFrame(self.SETTINGS_TAB)
        self.line_16.setGeometry(QRect(470, 190, 411, 20))
        self.line_16.setFrameShape(QFrame.HLine)
        self.line_16.setFrameShadow(QFrame.Sunken)
        self.line_16.setObjectName("line_16")
        self.line_17 = QFrame(self.SETTINGS_TAB)
        self.line_17.setGeometry(QRect(460, 30, 20, 161))
        self.line_17.setFrameShape(QFrame.VLine)
        self.line_17.setFrameShadow(QFrame.Sunken)
        self.line_17.setObjectName("line_17")
        self.line_18 = QFrame(self.SETTINGS_TAB)
        self.line_18.setGeometry(QRect(560, 20, 321, 20))
        self.line_18.setFrameShape(QFrame.HLine)
        self.line_18.setFrameShadow(QFrame.Sunken)
        self.line_18.setObjectName("line_18")
        self.line_19 = QFrame(self.SETTINGS_TAB)
        self.line_19.setGeometry(QRect(490, 70, 231, 20))
        self.line_19.setFrameShape(QFrame.HLine)
        self.line_19.setFrameShadow(QFrame.Sunken)
        self.line_19.setObjectName("line_19")
        self.line_20 = QFrame(self.SETTINGS_TAB)
        self.line_20.setGeometry(QRect(490, 150, 231, 20))
        self.line_20.setFrameShape(QFrame.HLine)
        self.line_20.setFrameShadow(QFrame.Sunken)
        self.line_20.setObjectName("line_20")
        self.line_21 = QFrame(self.SETTINGS_TAB)
        self.line_21.setGeometry(QRect(490, 110, 231, 20))
        self.line_21.setFrameShape(QFrame.HLine)
        self.line_21.setFrameShadow(QFrame.Sunken)
        self.line_21.setObjectName("line_21")
        
        self.BepInExVersion = QLabel(self.SETTINGS_TAB)
        self.BepInExVersion.setGeometry(QRect(490, 170, 131, 16))
        self.BepInExVersion.setObjectName("BepInExVersion")
        self.BepInExVersion.setFont(fontSegoe)
        
        self.BG_StatusSend = QLabel(self.SETTINGS_TAB)
        self.BG_StatusSend.setGeometry(QRect(20, 165, 291, 26))
        self.BG_StatusSend.setFont(fontSegoe)
        self.BG_StatusSend.setStyleSheet("background-color: rgb(176, 176, 176);")
        self.BG_StatusSend.setText("")
        self.BG_StatusSend.setObjectName("BG_StatusSend")
        
        self.BepInExVersionVAR = QLabel(self.SETTINGS_TAB)
        self.BepInExVersionVAR.setGeometry(QRect(630, 170, 91, 16))
        self.BepInExVersionVAR.setAlignment(Qt.AlignCenter)
        self.BepInExVersionVAR.setObjectName("BepInExVersionVAR")
        self.BepInExVersionVAR.setFont(fontSegoe)
        
        self.VersionPUNModVAR = QLabel(self.SETTINGS_TAB)
        self.VersionPUNModVAR.setGeometry(QRect(630, 130, 91, 16))
        self.VersionPUNModVAR.setAlignment(Qt.AlignCenter)
        self.VersionPUNModVAR.setObjectName("VersionPUNModVAR")
        self.VersionPUNModVAR.setFont(fontSegoe)
        
        self.VersionREnylandModVAR = QLabel(self.SETTINGS_TAB)
        self.VersionREnylandModVAR.setGeometry(QRect(630, 90, 91, 16))
        self.VersionREnylandModVAR.setAlignment(Qt.AlignCenter)
        self.VersionREnylandModVAR.setObjectName("VersionREnylandModVAR")
        self.VersionREnylandModVAR.setFont(fontSegoe)
        
        self.VersionLauncherVAR = QLabel(self.SETTINGS_TAB)
        self.VersionLauncherVAR.setGeometry(QRect(630, 50, 91, 16))
        self.VersionLauncherVAR.setAlignment(Qt.AlignCenter)
        self.VersionLauncherVAR.setObjectName("VersionLauncherVAR")
        self.VersionLauncherVAR.setFont(fontSegoe)
        
        self.GameLocationEdit = QLineEdit(self.SETTINGS_TAB)
        self.GameLocationEdit.setGeometry(QRect(110, 250, 701, 20))
        self.GameLocationEdit.setObjectName("GameLocationEdit")
        self.GameLocationEdit.setReadOnly(1)
        self.GameLocationEdit.setFont(fontSegoe)
        
        self.GameLocation = QLabel(self.SETTINGS_TAB)
        self.GameLocation.setGeometry(QRect(20, 250, 81, 21))
        self.GameLocation.setObjectName("GameLocation")
        self.GameLocation.setFont(fontSegoe)
        
        self.toolButton_2 = QToolButton(self.SETTINGS_TAB)
        self.toolButton_2.setGeometry(QRect(830, 250, 31, 21))
        self.toolButton_2.setObjectName("toolButton_2")
        self.toolButton_2.mouseReleaseEvent = self.RelocateGame
        self.toolButton_2.setFont(fontSegoeBlack)
        
        self.line_22 = QFrame(self.SETTINGS_TAB)
        self.line_22.setGeometry(QRect(110, 220, 771, 20))
        self.line_22.setFrameShape(QFrame.HLine)
        self.line_22.setFrameShadow(QFrame.Sunken)
        self.line_22.setObjectName("line_22")
        self.line_23 = QFrame(self.SETTINGS_TAB)
        self.line_23.setGeometry(QRect(870, 234, 20, 131))
        self.line_23.setFrameShape(QFrame.VLine)
        self.line_23.setFrameShadow(QFrame.Sunken)
        self.line_23.setObjectName("line_23")
        self.line_24 = QFrame(self.SETTINGS_TAB)
        self.line_24.setGeometry(QRect(0, 231, 20, 131))
        self.line_24.setFrameShape(QFrame.VLine)
        self.line_24.setFrameShadow(QFrame.Sunken)
        self.line_24.setObjectName("line_24")
        
        self.TitleProgramSettings = QLabel(self.SETTINGS_TAB)
        self.TitleProgramSettings.setGeometry(QRect(10, 220, 101, 16))
        self.TitleProgramSettings.setFont((fontSegoe))
        self.TitleProgramSettings.setAlignment(Qt.AlignCenter)
        self.TitleProgramSettings.setObjectName("TitleProgramSettings")
        
        self.line_25 = QFrame(self.SETTINGS_TAB)
        self.line_25.setGeometry(QRect(20, 280, 841, 20))
        self.line_25.setFrameShape(QFrame.HLine)
        self.line_25.setFrameShadow(QFrame.Sunken)
        self.line_25.setObjectName("line_25")
        
        self.btn_ClearAllMods = QPushButton(self.SETTINGS_TAB)
        self.btn_ClearAllMods.setGeometry(QRect(330, 310, 231, 41))
        self.btn_ClearAllMods.setObjectName("btn_ClearAllMods")
        self.btn_ClearAllMods.mouseReleaseEvent = self.ClearAllMods
        self.btn_ClearAllMods.setFont(fontSegoe)
        
        self.pushButton_10 = QPushButton(self.SETTINGS_TAB)
        self.pushButton_10.setGeometry(QRect(60, 310, 231, 41))
        self.pushButton_10.setObjectName("pushButton_10")
        self.pushButton_10.mouseReleaseEvent = self.ClearREnylandData
        self.pushButton_10.setFont(fontSegoe)
        
        self.line_51 = QFrame(self.SETTINGS_TAB)
        self.line_51.setGeometry(QRect(10, 360, 871, 20))
        self.line_51.setFrameShape(QFrame.HLine)
        self.line_51.setFrameShadow(QFrame.Sunken)
        self.line_51.setObjectName("line_51")
        self.line_52 = QFrame(self.SETTINGS_TAB)
        self.line_52.setGeometry(QRect(720, 50, 20, 141))
        self.line_52.setFrameShape(QFrame.VLine)
        self.line_52.setFrameShadow(QFrame.Sunken)
        self.line_52.setObjectName("line_52")
        
        self.InternetConnexion = QLabel(self.SETTINGS_TAB)
        self.InternetConnexion.setGeometry(QRect(740, 50, 131, 61))
        self.InternetConnexion.setAlignment(Qt.AlignCenter)
        self.InternetConnexion.setObjectName("InternetConnexion")
        self.InternetConnexion.setFont(fontSegoe)
        
        self.line_53 = QFrame(self.SETTINGS_TAB)
        self.line_53.setGeometry(QRect(740, 110, 131, 20))
        self.line_53.setFrameShape(QFrame.HLine)
        self.line_53.setFrameShadow(QFrame.Sunken)
        self.line_53.setObjectName("line_53")
        
        self.RenylandConnexion = QLabel(self.SETTINGS_TAB)
        self.RenylandConnexion.setGeometry(QRect(740, 130, 131, 61))
        self.RenylandConnexion.setAlignment(Qt.AlignCenter)
        self.RenylandConnexion.setObjectName("RenylandConnexion")
        self.RenylandConnexion.setFont(fontSegoe)
        
        self.GPLNotice = QLabel(self.SETTINGS_TAB)
        self.GPLNotice.setGeometry(QRect(10, 375, 701, 21))
        self.GPLNotice.setObjectName("GPLNotice")
        self.GPLNotice.setFont(fontSegoe)
        
        self.InfoLogo = QLabel(self.SETTINGS_TAB)
        self.InfoLogo.setGeometry(QRect(860, 373, 21, 21))
        self.InfoLogo.setStyleSheet("image: url(:/Asset/32175-100px.png);")
        self.InfoLogo.setText("")
        self.InfoLogo.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.InfoLogo.setObjectName("InfoLogo")
        self.InfoLogo.mouseReleaseEvent = self.Info
        
        self.ClickGPL = QLabel(self.SETTINGS_TAB)
        self.ClickGPL.setGeometry(QRect(735, 373, 121, 21))
        self.ClickGPL.setObjectName("ClickGPL")
        self.ClickGPL.setFont(fontSegoe)
        
        self.BG_StatusSend.raise_()
        self.pushButton_3.raise_()
        self.VersionLauncher.raise_()
        self.VersionPUNMod.raise_()
        self.VersionREnylandMod.raise_()
        self.line_14.raise_()
        self.TitleArtWork.raise_()
        self.line_12.raise_()
        self.line_13.raise_()
        self.line_11.raise_()
        self.toolButton.raise_()
        self.ArtWorkText.raise_()
        self.IMGPathEdit.raise_()
        self.btn_sendDiscord.raise_()
        self.StatusSendIMG.raise_()
        self.YourPicture.raise_()
        self.UsernameEdit.raise_()
        self.YourUsername.raise_()
        self.TitleProgramInfo.raise_()
        self.line_15.raise_()
        self.line_16.raise_()
        self.line_17.raise_()
        self.line_18.raise_()
        self.line_19.raise_()
        self.line_20.raise_()
        self.line_21.raise_()
        self.BepInExVersion.raise_()
        self.BepInExVersionVAR.raise_()
        self.VersionPUNModVAR.raise_()
        self.VersionREnylandModVAR.raise_()
        self.VersionLauncherVAR.raise_()
        self.GameLocationEdit.raise_()
        self.GameLocation.raise_()
        self.toolButton_2.raise_()
        self.line_22.raise_()
        self.line_23.raise_()
        self.line_24.raise_()
        self.TitleProgramSettings.raise_()
        self.line_25.raise_()
        self.btn_ClearAllMods.raise_()
        self.pushButton_10.raise_()
        self.line_51.raise_()
        self.line_52.raise_()
        self.InternetConnexion.raise_()
        self.line_53.raise_()
        self.RenylandConnexion.raise_()
        self.GPLNotice.raise_()
        self.InfoLogo.raise_()
        self.ClickGPL.raise_()
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/Asset/param.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.tabWidget.addTab(self.SETTINGS_TAB, icon2, "")
        
        self.FULLBG = QLabel(self.centralwidget)
        self.FULLBG.setGeometry(QRect(0, -5, 1001, 611))
        self.FULLBG.setStyleSheet("background-image: url(:/Asset/reanyland_bg.png);")
        self.FULLBG.setText("")
        self.FULLBG.setObjectName("FULLBG")
        self.FULLBG.mousePressEvent = self.mousePressEvent
        self.FULLBG.mouseMoveEvent = self.mouseMoveEvent
        self.FULLBG.mouseReleaseEvent = self.mouseReleaseEvent
        
        self.CROSS = QLabel(self.centralwidget)
        self.CROSS.setGeometry(QRect(948, 6, 47, 41))
        self.CROSS.setStyleSheet("image: url(:/Asset/croixx.png);")
        self.CROSS.setText("")
        self.CROSS.setObjectName("CROSS")
        self.CROSS.mouseReleaseEvent = self.exit_clicked
        
        self.LOGO = QLabel(self.centralwidget)
        self.LOGO.setGeometry(QRect(10, 10, 981, 81))
        self.LOGO.setStyleSheet("image: url(:/Asset/REAnyland.png);")
        self.LOGO.setText("")
        self.LOGO.setObjectName("LOGO")
        self.LOGO.mousePressEvent = self.mousePressEvent
        self.LOGO.mouseMoveEvent = self.mouseMoveEvent
        self.LOGO.mouseReleaseEvent = self.mouseReleaseEvent
        
        self.FULLBG.raise_()
        self.tabWidget.raise_()
        self.LOGO.raise_()
        self.CROSS.raise_()
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QMetaObject.connectSlotsByName(MainWindow)
        
        # self.tabWidget.currentChanged.connect(self.on_tab_change)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle("MainWindow")
        self.progressBar.setValue(0)
        self.PLAYOFFLINE.setText("PLAY OFFLINE")
        self.PLAYONLINE.setText("PLAY ONLINE")
        self.OnlinePayer.setText("ONLINE PLAYER : XX")
        self.PUNServerChoice.setItemText(0, "REnyland - Main MP Server")
        self.PUNServerChoice.setItemText(1, "REnyland - MP SERVER #2")
        self.PUNServerChoice.setItemText(2, "REnyland - MP SERVER #3")
        self.Status.setText("SERVER STATUS : Loading the application . . .")
        self.TotalNewPlayers.setText("Total New Players : XXX")
        self.TotalArea.setText("Total Areas : X XXX")
        self.TotalThings.setText("Total Things : XXX XXX")
        self.ServerInfos.setText("Server Infos :")
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.HOME_TAB), "MAIN")
        self.rdo_Steam.setText("Steam Version :")
        self.rdo_Crack.setText("Github / NonSteam Version :")
        self.rdo_SteamInstall.setText("Install BepInEx (Needed)")
        self.chk_SteamModRedirect.setText("Redirection to REnyland (Mod)")
        self.rdo_SteamNoInstall.setText("Do not install BepInEx")
        self.rdo_CrackInstall.setText("Install BepInEx (Needed)")
        self.chk_CrackAddCrack.setText("Add Steam Bypass")
        self.rdo_CrackNoInstall.setText("Do not install BepInEx")
        self.chk_CrackModRedirect.setText("Redirection to REnyland (Mod)")
        self.btn_Apply.setText("APPLY && PATCH")
        self.questiongame.setText("Which version of the game do you have :")
        self.PatchResult.setHtml("<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" color:#000000;\"><br /><br /><br />Waiting for &quot;Apply &amp; Patch&quot; ...</span></p></body></html>")
        self.AutoDetect.setText("( Auto-Detected : STEAM )")
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.PATCH_TAB), "PATCH")
        self.pushButton_3.setText("Uninstall All (BepInEx && Mods)")
        self.VersionLauncher.setText("Launcher Version :")
        self.VersionPUNMod.setText("PUN Mod Version :")
        self.VersionREnylandMod.setText("REnyland Mod Version :")
        self.TitleArtWork.setText("Upload ur Artwork :")
        self.toolButton.setText("...")
        self.ArtWorkText.setText("Upload your screenshots so that they appear in the main menu of \nREnyland_Launcher (After verification)")
        self.btn_sendDiscord.setText("Send")
        self.StatusSendIMG.setText("Waiting to be sent...")
        self.YourPicture.setText("Your picture :")
        self.YourUsername.setText("Your username :")
        self.TitleProgramInfo.setText("Program Info :")
        self.BepInExVersion.setText("BepInEx Version :")
        self.BepInExVersionVAR.setText("VERSION")
        self.VersionPUNModVAR.setText("VERSION")
        self.VersionREnylandModVAR.setText("VERSION")
        self.VersionLauncherVAR.setText(f"{version}")
        self.GameLocation.setText("Game Location :")
        self.toolButton_2.setText("...")
        self.TitleProgramSettings.setText("Program Settings :")
        self.btn_ClearAllMods.setText("CLEAR All REnyland MODs")
        self.pushButton_10.setText("CLEAR REnyland-Launcher Config\n(And close app)")
        self.InternetConnexion.setText("Internet Connexion : \n\nnOFFLINE")
        self.RenylandConnexion.setText("REnyland Server : \n\nOFFLINE")
        self.GPLNotice.setText("This software is developed by KSH-Soft (aka Axsys) and distributed under the GNU General Public License v3 (GPLv3).")
        self.ClickGPL.setText("Click here for more info :")
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.SETTINGS_TAB), "SETTINGS && OTHERS")
        self.ArtworkDesc.setText("   Artwork by : {Username}")
    
    def exit_clicked(self, event):
        sys.exit(0)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - MainWindow.pos()
            event.accept()

    def mouseMoveEvent(self, event):
        if hasattr(self, 'drag_position') and event.buttons() == Qt.LeftButton:
            MainWindow.move(event.globalPos() - self.drag_position)
            event.accept()
    def mouseReleaseEvent(self, event):
        if hasattr(self, 'drag_position'):
            del self.drag_position
    
    def open_file_chooser(self):
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setNameFilter("Executables (Anyland.exe)")
        file_dialog.setViewMode(QFileDialog.List)

        if file_dialog.exec_():
            file_path = file_dialog.selectedFiles()[0]
            return file_path
        else:
            return None
            
    def CheckFirstLaunch(self):
        if not os.path.exists(KSHDIR):
            try:
                os.mkdir(KSHDIR)
            except:
                pass
        if not os.path.exists(KSHRPDIR):
            try:
                os.mkdir(KSHRPDIR)
            except:
                pass
        if not os.path.exists(KSHRPTMPDIR):
            try:
                os.mkdir(KSHRPTMPDIR)
            except:
                pass
        if not os.path.exists(KSHRLFile):
            box = QMessageBox()
            box.setIcon(QMessageBox.Information)
            app_icon = QtGui.QIcon()
            app_icon.addFile(':/Asset/logo.ico', QSize(48, 48))
            box.setWindowIcon(app_icon)
            box.setWindowTitle('REnyland First Launch !')
            box.setFont(QtGui.QFont('Segoe UI', 8))
            box.setText(f"\nThank you for using REnyland_Launcher\n\n(This Application is in version {version}, there are risks of crash.\nFor each interaction on the application, make sure you get a confirmation message)\n\nThis is the first launch of REnyland_Launcher,\nAfter clicking 'OK' please select the 'Anyland.exe' executable.\n")
            box.setStandardButtons(QMessageBox.Ok)
            box.exec_()
            GAMEEXE = self.open_file_chooser()
            # print('Game EXE : '+ GAMEEXE)
            if GAMEEXE == None:
                self.show_critical("A valid ‘Anyland.exe’ path is required to use the Launcher")
                sys.exit(0)
                
            self.save_to_ini(KSHRLFile, 'Config', 'exeloc', GAMEEXE)
            self.save_to_ini(KSHRLFile, 'Config', 'patched', "NotPatched")
            self.save_to_ini(KSHRLFile, 'Config', 'BepInExVersion', "NotInstalled")
            self.save_to_ini(KSHRLFile, 'Config', 'VersionPUNMod', "NotInstalled")
            self.save_to_ini(KSHRLFile, 'Config', 'VersionREnylandMod', "NotInstalled")
            self.save_to_ini(KSHRLFile, 'Config', 'PUNLobby', "1")
        GameLoc = self.read_value_from_ini('Config', 'exeloc', KSHRLFile)
        self.GameLocationEdit.setText(GameLoc)
        DetectVersion = ''
        try:
            DetectVersion = self.detect_version(GameLoc)
        except:
            self.show_critical("CONFIG file corrupted\nPlease restart REnyland_Launcher")
            os.remove(KSHRLFile)
            sys.exit(0)
        if DetectVersion == "Steam":
            self.rdo_Steam.setChecked(True)
            self.rdo_Crack.setChecked(False)
            self.groupBoxCrack.setDisabled(1)
            self.AutoDetect.setText("( Auto-Detected : STEAM )")
        else:
            self.rdo_Crack.setChecked(True)
            self.rdo_Steam.setChecked(False)
            self.groupBoxSteam.setDisabled(1)
            self.AutoDetect.setText("( Auto-Detected : NonSteam )")
        PUNLobby = self.read_value_from_ini('Config', 'PUNLobby', KSHRLFile)
        PUNLobby = int(PUNLobby)
        self.PUNServerChoice.setCurrentIndex(PUNLobby - 1)
        
        # self.exec_thread = QtCore.QThread()
        # self.exec_thread.run = self.RunCheckAll
        # self.exec_thread.start()
        
        self.exec_thread2 = QThread()
        self.exec_thread2.run = self.reload_info 
        self.exec_thread2.start()
        
        self.RunCheckAll()
        
        # self.reload_info() 
        
        # self.exec_threadr = QtCore.QThread()
        # self.exec_threadr.run = self.ApiRequest 
        # self.exec_threadr.start()
        
        self.ApiRequest()
        
        self.start_Slide()


    def save_to_ini(self, ini_file, section, option, value):
        config = ConfigParser()
        try:
            config.read(ini_file)
            if not config.has_section(section):
                config.add_section(section)
            config.set(section, option, value)
            with open(ini_file, 'w') as configfile:
                config.write(configfile)
        except Exception as e:
            box = QMessageBox()
            box.setIcon(QMessageBox.Critical)
            app_icon = QtGui.QIcon()
            app_icon.addFile(':/Asset/logo.ico', QSize(48, 48))
            box.setWindowIcon(app_icon)
            box.setWindowTitle('REnyland BUG !')
            box.setFont(QtGui.QFont('Segoe UI', 8))
            box.setText(f"{e}")
            box.setStandardButtons(QMessageBox.Ok)
            box.exec_()
        
    def read_value_from_ini(self, section, key, filename):
        config = ConfigParser()
        config.read(filename)
        if config.has_section(section) and config.has_option(section, key):
            value = config.get(section, key)
            return value
        else:
            return None
        
    def ClearREnylandData(self,event):
        if os.path.exists(KSHRPDIR):
            rmtree(KSHRPDIR)
        self.pushButton_10.setText('DATA CLEARED !!\nAPP CLOSE !!')
        sys.exit(0)
        
    def RelocateGame(self,event):
        GAMEEXE = self.open_file_chooser()
        if GAMEEXE == None:
            return
        self.save_to_ini(KSHRLFile, 'Config', 'exeloc', GAMEEXE)
        GameLoc = self.read_value_from_ini('Config', 'exeloc', KSHRLFile)
        self.GameLocationEdit.setText(GameLoc)
        DetectVersion = self.detect_version(GameLoc)
        if DetectVersion == "Steam":
            self.rdo_Steam.setChecked(True)
            self.rdo_Crack.setChecked(False)
            self.groupBoxCrack.setDisabled(1)
            self.AutoDetect.setText("( Auto-Detected : STEAM )")
        else:
            self.rdo_Crack.setChecked(True)
            self.rdo_Steam.setChecked(False)
            self.groupBoxSteam.setDisabled(1)
            self.AutoDetect.setText("( Auto-Detected : NonSteam )")

    def detect_version(self, path: str) -> str:
        if "steamapps/common/Anyland" in path:
            return "Steam"
        else:
            return "GitHub"
    
    def SteamToggled(self, state):
        if state == False: #(Qt.Checked)
            self.groupBoxSteam.setDisabled(1)
            self.groupBoxCrack.setDisabled(0)
        else:  # (Qt.Unchecked)
            self.groupBoxSteam.setDisabled(0)
            self.groupBoxCrack.setDisabled(1)
    
    def show_info(self, message):
        box = QMessageBox()
        app_icon = QtGui.QIcon()
        app_icon.addFile(':/Asset/logo.ico', QSize(48, 48))
        box.setWindowIcon(app_icon)
        box.setIcon(QMessageBox.Information)
        box.setWindowTitle('REnyland Info !')
        box.setFont(QtGui.QFont('Arial', 8))
        box.setText(message)
        box.setStandardButtons(QMessageBox.Ok)
        box.exec_()
    
    def show_critical(self, message):
        box = QMessageBox()
        app_icon = QtGui.QIcon()
        app_icon.addFile(':/Asset/logo.ico', QSize(48, 48))
        box.setWindowIcon(app_icon)
        box.setIcon(QMessageBox.Critical)
        box.setWindowTitle('REnyland Critical !')
        box.setFont(QtGui.QFont('Arial', 8))
        box.setText(message)
        box.setStandardButtons(QMessageBox.Ok)
        box.exec_()
        
    def BrowseIMGArtwork(self,event):
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setNameFilter("Images (*.jpg *.jpeg *.png *.gif *.bmp)")
        file_dialog.setViewMode(QFileDialog.List)

        if file_dialog.exec_():
            file_path = file_dialog.selectedFiles()[0]
            self.IMGPathEdit.setText(file_path)
    
    def SendToDiscord(self,event):
        imgPath = self.IMGPathEdit.text()
        file_name = os.path.basename(imgPath)
        if not imgPath:
            self.show_critical("Please select an image")
            return
        Username = self.UsernameEdit.text()
        if not Username:
            self.show_critical("Please enter your username")
            return
        
        webhook = DiscordWebhook(url=webhook_url)
        embed = DiscordEmbed()
        embed.set_title('Nouvelle image !')
        embed.set_description(f'Par : {Username}')
        with open(imgPath, 'rb') as f:
            file_data = f.read() 
        webhook.add_file(file_data, file_name)
        webhook.add_embed(embed)
        response = webhook.execute()
        if response.status_code == 200:
            self.StatusSendIMG.setText("Image  successfully !")
            self.IMGPathEdit.clear()
            self.UsernameEdit.clear()
            self.BG_StatusSend.setStyleSheet("\n"
    "background-color: rgb(0, 125, 0);")
        else:
            self.StatusSendIMG.setText(f"Error sending : {response.status_code}")
            self.BG_StatusSend.setStyleSheet("\n"
    "background-color: rgb(125, 0, 0);")
            
    def ClearAllMods(self, event):
        GameLoc = self.read_value_from_ini('Config', 'exeloc', KSHRLFile)
        directory = os.path.dirname(GameLoc)
        folder_bepinexPlugin = os.path.join(directory, "BepInEx", "plugins")
        DNS_bepinexPlugin = os.path.join(folder_bepinexPlugin, "Renyland_DNS.dll")
        PUN_bepinexPlugin = os.path.join(folder_bepinexPlugin, "Renyland_PUN.dll")
        if os.path.exists(DNS_bepinexPlugin):
            os.remove(DNS_bepinexPlugin)
        if os.path.exists(PUN_bepinexPlugin):
            os.remove(PUN_bepinexPlugin)
        self.save_to_ini(KSHRLFile, 'Config', 'versionpunmod', "NotInstalled")
        self.VersionPUNModVAR.setText("NotInstalled")
        self.save_to_ini(KSHRLFile, 'Config', 'versionrenylandmod', "NotInstalled")
        self.VersionREnylandModVAR.setText("NotInstalled")
        self.save_to_ini(KSHRLFile, 'Config', 'patched', "NotPatched")
        self.show_info("All REnyland mods have been deleted")
            
            
    def ClearAllBepInEx(self, event):
        GameLoc = self.read_value_from_ini('Config', 'exeloc', KSHRLFile)
        directory = os.path.dirname(GameLoc)
        folder_bepinex = os.path.join(directory, "BepInEx")
        doorstop_version_File = os.path.join(directory, ".doorstop_version")
        doorstop_config_File = os.path.join(directory, "doorstop_config.ini")
        winhttp_File = os.path.join(directory, "winhttp.dll")
        changelog_File = os.path.join(directory, "changelog.txt")
        if os.path.exists(folder_bepinex):
            rmtree(folder_bepinex)
        if os.path.exists(doorstop_version_File):
            os.remove(doorstop_version_File)
        if os.path.exists(doorstop_config_File):
            os.remove(doorstop_config_File)
        if os.path.exists(winhttp_File):
            os.remove(winhttp_File)
        if os.path.exists(changelog_File):
            os.remove(changelog_File)
        self.save_to_ini(KSHRLFile, 'Config', 'bepinexversion', "NotInstalled")
        self.BepInExVersionVAR.setText("NotInstalled")
        self.save_to_ini(KSHRLFile, 'Config', 'versionpunmod', "NotInstalled")
        self.VersionPUNModVAR.setText("NotInstalled")
        self.save_to_ini(KSHRLFile, 'Config', 'versionrenylandmod', "NotInstalled")
        self.VersionREnylandModVAR.setText("NotInstalled")
        self.save_to_ini(KSHRLFile, 'Config', 'patched', "NotPatched")
        self.show_info("All REnyland mods And BepInEx have been deleted")
        

    def Info(self,event):  
        dialog = QDialog(self.MainWindow, Qt.WindowCloseButtonHint | Qt.WindowTitleHint)
        dialog.setWindowTitle("Some Information")
        # app_icon = QtGui.QIcon()
        # app_icon.addFile(':/Asset/logo.ico', QSize(48, 48))
        app_icon = QtGui.QIcon()
        app_icon.addFile(':/Asset/logo.ico', QSize(48, 48))
        dialog.setWindowIcon(app_icon)
        layout = QVBoxLayout(dialog)
        self.LabelInfo = QLabel("Nom de l'application : MonApplication\n"
            f"Version : {version}\n"
            "Développé par : KSH-Soft (aka Axsys)\n\n"
            "Licences :\n"
            "- Ce logiciel est distribué sous licence GNU General Public License v3 (GPLv3).\n"
            "- Il utilise les bibliothèques suivantes :\n"
            "  - PyQt5, sous licence GPLv3.\n"
            "  - BepInEx, sous licence LGPL 2.0.\n\n"
            "Conformément à ces licences, le code source de cette application est disponible ici :\n"
            "https://github.com/KSH-Soft/REnyland_Launcher\n\n"
            "Pour plus d'informations sur la GPLv3 :\n"
            "https://www.gnu.org/licenses/gpl-3.0.fr.html\n\n", dialog)
        self.LabelInfo.setFont(QtGui.QFont('Arial', 8))        
        layout.addWidget(self.LabelInfo)
                
        text_icon_layout = QHBoxLayout()
        self.info_label = QLabel("Admin-DEV : Axsys (aka KSH-SOFT)\nLicence : Distribué sous licence GNU General Public License v3 (GPLv3).", dialog)
        self.info_label.setFont(QtGui.QFont('Arial', 8))
        self.info_label.setAlignment(Qt.AlignCenter)
        text_icon_layout.addWidget(self.info_label)

        text_icon_layout.setAlignment(Qt.AlignCenter)
        layout.addLayout(text_icon_layout)
    
        dialog.setLayout(layout)
        dialog.exec_()
        
        
    def launch_tests_thread(self,event):
        self.Reload.setDisabled(1)
        
        self.rotation_thread = QThread()
        self.rotation_thread.run = self.animate_rotation
        self.rotation_thread.start()
        
        self.ApiRequest()
        self.RunCheckAll()
        
        # self.exec_threado = QtCore.QThread()
        # self.exec_threado.run = self.RunCheckAll
        # self.exec_threado.start()
        
    
        
    
    def reload_info_bis(self):
        image_url = ""
        self.display_image_from_url_Patch(image_url)
        
        image_url = ""
        self.display_image_from_url_Head(image_url)

    def reload_info(self):
        image_url = ""
        self.display_image_from_url_Patch(image_url)
        
        image_url = ""
        self.display_image_from_url_Head(image_url)
        
        def download_file(url, local_filename):
            try:
                response = requests.get(url)
                response.raise_for_status()

                with open(local_filename, 'wb') as f:
                    f.write(response.content)
                # print(f"Fichier téléchargé avec succès: {local_filename}")
            except requests.exceptions.RequestException as e:
                print(f"Erreur lors du téléchargement: {e}")
        
        def read_file_and_store_variables(file_path):
            data = []
            try:
                with open(file_path, 'r') as f:
                    lines = f.readlines()
                    for line in lines:
                        line = line.strip()
                        if line and '"' in line:
                            try:
                                url, name = line.split('","')
                                url = url.replace('"', '')
                                name = name.replace('"', '') 
                                data.append({"url": url, "name": name})
                            except ValueError:
                                print(f"Format de ligne incorrect: {line}")
                return data
            except FileNotFoundError:
                print(f"Le fichier {file_path} n'a pas été trouvé.")
            except Exception as e:
                print(f"Erreur lors de la lecture du fichier: {e}")
            return data
        
        # def read_random_line(data):
        #     if data:
        #         random_item = random.choice(data)
        #         image_url = random_item['url']
        #         self.display_image_from_url_Main(image_url)
        #         self.ArtworkDesc.setText(f"   Artwork by : {random_item['name']}")
        #         # print(f"Ligne aléatoire: URL = {random_item['url']}, NAME = {random_item['name']}")
        #     else:
        #         print("Aucune donnée disponible.")

        # url = ""
        # local_filename = "ArtworkList"
        # local_filename = os.path.join(appdata_path, 'KSH-Soft', 'RenylandLauncher', local_filename)
        # download_file(url, local_filename)
        # data = read_file_and_store_variables(local_filename)

        urll = ""
        local_filenamee = "VERSIONS.ini"
        local_filenamee = os.path.join(appdata_path, 'KSH-Soft', 'RenylandLauncher', local_filenamee)
        download_file(urll, local_filenamee)

        # urllll = ""
        # local_filenameeee = "LASTV"
        # local_filenameeee = os.path.join(appdata_path, 'KSH-Soft', 'RenylandLauncher', local_filenameeee)
        # download_file(urllll, local_filenameeee)
        
        
        self.Reload.setDisabled(0)
        # read_random_line(data)
        
        # while True:
        #     time.sleep(20)
        #     try:
        #         read_random_line(data)
        #     except:
        #         pass
            
    
    def animate_rotation(self):
        self.reload_info_bis()        
        for angle in range(0, 181, 20):
            self.reload_rotate(angle)
            QThread.msleep(25)
        self.Reload.setDisabled(0)
        
    def reload_rotate(self, angle):
        pixmap = QtGui.QPixmap(":/Asset/reload.png")
        transform = QtGui.QTransform().rotate(angle)
        pixmap = pixmap.transformed(transform, Qt.SmoothTransformation)
        self.Reload.setPixmap(pixmap)
    
    def handle_update(self, message):
        self.STATUS.setText(message)
        
    def RunCheckAll(self):
        self.Status.setText("STATUS : check in progress . . .")
        self.LedStatus.setStyleSheet("image: url(:/Asset/led-r.png);")
        def has_internet(host="8.8.8.8", port=53, timeout=3):
            try:
                socket.setdefaulttimeout(timeout)
                socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
                return True
            except socket.error:
                return False
 
        if has_internet():
            self.InternetConnexion.setText("Internet Connexion : \n\nONLINE")
        else:
            self.InternetConnexion.setText("Internet Connexion : \n\nOFFLINE")
            
        def is_port_open(ip, port, timeout=3):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.settimeout(timeout)
                    sock.connect((ip, port))
                return True
            except (socket.timeout, socket.error):
                return False
        
        if is_port_open(serverIP, 8003):
            self.RenylandConnexion.setText("REnyland Server : \n\nONLINE")
        else:
            self.RenylandConnexion.setText("REnyland Server : \n\nOFFLINE")
            
        BepInExVersion_VAR = self.read_value_from_ini('Config', 'BepInExVersion', KSHRLFile)    
        self.BepInExVersionVAR.setText(f"{BepInExVersion_VAR}")
        VersionPUNMod_VAR = self.read_value_from_ini('Config', 'VersionPUNMod', KSHRLFile) 
        self.VersionPUNModVAR.setText(f"{VersionPUNMod_VAR}")
        VersionREnylandMod_VAR = self.read_value_from_ini('Config', 'VersionREnylandMod', KSHRLFile) 
        self.VersionREnylandModVAR.setText(f"{VersionREnylandMod_VAR}")
        
        internet_status = self.InternetConnexion.text()
        renyland_status = self.RenylandConnexion.text()
        
        VAR = self.read_value_from_ini('Config', 'patched', KSHRLFile) 
        
        def download_file(url, local_filename):
            try:
                response = requests.get(url)
                response.raise_for_status()

                with open(local_filename, 'wb') as f:
                    f.write(response.content)
                # print(f"Fichier téléchargé avec succès: {local_filename}")
            except requests.exceptions.RequestException as e:
                # print(f"Erreur lors du téléchargement: {e}")
                pass
        
        urllll = ""
        local_filenameeee = "LASTV"
        local_filenameeee = os.path.join(appdata_path, 'KSH-Soft', 'RenylandLauncher', local_filenameeee)
        download_file(urllll, local_filenameeee)
        
        LASTV = os.path.join(appdata_path, 'KSH-Soft', 'RenylandLauncher', "LASTV")
        with open(LASTV, 'r') as file:
            first_line = file.readline().strip() 
        # print(first_line)
        if first_line == version:
            # print('no need update')
            if not VAR == "NotPatched":
                # print('patched')
                if internet_status == "Internet Connexion : \n\nONLINE":
                    # print('INT ONLINE')
                    if renyland_status == "REnyland Server : \n\nONLINE":
                        # print('REN ONLINE')
                        self.Status.setText("STATUS : Everything's OK, you're ready to play . . .")
                        self.LedStatus.setStyleSheet("image: url(:/Asset/led-v.png);")
                    else:
                        self.Status.setText("STATUS : Error with Renyland's Server")
                        self.LedStatus.setStyleSheet("image: url(:/Asset/led-o.png);")
                else:
                    self.Status.setText("STATUS : Error with your internet connexion")
                    self.LedStatus.setStyleSheet("image: url(:/Asset/led-r.png);")
            else:
                self.Status.setText("STATUS : Error with your game (NotPatched), Please patch it before joining server.")
                self.LedStatus.setStyleSheet("image: url(:/Asset/led-o.png);")
        else:
            self.Status.setText("STATUS : An update of REnyland_Launcher is available, please download and use it.")
            self.LedStatus.setStyleSheet("image: url(:/Asset/led-r.png);")
        # self.MainWindow.clearFocus()
    
    def ApplyPatch(self,event):
        self.btn_Apply.setDisabled(1)
        self.groupBoxCrack.setDisabled(1)
        self.groupBoxSteam.setDisabled(1)
        self.Allbox.setDisabled(1)
        
        self.start_patch_thread()
 
    def display_image_from_url_Main(self, url):
        response = requests.get(url)
        if response.status_code == 200:
            image_data = BytesIO(response.content)
            pixmap = QtGui.QPixmap()
            pixmap.loadFromData(image_data.read())
            scaled_pixmap = pixmap.scaled(self.ArtworkIMG.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            self.ArtworkIMG.setPixmap(scaled_pixmap)
        else:
            pass
            # print(f"Erreur de téléchargement de l'image : {response.status_code}")
            
    def display_image_from_url_Patch(self, url):
        response = requests.get(url)
        if response.status_code == 200:
            image_data = BytesIO(response.content)
            pixmap = QtGui.QPixmap()
            pixmap.loadFromData(image_data.read())
            scaled_pixmap = pixmap.scaled(self.IMGPatch.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.IMGPatch.setPixmap(scaled_pixmap)
        else:
            pass
            # print(f"Erreur de téléchargement de l'image : {response.status_code}")
        
    def display_image_from_url_Head(self, url):
        response = requests.get(url)
        if response.status_code == 200:
            image_data = BytesIO(response.content)
            pixmap = QtGui.QPixmap()
            pixmap.loadFromData(image_data.read())
            scaled_pixmap = pixmap.scaled(self.WebsiteView.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.WebsiteView.setPixmap(scaled_pixmap)
        else:
            pass
            # print(f"Erreur de téléchargement de l'image : {response.status_code}")
        # pass
        
    def RUN_OFFLINE(self, event):
        Patched = self.read_value_from_ini('Config', 'patched', KSHRLFile)
        if Patched == "NotPatched":
            self.show_info("You must first patch the game before you can launch it.")
            return
        GameLoc = self.read_value_from_ini('Config', 'exeloc', KSHRLFile)
        directory = os.path.dirname(GameLoc)
        directory_file = os.path.join(directory, "BepInEx", "plugins", "Renyland_PUN.dll")
        if os.path.exists(directory_file):
            os.remove(directory_file)
            self.save_to_ini(KSHRLFile, 'Config', 'versionpunmod', 'NotInstalled')
        os.system(f'start "" "{GameLoc}"')
        
    def RUN_ONLINE(self, event):
        Patched = self.read_value_from_ini('Config', 'patched', KSHRLFile)
        if Patched == "NotPatched":
            self.show_info("You must first patch the game before you can launch it.")
            return
        
        def download_file(url, local_filename):
            try:
                response = requests.get(url)
                response.raise_for_status()
        
                with open(local_filename, 'wb') as f:
                    f.write(response.content)
                # print(f"Fichier téléchargé avec succès: {local_filename}")
            except requests.exceptions.RequestException as e:
                pass
                # print(f"Erreur lors du téléchargement: {e}")
        
        def move_file_with_replace(src, dst):
            try:
                if os.path.exists(dst):
                    os.remove(dst)
                    # print(f"Fichier existant {dst} supprimé.")
                move(src, dst)
                # print(f"Fichier déplacé de {src} vers {dst}.")
            except Exception as e:
                # print(f"Erreur lors du déplacement du fichier : {e}")
                pass
        
        index = self.PUNServerChoice.currentIndex()
        # print(f"Index sélectionné : {index}")
        url = ""
        if index == 0:
            url = ""
        elif index == 1:
            url = ""
        elif index == 2:
            url = ""
        else:
            return
        
        StoredLobby = self.read_value_from_ini('Config', 'PUNLobby', KSHRLFile)
        # print(StoredLobby)
        GUILobby = index + 1
        # print(GUILobby)
        GUILobbyy = str(GUILobby)
        
        StoredVersionPUN = self.read_value_from_ini('Config', 'versionpunmod', KSHRLFile)
        ONLINEVersionPUN = self.read_value_from_ini('Version', 'versionpunmod', KSHRLVERSIONFile)
        
        if not (StoredLobby == GUILobbyy and StoredVersionPUN == ONLINEVersionPUN):
            # print('GO DL NEW DLL')
            local_filenamee = "Renyland_PUN.dll"
            local_filename = os.path.join(appdata_path, 'KSH-Soft', 'RenylandLauncher', local_filenamee)
            download_file(url, local_filename)
            GameLoc = self.read_value_from_ini('Config', 'exeloc', KSHRLFile)
            directory = os.path.dirname(GameLoc)
            directory_file = os.path.join(directory, "BepInEx", "plugins", local_filenamee)
            move_file_with_replace(local_filename, directory_file)
            self.save_to_ini(KSHRLFile, 'Config', 'PUNLobby', GUILobbyy)
            self.save_to_ini(KSHRLFile, 'Config', 'versionpunmod', ONLINEVersionPUN)
            
        os.system(f'start "" "{GameLoc}"')
    
    def OpenWebsite(self, event):
        url = "http://kashi.world.free.fr/REnyland/"
        webbrowser.open(url)
        
    def ApiRequest(self):
        try:
            url = ""
            response = requests.get(url, timeout=1)
            if response.status_code == 200:
                data = response.json()
                
                OnlinePlayer = data["OnlinePlayer"]
                OnlinePlayer = f"{int(OnlinePlayer):,}".replace(",", " ")
                
                NumberAreas = data["NumberAreas"]
                NumberAreas = f"{int(NumberAreas):,}".replace(",", " ")
                
                NumberThings = data["NumberThings"]
                NumberThings = f"{int(NumberThings):,}".replace(",", " ")
                
                NumberNewPlayer = data["NumberNewPlayer"]
                NumberNewPlayer = f"{int(NumberNewPlayer):,}".replace(",", " ")
                
                # print('Online : ',OnlinePlayer)
                # print('NumberAreas : ',NumberAreas)
                # print('NumberThings : ',NumberThings)
                # print('NumberNewPlayer : ',NumberNewPlayer)
                self.TotalNewPlayers.setText(f"Total New Players : {NumberNewPlayer}")
                self.TotalArea.setText(f"Total Areas : {NumberAreas}")
                self.TotalThings.setText(f"Total Things : {NumberThings}")
                self.OnlinePayer.setText(f"ONLINE PLAYER : {OnlinePlayer}")
            else:
                self.TotalNewPlayers.setText("Total New Players : XXX")
                self.TotalArea.setText("Total Areas : X XXX")
                self.TotalThings.setText("Total Things : XXX XXX")
                self.OnlinePayer.setText("ONLINE PLAYER : XX")
        except:
            self.TotalNewPlayers.setText("Total New Players : XXX")
            self.TotalArea.setText("Total Areas : X XXX")
            self.TotalThings.setText("Total Things : XXX XXX")
            self.OnlinePayer.setText("ONLINE PLAYER : XX")
            
    # def on_tab_change(self, index):
    #     if index == 0:
    #         try:
    #             # self.RunCheckAll()
    #             self.exec_thread = QtCore.QThread()
    #             self.exec_thread.run = self.RunCheckAll
    #             self.exec_thread.start()
    #         except:
    #             pass
            
            
        
import ressources

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    app.setAttribute(Qt.AA_EnableHighDpiScaling)
    app.setStyle("Fusion")
    MainWindow = QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    ui.CheckFirstLaunch()
    sys.exit(app.exec_())
