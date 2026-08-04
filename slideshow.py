from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageOps
from pillow_heif import register_heif_opener
from PySide6.QtCore import QRunnable, QThreadPool, QTimer, Qt, Signal, Slot
from PySide6.QtGui import QAction, QImage, QKeySequence, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QLabel,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QToolBar,
)


register_heif_opener()

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".heic", ".heif"}
EXIF_DATE_TAGS = (36867, 36868, 306)  # DateTimeOriginal, DateTimeDigitized, DateTime


def parse_exif_date(value: object) -> datetime | None:
    if isinstance(value, bytes):
        value = value.decode("utf-8", errors="ignore")
    if not isinstance(value, str):
        return None

    value = value.strip().strip("\x00")
    for fmt in ("%Y:%m:%d %H:%M:%S", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(value[:19], fmt)
        except ValueError:
            pass
    return None


def photo_date(path: Path) -> datetime:
    try:
        with Image.open(path) as image:
            exif = image.getexif()
            for tag in EXIF_DATE_TAGS:
                parsed = parse_exif_date(exif.get(tag))
                if parsed is not None:
                    return parsed
    except (OSError, ValueError):
        pass
    return datetime.fromtimestamp(path.stat().st_mtime)


def discover_photos(folder: Path) -> list[Path]:
    photos = (
        path
        for path in folder.rglob("*")
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
    )
    return sorted(photos, key=lambda path: (photo_date(path), str(path).casefold()))


class ScanTask(QRunnable):
    def __init__(self, folder: Path, finished: Signal, failed: Signal) -> None:
        super().__init__()
        self.folder = folder
        self.finished = finished
        self.failed = failed

    @Slot()
    def run(self) -> None:
        try:
            self.finished.emit(discover_photos(self.folder))
        except Exception as error:  # Keep worker failures visible in the UI.
            self.failed.emit(str(error))


class SlideShowWindow(QMainWindow):
    scan_completed = Signal(object)
    scan_errored = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("SlideShower")
        self.resize(1100, 750)
        self.setStyleSheet("QMainWindow { background: black; } QLabel { color: white; }")

        self.image_label = QLabel("Välj en huvudmapp för att börja")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setMinimumSize(1, 1)
        self.setCentralWidget(self.image_label)

        self.photos: list[Path] = []
        self.index = -1
        self.current_pixmap: QPixmap | None = None
        self.interval_ms = 5000
        self.thread_pool = QThreadPool.globalInstance()
        self.scan_task: ScanTask | None = None
        self.scan_completed.connect(self.scan_finished)
        self.scan_errored.connect(self.scan_failed)

        self.timer = QTimer(self)
        self.timer.setInterval(self.interval_ms)
        self.timer.timeout.connect(self.next_photo)

        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.setMaximumWidth(160)
        self.progress.hide()

        self._create_actions()
        self._create_toolbar()
        self.statusBar().showMessage("Redo")
        QTimer.singleShot(0, self.choose_folder)

    def _create_actions(self) -> None:
        self.open_action = QAction("Välj mapp", self)
        self.open_action.setShortcut(QKeySequence.StandardKey.Open)
        self.open_action.triggered.connect(self.choose_folder)

        self.previous_action = QAction("Föregående", self)
        self.previous_action.setShortcut(Qt.Key.Key_Left)
        self.previous_action.triggered.connect(self.previous_photo)

        self.pause_action = QAction("Pausa", self)
        self.pause_action.setShortcut(Qt.Key.Key_Space)
        self.pause_action.triggered.connect(self.toggle_pause)

        self.next_action = QAction("Nästa", self)
        self.next_action.setShortcut(Qt.Key.Key_Right)
        self.next_action.triggered.connect(self.next_photo)

        self.fullscreen_action = QAction("Helskärm", self)
        self.fullscreen_action.setShortcut(Qt.Key.Key_F11)
        self.fullscreen_action.triggered.connect(self.toggle_fullscreen)

        self.quit_fullscreen_action = QAction(self)
        self.quit_fullscreen_action.setShortcut(Qt.Key.Key_Escape)
        self.quit_fullscreen_action.triggered.connect(self.leave_fullscreen)
        self.addAction(self.quit_fullscreen_action)

        self.faster_action = QAction(self)
        self.faster_action.setShortcut(Qt.Key.Key_Plus)
        self.faster_action.triggered.connect(lambda: self.change_speed(-1000))
        self.addAction(self.faster_action)

        self.slower_action = QAction(self)
        self.slower_action.setShortcut(Qt.Key.Key_Minus)
        self.slower_action.triggered.connect(lambda: self.change_speed(1000))
        self.addAction(self.slower_action)

    def _create_toolbar(self) -> None:
        toolbar = QToolBar("Kontroller")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        toolbar.addAction(self.open_action)
        toolbar.addSeparator()
        toolbar.addAction(self.previous_action)
        toolbar.addAction(self.pause_action)
        toolbar.addAction(self.next_action)
        toolbar.addSeparator()
        toolbar.addAction(self.fullscreen_action)
        toolbar.addWidget(self.progress)
        self.toolbar = toolbar

    @Slot()
    def choose_folder(self) -> None:
        folder_name = QFileDialog.getExistingDirectory(self, "Välj huvudmapp med bilder")
        if not folder_name:
            return

        self.timer.stop()
        self.progress.show()
        self.open_action.setEnabled(False)
        self.current_pixmap = None
        self.image_label.clear()
        self.image_label.setText("Läser bilder från huvudmappen och alla undermappar …")
        self.statusBar().showMessage("Läser bilder och fotograferingsdatum …")
        task = ScanTask(Path(folder_name), self.scan_completed, self.scan_errored)
        # Keep the Python QRunnable wrapper alive until Qt has delivered the
        # result. The signal owner is the window and cannot disappear mid-scan.
        self.scan_task = task
        self.thread_pool.start(task)

    @Slot(object)
    def scan_finished(self, photos: object) -> None:
        self.scan_task = None
        self.open_action.setEnabled(True)
        self.progress.hide()
        self.photos = list(photos) if isinstance(photos, list) else []
        self.index = 0 if self.photos else -1
        if not self.photos:
            self.image_label.setText("Inga JPG- eller HEIC-bilder hittades")
            self.statusBar().showMessage("Inga bilder hittades")
            return

        self.show_current_photo()
        self.timer.start()
        self.pause_action.setText("Pausa")
        self.statusBar().showMessage(f"{len(self.photos)} bilder • {self.interval_ms // 1000} s")

    @Slot(str)
    def scan_failed(self, message: str) -> None:
        self.scan_task = None
        self.open_action.setEnabled(True)
        self.progress.hide()
        QMessageBox.critical(self, "Kunde inte läsa mappen", message)
        self.statusBar().showMessage("Ett fel uppstod")

    def show_current_photo(self) -> None:
        if not self.photos or self.index < 0:
            return
        path = self.photos[self.index]
        try:
            with Image.open(path) as image:
                image = ImageOps.exif_transpose(image).convert("RGB")
                data = image.tobytes("raw", "RGB")
                qimage = QImage(
                    data,
                    image.width,
                    image.height,
                    image.width * 3,
                    QImage.Format.Format_RGB888,
                ).copy()
            self.current_pixmap = QPixmap.fromImage(qimage)
            self._fit_image()
            self.statusBar().showMessage(
                f"{self.index + 1} / {len(self.photos)} • {path.name} • {self.interval_ms // 1000} s"
            )
        except (OSError, ValueError) as error:
            self.current_pixmap = None
            self.image_label.setText(f"Kunde inte visa:\n{path}\n\n{error}")

    def _fit_image(self) -> None:
        if self.current_pixmap is None:
            return
        scaled = self.current_pixmap.scaled(
            self.image_label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.image_label.setPixmap(scaled)

    def resizeEvent(self, event) -> None:  # noqa: N802 (Qt method name)
        super().resizeEvent(event)
        self._fit_image()

    @Slot()
    def next_photo(self) -> None:
        if self.photos:
            self.index = (self.index + 1) % len(self.photos)
            self.show_current_photo()

    @Slot()
    def previous_photo(self) -> None:
        if self.photos:
            self.index = (self.index - 1) % len(self.photos)
            self.show_current_photo()

    @Slot()
    def toggle_pause(self) -> None:
        if not self.photos:
            return
        if self.timer.isActive():
            self.timer.stop()
            self.pause_action.setText("Fortsätt")
        else:
            self.timer.start()
            self.pause_action.setText("Pausa")

    @Slot()
    def toggle_fullscreen(self) -> None:
        if self.isFullScreen():
            self.leave_fullscreen()
        else:
            self.toolbar.hide()
            self.statusBar().hide()
            self.showFullScreen()

    @Slot()
    def leave_fullscreen(self) -> None:
        if self.isFullScreen():
            self.showNormal()
            self.toolbar.show()
            self.statusBar().show()

    def change_speed(self, delta_ms: int) -> None:
        self.interval_ms = min(60_000, max(1_000, self.interval_ms + delta_ms))
        self.timer.setInterval(self.interval_ms)
        self.statusBar().showMessage(f"Bildtid: {self.interval_ms // 1000} sekunder")


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("SlideShower")
    window = SlideShowWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
