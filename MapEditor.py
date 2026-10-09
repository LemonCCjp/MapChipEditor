import sys
import os

from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QColor, QPainter, QPixmap, QIcon

from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QFrame,
    QListWidget,
    QListWidgetItem,
    QSpinBox,
    QMessageBox,
    QDialog,
    QDialogButtonBox
)

from BlockManager import BlockManager


class BlockIDDialog(QDialog):
    def __init__(self, block_name, image_path, parent=None):
        super().__init__(parent)

        self.setWindowTitle("ブロックID設定")
        self.setFixedSize(250, 230)

        layout = QVBoxLayout(self)

        # 画像
        image_label = QLabel()
        image_label.setFixedSize(64, 64)
        image_label.setAlignment(Qt.AlignCenter)

        pixmap = QPixmap(image_path)

        if not pixmap.isNull():
            image_label.setPixmap(
                pixmap.scaled(
                    64,
                    64,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
            )

        layout.addWidget(image_label, alignment=Qt.AlignCenter)

        # ブロック名
        name_label = QLabel(f"ブロック名: {block_name}")
        layout.addWidget(name_label)

        # ID入力
        id_layout = QHBoxLayout()

        id_layout.addWidget(QLabel("ID:"))

        self.id_edit = QLineEdit()
        self.id_edit.setMaxLength(1)
        self.id_edit.setFixedWidth(50)

        id_layout.addWidget(self.id_edit)
        id_layout.addStretch()

        layout.addLayout(id_layout)

        # ボタン
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok |
            QDialogButtonBox.Cancel
        )

        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        layout.addWidget(button_box)

    def get_id(self):
        return self.id_edit.text()




# ============================================================
# グリッド表示部分
# ============================================================

class MapCanvas(QWidget):
    def __init__(
        self,
        block_manager,
        width_count=50,
        height_count=30,
        cell_size=32
    ):
        super().__init__()

        self.block_manager = block_manager

        self.width_count = width_count
        self.height_count = height_count
        self.cell_size = cell_size

        # 現在選択されているブロックID
        self.selected_block_id = None

        # マップデータ
        self.map_data = []

        self.update_size()

    def update_size(self):
        self.setFixedSize(
            self.width_count * self.cell_size,
            self.height_count * self.cell_size
        )

    def paintEvent(self, event):
        painter = QPainter(self)

        # 背景
        painter.fillRect(self.rect(), QColor(240, 240, 240))

        # マップチップ画像
        for y in range(self.height_count):
            for x in range(self.width_count):

                # マップデータが存在しない場合
                if y >= len(self.map_data):
                    continue

                if x >= len(self.map_data[y]):
                    continue

                block_id = self.map_data[y][x]

                # 0は空白
                if block_id == "0" or block_id == 0:
                    continue

                # IDからブロックを探す
                block = self.block_manager.get_block_by_id(block_id)

                if block is None:
                    continue

                image_path = os.path.join(
                    self.block_manager.block_folder,
                    block["file_name"]
                )

                pixmap = QPixmap(image_path)

                if pixmap.isNull():
                    continue

                # セルサイズに合わせて画像を表示
                pixmap = pixmap.scaled(
                    self.cell_size,
                    self.cell_size,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )

                px = x * self.cell_size
                py = y * self.cell_size

                # セル中央に表示
                image_x = px + (self.cell_size - pixmap.width()) // 2
                image_y = py + (self.cell_size - pixmap.height()) // 2

                painter.drawPixmap(
                    image_x,
                    image_y,
                    pixmap
                )

        # グリッド
        painter.setPen(QColor(180, 180, 180))

        for x in range(self.width_count + 1):
            px = x * self.cell_size

            painter.drawLine(
                px,
                0,
                px,
                self.height_count * self.cell_size
            )

        for y in range(self.height_count + 1):
            py = y * self.cell_size

            painter.drawLine(
                0,
                py,
                self.width_count * self.cell_size,
                py
            )

    
    def mousePressEvent(self, event):
        # マウスボタンを押したとき
        if event.button() == Qt.LeftButton:
            self.edit_cell(event.pos(), Qt.LeftButton)

        elif event.button() == Qt.RightButton:
            self.edit_cell(event.pos(), Qt.RightButton)

    def mouseMoveEvent(self, event):
        # 左クリックを押したまま移動 → 連続配置
        if event.buttons() & Qt.LeftButton:
            self.edit_cell(event.pos(), Qt.LeftButton)

        # 右クリックを押したまま移動 → 連続削除
        elif event.buttons() & Qt.RightButton:
            self.edit_cell(event.pos(), Qt.RightButton)

    def edit_cell(self, pos, button):
        # マウス位置からマスの座標を計算
        x = pos.x() // self.cell_size
        y = pos.y() // self.cell_size

        # マップの範囲外なら何もしない
        if x < 0 or x >= self.width_count:
            return

        if y < 0 or y >= self.height_count:
            return

        if y >= len(self.map_data):
            return

        if x >= len(self.map_data[y]):
            return

        # 左クリック → ブロック配置
        if button == Qt.LeftButton:
            if self.selected_block_id is None:
                return

            self.map_data[y][x] = self.selected_block_id

        # 右クリック → ブロック削除
        elif button == Qt.RightButton:
            self.map_data[y][x] = "0"

        self.update()
        

    def set_map_size(self, width, height):
        self.width_count = width
        self.height_count = height

        self.setFixedSize(
            width * self.cell_size,
            height * self.cell_size
        )

        self.update()

    def set_map_data(self, map_data):
        self.map_data = map_data
        self.update()

    def set_selected_block(self, block_id):
        self.selected_block_id = block_id


