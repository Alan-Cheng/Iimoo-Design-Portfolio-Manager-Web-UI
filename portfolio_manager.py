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
        try:
            with open(PortfolioManager.DESCRIPTION_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for item in data:
                    img_link = item.get("圖片連結", "")
                    if img_link:
                        folder_key = img_link.strip('/').split('/')[-1]
                        if folder_key and folder_key.startswith('w'):
                            descriptions[folder_key] = item
        except FileNotFoundError:
            print(f"描述文件未找到，将创建新的: {PortfolioManager.DESCRIPTION_FILE}")
        except json.JSONDecodeError as e:
            print(f"描述文件格式错误: {PortfolioManager.DESCRIPTION_FILE}: {e}")
        except Exception as e:
            print(f"加载描述文件时出错: {e}")
        return descriptions

    @staticmethod
    def add_description_entry(folder_name: str, data: Dict) -> bool:
        """添加新的描述条目到JSON文件"""
        try:
            entries = []
            if os.path.exists(PortfolioManager.DESCRIPTION_FILE):
                try:
                    with open(PortfolioManager.DESCRIPTION_FILE, 'r', encoding='utf-8') as f:
                        entries = json.load(f)
                    if not isinstance(entries, list): 
                        print(f"警告: 描述文件不是列表格式，将重置为空列表。")
                        entries = []
                except json.JSONDecodeError:
                     print(f"警告: 描述文件格式错误，将重置为空列表。")
                     entries = []

            new_entry = {
                "專案名": data.get("project_name", ""),
                "圖片連結": f"./assets/img/portfolio/{folder_name}/",
                "描述": data.get("description", ""),
                "區域": data.get("area", ""),
                "日期": data.get("date", ""),
                "坪數": data.get("size", ""),
                "種類": data.get("type", "")
            }
            entries.append(new_entry)

            with open(PortfolioManager.DESCRIPTION_FILE, 'w', encoding='utf-8') as f:
                json.dump(entries, f, ensure_ascii=False, indent=4) 
            
            print(f"成功添加描述到 {PortfolioManager.DESCRIPTION_FILE} for {folder_name}")
            return True
        except Exception as e:
            print(f"添加描述到 {PortfolioManager.DESCRIPTION_FILE} 时出错: {e}")
            return False

    @staticmethod
    def get_portfolio_items() -> List[Dict]:
        """获取所有作品集及其图片和描述，按文件夹名称数字降序排序"""
        items = []
        portfolio_path = os.path.join(PortfolioManager.BASE_DIR, PortfolioManager.PORTFOLIO_DIR)
        descriptions = PortfolioManager.load_descriptions()
        
        if not os.path.exists(portfolio_path):
            os.makedirs(portfolio_path, exist_ok=True)
            return items

        # First, collect all items
        temp_items = []
        for item_dir in os.listdir(portfolio_path): # No need to sort here initially
            dir_path = os.path.join(portfolio_path, item_dir)
            if not os.path.isdir(dir_path) or not item_dir.startswith('w'):
                continue

            # Extract number for sorting, handle potential errors
            try:
                folder_num = int(item_dir[1:])
            except ValueError:
                print(f"警告: 无法从文件夹名称提取数字: {item_dir}")
                continue # Skip folders that don't match w<number> format

            images = []
            for filename in sorted(os.listdir(dir_path)): # Sort images within folder
                filepath = os.path.join(dir_path, filename)
                if os.path.isfile(filepath) and filename.lower().endswith('.jpg'):
                    images.append({
                        'name': filename,
                        'path': f"/assets/img/portfolio/{item_dir}/{filename}"
                    })
            
            if images:
                desc_data = descriptions.get(item_dir, {}) 
                temp_items.append({
                    'name': desc_data.get("專案名", f"作品集 {item_dir[1:]}"), 
                    'folder': item_dir, 
                    'folder_num': folder_num, # Store number for sorting
                    'images': images,
                    'description': desc_data.get("描述", "").replace('\n', '<br>'), 
                    'area': desc_data.get("區域", ""),
                    'date': desc_data.get("日期", ""),
                    'size': desc_data.get("坪數", ""),
                    'type': desc_data.get("種類", "")
                })
        
        # Sort the collected items by folder_num in descending order
        items = sorted(temp_items, key=lambda x: x['folder_num'], reverse=True)
        
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
    def create_new_portfolio(images: List[bytes], description_data: Dict) -> Tuple[bool, str]:
        """创建新作品集、上传图片并添加描述"""
        folder_name = ""
        try:
            next_num = PortfolioManager.get_next_portfolio_number()
            folder_name = f"w{next_num}"
            portfolio_path = os.path.join(PortfolioManager.BASE_DIR, PortfolioManager.PORTFOLIO_DIR, folder_name)
            os.makedirs(portfolio_path, exist_ok=True)
            
            for i, image_data in enumerate(images):
                with open(os.path.join(portfolio_path, f"{i}.jpg"), "wb") as f:
                    f.write(image_data)
            
            if PortfolioManager.add_description_entry(folder_name, description_data):
                return True, f"成功创建作品集 {folder_name} 并添加描述"
            else:
                return False, f"成功创建作品集 {folder_name} 但添加描述失败"

        except Exception as e:
            return False, f"创建作品集 {folder_name} 时出错: {e}"

    @staticmethod
    def delete_portfolio(folder_name: str) -> Tuple[bool, str]:
        """删除指定的作品集文件夹和对应的描述"""
        delete_folder_success = False
        delete_desc_success = False
        folder_message = ""
        desc_message = ""

        # 1. Delete folder
        try:
            if not folder_name or not folder_name.startswith('w') or not folder_name[1:].isdigit():
                folder_message = "无效的作品集文件夹名称"
            else:
                portfolio_path = os.path.join(PortfolioManager.BASE_DIR, PortfolioManager.PORTFOLIO_DIR, folder_name)
                if os.path.exists(portfolio_path) and os.path.isdir(portfolio_path):
                    shutil.rmtree(portfolio_path)
                    delete_folder_success = True
                    folder_message = f"成功删除文件夹 {folder_name}"
                    print(f"Deleted portfolio folder: {portfolio_path}")
                else:
                    folder_message = f"作品集文件夹 {folder_name} 不存在"
        except Exception as e:
            folder_message = f"删除文件夹 {folder_name} 时出错: {e}"
            print(f"Error deleting portfolio folder {folder_name}: {e}")

        # 2. Delete description entry
        try:
            entries = []
            if os.path.exists(PortfolioManager.DESCRIPTION_FILE):
                with open(PortfolioManager.DESCRIPTION_FILE, 'r', encoding='utf-8') as f:
                    entries = json.load(f)
                
                if isinstance(entries, list):
                    original_length = len(entries)
                    entries = [entry for entry in entries if entry.get("圖片連結", "").strip('/').split('/')[-1] != folder_name]
                    
                    if len(entries) < original_length:
                        with open(PortfolioManager.DESCRIPTION_FILE, 'w', encoding='utf-8') as f:
                            json.dump(entries, f, ensure_ascii=False, indent=4)
                        delete_desc_success = True
                        desc_message = f"成功从描述文件中移除 {folder_name}"
                        print(f"Removed description for {folder_name}")
                    else:
                        desc_message = f"描述文件中未找到 {folder_name}"
                else:
                    desc_message = "描述文件格式非列表，无法删除条目"
            else:
                desc_message = "描述文件不存在，无需删除条目"
        except Exception as e:
            desc_message = f"删除描述条目 {folder_name} 时出错: {e}"
            print(f"Error deleting description entry {folder_name}: {e}")

        final_success = delete_folder_success 
        final_message = f"{folder_message}. {desc_message}."
        
        return final_success, final_message