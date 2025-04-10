import os
from typing import List, Dict

class PortfolioManager:
    BASE_DIR = os.path.join("resources", "remote-access-test")
    PORTFOLIO_DIR = os.path.join("assets", "img", "portfolio")

    @staticmethod
    def get_portfolio_items() -> List[Dict]:
        """Get all portfolio items with their images"""
        items = []
        portfolio_path = os.path.join(PortfolioManager.BASE_DIR, PortfolioManager.PORTFOLIO_DIR)
        
        if not os.path.exists(portfolio_path):
            print(f"Portfolio directory not found: {portfolio_path}")
            return items

        for item_dir in sorted(os.listdir(portfolio_path)):
            dir_path = os.path.join(portfolio_path, item_dir)
            if not os.path.isdir(dir_path):
                continue

            images = []
            for filename in sorted(os.listdir(dir_path)):
                filepath = os.path.join(dir_path, filename)
                print(f"Checking file: {filepath}")  # 调试输出
                
                if os.path.isfile(filepath) and filename.lower().endswith('.jpg'):
                    images.append({
                        'name': filename,
                        'path': f"/assets/img/portfolio/{item_dir}/{filename}"
                    })
            
            if images:
                items.append({
                    'name': f"作品集 {item_dir[1:]}" if item_dir.startswith('w') else item_dir,
                    'images': images
                })
        
        return items