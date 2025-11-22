from uuid import UUID
from typing import List
from app.domain.users.user import User
from app.domain.enum import RoleEnum
from app.domain.users.child import Child

class Admin(User):
    def __init__(self, user_id: UUID, username: str, email: str, password: str, role: RoleEnum, name: str,
                 all_child: List[Child] = None):
        super().__init__(user_id, username, email, password, role, name)
        self.all_child = all_child or []

    def manage_users(self, user_id: UUID, action: str) -> dict:
        """Quản lý người dùng (create, update, delete)"""
        valid_actions = ["create", "update", "delete", "view"]
        if action not in valid_actions:
            return {"status": "failed", "message": f"Invalid action. Must be one of {valid_actions}"}
        
        return {"status": "success", "message": f"Action {action} executed for user {user_id}"}

    def manage_content(self, content: dict) -> dict:
        """Quản lý nội dung game (create, update, delete)"""
        if not content.get("content_id") or not content.get("action"):
            return {"status": "failed", "message": "content_id and action are required"}
        
        return {"status": "success", "message": f"Content {content['content_id']} managed"}

    def view_all_reports(self, report_type: str = None) -> List[dict]:
        """Xem báo cáo của tất cả trẻ"""
        # Logic để lấy reports từ repository
        # Placeholder - cần implement với repository
        return []

    def update_system_settings(self, settings: dict) -> dict:
        """Cập nhật cài đặt hệ thống"""
        if not settings:
            return {"status": "failed", "message": "Settings cannot be empty"}
        
        # Logic cập nhật settings
        return {"status": "success", "message": "System settings updated"}

    def get_all_children(self) -> List[Child]:
        """Lấy danh sách tất cả children mà admin quản lý"""
        return self.all_child

    def add_child(self, child: Child) -> dict:
        """Thêm child vào danh sách quản lý"""
        if child not in self.all_child:
            self.all_child.append(child)
            return {"status": "success", "message": f"Child {child.user_id} added"}
        return {"status": "failed", "message": "Child already exists"}

    def remove_child(self, child_id: str) -> dict:
        """Xóa child khỏi danh sách quản lý"""
        self.all_child = [c for c in self.all_child if c.user_id != child_id]
        return {"status": "success", "message": f"Child {child_id} removed"}

    def get_statistics(self) -> dict:
        """Lấy thống kê tổng quan"""
        return {
            "total_children": len(self.all_child),
            "admin_info": {
                "user_id": str(self.user_id),
                "username": self.username,
                "name": self.name
            }
        }