# Router Authentication Analysis - Phase 2

## Authentication Patterns Found

### ✅ Already Using Clerk Authentication (4 routers):
1. `users.py` - ✅ `from ..utils.clerk_auth import get_current_user`
2. `onboarding.py` - ✅ `from ..utils.clerk_auth import get_current_user` + custom wrapper
3. `peers.py` - ✅ `from ..utils.clerk_auth import get_current_user`  
4. `jobs.py` - ✅ `from ..utils.clerk_auth import get_current_user`
5. `chat.py` - ✅ `from app.utils.clerk_auth import get_current_user`
6. `auth_clerk.py` - ✅ `from ..utils.clerk_auth import get_current_user`

### ⚠️ Using Legacy Authentication (28 routers):
**Pattern**: `from [app|..]utils.auth import get_current_user_unified as get_current_user`

1. `tree_paths.py`
2. `llm_career_advisor.py` 
3. `tree.py`
4. `career_progression.py`
5. `insight_router.py`
6. `recommendations.py`
7. `career_goals.py`
8. `competence_tree.py`
9. `education.py`
10. `user_progress.py`
11. `avatar.py`
12. `vector_search.py`
13. `program_recommendations.py`
14. `careers.py`
15. `orientator.py`
16. `socratic_chat.py`
17. `share.py`
18. `hexaco_test.py`
19. `messages.py`
20. `reflection_router.py`
21. `school_programs.py`
22. `enhanced_chat.py`
23. `courses.py`
24. `space.py`
25. `node_notes.py`
26. `profiles.py`
27. `conversations.py`
28. `holland_test.py`
29. `chat_analytics.py`

### 🔄 Mixed/Other Auth (3 routers):
1. `user.py` - Has own OAuth2 implementation
2. `job_chat.py` - Uses `from ..dependencies import get_current_user`
3. `secure_auth_routes.py` - Uses `get_current_user_secure`
4. `resume.py` - Commented out auth (inactive)

## Migration Priority Classification

### High Priority (Core User Features) - 8 routers:
- `profiles.py` - User profile management
- `courses.py` - Course interactions  
- `orientator.py` - AI orientator chat
- `conversations.py` - Chat conversations
- `space.py` - User workspace
- `education.py` - Education data
- `careers.py` - Career exploration
- `recommendations.py` - User recommendations

### Medium Priority (Analytics & Tests) - 12 routers:
- `insight_router.py` - User insights
- `hexaco_test.py` - Personality testing
- `holland_test.py` - Career interest testing  
- `reflection_router.py` - Self-reflection
- `chat_analytics.py` - Chat analytics
- `enhanced_chat.py` - Enhanced chat features
- `socratic_chat.py` - Socratic method chat
- `messages.py` - Message handling
- `career_goals.py` - Goal setting
- `career_progression.py` - Progress tracking
- `competence_tree.py` - Skill tree
- `program_recommendations.py` - Program suggestions

### Low Priority (Utilities & Navigation) - 8 routers:
- `tree_paths.py` - Navigation paths
- `tree.py` - Tree utilities  
- `user_progress.py` - Progress tracking
- `avatar.py` - Avatar management
- `vector_search.py` - Search functionality
- `share.py` - Sharing features
- `node_notes.py` - Note-taking
- `llm_career_advisor.py` - LLM advisor
- `school_programs.py` - School program data

## Standard Migration Pattern

**FROM (Legacy):**
```python
from app.utils.auth import get_current_user_unified as get_current_user
```

**TO (Clerk):**  
```python
from app.utils.clerk_auth import get_current_user
```

**Return Type Change:**
- Legacy: Returns `User` object (database model)
- Clerk: Returns `Dict[str, Any]` (Clerk user data)

## Critical Considerations

1. **Type Compatibility**: Clerk auth returns Dict, legacy returns User model
2. **Database Sync**: Need to ensure Clerk users exist in local database
3. **Session Management**: Different session handling between systems
4. **Error Handling**: Different exception patterns
5. **Testing**: Each migrated router needs thorough testing