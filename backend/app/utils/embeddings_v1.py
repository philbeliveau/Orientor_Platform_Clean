# import logging
# import os
# import joblib
# import pickle
# import numpy as np
# from sqlalchemy import text
# from sqlalchemy.orm import Session
# from ..models import User, UserProfile, SuggestedPeers
# from typing import List, Dict, Any, Optional
# import time
# import pandas as pd
# import pinecone
# import json
# from sklearn.metrics.pairwise import cosine_similarity

# # Configure logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# # Define paths to the fine-tuned models
# MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), 
#                          "data_n_notebook", "siamese_pipeline", "mlruns", "models")
# PCA_MODEL_PATH = os.path.join(MODELS_DIR, "pca384_Siamese.pkl")
# SCALER_MODEL_PATH = os.path.join(MODELS_DIR, "scaler_Siamese.pkl")
# OHE_MODEL_PATH = os.path.join(MODELS_DIR, "ohe_Siamese.pkl")
# FINETUNED_MODEL_DIR = os.path.join(MODELS_DIR, "finetuned_model")

# try:
#     from sentence_transformers import SentenceTransformer
#     SENTENCE_TRANSFORMERS_AVAILABLE = True
# except ImportError:
#     logger.warning("sentence_transformers not available. Install with: pip install sentence-transformers")
#     SENTENCE_TRANSFORMERS_AVAILABLE = False

# # Model configuration
# DEFAULT_MODEL_NAME = 'sentence-transformers/all-MiniLM-L6-v2'

# def load_processing_models():
#     """Load the preprocessing models (scaler, one-hot encoder, PCA)"""
#     try:
#         print(f"Current working directory: {os.getcwd()}")
#         print(f"MODELS_DIR: {MODELS_DIR}")
#         print(f"PCA_MODEL_PATH: {PCA_MODEL_PATH}")
#         print(f"SCALER_MODEL_PATH: {SCALER_MODEL_PATH}")
#         print(f"OHE_MODEL_PATH: {OHE_MODEL_PATH}")
        
#         print(f"Does PCA model exist? {os.path.exists(PCA_MODEL_PATH)}")
#         print(f"Does Scaler model exist? {os.path.exists(SCALER_MODEL_PATH)}")
#         print(f"Does OHE model exist? {os.path.exists(OHE_MODEL_PATH)}")
        
#         if not os.path.exists(PCA_MODEL_PATH):
#             print(f"PCA model not found at: {PCA_MODEL_PATH}")
#             raise FileNotFoundError(f"PCA model not found at: {PCA_MODEL_PATH}")
#         if not os.path.exists(SCALER_MODEL_PATH):
#             print(f"Scaler model not found at: {SCALER_MODEL_PATH}")
#             raise FileNotFoundError(f"Scaler model not found at: {SCALER_MODEL_PATH}")
#         if not os.path.exists(OHE_MODEL_PATH):
#             print(f"OHE model not found at: {OHE_MODEL_PATH}")
#             raise FileNotFoundError(f"OHE model not found at: {OHE_MODEL_PATH}")
            
#         scaler = joblib.load(SCALER_MODEL_PATH)
#         print("Successfully loaded scaler model")
        
#         ohe = joblib.load(OHE_MODEL_PATH)
#         print("Successfully loaded OHE model")
        
#         pca = joblib.load(PCA_MODEL_PATH)
#         print("Successfully loaded PCA model")
        
#         print("Successfully loaded all preprocessing models")
#         return scaler, ohe, pca
#     except Exception as e:
#         print(f"Error loading preprocessing models: {str(e)}")
#         raise

# def get_embedding_model(use_finetuned: bool = True) -> Any:
#     """Load and return the embedding model."""
#     if not SENTENCE_TRANSFORMERS_AVAILABLE:
#         raise ImportError("sentence_transformers is required. Install with: pip install sentence-transformers")
    
#     if use_finetuned and os.path.exists(FINETUNED_MODEL_DIR):
#         logger.info(f"Loading fine-tuned embedding model from: {FINETUNED_MODEL_DIR}")
#         return SentenceTransformer(FINETUNED_MODEL_DIR)
#     else:
#         logger.info(f"Loading default embedding model: {DEFAULT_MODEL_NAME}")
#         return SentenceTransformer(DEFAULT_MODEL_NAME)

