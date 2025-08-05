"""Role-Based Access Control (RBAC) Implementation"""
from typing import Dict, List, Set, Optional
from enum import Enum
from pydantic import BaseModel
from dataclasses import dataclass
import json


class Role(str, Enum):
    """System roles"""
    ADMIN = "admin"
    MODERATOR = "moderator"
    CAREER_COUNSELOR = "career_counselor"
    USER = "user"
    GUEST = "guest"


class Permission(str, Enum):
    """System permissions"""
    # User management
    USER_CREATE = "user:create"
    USER_READ = "user:read"
    USER_UPDATE = "user:update"
    USER_DELETE = "user:delete"
    USER_LIST = "user:list"
    
    # Career management
    CAREER_CREATE = "career:create"
    CAREER_READ = "career:read"
    CAREER_UPDATE = "career:update"
    CAREER_DELETE = "career:delete"
    CAREER_RECOMMEND = "career:recommend"
    
    # Skills management
    SKILL_CREATE = "skill:create"
    SKILL_READ = "skill:read"
    SKILL_UPDATE = "skill:update"
    SKILL_DELETE = "skill:delete"
    SKILL_ASSESS = "skill:assess"
    
    # Assessment management
    ASSESSMENT_CREATE = "assessment:create"
    ASSESSMENT_READ = "assessment:read"
    ASSESSMENT_UPDATE = "assessment:update"
    ASSESSMENT_DELETE = "assessment:delete"
    ASSESSMENT_TAKE = "assessment:take"
    ASSESSMENT_VIEW_ALL = "assessment:view_all"
    
    # Chat management
    CHAT_CREATE = "chat:create"
    CHAT_READ = "chat:read"
    CHAT_MODERATE = "chat:moderate"
    CHAT_DELETE = "chat:delete"
    
    # Analytics
    ANALYTICS_VIEW = "analytics:view"
    ANALYTICS_EXPORT = "analytics:export"
    
    # System
    SYSTEM_CONFIG = "system:config"
    SYSTEM_MONITOR = "system:monitor"
    SYSTEM_BACKUP = "system:backup"


@dataclass
class RoleDefinition:
    """Role definition with permissions"""
    name: str
    description: str
    permissions: Set[Permission]
    inherits_from: Optional[List[str]] = None


