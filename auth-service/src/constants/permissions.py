from typing import Dict, Any
from enum import IntEnum


class RolePermissions(IntEnum):
    """Битовые флаги прав доступа для ролей"""

    CREATE_ROLES = 1 << 0    # 1  - Создавать новые роли
    EDIT_ROLES = 1 << 1      # 2  - Редактировать существующие роли
    ASSIGN_ROLES = 1 << 2    # 4  - Назначать роли пользователям

    DELETE_ROLES = 1 << 3    # 8  - Удалять роли
    VIEW_PERMISSIONS = 1 << 4 # 16 - Просматривать права ролей
    MANAGE_PERMISSIONS = 1 << 5 # 32 - Управлять правами
    
    @classmethod
    def get_basic_permissions(cls) -> int:
        """Получить базовые права (создание, редактирование, назначение)"""
        return cls.CREATE_ROLES | cls.EDIT_ROLES | cls.ASSIGN_ROLES
    
    @classmethod
    def get_all_permissions(cls) -> int:
        """Получить все доступные права"""
        return (
            cls.CREATE_ROLES | 
            cls.EDIT_ROLES | 
            cls.ASSIGN_ROLES | 
            cls.DELETE_ROLES | 
            cls.VIEW_PERMISSIONS | 
            cls.MANAGE_PERMISSIONS
        )
    
    @classmethod
    def get_permission_names(cls) -> Dict[int, str]:
        """Получить словарь {бит: название_права}"""
        return {
            cls.CREATE_ROLES: "create_roles",
            cls.EDIT_ROLES: "edit_roles", 
            cls.ASSIGN_ROLES: "assign_roles",
            cls.DELETE_ROLES: "delete_roles",
            cls.VIEW_PERMISSIONS: "view_permissions",
            cls.MANAGE_PERMISSIONS: "manage_permissions"
        }
    
    @classmethod
    def get_permissions_list(cls, permissions_int: int) -> list[str]:
        """Преобразовать битовую маску в список названий прав"""
        permission_names = cls.get_permission_names()
        active_permissions = []
        
        for permission_bit, permission_name in permission_names.items():
            if permissions_int & permission_bit:
                active_permissions.append(permission_name)
        
        return active_permissions
    
    @classmethod
    def has_permission(cls, permissions_int: int, required_permission: int) -> bool:
        """Проверить есть ли право в битовой маске"""
        return bool(permissions_int & required_permission)


class RolePriority:
    """Константы приоритетов ролей"""
    
    # Чем выше число, тем выше роль в иерархии
    USER = 1          # Обычный пользователь
    SUBSCRIBER = 2    # Подписчик (платный)
    ADMIN = 5         # Администратор
    SUPERUSER = 10    # Суперпользователь
    
    @classmethod
    def get_priority_map(cls) -> Dict[str, int]:
        """Получить словарь {название_роли: приоритет}"""
        return {
            "user": cls.USER,
            "subscriber": cls.SUBSCRIBER,
            "admin": cls.ADMIN,
            "superuser": cls.SUPERUSER
        }
    
    @classmethod
    def can_assign_role(cls, assigner_priority: int, target_priority: int) -> bool:
        """Проверить может ли роль с приоритетом assigner_priority назначить роль с target_priority"""
        return assigner_priority >= target_priority


class InitialRoles:
    """Начальные данные для ролей системы"""
    
    @classmethod
    def get_roles_data(cls) -> list[Dict[str, Any]]:
        """Получить список начальных ролей"""
        return [
            {
                "name": "user",
                "description": "Обычный пользователь",
                "permissions": 0,
                "priority": RolePriority.USER
            },
            {
                "name": "subscriber", 
                "description": "Подписчик с доступом к премиум функциям",
                "permissions": 0,
                "priority": RolePriority.SUBSCRIBER
            },
            
            {
                "name": "admin",
                "description": "Администратор - полное управление ролями и пользователями",
                "permissions": RolePermissions.EDIT_ROLES | RolePermissions.ASSIGN_ROLES | RolePermissions.VIEW_PERMISSIONS,
                "priority": RolePriority.ADMIN
            },
            {
                "name": "superuser",
                "description": "Суперпользователь - полный доступ ко всем функциям",
                "permissions": RolePermissions.get_all_permissions(),
                "priority": RolePriority.SUPERUSER
            }
        ]