# def create_structured_features(profile: UserProfile) -> pd.DataFrame:
#     """Convert profile to structured features for the model pipeline"""
#     # Create a dictionary with the structured profile data
#     data = {
#         'gpa': [profile.gpa if profile.gpa else 0.0],
#         'age': [profile.age if profile.age else 0],
#         'year': [profile.year if profile.year else 0],
#         'sex': [profile.sex if profile.sex else "Unknown"],
#         'major': [profile.major if profile.major else "Unknown"],
#         'country': [profile.country if profile.country else "Unknown"],
#         'state_province': [profile.state_province if profile.state_province else "Unknown"],
#         'learning_style': [profile.learning_style if profile.learning_style else "Unknown"]
#     }
    
#     # Create DataFrame
#     return pd.DataFrame(data)

# def process_structured_features(df: pd.DataFrame, scaler, ohe, pca):
#     """Process structured features through the trained preprocessing pipeline"""
#     try:
#         # Handle categorical features with one-hot encoding
#         categorical_cols = ['sex', 'major', 'country', 'state_province', 'learning_style']
#         numerical_cols = ['gpa', 'age', 'year']
        
#         # Fill NaN values
#         for col in categorical_cols:
#             df[col] = df[col].fillna("Unknown")
#         for col in numerical_cols:
#             df[col] = df[col].fillna(0)
        
#         # Apply one-hot encoding to categorical features
#         categorical_features = pd.DataFrame(ohe.transform(df[categorical_cols]).toarray())
        
#         # Scale numerical features
#         numerical_features = pd.DataFrame(scaler.transform(df[numerical_cols]), 
#                                          columns=numerical_cols)
        
#         # Combine features
#         combined_features = pd.concat([numerical_features, categorical_features], axis=1)
        
#         # Apply PCA
#         pca_features = pca.transform(combined_features)
        
#         return pca_features
#     except Exception as e:
#         logger.error(f"Error processing structured features: {str(e)}")
#         raise

# def create_text_features(profile: UserProfile) -> str:
#     """Create a text representation of a user profile for embedding."""
#     parts = []
    
#     if profile.name:
#         parts.append(f"Name: {profile.name}")
#     if profile.major:
#         parts.append(f"Major: {profile.major}")
#     if profile.hobbies:
#         parts.append(f"Hobbies: {profile.hobbies}")
#     if profile.interests:
#         parts.append(f"interests: {profile.interests}")
#     if profile.unique_quality:
#         parts.append(f"Unique Quality: {profile.unique_quality}")
#     if profile.story:
#         parts.append(f"Story: {profile.story}")
#     if profile.favorite_movie:
#         parts.append(f"Favorite Movie: {profile.favorite_movie}")
#     if profile.favorite_book:
#         parts.append(f"Favorite Book: {profile.favorite_book}")
#     if profile.favorite_celebrities:
#         parts.append(f"Favorite Celebrities: {profile.favorite_celebrities}")
    
#     return "\n".join(parts)

# def generate_embedding_for_profile(profile: UserProfile) -> List[float]:
#     """Generate embedding for a single user profile using the fine-tuned model and preprocessing."""
#     try:
#         # Load models
#         scaler, ohe, pca = load_processing_models()
#         model = get_embedding_model(use_finetuned=True)
        
#         # Process structured features
#         structured_df = create_structured_features(profile)
#         structured_features = process_structured_features(structured_df, scaler, ohe, pca)
        
#         # Process text features
#         text_features = create_text_features(profile)
#         text_embedding = model.encode(text_features)
        
#         # Combine structured and text features
#         # Since the PCA output is already 384 dimensions, we just return it
#         # In a more complex scenario, you might want to combine the vectors differently
#         return structured_features[0].tolist()
#     except Exception as e:
#         logger.error(f"Error generating embedding for profile {profile.id}: {str(e)}")
#         raise

# def generate_and_store_embeddings(db: Session) -> int:
#     """
#     Generate embeddings for users and store them as pickle files.
#     Returns the count of profiles processed.
#     """
#     if not SENTENCE_TRANSFORMERS_AVAILABLE:
#         logger.error("sentence_transformers not available. Cannot generate embeddings.")
#         return 0
    
#     try:
#         # Fetch all profiles
#         profiles = db.query(UserProfile).all()
        
#         if not profiles:
#             logger.info("No profiles found.")
#             return 0
        
#         logger.info(f"Generating embeddings for {len(profiles)} profiles...")
#         count = 0
        
#         for profile in profiles:
#             try:
#                 # Generate embedding
#                 embedding_vector = generate_embedding_for_profile(profile)
                
#                 # Store embedding as pickle file
#                 embedding_path = os.path.join(MODELS_DIR, f"user_{profile.user_id}_embedding.pkl")
#                 with open(embedding_path, 'wb') as f:
#                     pickle.dump(embedding_vector, f)
                
