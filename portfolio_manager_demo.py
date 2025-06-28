import os
import json
import shutil
from datetime import datetime
from typing import List, Dict, Tuple
from werkzeug.utils import secure_filename
import uuid

class PortfolioManagerDemo:
    BASE_DIR = os.path.abspath("resources")
    PORTFOLIO_DIR = os.path.join(BASE_DIR, "demo-portfolio")
    DESCRIPTION_FILE = "description.json"
    
    # Demo data for testing
    DEMO_PORTFOLIOS = [
        {
            "folder_name": "demo-project-1",
            "project_name": "現代住宅設計",
            "description": "這是一個現代風格的住宅設計項目，注重空間利用和自然採光。",
            "area": "120平方米",
            "date": "2024-01-15",
            "size": "3房2廳",
            "type": "住宅設計",
            "images": ["demo1_1.jpg", "demo1_2.jpg"]
        },
        {
            "folder_name": "demo-project-2", 
            "project_name": "商業空間規劃",
            "description": "為企業打造的現代化辦公空間，強調協作和創意氛圍。",
            "area": "500平方米",
            "date": "2024-02-20",
            "size": "開放式辦公",
            "type": "商業設計",
            "images": ["demo2_1.jpg", "demo2_2.jpg", "demo2_3.jpg"]
        }
    ]

    @classmethod
    def _ensure_demo_structure(cls):
        """Ensure demo directory structure exists"""
        if not os.path.exists(cls.PORTFOLIO_DIR):
            os.makedirs(cls.PORTFOLIO_DIR)
            
        # Create demo portfolios if they don't exist
        for portfolio in cls.DEMO_PORTFOLIOS:
            portfolio_path = os.path.join(cls.PORTFOLIO_DIR, portfolio["folder_name"])
            if not os.path.exists(portfolio_path):
                os.makedirs(portfolio_path)
                
                # Create description file
                desc_data = {k: v for k, v in portfolio.items() if k != "images"}
                with open(os.path.join(portfolio_path, cls.DESCRIPTION_FILE), 'w', encoding='utf-8') as f:
                    json.dump(desc_data, f, ensure_ascii=False, indent=2)
                    
                # Create demo image files (empty files for demo)
                for img in portfolio["images"]:
                    img_path = os.path.join(portfolio_path, img)
                    with open(img_path, 'w') as f:
                        f.write("Demo image file")

    @classmethod
    def get_portfolio_items(cls) -> List[Dict]:
        """Get all portfolio items with demo data"""
        cls._ensure_demo_structure()
        
        portfolios = []
        if os.path.exists(cls.PORTFOLIO_DIR):
            for folder_name in os.listdir(cls.PORTFOLIO_DIR):
                folder_path = os.path.join(cls.PORTFOLIO_DIR, folder_name)
                if os.path.isdir(folder_path):
                    desc_file = os.path.join(folder_path, cls.DESCRIPTION_FILE)
                    
                    if os.path.exists(desc_file):
                        try:
                            with open(desc_file, 'r', encoding='utf-8') as f:
                                portfolio_data = json.load(f)
                                
                            # Get image files
                            images = []
                            for file in os.listdir(folder_path):
                                if file.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                                    images.append(file)
                            
                            portfolio_data['images'] = images
                            portfolios.append(portfolio_data)
                            
                        except Exception as e:
                            print(f"Error reading portfolio {folder_name}: {e}")
                            
        return portfolios

    @classmethod
    def create_new_portfolio(cls, uploaded_files: List, description_data: Dict) -> Tuple[bool, str]:
        """Create a new portfolio with demo data"""
        try:
            # Generate unique folder name
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            folder_name = f"demo-portfolio-{timestamp}"
            portfolio_path = os.path.join(cls.PORTFOLIO_DIR, folder_name)
            
            if os.path.exists(portfolio_path):
                return False, "Portfolio folder already exists"
                
            os.makedirs(portfolio_path)
            
            # Save description
            description_data['folder_name'] = folder_name
            desc_file = os.path.join(portfolio_path, cls.DESCRIPTION_FILE)
            with open(desc_file, 'w', encoding='utf-8') as f:
                json.dump(description_data, f, ensure_ascii=False, indent=2)
            
            # Save uploaded files (simulate)
            saved_images = []
            for i, file in enumerate(uploaded_files):
                if file and file.filename:
                    filename = secure_filename(file.filename)
                    # Generate demo filename
                    demo_filename = f"demo_img_{timestamp}_{i+1}.jpg"
                    file_path = os.path.join(portfolio_path, demo_filename)
                    
                    # Create demo file
                    with open(file_path, 'w') as f:
                        f.write(f"Demo image content for {filename}")
                    
                    saved_images.append(demo_filename)
            
            return True, f"Demo: 成功創建作品集 '{description_data.get('project_name', 'New Portfolio')}' 包含 {len(saved_images)} 張圖片"
            
        except Exception as e:
            return False, f"Demo: 創建作品集時發生錯誤: {str(e)}"

    @classmethod
    def update_description_entry(cls, folder_name: str, update_data: Dict) -> Tuple[bool, str]:
        """Update portfolio description"""
        try:
            portfolio_path = os.path.join(cls.PORTFOLIO_DIR, folder_name)
            desc_file = os.path.join(portfolio_path, cls.DESCRIPTION_FILE)
            
            if not os.path.exists(desc_file):
                return False, f"Demo: 找不到作品集資料夾 '{folder_name}'"
            
            # Read existing data
            with open(desc_file, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
            
            # Update with new data
            existing_data.update(update_data)
            
            # Write back
            with open(desc_file, 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, ensure_ascii=False, indent=2)
            
            return True, f"Demo: 成功更新作品集 '{folder_name}' 的描述"
            
        except Exception as e:
            return False, f"Demo: 更新描述時發生錯誤: {str(e)}"

    @classmethod
    def replace_portfolio_images(cls, folder_name: str, new_images: List) -> Tuple[bool, str]:
        """Replace portfolio images"""
        try:
            portfolio_path = os.path.join(cls.PORTFOLIO_DIR, folder_name)
            
            if not os.path.exists(portfolio_path):
                return False, f"Demo: 找不到作品集資料夾 '{folder_name}'"
            
            # Remove existing images
            for file in os.listdir(portfolio_path):
                if file.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                    os.remove(os.path.join(portfolio_path, file))
            
            # Save new images
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            saved_images = []
            
            for i, file in enumerate(new_images):
                if file and file.filename:
                    filename = secure_filename(file.filename)
                    demo_filename = f"demo_img_{timestamp}_{i+1}.jpg"
                    file_path = os.path.join(portfolio_path, demo_filename)
                    
                    # Create demo file
                    with open(file_path, 'w') as f:
                        f.write(f"Demo image content for {filename}")
                    
                    saved_images.append(demo_filename)
            
            return True, f"Demo: 成功替換作品集 '{folder_name}' 的圖片，共 {len(saved_images)} 張"
            
        except Exception as e:
            return False, f"Demo: 替換圖片時發生錯誤: {str(e)}"

    @classmethod
    def delete_portfolio(cls, folder_name: str) -> Tuple[bool, str]:
        """Delete portfolio"""
        try:
            portfolio_path = os.path.join(cls.PORTFOLIO_DIR, folder_name)
            
            if not os.path.exists(portfolio_path):
                return False, f"Demo: 找不到作品集資料夾 '{folder_name}'"
            
            # Remove directory
            shutil.rmtree(portfolio_path)
            
            return True, f"Demo: 成功刪除作品集 '{folder_name}'"
            
        except Exception as e:
            return False, f"Demo: 刪除作品集時發生錯誤: {str(e)}" 