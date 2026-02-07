from typing import List, Optional
import logging
from datetime import datetime

from app.core.supabase_client import get_supabase_client
from app.schemas.child import ChildCreate, ChildUpdate, ChildResponse
from app.core.config import settings

logger = logging.getLogger(__name__)


class ChildService:
    """Service for child management operations"""
    
    def __init__(self):
        self.supabase = get_supabase_client()
    
    async def create_child(self, child_data: ChildCreate, parent_id: str) -> ChildResponse:
        """
        Create a new child profile
        """
        try:
            # Check max children limit
            existing = self.supabase.table("children")\
                .select("id")\
                .eq("parent_id", parent_id)\
                .execute()
            
            if len(existing.data) >= settings.MAX_CHILDREN_PER_PARENT:
                raise ValueError(f"Maximum {settings.MAX_CHILDREN_PER_PARENT} children per account")
            
            # Validate age
            if child_data.age < settings.MIN_CHILD_AGE or child_data.age > settings.MAX_CHILD_AGE:
                raise ValueError(f"Age must be between {settings.MIN_CHILD_AGE} and {settings.MAX_CHILD_AGE}")
            
            # Create child record
            now = datetime.utcnow().isoformat()
            child_record = {
                "name": child_data.name,
                "age": child_data.age,
                "avatar": child_data.avatar,
                "parent_id": parent_id,
                "current_level": 1,
                "total_points": 0,
                "created_at": now,
                "updated_at": now
            }
            
            response = self.supabase.table("children").insert(child_record).execute()
            
            if not response.data:
                raise ValueError("Failed to create child")
            
            created_child = response.data[0]
            logger.info(f"Child created: {created_child['id']} for parent {parent_id}")
            
            return ChildResponse(**created_child)
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Create child failed: {str(e)}")
            raise
    
    async def get_children_by_parent(
        self,
        parent_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[ChildResponse]:
        """
        Get all children for a parent
        """
        try:
            response = self.supabase.table("children")\
                .select("*")\
                .eq("parent_id", parent_id)\
                .range(skip, skip + limit - 1)\
                .execute()
            
            return [ChildResponse(**child) for child in response.data]
            
        except Exception as e:
            logger.error(f"Get children failed: {str(e)}")
            raise
    
    async def get_child_by_id(self, child_id: str, parent_id: str) -> Optional[ChildResponse]:
        """
        Get a specific child by ID
        """
        try:
            response = self.supabase.table("children")\
                .select("*")\
                .eq("id", child_id)\
                .eq("parent_id", parent_id)\
                .single()\
                .execute()
            
            if response.data:
                return ChildResponse(**response.data)
            return None
            
        except Exception as e:
            logger.error(f"Get child failed: {str(e)}")
            return None
    
    async def update_child(
        self,
        child_id: str,
        child_data: ChildUpdate,
        parent_id: str
    ) -> Optional[ChildResponse]:
        """
        Update child profile
        """
        try:
            # Verify ownership
            existing = await self.get_child_by_id(child_id, parent_id)
            if not existing:
                return None
            
            # Build update data
            update_data = {}
            if child_data.name is not None:
                update_data["name"] = child_data.name
            if child_data.age is not None:
                if child_data.age < settings.MIN_CHILD_AGE or child_data.age > settings.MAX_CHILD_AGE:
                    raise ValueError(f"Age must be between {settings.MIN_CHILD_AGE} and {settings.MAX_CHILD_AGE}")
                update_data["age"] = child_data.age
            if child_data.avatar is not None:
                update_data["avatar"] = child_data.avatar
            
            update_data["updated_at"] = datetime.utcnow().isoformat()
            
            response = self.supabase.table("children")\
                .update(update_data)\
                .eq("id", child_id)\
                .eq("parent_id", parent_id)\
                .execute()
            
            if response.data:
                logger.info(f"Child updated: {child_id}")
                return ChildResponse(**response.data[0])
            return None
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Update child failed: {str(e)}")
            raise
    
    async def delete_child(self, child_id: str, parent_id: str) -> bool:
        """
        Delete child profile
        """
        try:
            response = self.supabase.table("children")\
                .delete()\
                .eq("id", child_id)\
                .eq("parent_id", parent_id)\
                .execute()
            
            if response.data:
                logger.info(f"Child deleted: {child_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Delete child failed: {str(e)}")
            raise