#                 count += 1
                
#                 # Log progress periodically
#                 if count % 10 == 0:
#                     logger.info(f"Processed {count}/{len(profiles)} profiles...")
#             except Exception as e:
#                 logger.error(f"Error processing profile {profile.id}: {str(e)}")
#                 continue
        
#         logger.info(f"Successfully generated embeddings for {count} profiles.")
#         return count
        
#     except Exception as e:
#         logger.error(f"Error generating embeddings: {str(e)}")
#         raise

# def find_and_store_similar_peers(db: Session, batch_size: int = 100, top_n: int = 5) -> int:
#     """
#     Find similar peers for each user and store them in the suggested_peers table.
#     Returns the count of users processed.
#     """
#     try:
#         # Get all users
#         profiles = db.query(UserProfile).all()
        
#         if not profiles:
#             logger.info("No users found.")
#             return 0
        
#         logger.info(f"Finding similar peers for {len(profiles)} users...")
#         total_processed = 0
        
#         # Process in batches to avoid memory issues
#         for i in range(0, len(profiles), batch_size):
#             batch = profiles[i:i+batch_size]
            
#             for profile in batch:
#                 try:
#                     # Generate embedding for this profile
#                     profile_data = {
#                         "job_title": profile.job_title,
#                         "industry": profile.industry,
#                         "years_experience": profile.years_experience,
#                         "education_level": profile.education_level,
#                         "career_goals": profile.career_goals,
#                         "skills": profile.skills if profile.skills else [],
#                         "interests": profile.interests if profile.interests else []
#                     }
                    
#                     embedding = generate_embedding_for_profile(profile)
#                     if embedding is None:
#                         continue
                    
#                     # Find similar users
#                     similar_users = []
#                     for other_profile in profiles:
#                         if other_profile.user_id == profile.user_id:
#                             continue
                            
#                         other_data = {
#                             "job_title": other_profile.job_title,
#                             "industry": other_profile.industry,
#                             "years_experience": other_profile.years_experience,
#                             "education_level": other_profile.education_level,
#                             "career_goals": other_profile.career_goals,
#                             "skills": other_profile.skills if other_profile.skills else [],
#                             "interests": other_profile.interests if other_profile.interests else []
#                         }
                        
#                         other_embedding = generate_embedding_for_profile(other_profile)
#                         if other_embedding is not None:
#                             similarity = cosine_similarity(embedding, other_embedding)
#                             similar_users.append((other_profile.user_id, similarity))
                    
#                     # Sort by similarity and get top N
#                     similar_users.sort(key=lambda x: x[1], reverse=True)
#                     similar_users = similar_users[:top_n]
                    
#                     # Store results
#                     for peer_id, similarity in similar_users:
#                         db.execute(
#                             text("""
#                                 INSERT INTO suggested_peers (user_id, suggested_id, similarity)
#                                 VALUES (:user_id, :suggested_id, :similarity)
#                                 ON CONFLICT (user_id, suggested_id) 
#                                 DO UPDATE SET similarity = :similarity, updated_at = NOW()
#                             """),
#                             {"user_id": profile.user_id, "suggested_id": peer_id, "similarity": similarity}
#                         )
                    
#                     total_processed += 1
#                 except Exception as e:
#                     logger.error(f"Error processing user {profile.user_id}: {str(e)}")
#                     continue
            
#             # Commit after each batch
#             db.commit()
#             logger.info(f"Processed {total_processed}/{len(profiles)} users...")
        
#         logger.info(f"Successfully found similar peers for {total_processed} users.")
#         return total_processed
        
#     except Exception as e:
#         db.rollback()
#         logger.error(f"Error finding similar peers: {str(e)}")
#         raise

# def recommend_careers_for_user(user_id: int, db: Session, top_k: int = 5) -> List[Dict]:
#     """
#     Recommend careers for a user based on their embedding.
#     Returns a list of recommended careers.
#     """
#     try:
#         # Get user profile
#         profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
#         if not profile:
#             logger.error(f"No profile found for user {user_id}")
#             return []
        
#         # Get embedding for the user
#         embedding_query = db.execute(
#             text("SELECT embedding FROM user_profiles WHERE user_id = :user_id"),
#             {"user_id": user_id}
#         ).fetchone()
        
#         if not embedding_query or not embedding_query[0]:
#             # If embedding doesn't exist, generate it
#             logger.info(f"No embedding found for user {user_id}, generating one...")
#             generate_and_store_embeddings(db)
            
