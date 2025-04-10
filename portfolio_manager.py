import os
import json
from typing import List, Dict, Tuple
import shutil
from io import BytesIO 

try:
    from PIL import Image, ImageChops, ImageOps
except ImportError:
    print("警告: Pillow 库未安装。图片处理功能将不可用。请运行 'pip install Pillow'")
    Image = None 

class PortfolioManager:
    BASE_DIR = os.path.join("resources", "remote-access-test")
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
            target_w = canvas_size[0] - 20 
            target_h = canvas_size[1] - 20
            if img_ratio > canvas_ratio:
                new_width = target_w
                new_height = int(new_width / img_ratio)
            else:
                new_height = target_h
                new_width = int(new_height * img_ratio)
            new_width = max(1, new_width)
            new_height = max(1, new_height)
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
            # This is expected if the file doesn't exist yet
            pass 
        except json.JSONDecodeError as e:
            print(f"描述文件格式错误: {PortfolioManager.DESCRIPTION_FILE}: {e}")
        except Exception as e:
            print(f"加载描述文件时出错: {e}")
        return descriptions

    @staticmethod
    def add_description_entry(folder_name: str, data: Dict) -> bool:
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
            entries = [e for e in entries if e.get("圖片連結", "").strip('/').split('/')[-1] != folder_name]
            entries.append(new_entry)

            with open(PortfolioManager.DESCRIPTION_FILE, 'w', encoding='utf-8') as f:
                json.dump(entries, f, ensure_ascii=False, indent=4) 
            
            # print(f"成功添加/更新描述到 {PortfolioManager.DESCRIPTION_FILE} for {folder_name}") # Removed Debug
            return True
        except Exception as e:
            print(f"添加描述到 {PortfolioManager.DESCRIPTION_FILE} 时出错: {e}")
            return False

    @staticmethod
    def update_description_entry(folder_name: str, data: Dict) -> Tuple[bool, str]:
        try:
            entries = []
            if not os.path.exists(PortfolioManager.DESCRIPTION_FILE):
                return False, "描述文件不存在"

            with open(PortfolioManager.DESCRIPTION_FILE, 'r', encoding='utf-8') as f:
                entries = json.load(f)
            
            if not isinstance(entries, list):
                return False, "描述文件格式错误 (非列表)"

            found = False
            for i, entry in enumerate(entries):
                entry_folder = entry.get("圖片連結", "").strip('/').split('/')[-1]
                if entry_folder == folder_name:
                    entries[i]["專案名"] = data.get("project_name", entry.get("專案名", ""))
                    entries[i]["描述"] = data.get("description", entry.get("描述", ""))
                    entries[i]["區域"] = data.get("area", entry.get("區域", ""))
                    entries[i]["日期"] = data.get("date", entry.get("日期", ""))
                    entries[i]["坪數"] = data.get("size", entry.get("坪數", ""))
                    entries[i]["種類"] = data.get("type", entry.get("種類", ""))
                    found = True
                    break
            
            if not found:
                return False, f"未在描述文件中找到作品集 {folder_name}"

            with open(PortfolioManager.DESCRIPTION_FILE, 'w', encoding='utf-8') as f:
                json.dump(entries, f, ensure_ascii=False, indent=4)
            
            # print(f"成功更新描述 {PortfolioManager.DESCRIPTION_FILE} for {folder_name}") # Removed Debug
            return True, f"成功更新作品集 {folder_name} 的描述"

        except json.JSONDecodeError:
            return False, "描述文件格式错误"
        except Exception as e:
            print(f"更新描述 {PortfolioManager.DESCRIPTION_FILE} 时出错 for {folder_name}: {e}")
            return False, f"更新描述时出错: {e}"


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
                # print(f"警告: 无法从文件夹名称提取数字: {item_dir}") # Removed Debug
                continue 

            images = []
            filenames_sorted = sorted(os.listdir(dir_path), key=lambda name: int(name.split('.')[0]) if name.split('.')[0].isdigit() else float('inf'))
            
            for filename in filenames_sorted: 
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
                    'folder_num': folder_num, 
                    'images': images,
                    'description': desc_data.get("描述", ""), 
                    'area': desc_data.get("區域", ""),
                    'date': desc_data.get("日期", ""),
                    'size': desc_data.get("坪數", ""),
                    'type': desc_data.get("種類", "")
                })
        
        items = sorted(temp_items, key=lambda x: x['folder_num'], reverse=True)
        return items

    @staticmethod
    def get_next_portfolio_number() -> int:
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
    def create_new_portfolio(uploaded_files: List, description_data: Dict) -> Tuple[bool, str]:
        folder_name = ""
        if not Image: 
             return False, "错误: Pillow 库未安装，无法处理图片。"
        try:
            next_num = PortfolioManager.get_next_portfolio_number()
            folder_name = f"w{next_num}"
            portfolio_path = os.path.join(PortfolioManager.BASE_DIR, PortfolioManager.PORTFOLIO_DIR, folder_name)
            os.makedirs(portfolio_path, exist_ok=True)
            # print(f"Created folder: {portfolio_path}") # Removed Debug
            
            saved_filenames = []
            file_map = {} 
            for file_storage in uploaded_files:
                original_filename = file_storage.filename
                if original_filename and original_filename.lower().endswith('.jpg'):
                    safe_filename = original_filename 
                    file_path = os.path.join(portfolio_path, safe_filename)
                    file_storage.save(file_path) 
                    saved_filenames.append(safe_filename)
                    file_map[safe_filename] = file_path
                    # print(f"Saved image: {file_path}") # Removed Debug
                # else:
                    # print(f"Skipped invalid file: {original_filename}") # Removed Debug

            if not saved_filenames:
                shutil.rmtree(portfolio_path)
                return False, "没有有效的JPG图片被保存"

            path_0 = file_map.get("0.jpg")
            path_1 = file_map.get("1.jpg")
            processing_done = False
            if path_0 and path_1:
                # print(f"Attempting to process {path_0} based on {path_1} dimensions...") # Removed Debug
                try:
                    with Image.open(path_0) as img_0, Image.open(path_1) as img_1:
                        canvas_size = img_1.size
                        # print(f"  Reference canvas size from {path_1}: {canvas_size}") # Removed Debug
                        processed_img_0 = PortfolioManager._resize_and_center_image(img_0, canvas_size)
                        if processed_img_0: 
                            processed_img_0.save(path_0, format='JPEG', quality=95)
                            processing_done = True
                            # print(f"  Successfully processed and overwrote {path_0}") # Removed Debug
                        # else:
                            # print(f"  Image processing returned None for {path_0}. Keeping original.") # Removed Debug
                except FileNotFoundError as fnf_e:
                     print(f"  Error opening image file during processing: {fnf_e}. Keeping original.") 
                except Exception as img_proc_e:
                    print(f"  Error processing image {path_0}: {img_proc_e}. Keeping original.") 
            # elif path_0:
                 # print(f"  Found {path_0} but not 1.jpg. Skipping processing.") # Removed Debug
            # else:
                 # print("  Did not find 0.jpg. Skipping processing.") # Removed Debug

            if PortfolioManager.add_description_entry(folder_name, description_data):
                # On success, return True and the folder name
                return True, folder_name
            else:
                # If description fails, still consider portfolio created but return error message
                return False, f"作品集資料夾 '{folder_name}' 已建立，但新增描述失敗"
        except Exception as e:
            if folder_name and os.path.exists(os.path.join(PortfolioManager.BASE_DIR, PortfolioManager.PORTFOLIO_DIR, folder_name)):
                 try:
                     shutil.rmtree(os.path.join(PortfolioManager.BASE_DIR, PortfolioManager.PORTFOLIO_DIR, folder_name))
                     # print(f"Cleaned up folder {folder_name} due to error.") # Removed Debug
                 except Exception as cleanup_e:
                     print(f"Error during cleanup of folder {folder_name}: {cleanup_e}")
            return False, f"建立作品集 '{folder_name}' 時發生錯誤: {e}"

    @staticmethod
    def delete_portfolio(folder_name: str) -> Tuple[bool, str]:
        delete_folder_success = False
        delete_desc_success = False
        folder_message = ""
        desc_message = ""
        try:
            if not folder_name or not folder_name.startswith('w') or not folder_name[1:].isdigit():
                folder_message = "无效的作品集文件夹名称"
            else:
                portfolio_path = os.path.join(PortfolioManager.BASE_DIR, PortfolioManager.PORTFOLIO_DIR, folder_name)
                if os.path.exists(portfolio_path) and os.path.isdir(portfolio_path):
                    shutil.rmtree(portfolio_path)
                    delete_folder_success = True
                    folder_message = f"成功删除文件夹 {folder_name}"
                    # print(f"Deleted portfolio folder: {portfolio_path}") # Removed Debug
                else:
                    folder_message = f"作品集文件夹 {folder_name} 不存在"
        except Exception as e:
            folder_message = f"删除文件夹 {folder_name} 时出错: {e}"
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
                        desc_message = f"成功从描述文件中移除 {folder_name}"
                        # print(f"Removed description for {folder_name}") # Removed Debug
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