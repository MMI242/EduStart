from typing import List, Optional, Dict, Any
import logging

from app.core.supabase_client import get_supabase_client
from app.schemas.module import ModuleResponse, ModuleDetail, Question, ModuleDownload

logger = logging.getLogger(__name__)


class ModuleService:
    """Service for learning module operations"""
    
    def __init__(self):
        self.supabase = get_supabase_client()
    
    async def get_modules(
        self,
        module_type: Optional[str] = None,
        difficulty_level: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[ModuleResponse]:
        """
        Get all modules with optional filters
        """
        try:
            query = self.supabase.table("modules").select("*")
            
            if module_type:
                query = query.eq("module_type", module_type)
            if difficulty_level:
                query = query.eq("difficulty_level", difficulty_level)
            
            response = query.range(skip, skip + limit - 1).execute()
            
            # Map database fields to response schema
            modules = []
            for module in response.data:
                modules.append(ModuleResponse(
                    id=module["id"],
                    title=module["title"],
                    description=module.get("description", ""),
                    type=module["module_type"],
                    difficulty_level=module["difficulty_level"],
                    estimated_duration_minutes=module.get("estimated_duration_minutes", 10),
                    thumbnail_url=module.get("thumbnail_url"),
                    total_questions=len(module.get("content", {}).get("questions", [])) if module.get("content") else 0,
                    points_reward=module["difficulty_level"] * 10
                ))
            
            return modules
            
        except Exception as e:
            logger.error(f"Get modules failed: {str(e)}")
            raise
    
    async def get_module_by_id(self, module_id: str) -> Optional[ModuleDetail]:
        """
        Get detailed module information including questions from content field
        """
        try:
            # Get module
            module_response = self.supabase.table("modules")\
                .select("*")\
                .eq("id", module_id)\
                .single()\
                .execute()
            
            if not module_response.data:
                logger.warning(f"Module not found: {module_id}")
                return None
            
            module_data = module_response.data
            logger.info(f"Module data keys: {module_data.keys()}")
            logger.info(f"Content field: {module_data.get('content')}")
            
            content = module_data.get("content", {}) or {}
            
            # Extract questions from content JSONB field
            questions_data = content.get("questions", [])
            logger.info(f"Found {len(questions_data)} questions")
            questions = [Question(**q) for q in questions_data]
            
            # Extract learning objectives
            learning_objectives = content.get("learning_objectives", [])
            
            return ModuleDetail(
                id=module_data["id"],
                title=module_data["title"],
                description=module_data.get("description", ""),
                type=module_data["module_type"],
                difficulty_level=module_data["difficulty_level"],
                estimated_duration_minutes=module_data.get("estimated_duration_minutes", 10),
                thumbnail_url=module_data.get("thumbnail_url"),
                total_questions=len(questions),
                points_reward=module_data["difficulty_level"] * 10,
                questions=questions,
                learning_objectives=learning_objectives,
                created_at=module_data["created_at"],
                updated_at=module_data.get("created_at")  # Use created_at if no updated_at
            )
            
        except Exception as e:
            logger.error(f"Get module detail failed: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    async def prepare_module_download(self, module_id: str) -> Optional[ModuleDownload]:
        """
        Prepare module data for offline download
        """
        try:
            module = await self.get_module_by_id(module_id)
            if not module:
                return None
            
            # Calculate size (rough estimate)
            size_mb = len(str(module.dict())) / (1024 * 1024)
            
            return ModuleDownload(
                module_id=module_id,
                offline_data=module.dict(),
                size_mb=round(size_mb, 2),
                version="1.0"
            )
            
        except Exception as e:
            logger.error(f"Prepare module download failed: {str(e)}")
            return None
    
    async def get_module_types(self) -> List[str]:
        """
        Get list of all module types
        """
        try:
            response = self.supabase.table("modules")\
                .select("module_type")\
                .execute()
            
            types = list(set([m["module_type"] for m in response.data]))
            return sorted(types)
            
            
        except Exception as e:
            logger.error(f"Get module types failed: {str(e)}")
            return []
            
    async def create_module(self, data: Dict[str, Any]) -> Optional[ModuleResponse]:
        """
        Create a new learning module
        """
        try:
            # Prepare module data - map schema to db columns
            module_data = {
                "title": data["title"],
                "description": data["description"],
                "module_type": data["module_type"],
                "difficulty_level": data["difficulty_level"],
                "estimated_duration_minutes": data["estimated_duration_minutes"],
                "thumbnail_url": data.get("thumbnail_url"),
                "is_premium": data.get("is_premium", False),
                "content": data["content"]
            }
            
            response = self.supabase.table("modules")\
                .insert(module_data)\
                .execute()
                
            if not response.data:
                return None
                
            new_module = response.data[0]
            
            return ModuleResponse(
                id=new_module["id"],
                title=new_module["title"],
                description=new_module.get("description", ""),
                type=new_module["module_type"],
                difficulty_level=new_module["difficulty_level"],
                estimated_duration_minutes=new_module.get("estimated_duration_minutes", 10),
                thumbnail_url=new_module.get("thumbnail_url"),
                total_questions=len(new_module.get("content", {}).get("questions", [])),
                points_reward=new_module["difficulty_level"] * 10
            )
            
        except Exception as e:
            logger.error(f"Create module failed: {str(e)}")
            raise

    async def update_module(self, module_id: str, data: Dict[str, Any]) -> Optional[ModuleResponse]:
        """
        Update an existing module
        """
        try:
            # Filter out None values
            update_data = {k: v for k, v in data.items() if v is not None}
            if not update_data:
                return None
                
            response = self.supabase.table("modules")\
                .update(update_data)\
                .eq("id", module_id)\
                .execute()
                
            if not response.data:
                return None
                
            updated = response.data[0]
            
            return ModuleResponse(
                id=updated["id"],
                title=updated["title"],
                description=updated.get("description", ""),
                type=updated["module_type"],
                difficulty_level=updated["difficulty_level"],
                estimated_duration_minutes=updated.get("estimated_duration_minutes", 10),
                thumbnail_url=updated.get("thumbnail_url"),
                total_questions=len(updated.get("content", {}).get("questions", [])),
                points_reward=updated["difficulty_level"] * 10
            )
            
        except Exception as e:
            logger.error(f"Update module failed: {str(e)}")
            raise

    async def delete_module(self, module_id: str) -> bool:
        """
        Delete a module
        """
        try:
            response = self.supabase.table("modules")\
                .delete()\
                .eq("id", module_id)\
                .execute()
                
            # Check if any row was deleted (response.data should not be empty)
            return len(response.data) > 0
            
        except Exception as e:
            logger.error(f"Delete module failed: {str(e)}")
            raise