#             # Try again
#             embedding_query = db.execute(
#                 text("SELECT embedding FROM user_profiles WHERE user_id = :user_id"),
#                 {"user_id": user_id}
#             ).fetchone()
            
#             if not embedding_query or not embedding_query[0]:
#                 logger.error(f"Failed to generate embedding for user {user_id}")
#                 return []
        
#         embedding = embedding_query[0]
        
#         # Initialize Pinecone
#         pinecone_api_key = os.getenv("PINECONE_API_KEY")
#         pinecone_environment = os.getenv("PINECONE_ENVIRONMENT")
        
#         if not pinecone_api_key or not pinecone_environment:
#             logger.error("Pinecone API key or environment not set")
#             return []
        
#         try:
#             pinecone.init(api_key=pinecone_api_key, environment=pinecone_environment)
#             index = pinecone.Index("oasis-minilm-index")
            
#             # Query Pinecone
#             query_results = index.query(
#                 namespace="",
#                 vector=embedding,
#                 top_k=top_k,
#                 include_metadata=True
#             )
            
#             # Extract results
#             results = []
#             for match in query_results['matches']:
#                 oasis_code = match['id'].split('-')[1] if '-' in match['id'] else ""
#                 metadata = match.get('metadata', {})
                
#                 # Parse text for additional fields
#                 text = metadata.get('text', '')
#                 parsed_fields = {}
                
#                 # Reuse the extract_fields_from_text function from vector_search.py
#                 # For simplicity, we'll parse some common fields
#                 import re
                
#                 # Extract field-value pairs
#                 field_pattern = re.compile(r'([\w\s\-:]+):\s+([^.:|]+(?:\|[^.:]+)*)')
#                 matches = field_pattern.findall(text)
                
#                 for key, value in matches:
#                     key_clean = (
#                         key.strip()
#                         .replace(" ", "_")
#                         .replace("-", "_")
#                         .replace("__", "_")
#                         .lower()
#                     )
#                     parsed_fields[key_clean] = value.strip()
                
#                 # Create result object
#                 result = {
#                     "id": match['id'],
#                     "score": match['score'],
#                     "oasis_code": oasis_code,
#                     "label": parsed_fields.get("oasis_label__final_x") or parsed_fields.get("label") or "",
#                     "lead_statement": parsed_fields.get("lead_statement", ""),
#                     "main_duties": parsed_fields.get("main_duties", ""),
#                     "creativity": parsed_fields.get("creativity"),
#                     "leadership": parsed_fields.get("leadership"),
#                     "digital_literacy": parsed_fields.get("digital_literacy"),
#                     "critical_thinking": parsed_fields.get("critical_thinking"),
#                     "problem_solving": parsed_fields.get("problem_solving"),
#                     "stress_tolerance": parsed_fields.get("stress_tolerance"),
#                     "analytical_thinking": parsed_fields.get("analytical_thinking"),
#                     "attention_to_detail": parsed_fields.get("attention_to_detail"),
#                     "collaboration": parsed_fields.get("collaboration"),
#                     "adaptability": parsed_fields.get("adaptability"),
#                     "independence": parsed_fields.get("independence"),
#                     "all_fields": parsed_fields
#                 }
#                 results.append(result)
            
#             return results
            
#         except Exception as e:
#             logger.error(f"Error querying Pinecone: {str(e)}")
#             return []
        
#     except Exception as e:
#         logger.error(f"Error recommending careers: {str(e)}")
#         return []

# def refresh_all_embeddings_and_peers(db: Session) -> Dict[str, int]:
#     """
#     Full refresh of all embeddings and peer suggestions.
#     Returns counts of operations performed.
#     """
#     start_time = time.time()
    
#     try:
#         # Clear existing peer suggestions
#         db.execute(text("DELETE FROM suggested_peers"))
#         db.commit()
        
#         # Generate new embeddings
#         profiles_count = generate_and_store_embeddings(db)
        
#         # Find and store similar peers
#         peers_count = find_and_store_similar_peers(db) if profiles_count > 0 else 0
        
#         elapsed_time = time.time() - start_time
#         logger.info(f"Refresh completed in {elapsed_time:.2f} seconds")
        
#         return {
#             "profiles_processed": profiles_count,
#             "users_with_peers": peers_count,
#             "elapsed_seconds": round(elapsed_time, 2)
#         }
        
#     except Exception as e:
#         db.rollback()
#         logger.error(f"Error in refresh operation: {str(e)}")
#         raise 