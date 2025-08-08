# 🚨 Critical Tables Priority List - Emergency Remediation Order

Based on the comprehensive audit and impact analysis, here is the prioritized order for fixing database tables, focusing on user-blocking issues first.

## 🔴 TIER 1: IMMEDIATE HOTFIX REQUIRED (0-4 hours)

These tables are causing **confirmed user-blocking failures** and must be fixed immediately.

### 1. `user_skills` - **CRITICAL USER BLOCKER**
- **Status**: 🚫 CONFIRMED BROKEN
- **Impact**: Skills assessment completely fails  
- **User Journey**: Onboarding process stops at skills evaluation
- **Priority**: #1 - Fix immediately
- **Model File**: `backend/app/models/user_skill.py`

### 2. `career_goals` - **CRITICAL USER BLOCKER**
- **Status**: 🚫 CONFIRMED BROKEN  
- **Impact**: Users cannot set or save career goals
- **User Journey**: Goal setting feature completely non-functional
- **Priority**: #2 - Fix immediately
- **Model File**: `backend/app/models/career_goal.py`

## 🟡 TIER 2: HIGH-RISK CORE FEATURES (4-12 hours)

These tables support core functionality that users heavily rely on.

### 3. `chat_messages` - **HIGH-RISK CORE FEATURE**
- **Status**: ⚠️ LIKELY BROKEN (not confirmed)
- **Impact**: New messages may fail to send
- **User Journey**: Chat system becomes unreliable  
- **Priority**: #3 - Test and fix within hours
- **Model File**: `backend/app/models/chat_message.py`

### 4. `users` - **FOUNDATION TABLE**
- **Status**: 🤔 UNCLEAR (worked in test but missing autoincrement)
- **Impact**: New user registration may fail
- **User Journey**: Account creation becomes unreliable
- **Priority**: #4 - Investigate and fix proactively
- **Model File**: `backend/app/models/user.py`

### 5. `courses` - **ACADEMIC TRACKING**
- **Status**: ⚠️ LIKELY BROKEN
- **Impact**: Course enrollment and academic tracking fails
- **User Journey**: Academic progress tracking non-functional
- **Priority**: #5 - Educational features broken
- **Model File**: `backend/app/models/course.py`

### 6. `user_profiles` - **USER DATA**
- **Status**: ⚠️ LIKELY BROKEN
- **Impact**: Profile updates and creation may fail  
- **User Journey**: User personalization broken
- **Priority**: #6 - User experience degradation
- **Model File**: `backend/app/models/user_profile.py`

## 🟡 TIER 3: IMPORTANT SECONDARY FEATURES (12-24 hours)

These tables affect important but non-critical user functionality.

### 7. `saved_recommendations` - **RECOMMENDATION ENGINE**
- **Impact**: Cannot save job recommendations
- **Model File**: `backend/app/models/saved_recommendation.py`

### 8. `conversation_categories` - **CHAT ORGANIZATION**
- **Impact**: Chat categorization and organization fails
- **Model File**: `backend/app/models/conversation_category.py`

### 9. `user_chat_analytics` - **USAGE TRACKING**
- **Impact**: Chat analytics and insights collection fails
- **Model File**: `backend/app/models/user_chat_analytics.py`

### 10. `node_notes` - **INTERACTIVE LEARNING**
- **Impact**: Note-taking in interactive tree fails
- **Model File**: `backend/app/models/node_note.py`

### 11. `user_notes` - **PERSONAL NOTES**
- **Impact**: User personal notes cannot be saved
- **Model File**: `backend/app/models/user_note.py`

## 🟢 TIER 4: SUPPORTING FEATURES (24-48 hours)

These tables support less critical functionality but need fixing for completeness.

### Remaining 18 Tables:
- `career_milestones` - Progress tracking
- `psychological_insights` - AI insights
- `career_signals` - Career intelligence  
- `conversation_logs` - Detailed logging
- `tool_invocations` - AI tool usage tracking
- `user_journey_milestones` - Journey progress
- `message_components` - Rich message features
- `user_representations` - Vector embeddings
- `conversation_shares` - Social sharing
- `reflections` - Self-assessment
- `user_skill_tree` - Skill tree visualization
- And 7 more supporting tables...

## ✅ CONFIRMED WORKING TABLES

These tables are correctly implemented and don't need immediate fixes:

### 1. `conversations` ✅
- **Model File**: `backend/app/models/conversation.py`
- **Status**: Has `autoincrement=True` - correctly implemented

### 2. `personality_profiles` ✅  
- **Model File**: `backend/app/models/personality_profiles.py`
- **Status**: Has `autoincrement=True` - correctly implemented

## 🔄 SPECIAL CASES (Review Required)

### 1. `tree_path` - Non-Integer Primary Key
- Uses UUID primary key - different pattern, may be working
- **Model File**: `backend/app/models/tree_path.py`

### 2. `user_progress` - Non-Integer Primary Key  
- Uses UUID primary key - different pattern, may be working
- **Model File**: `backend/app/models/user_progress.py`

### 3. `message` - Custom Sequence
- Uses custom sequence pattern - may be working
- **Model File**: `backend/app/models/message.py`

## Remediation Strategy

### Phase 1: Emergency Hotfix (Immediate)
Fix Tier 1 tables (`user_skills`, `career_goals`) to restore critical user functionality.

### Phase 2: Core Feature Stabilization (4-12 hours)  
Fix Tier 2 tables to ensure core platform reliability.

### Phase 3: Complete Remediation (12-48 hours)
Fix all remaining Tier 3 and Tier 4 tables systematically.

### Phase 4: Architecture Improvements (48+ hours)
Implement base model class, migration standards, and comprehensive testing.

---

**Next Action**: Begin Phase 1 emergency hotfix with `user_skills` table.