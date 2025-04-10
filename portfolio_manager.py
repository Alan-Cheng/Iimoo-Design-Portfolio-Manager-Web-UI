import os
import json
from typing import List, Dict, Tuple
import shutil

class PortfolioManager:
    BASE_DIR = os.path.join("resources", "remote-access-test")
    PORTFOLIO_DIR = os.path.join("assets", "img", "portfolio")
    DESCRIPTION_FILE = os.path.join(BASE_DIR, "portfolio_description.json")

    @staticmethod
    def load_descriptions() -> Dict[str, Dict]:
        """加载作品集描述信息"""
        descriptions = {}
        # print(f"--- Loading descriptions from: {PortfolioManager.DESCRIPTION_FILE} ---") # Debug
        try:
            with open(PortfolioManager.DESCRIPTION_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for item in data:
                    img_link = item.get("圖片連結", "")
                    if img_link:
                        folder_key = img_link.strip('/').split('/')[-1]
                        if folder_key and folder_key.startswith('w'):
                            # print(f"  Loaded description for key: {folder_key} (from path: {img_link})") # Debug
                            descriptions[folder_key] = item
                        # else:
                            # print(f"  Warning: Could not extract valid folder key '{folder_key}' from path: {img_link}") # Debug
                    # else:
                        # print(f"  Warning: Missing '圖片連結' in item: {item.get('專案名')}") # Debug

        except FileNotFoundError:
            print(f"  Error: Description file not found: {PortfolioManager.DESCRIPTION_FILE}") # Debug
        except json.JSONDecodeError as e:
            print(f"  Error: JSON Decode Error in {PortfolioManager.DESCRIPTION_FILE}: {e}") # Debug
        except Exception as e:
            print(f"  Error loading description file: {e}") # Debug
        # print(f"--- Finished loading descriptions. Found {len(descriptions)} entries. ---") # Debug
        return descriptions

    @staticmethod
    def get_portfolio_items() -> List[Dict]:
        """获取所有作品集及其图片和描述"""
        items = []
        portfolio_path = os.path.join(PortfolioManager.BASE_DIR, PortfolioManager.PORTFOLIO_DIR)
        descriptions = PortfolioManager.load_descriptions()
        
        # print(f"--- Getting portfolio items from: {portfolio_path} ---") # Debug
        if not os.path.exists(portfolio_path):
            # print(f"  Portfolio directory does not exist: {portfolio_path}") # Debug
            os.makedirs(portfolio_path, exist_ok=True)
            return items

        for item_dir in sorted(os.listdir(portfolio_path)):
            dir_path = os.path.join(portfolio_path, item_dir)
            if not os.path.isdir(dir_path) or not item_dir.startswith('w'):
                continue

            images = []
            for filename in sorted(os.listdir(dir_path)):
                filepath = os.path.join(dir_path, filename)
                if os.path.isfile(filepath) and filename.lower().endswith('.jpg'):
                    images.append({
                        'name': filename,
                        'path': f"/assets/img/portfolio/{item_dir}/{filename}"
                    })
            
            if images:
                desc_data = descriptions.get(item_dir, {}) # 获取对应的描述信息
                # if desc_data:
                     # print(f"    Found description data for {item_dir}: {desc_data.get('專案名')}") # Debug
                # else:
                     # print(f"    No description data found for {item_dir}.") # Debug

                items.append({
                    'name': desc_data.get("專案名", f"作品集 {item_dir[1:]}"), 
                    'folder': item_dir, # Keep folder name for deletion
                    'images': images,
                    'description': desc_data.get("描述", "").replace('\n', '<br>'), 
                    'area': desc_data.get("區域", ""),
                    'date': desc_data.get("日期", ""),
                    'size': desc_data.get("坪數", ""),
                    'type': desc_data.get("種類", "")
                })
        
        # print(f"--- Finished getting portfolio items. Found {len(items)} items. ---") # Debug
        return items

    @staticmethod
    def get_next_portfolio_number() -> int:
        """获取下一个作品集编号"""
        portfolio_path = os.path.join(PortfolioManager.BASE_DIR, PortfolioManager.PORTFOLIO_DIR)
        if not os.path.exists(portfolio_path):
            return 1

        max_num = 0
        for item in os.listdir(portfolio_path):
            if item.startswith('w') and item[1:].isdigit():
                num = int(item[1:])
                if num > max_num:
                    max_num = num
        return max_num + 1

    @staticmethod
    def create_new_portfolio(images: List[bytes]) -> Tuple[bool, str]:
        """创建新作品集并上传图片"""
        try:
            next_num = PortfolioManager.get_next_portfolio_number()
            folder_name = f"w{next_num}"
            portfolio_path = os.path.join(PortfolioManager.BASE_DIR, PortfolioManager.PORTFOLIO_DIR, folder_name)
            
            os.makedirs(portfolio_path, exist_ok=True)
            
            for i, image_data in enumerate(images):
                with open(os.path.join(portfolio_path, f"{i}.jpg"), "wb") as f:
                    f.write(image_data)
            
            return True, f"成功创建作品集 {folder_name}"
        except Exception as e:
            return False, str(e)

    @staticmethod
    def delete_portfolio(folder_name: str) -> Tuple[bool, str]:
        """删除指定的作品集文件夹"""
        try:
            if not folder_name or not folder_name.startswith('w') or not folder_name[1:].isdigit():
                return False, "无效的作品集文件夹名称"

            portfolio_path = os.path.join(PortfolioManager.BASE_DIR, PortfolioManager.PORTFOLIO_DIR, folder_name)
            
            if os.path.exists(portfolio_path) and os.path.isdir(portfolio_path):
                shutil.rmtree(portfolio_path)
                print(f"Deleted portfolio folder: {portfolio_path}") # Debug
                return True, f"成功删除作品集 {folder_name}"
            else:
                return False, f"作品集文件夹 {folder_name} 不存在"
        except Exception as e:
            print(f"Error deleting portfolio {folder_name}: {e}") # Debug
            return False, f"删除作品集 {folder_name} 时出错: {e}"