# ============================================================
# ブロック一覧
# ============================================================

class BlockPanel(QWidget):

    block_selected = pyqtSignal(str)

    def __init__(self, block_manager, parent=None):
        super().__init__(parent)

        self.block_manager = block_manager

        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignTop)

        self.selected_block_id = None
        self.block_widgets = []

        self.refresh_blocks()

    def refresh_blocks(self):
        # 現在表示されているブロックを削除
        while self.layout.count():
            item = self.layout.takeAt(0)

            widget = item.widget()

            if widget is not None:
                widget.deleteLater()

        # 古いウィジェット情報を削除
        self.block_widgets.clear()

        # BlockManagerからブロックを取得
        blocks = self.block_manager.get_blocks()

        for block in blocks:
            self.add_block(block)

        # 一番上のブロックを自動選択
        if blocks:
            self.select_block(blocks[0])

    def add_block(self, block):
        # 1ブロック分のウィジェット
        block_widget = QPushButton()
        block_widget.setCheckable(True)

        block_widget.setFixedHeight(80)

        # -------------------------
        # 画像
        # -------------------------

        image_path = os.path.join(
            self.block_manager.block_folder,
            block["file_name"]
        )

        pixmap = QPixmap(image_path)

        if not pixmap.isNull():
            pixmap = pixmap.scaled(
                64,
                64,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )

            block_widget.setIcon(QIcon(pixmap))
            block_widget.setIconSize(QSize(64, 64))

        # -------------------------
        # 名前・ID
        # -------------------------

        block_id = block["id"]

        if block_id is None:
            id_text = "ID: 未設定"
        else:
            id_text = f"ID: {block_id}"

        block_widget.setText(
            f"{block['name']}\n{id_text}"
        )

        # -------------------------
        # クリック時
        # -------------------------

        block_widget.clicked.connect(
            lambda checked=False, b=block:
            self.select_block(b)
        )

        self.block_widgets.append(
            (block, block_widget)
        )

        self.layout.addWidget(block_widget)

    def select_block(self, block):
        self.selected_block_id = block["id"]

        self.update_selection_style()

        self.block_selected.emit(
            block["id"]
    )

    def update_selection_style(self):
        for block, widget in self.block_widgets:

            if block["id"] == self.selected_block_id:
                widget.setChecked(True)
            else:
                widget.setChecked(False)


