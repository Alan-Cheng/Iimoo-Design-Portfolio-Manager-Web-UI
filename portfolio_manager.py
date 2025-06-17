import os
import json
from typing import List, Dict, Tuple
import shutil
from io import BytesIO 

try:
    from PIL import Image, ImageChops, ImageOps
except ImportError:
    print("警告: Pillow 未安裝。圖片處理功能無法使用。请在終端機執行 'pip install Pillow'")
    Image = None 

class PortfolioManager:
    BASE_DIR = os.path.join("resources", os.getenv('GITHUB_REPO_NAME'))
    PORTFOLIO_DIR = os.path.join("assets", "img", "portfolio")
    DESCRIPTION_FILE = os.path.join(BASE_DIR, "portfolio_description.json")

    # --- Image Processing Helper Functions ---
    @staticmethod
    def _trim_whitespace(img, border=10):
        if not Image: return img 
        try:
            img_rgb = img.convert("RGB")
            bg = Image.new("RGB", img_rgb.size, (255, 255, 255))
            diff = ImageChops.difference(img_rgb, bg)
            diff = ImageChops.add(diff, diff, 2.0, -100)
            bbox = diff.getbbox() 
            if bbox:
                img_cropped = img_rgb.crop(bbox)
                img_expanded = ImageOps.expand(img_cropped, border=border, fill="white")
                return img_expanded
            else:
                return img_rgb 
        except Exception as e:
            print(f"  _trim_whitespace: Error during trim: {e}") 
            return img.convert("RGB") 

    @staticmethod
    def _resize_and_center_image(img_to_resize, canvas_size):
        if not Image: return img_to_resize 
        try:
            img = PortfolioManager._trim_whitespace(img_to_resize, border=10)
            img_ratio = img.width / img.height
            canvas_ratio = canvas_size[0] / canvas_size[1]
            # target_w = canvas_size[0] - 20 
            # target_h = canvas_size[1] - 20
            if img_ratio > canvas_ratio:
                new_width = canvas_size[0]
                new_height = int(new_width / img_ratio)
            else:
                new_height = canvas_size[1]
                new_width = int(new_height * img_ratio)
            img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS) 
            canvas = Image.new("RGB", canvas_size, (255, 255, 255))
            x_offset = (canvas_size[0] - new_width) // 2
            y_offset = (canvas_size[1] - new_height) // 2
            canvas.paste(img_resized, (x_offset, y_offset))
            return canvas
        except Exception as e:
            print(f"  _resize_and_center_image: Error during resize/center: {e}") 
            return img_to_resize.convert("RGB") 
    # --- End Image Processing ---

    @staticmethod
    def load_descriptions() -> Dict[str, Dict]:
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
            pass 
        except json.JSONDecodeError as e:
            print(f"作品描述json檔案錯誤: {PortfolioManager.DESCRIPTION_FILE}: {e}")
        except Exception as e:
            print(f"載入作品描述json檔案時發生錯誤: {e}")
        return descriptions

    @staticmethod
    def add_description_entry(folder_name: str, data: Dict) -> bool:
        try:
            # 確保目錄存在
            os.makedirs(os.path.dirname(PortfolioManager.DESCRIPTION_FILE), exist_ok=True)
            
            entries = []
            if os.path.exists(PortfolioManager.DESCRIPTION_FILE):
                try:
                    with open(PortfolioManager.DESCRIPTION_FILE, 'r', encoding='utf-8') as f:
                        entries = json.load(f)
                    if not isinstance(entries, list): 
                        print(f"警告: 作品描述json檔案是陣列，重置為空陣列。")
                        entries = []
                except json.JSONDecodeError:
                     print(f"警告: 作品描述json檔案錯誤，重置為空陣列。")
                     entries = []

            new_entry = {
                "專案名": data.get("project_name", ""),
                "圖片連結": f"./assets/img/portfolio/{folder_name}/",
                "風格": data.get("style", ""),
                "屋況": data.get("condition", ""),
                "格局": data.get("layout", ""),
                "坪數": data.get("size", ""),
                "地點": data.get("location", ""),
                "種類": data.get("type", "")
            }
            entries = [e for e in entries if e.get("圖片連結", "").strip('/').split('/')[-1] != folder_name]
            entries.append(new_entry)

            with open(PortfolioManager.DESCRIPTION_FILE, 'w', encoding='utf-8') as f:
                json.dump(entries, f, ensure_ascii=False, indent=4) 
            return True
        except Exception as e:
            print(f"新增作品描述到 {PortfolioManager.DESCRIPTION_FILE} 時出現錯誤: {e}")
            return False

    @staticmethod
    def update_description_entry(folder_name: str, data: Dict) -> Tuple[bool, str]:
        try:
            # 確保目錄存在
            os.makedirs(os.path.dirname(PortfolioManager.DESCRIPTION_FILE), exist_ok=True)
            
            entries = []
            if not os.path.exists(PortfolioManager.DESCRIPTION_FILE):
                return False, "作品描述json檔案不存在"
            
            # 讀取現有資料
            with open(PortfolioManager.DESCRIPTION_FILE, 'r', encoding='utf-8') as f:
                entries = json.load(f)
            
            if not isinstance(entries, list):
                return False, "作品描述json檔案格式错误 (非陣列)"
            
            # 尋找並更新對應的項目
            found = False
            for i, entry in enumerate(entries):
                entry_folder = entry.get("圖片連結", "").strip('/').split('/')[-1]
                if entry_folder == folder_name:
                    # 更新所有欄位，保留原始值作為預設值
                    entries[i] = {
                        "專案名": data.get("project_name", entry.get("專案名", "")),
                        "圖片連結": entry.get("圖片連結", f"./assets/img/portfolio/{folder_name}/"),
                        "風格": data.get("style", entry.get("風格", "")),
                        "屋況": data.get("condition", entry.get("屋況", "")),
                        "格局": data.get("layout", entry.get("格局", "")),
                        "坪數": data.get("size", entry.get("坪數", "")),
                        "地點": data.get("location", entry.get("地點", "")),
                        "種類": data.get("type", entry.get("種類", ""))
                    }
                    found = True
                    break
            
            if not found:
                return False, f"未在作品描述json檔案中找到作品集 {folder_name} - {data.get('project_name', '')}"
            
            # 寫入更新後的資料
            with open(PortfolioManager.DESCRIPTION_FILE, 'w', encoding='utf-8') as f:
                json.dump(entries, f, ensure_ascii=False, indent=4)
            
            return True, f"成功更新作品《{data.get('project_name', '')}》的描述"
        except json.JSONDecodeError:
            return False, "作品描述json檔案格式错误"
        except Exception as e:
            print(f"更新描述 {PortfolioManager.DESCRIPTION_FILE} 時出错 for {folder_name}: {e}")
            return False, f"更新描述時出錯: {e}"

    @staticmethod
    def get_portfolio_items() -> List[Dict]:
        items = []
        portfolio_path = os.path.join(PortfolioManager.BASE_DIR, PortfolioManager.PORTFOLIO_DIR)
        descriptions = PortfolioManager.load_descriptions()
        if not os.path.exists(portfolio_path):
            os.makedirs(portfolio_path, exist_ok=True)
            return items
        temp_items = []
        for item_dir in os.listdir(portfolio_path): 
            dir_path = os.path.join(portfolio_path, item_dir)
            if not os.path.isdir(dir_path) or not item_dir.startswith('w'):
                continue
            try:
                folder_num = int(item_dir[1:])
            except ValueError:
                continue 
            images = []
            filenames_sorted = sorted(os.listdir(dir_path), key=lambda name: int(name.split('.')[0]) if name.split('.')[0].isdigit() else float('inf'))
            for filename in filenames_sorted: 
                filepath = os.path.join(dir_path, filename)
                if os.path.isfile(filepath) and filename.lower().endswith('.webp'):
                    images.append({ 'name': filename, 'path': f"/assets/img/portfolio/{item_dir}/{filename}" })
            if images:
                desc_data = descriptions.get(item_dir, {}) 
                temp_items.append({
                    'name': desc_data.get("專案名", f"作品集 {item_dir[1:]}"), 
                    'folder': item_dir, 'folder_num': folder_num, 'images': images,
                    'style': desc_data.get("風格", ""),
                    'condition': desc_data.get("屋況", ""),
                    'layout': desc_data.get("格局", ""),
                    'size': desc_data.get("坪數", ""),
                    'location': desc_data.get("地點", ""),
                    'type': desc_data.get("種類", "")
                })
        items = sorted(temp_items, key=lambda x: x['folder_num'], reverse=True)
        return items

    @staticmethod
    def get_next_portfolio_number() -> int:
        portfolio_path = os.path.join(PortfolioManager.BASE_DIR, PortfolioManager.PORTFOLIO_DIR)
        if not os.path.exists(portfolio_path): return 1
        max_num = 0
        for item in os.listdir(portfolio_path):
            if item.startswith('w') and item[1:].isdigit():
                num = int(item[1:])
                if num > max_num: max_num = num
        return max_num + 1

    @staticmethod
    def replace_portfolio_images(folder_name: str, uploaded_files: List) -> Tuple[bool, str]:
        if not Image: 
            return False, "錯誤: Pillow 未安装，無法處理圖片。"
        
        portfolio_path = os.path.join(PortfolioManager.BASE_DIR, PortfolioManager.PORTFOLIO_DIR, folder_name)
        if not os.path.exists(portfolio_path):
            os.makedirs(portfolio_path, exist_ok=True)
        elif not os.path.isdir(portfolio_path):
            return False, f"目標路徑並非資料夾: {portfolio_path}"

        try:
            # 1. Delete existing files
            for filename in os.listdir(portfolio_path):
                if filename.lower().endswith(('.jpg', '.png', '.webp')):
                    try:
                        os.remove(os.path.join(portfolio_path, filename))
                    except OSError as e:
                        print(f"無法刪除檔案 {filename}: {e}")
            
            # 2. 判斷是否全部為編號命名的圖片
            is_all_numbered = True
            for file_storage in uploaded_files:
                original_filename = file_storage.filename
                if original_filename and original_filename.lower().endswith(('.jpg', '.png')):
                    name_part = os.path.splitext(original_filename)[0]
                    if not name_part.isdigit():
                        is_all_numbered = False
                        break

            # 3. 儲存圖片
            saved_filenames = []
            file_map = {}
            for idx, file_storage in enumerate(uploaded_files):
                original_filename = file_storage.filename
                if original_filename and original_filename.lower().endswith(('.jpg', '.png')):
                    if is_all_numbered:
                        safe_filename = original_filename  # 保留原名
                    else:
                         return False, "請將圖檔以數字編號（0.jpg、1.jpg...）， 規則：0為平面圖，往後為實景圖。"

                    file_path = os.path.join(portfolio_path, safe_filename)
                    file_storage.save(file_path)
                    saved_filenames.append(safe_filename)
                    file_map[safe_filename] = file_path

            if not saved_filenames:
                return False, "無有效圖片檔案上傳，無法替換圖片"

            # 4. Process 0.jpg if 0.jpg and 1.jpg exist
            path_0 = file_map.get("0.jpg") or file_map.get("0.png")
            path_1 = file_map.get("1.jpg") or file_map.get("1.png")
            processing_done = False
            if path_0 and path_1:
                try:
                    with Image.open(path_0) as img_0, Image.open(path_1) as img_1:
                        canvas_size = img_1.size
                        processed_img_0 = PortfolioManager._resize_and_center_image(img_0, canvas_size)
                        if processed_img_0: 
                            # 轉換為 webp
                            webp_path = os.path.splitext(path_0)[0] + '.webp'
                            processed_img_0.save(webp_path, format='WEBP', quality=75)
                            os.remove(path_0)  # 刪除原始檔案
                            processing_done = True
                except Exception as img_proc_e:
                    print(f"Error processing replaced image {path_0}: {img_proc_e}. Keeping original.")
            
            # 5. 將其他圖片轉換為 webp
            for filename, filepath in file_map.items():
                if filename != "0.jpg" and filename != "0.png":  # 跳過已經處理過的 0.jpg/0.png
                    try:
                        with Image.open(filepath) as img:
                            webp_path = os.path.splitext(filepath)[0] + '.webp'
                            img.save(webp_path, format='WEBP', quality=75)
                            os.remove(filepath)  # 刪除原始檔案
                    except Exception as e:
                        print(f"Error converting {filename} to webp: {e}")
            
            return True, f"圖片上傳成功"

        except Exception as e:
            print(f"替換作品 {folder_name} 圖片時出錯: {e}")
            return False, f"替換圖片時出現錯誤: {e}"

    @staticmethod
    def create_new_portfolio(uploaded_files: List, description_data: Dict) -> Tuple[bool, str]:
        folder_name = ""
        try:
            next_num = PortfolioManager.get_next_portfolio_number()
            folder_name = f"w{next_num}"
            
            save_success, save_message = PortfolioManager.replace_portfolio_images(folder_name, uploaded_files)

            if not save_success:
                 if os.path.exists(os.path.join(PortfolioManager.BASE_DIR, PortfolioManager.PORTFOLIO_DIR, folder_name)):
                     shutil.rmtree(os.path.join(PortfolioManager.BASE_DIR, PortfolioManager.PORTFOLIO_DIR, folder_name))
                 return False, f"建立作品《{description_data['project_name']} 》時上傳圖片失敗: {save_message}"

            if PortfolioManager.add_description_entry(folder_name, description_data):
                return True, f"成功建立作品《{description_data['project_name']} 》並新增作品描述. {save_message}"
            else:
                return False, f"成功建立作品《{description_data['project_name']} 》 ({save_message}) 但新增描述失敗"

        except Exception as e:
            if folder_name and os.path.exists(os.path.join(PortfolioManager.BASE_DIR, PortfolioManager.PORTFOLIO_DIR, folder_name)):
                 try:
                     shutil.rmtree(os.path.join(PortfolioManager.BASE_DIR, PortfolioManager.PORTFOLIO_DIR, folder_name))
                     # print(f"Cleaned up folder {folder_name} due to error.") # Removed Debug
                 except Exception as cleanup_e:
                     print(f"Error during cleanup of folder {folder_name}: {cleanup_e}")
            return False, f"建立作品集《{description_data['project_name']} 》時出現錯誤: {e}"


    @staticmethod
    def delete_portfolio(folder_name: str) -> Tuple[bool, str]:
        delete_folder_success = False
        delete_desc_success = False
        folder_message = ""
        desc_message = ""
        try:
            if not folder_name or not folder_name.startswith('w') or not folder_name[1:].isdigit():
                folder_message = "無效的作品資料夾名稱"
            else:
                portfolio_path = os.path.join(PortfolioManager.BASE_DIR, PortfolioManager.PORTFOLIO_DIR, folder_name)
                if os.path.exists(portfolio_path) and os.path.isdir(portfolio_path):
                    shutil.rmtree(portfolio_path)
                    delete_folder_success = True
                    folder_message = f"成功刪除作品"
                    # print(f"Deleted portfolio folder: {portfolio_path}") # Removed Debug
                else:
                    folder_message = f"作品資料夾 {folder_name} 不存在"
        except Exception as e:
            folder_message = f"删除資料夾 {folder_name} 時出錯: {e}"
            print(f"Error deleting portfolio folder {folder_name}: {e}")
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
                        # desc_message = f"成功從作品描述json檔案中移除 {folder_name}"
                        desc_message = f""
                        # print(f"Removed description for {folder_name}") # Removed Debug
                    else:
                        desc_message = f"作品描述json檔案中未找到 {folder_name}"
                else:
                    desc_message = "作品描述json檔案格式非陣列，無法刪除該項目"
            else:
                desc_message = "作品描述json檔案不存在，無需刪除項目"
        except Exception as e:
            desc_message = f"删除描述項目 {folder_name} 時出錯: {e}"
            print(f"Error deleting description entry {folder_name}: {e}")
        final_success = delete_folder_success 
        final_message = f"{folder_message}. {desc_message}."
        return final_success, final_message