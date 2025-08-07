"""
Utility module for Streamlit compatibility fixes.
This module contains fixes for known compatibility issues between Streamlit and other libraries.
"""

import logging
import sys
import streamlit.watcher.local_sources_watcher
import streamlit.watcher.path_watcher
import torch
from torch.serialization import add_safe_globals
import numpy as np

# Configure logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def apply_compatibility_fixes():
    """
    Apply all necessary compatibility fixes for Streamlit + PyTorch + GraphSAGE.
    This includes:
    1. Fixing torch.load() issues
    2. Patching Streamlit watchers
    3. Handling torch.classes crash
    """
    try:
        # Fix 1: Handle torch.classes crash
        sys.modules["torch.classes"] = None
        logger.info("Applied torch.classes fix")

        # Fix 2: Add safe globals for torch.load
        add_safe_globals([np.core.multiarray.scalar])
        logger.info("Added safe globals for torch.load")

        # Fix 3: Patch Streamlit watchers
        patch_streamlit_watchers()
        
        return True
    except Exception as e:
        logger.error(f"Error applying compatibility fixes: {str(e)}")
        return False

def patch_streamlit_watchers():
    """
    Apply patches to Streamlit watchers to fix compatibility issues with PyTorch.
    This fixes the 'Tried to instantiate class __path__._path' error.
    """
    try:
        # Patch the path_watcher
        original_watch_file = streamlit.watcher.path_watcher.watch_file
        
        def patched_watch_file(path, callback):
            if 'torch' in path or 'pytorch' in path.lower():
                return None
            return original_watch_file(path, callback)
        
        streamlit.watcher.path_watcher.watch_file = patched_watch_file
        
        logger.info("Successfully patched Streamlit watchers")
        return True
        
    except Exception as e:
        logger.error(f"Error patching Streamlit watchers: {str(e)}")
        return False

def verify_torch_model(model_path: str) -> bool:
    """
    Verify that a PyTorch model can be loaded correctly.
    
    Args:
        model_path: Path to the PyTorch model file
        
    Returns:
        bool: True if model loads successfully, False otherwise
    """
    try:
        # Use weights_only=False to load full model
        checkpoint = torch.load(model_path, map_location=torch.device("cpu"), weights_only=False)
        
        # Handle different checkpoint formats
        if isinstance(checkpoint, dict):
            if 'model_state_dict' in checkpoint:
                # Standard PyTorch checkpoint format
                model = checkpoint['model_state_dict']
            elif 'state_dict' in checkpoint:
                # Alternative checkpoint format
                model = checkpoint['state_dict']
            else:
                # Raw state dict
                model = checkpoint
        else:
            # Direct model
            model = checkpoint
            
        # If model is a state dict, we can't call eval() directly
        if not isinstance(model, torch.nn.Module):
            logger.info("Loaded model state dict successfully")
        else:
            model.eval()
            logger.info("Loaded and set model to eval mode")
            
        logger.info(f"Successfully loaded and verified model from {model_path}")
        return True
    except Exception as e:
        logger.error(f"Error loading model from {model_path}: {str(e)}")
        return False 