# ============================================================
# メインウィンドウ
# ============================================================

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.map_data = []

        self.block_manager = BlockManager()

        self.setWindowTitle("Map Chip Editor")
        self.resize(1270, 720)

        self.create_menu()
        self.create_ui()
        self.create_status_bar()

        self.setup_block_ids()
        self.block_panel.refresh_blocks()

        # 起動時にマップを読み込む
        width, height = self.load_map()

        self.width_spin.setValue(width)
        self.height_spin.setValue(height)

        self.map_canvas.set_map_size(width, height)
        self.map_canvas.set_map_data(self.map_data)
        

    # --------------------------------------------------------
    # メニューバー
    # --------------------------------------------------------

    def create_menu(self):
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu("ファイル")

        file_menu.addAction("新規")
        file_menu.addAction("開く")
        file_menu.addAction("保存")

        file_menu.addSeparator()

        file_menu.addAction("終了")

        edit_menu = menu_bar.addMenu("編集")

        edit_menu.addAction("元に戻す")
        edit_menu.addAction("やり直す")

    # --------------------------------------------------------
    # メインUI
    # --------------------------------------------------------

    def create_ui(self):

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ====================================================
        # ツールバー
        # ====================================================

        toolbar = QFrame()
        toolbar.setFrameShape(QFrame.StyledPanel)

        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(8, 5, 8, 5)

        # 横
        width_label = QLabel("横:")

        self.width_spin = QSpinBox()
        self.width_spin.setRange(1, 9999)
        self.width_spin.setValue(50)
        self.width_spin.setFixedWidth(80)

        # 縦
        height_label = QLabel("縦:")

        self.height_spin = QSpinBox()
        self.height_spin.setRange(1, 9999)
        self.height_spin.setValue(30)
        self.height_spin.setFixedWidth(80)

        # マスサイズ
        cell_label = QLabel("マスサイズ:")

        self.cell_spin = QSpinBox()
        self.cell_spin.setRange(1, 512)
        self.cell_spin.setValue(32)
        self.cell_spin.setFixedWidth(80)

        # マップ生成
        generate_button = QPushButton("マップ生成")
        generate_button.setFixedWidth(100)

        # 保存
        save_button = QPushButton("保存")
        save_button.setFixedWidth(80)

        toolbar_layout.addWidget(width_label)
        toolbar_layout.addWidget(self.width_spin)

        toolbar_layout.addSpacing(10)

        toolbar_layout.addWidget(height_label)
        toolbar_layout.addWidget(self.height_spin)

        toolbar_layout.addSpacing(10)

        toolbar_layout.addWidget(cell_label)
        toolbar_layout.addWidget(self.cell_spin)

        toolbar_layout.addSpacing(15)

        toolbar_layout.addWidget(generate_button)
        toolbar_layout.addWidget(save_button)

        toolbar_layout.addStretch()

        main_layout.addWidget(toolbar)

        # ====================================================
        # 中央部分
        # ====================================================

        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # ----------------------------------------------------
        # 左側
        # ----------------------------------------------------

        self.block_panel = BlockPanel(self.block_manager)
        self.block_panel.setFixedWidth(200)

        content_layout.addWidget(self.block_panel)

        # ----------------------------------------------------
        # 右側
        # ----------------------------------------------------

        map_area = QFrame()
        map_area.setFrameShape(QFrame.StyledPanel)

        map_layout = QVBoxLayout(map_area)
        map_layout.setContentsMargins(0, 0, 0, 0)

        self.scroll_area = QScrollArea()

        self.scroll_area.setWidgetResizable(False)

        self.scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAsNeeded
        )

        self.scroll_area.setVerticalScrollBarPolicy(
            Qt.ScrollBarAsNeeded
        )

        self.map_canvas = MapCanvas(
            self.block_manager,
            width_count=50,
            height_count=30,
            cell_size=32
        )

        # ブロック選択とマップを接続
        self.block_panel.block_selected.connect(
            self.map_canvas.set_selected_block
        )

        self.scroll_area.setWidget(self.map_canvas)

        map_layout.addWidget(self.scroll_area)

        content_layout.addWidget(map_area)

        main_layout.addLayout(content_layout)

        # ====================================================
        # マップ生成ボタン
        # ====================================================

        generate_button.clicked.connect(self.generate_map)

    # --------------------------------------------------------
    # マップ生成
    # --------------------------------------------------------

    def generate_map(self):

        new_width = self.width_spin.value()
        new_height = self.height_spin.value()
        cell_size = self.cell_spin.value()

        # 現在のマップサイズ
        old_height = len(self.map_data)

        if old_height > 0:
            old_width = len(self.map_data[0])
        else:
            old_width = 0

        # ========================================================
        # 横幅を変更
        # ========================================================

        for y in range(old_height):

            if new_width > old_width:
                # 右側に0を追加
                self.map_data[y].extend(
                    [0] * (new_width - old_width)
                )

            elif new_width < old_width:
                # 右側を削る
                self.map_data[y] = self.map_data[y][:new_width]

        # ========================================================
        # 高さを変更
        # ========================================================

        if new_height > old_height:
            # 上側に0の行を追加
            add_rows = [
                [0 for _ in range(new_width)]
                for _ in range(new_height - old_height)
            ]

            self.map_data = add_rows + self.map_data

        elif new_height < old_height:
            # 上側の行を削る
            self.map_data = self.map_data[
                old_height - new_height:
            ]

        # ========================================================
        # MapCanvasを更新
        # ========================================================

        self.map_canvas.width_count = new_width
        self.map_canvas.height_count = new_height
        self.map_canvas.cell_size = cell_size

        self.map_canvas.update_size()
        self.map_canvas.set_map_data(self.map_data)

    # --------------------------------------------------------
    # ステータスバー
    # --------------------------------------------------------

    def create_status_bar(self):

        self.statusBar().showMessage(
            "ブロック: なし    ID: -    座標: X=- Y=-"
        )

    def load_map(self):
        map_path = os.path.join("map", "map.txt")

        # map.txtが存在しない場合
        if not os.path.exists(map_path):
            width = self.width_spin.value()
            height = self.height_spin.value()

            self.map_data = [
                [0 for _ in range(width)]
                for _ in range(height)
            ]

            return width, height

        # map.txtが存在する場合
        with open(map_path, "r", encoding="utf-8") as f:
            lines = f.read().splitlines()

        # 空ファイルの場合
        if not lines:
            width = self.width_spin.value()
            height = self.height_spin.value()

            self.map_data = [
                [0 for _ in range(width)]
                for _ in range(height)
            ]

            return width, height

        # ファイルから幅・高さを取得
        height = len(lines)
        width = len(lines[0])

        self.map_data = []

        for line in lines:
            row = []

            for char in line:
                row.append(char)

            self.map_data.append(row)

        return width, height


    def setup_block_ids(self):
        for block in self.block_manager.get_blocks():
            if block["id"] is not None:
                continue

            block_name = block["name"]

            image_path = os.path.join(
                self.block_manager.block_folder,
                block["file_name"]
            )

            while True:
                dialog = BlockIDDialog(
                    block_name,
                    image_path,
                    self
                )

                result = dialog.exec_()

                if result != QDialog.Accepted:
                    break

                block_id = dialog.get_id()

                if len(block_id) != 1:
                    QMessageBox.warning(
                        self,
                        "入力エラー",
                        "IDは1文字で入力してください。"
                    )
                    continue

                # 既に使用されているIDか確認
                if self.block_manager.is_id_used(block_id):
                    QMessageBox.warning(
                        self,
                        "入力エラー",
                        f"ID「{block_id}」は既に使用されています。"
                    )
                    continue

                self.block_manager.set_block_id(
                    block_name,
                    block_id
                )

                break

# ============================================================
# 起動
# ============================================================

if __name__ == "__main__":

    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())