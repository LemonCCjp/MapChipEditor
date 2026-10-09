import os
import json


class BlockManager:
    def __init__(
        self,
        block_folder="Blocks",
        json_path="blocks.json"
    ):
        self.block_folder = block_folder
        self.json_path = json_path

        # ブロック情報
        self.blocks = []

        # JSONを読み込む
        self.block_ids = self.load_json()

        # Blocksフォルダを読み込む
        self.load_blocks()

        # 現在存在しない画像のデータをJSONから削除
        self.remove_missing_blocks()

        # JSONを保存
        self.save_json()

    # ============================================================
    # JSON
    # ============================================================

    def load_json(self):
        if not os.path.exists(self.json_path):
            return {}

        try:
            with open(self.json_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            if not isinstance(data, dict):
                return {}

            return data

        except (json.JSONDecodeError, OSError):
            return {}

    def save_json(self):
        with open(self.json_path, "w", encoding="utf-8") as f:
            json.dump(
                self.block_ids,
                f,
                ensure_ascii=False,
                indent=4
            )

    # ============================================================
    # ブロック読み込み
    # ============================================================

    def load_blocks(self):
        self.blocks.clear()

        if not os.path.exists(self.block_folder):
            return

        for file_name in os.listdir(self.block_folder):
            if not file_name.lower().endswith(".png"):
                continue

            block_name = os.path.splitext(file_name)[0]

            block_id = self.block_ids.get(block_name)

            self.blocks.append({
                "name": block_name,
                "file_name": file_name,
                "id": block_id
            })

    # ============================================================
    # 存在しないブロックをJSONから削除
    # ============================================================

    def remove_missing_blocks(self):
        current_names = {
            block["name"]
            for block in self.blocks
        }

        remove_names = []

        for block_name in self.block_ids:
            if block_name not in current_names:
                remove_names.append(block_name)

        for block_name in remove_names:
            del self.block_ids[block_name]

    # ============================================================
    # ブロック情報取得
    # ============================================================

    def get_blocks(self):
        return self.blocks

    def get_block_id(self, block_name):
        return self.block_ids.get(block_name)

    def set_block_id(self, block_name, block_id):
        self.block_ids[block_name] = block_id

        for block in self.blocks:
            if block["name"] == block_name:
                block["id"] = block_id
                break

        self.save_json()


    def is_id_used(self, block_id):
        for block in self.block_ids.values():
            if block == block_id:
                return True

        return False

    def get_block_by_id(self, block_id):
        for block in self.blocks:
            if block["id"] == block_id:
                return block

        return None