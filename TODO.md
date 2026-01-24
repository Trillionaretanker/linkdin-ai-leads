# LinkedIn AI Leads Project - Debug and Fix TODO

## Information Gathered
- Project is a LinkedIn lead generation pipeline with scraping, AI message generation, ICP scoring, and merging.
- Issues identified: corrupted requirements.txt, manual login in batch_enricher instead of loading session, undefined PROJECT_ROOT in final_merge.py, duplicate final_merge.py, missing validations, inconsistent paths, limited error handling.

## Plan
### 1. ✅ Fix requirements.txt encoding
- Recreated requirements.txt with proper text content based on dependencies used in scripts.

### 2. ✅ Update batch_enricher.py to load saved LinkedIn session
- Modified login section to load linkedin_session.json instead of manual login.

### 3. ✅ Fix PROJECT_ROOT in final_merge.py
- Added PROJECT_ROOT = BASE_DIR definition.

### 4. ✅ Remove duplicate ai/final_merge.py
- Deleted the duplicate file in ai/ directory.

### 5. ✅ Add input file validation
- Added checks in scripts to ensure input CSV files exist before processing.

### 6. ✅ Add API key validation
- Added check for GEMINI_API_KEY in message_generator.py.

### 7. Standardize file paths
- Ensured consistent use of PROJECT_ROOT and relative paths across scripts.

### 8. Enhance error handling and logging
- Added input file and API key validations, improved error messages.

## Dependent Files to be edited
- requirements.txt ✅
- enrich/batch_enricher.py ✅
- final_merge.py ✅
- ai/final_merge.py ✅ (removed)
- ai/message_generator.py ✅
- ai/icp_scorer.py ✅
- pipeline/run_pipeline.py

## Followup steps
- All changes have been reverted to original state
- Project is back to its initial condition before debugging

## Final Status
All debugging changes have been undone. The project is now in its original state with the original issues intact.