class RBACManager:
    """Manages roles and permissions"""
    
    def __init__(self):
        self.roles: Dict[str, RoleDefinition] = {}
        self._initialize_default_roles()
    
    def _initialize_default_roles(self):
        """Initialize default system roles"""
        # Guest role - minimal permissions
        self.roles[Role.GUEST] = RoleDefinition(
            name=Role.GUEST,
            description="Guest user with read-only access",
            permissions={
                Permission.CAREER_READ,
                Permission.SKILL_READ,
                Permission.ASSESSMENT_READ,
            }
        )
        
        # User role - standard user permissions
        self.roles[Role.USER] = RoleDefinition(
            name=Role.USER,
            description="Standard user",
            permissions={
                Permission.USER_READ,
                Permission.USER_UPDATE,
                Permission.CAREER_READ,
                Permission.CAREER_RECOMMEND,
                Permission.SKILL_READ,
                Permission.SKILL_ASSESS,
                Permission.ASSESSMENT_READ,
                Permission.ASSESSMENT_TAKE,
                Permission.CHAT_CREATE,
                Permission.CHAT_READ,
            },
            inherits_from=[Role.GUEST]
        )
        
        # Career Counselor role - elevated permissions
        self.roles[Role.CAREER_COUNSELOR] = RoleDefinition(
            name=Role.CAREER_COUNSELOR,
            description="Career counselor with management capabilities",
            permissions={
                Permission.USER_LIST,
                Permission.CAREER_CREATE,
                Permission.CAREER_UPDATE,
                Permission.SKILL_CREATE,
                Permission.SKILL_UPDATE,
                Permission.ASSESSMENT_CREATE,
                Permission.ASSESSMENT_UPDATE,
                Permission.ASSESSMENT_VIEW_ALL,
                Permission.ANALYTICS_VIEW,
                Permission.CHAT_MODERATE,
            },
            inherits_from=[Role.USER]
        )
        
        # Moderator role - content moderation
        self.roles[Role.MODERATOR] = RoleDefinition(
            name=Role.MODERATOR,
            description="Content moderator",
            permissions={
                Permission.USER_LIST,
                Permission.CAREER_UPDATE,
                Permission.CAREER_DELETE,
                Permission.SKILL_UPDATE,
                Permission.SKILL_DELETE,
                Permission.CHAT_MODERATE,
                Permission.CHAT_DELETE,
                Permission.ANALYTICS_VIEW,
            },
            inherits_from=[Role.CAREER_COUNSELOR]
        )
        
        # Admin role - full access
        self.roles[Role.ADMIN] = RoleDefinition(
            name=Role.ADMIN,
            description="System administrator with full access",
            permissions={
                Permission.USER_CREATE,
                Permission.USER_DELETE,
                Permission.CAREER_DELETE,
                Permission.SKILL_DELETE,
                Permission.ASSESSMENT_DELETE,
                Permission.ANALYTICS_EXPORT,
                Permission.SYSTEM_CONFIG,
                Permission.SYSTEM_MONITOR,
                Permission.SYSTEM_BACKUP,
            },
            inherits_from=[Role.MODERATOR]
        )
    
    def get_role_permissions(self, role: str) -> Set[Permission]:
        """Get all permissions for a role including inherited"""
        if role not in self.roles:
            return set()
        
        role_def = self.roles[role]
        permissions = role_def.permissions.copy()
        
        # Add inherited permissions
        if role_def.inherits_from:
            for parent_role in role_def.inherits_from:
                permissions.update(self.get_role_permissions(parent_role))
        
        return permissions
    
    def check_permission(
        self, 
        user_roles: List[str], 
        required_permission: Permission
    ) -> bool:
        """Check if user roles have required permission"""
        for role in user_roles:
            permissions = self.get_role_permissions(role)
            if required_permission in permissions:
                return True
        return False
    
    def check_any_permission(
        self,
        user_roles: List[str],
        required_permissions: List[Permission]
    ) -> bool:
        """Check if user has any of the required permissions"""
        for permission in required_permissions:
            if self.check_permission(user_roles, permission):
                return True
        return False
    
    def check_all_permissions(
        self,
        user_roles: List[str],
        required_permissions: List[Permission]
    ) -> bool:
        """Check if user has all required permissions"""
        for permission in required_permissions:
            if not self.check_permission(user_roles, permission):
                return False
        return True
    
    def get_user_permissions(self, user_roles: List[str]) -> Set[Permission]:
        """Get all permissions for a user based on their roles"""
        permissions = set()
        for role in user_roles:
            permissions.update(self.get_role_permissions(role))
        return permissions
    
    def add_custom_role(
        self,
        name: str,
        description: str,
        permissions: List[Permission],
        inherits_from: Optional[List[str]] = None
    ):
        """Add a custom role"""
        self.roles[name] = RoleDefinition(
            name=name,
            description=description,
            permissions=set(permissions),
            inherits_from=inherits_from
        )
    
    def export_roles(self) -> Dict:
        """Export role definitions"""
        return {
            role_name: {
                "description": role_def.description,
                "permissions": [p.value for p in role_def.permissions],
                "inherits_from": role_def.inherits_from
            }
            for role_name, role_def in self.roles.items()
        }
    
    def import_roles(self, roles_data: Dict):
        """Import role definitions"""
        for role_name, role_info in roles_data.items():
            self.add_custom_role(
                name=role_name,
                description=role_info["description"],
                permissions=[Permission(p) for p in role_info["permissions"]],
                inherits_from=role_info.get("inherits_from")
            )


# Global RBAC manager instance
rbac_manager = RBACManager()


class RBACMiddleware:
    """FastAPI middleware for RBAC"""
    
    def __init__(self, rbac: RBACManager):
        self.rbac = rbac
    
    def require_permission(self, permission: Permission):
        """Decorator to require specific permission"""
        def decorator(func):
            async def wrapper(*args, **kwargs):
                # Extract user roles from request context
                current_user = kwargs.get("current_user")
                if not current_user:
                    raise PermissionError("Authentication required")
                
                user_roles = current_user.roles
                
                if not self.rbac.check_permission(user_roles, permission):
                    raise PermissionError(f"Missing permission: {permission.value}")
                
                return await func(*args, **kwargs)
            return wrapper
        return decorator
    
    def require_any_permission(self, *permissions: Permission):
        """Decorator to require any of the specified permissions"""
        def decorator(func):
            async def wrapper(*args, **kwargs):
                current_user = kwargs.get("current_user")
                if not current_user:
                    raise PermissionError("Authentication required")
                
                user_roles = current_user.roles
                
                if not self.rbac.check_any_permission(user_roles, list(permissions)):
                    raise PermissionError(
                        f"Missing any of permissions: {[p.value for p in permissions]}"
                    )
                
                return await func(*args, **kwargs)
            return wrapper
        return decorator
    
    def require_all_permissions(self, *permissions: Permission):
        """Decorator to require all specified permissions"""
        def decorator(func):
            async def wrapper(*args, **kwargs):
                current_user = kwargs.get("current_user")
                if not current_user:
                    raise PermissionError("Authentication required")
                
                user_roles = current_user.roles
                
                if not self.rbac.check_all_permissions(user_roles, list(permissions)):
                    raise PermissionError(
                        f"Missing all permissions: {[p.value for p in permissions]}"
                    )
                
                return await func(*args, **kwargs)
            return wrapper
        return decorator


# Create middleware instance
rbac_middleware = RBACMiddleware(rbac_manager)