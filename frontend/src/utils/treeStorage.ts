import { TreeNode } from './convertToFlowGraph';
import { makeAuthenticatedRequest } from './clerkAuth';

// API URL based on environment
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Types
interface TreePath {
  id: number;
  user_id: number;
  tree_type: string;
  tree_json: any;
  created_at: string;
}

interface NodeNote {
  id: number;
  user_id: number;
  node_id: string;
  action_index: number;
  note_text: string;
  updated_at: string;
}

interface UserProgress {
  id: number;
  user_id: number;
  total_xp: number;
  level: number;
  last_completed_node: string | null;
  completed_actions: { [key: string]: boolean[] } | null;
  last_updated: string;
}

// Save tree to user's path
export async function saveTreePath(tree: TreeNode, treeType: 'career' | 'skills', token: string) {
  if (!token) {
    throw new Error('Authentication token required');
  }

  const response = await makeAuthenticatedRequest('/tree-paths/', {
    method: 'POST',
    body: JSON.stringify({
      tree_type: treeType,
      tree_json: tree
    })
  }, token);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to save tree path');
  }

  return await response.json();
}

// Fetch all tree paths for the current user
export async function fetchUserTreePaths(token: string) {
  if (!token) {
    throw new Error('Authentication token required');
  }

  const response = await makeAuthenticatedRequest('/tree-paths/', {
    method: 'GET'
  }, token);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to fetch tree paths');
  }

  return await response.json() as TreePath[];
}

// Save a note for a node action
export async function saveNodeNote(nodeId: string, actionIndex: number, noteText: string, token: string) {
  if (!token) {
    throw new Error('Authentication token required');
  }

  const response = await makeAuthenticatedRequest('/node-notes/', {
    method: 'POST',
    body: JSON.stringify({
      node_id: nodeId,
      action_index: actionIndex,
      note_text: noteText
    })
  }, token);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to save note');
  }

  return await response.json();
}

// Fetch all notes for a specific node
export async function fetchNodeNotes(nodeId: string, token: string) {
  if (!token) {
    throw new Error('Authentication token required');
  }

  const response = await makeAuthenticatedRequest(`/node-notes/node/${nodeId}/`, {
    method: 'GET'
  }, token);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to fetch notes');
  }

  return await response.json() as NodeNote[];
}

// Update user XP when completing an action
export async function updateUserXP(nodeId: string, token: string, xpGained = 10, completedActions?: { [key: string]: boolean[] }) {
  if (!token) {
    throw new Error('Authentication token required');
  }

  const response = await makeAuthenticatedRequest('/user-progress/update', {
    method: 'POST',
    body: JSON.stringify({
      node_id: nodeId,
      xp_gained: xpGained,
      completed_actions: completedActions
    })
  }, token);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to update XP');
  }

  return await response.json();
}

// Get user progress (XP, level)
export async function getUserProgress(token: string) {
  if (!token) {
    throw new Error('Authentication token required');
  }

  const response = await makeAuthenticatedRequest('/user-progress/', {
    method: 'GET'
  }, token);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to fetch user progress');
  }

  return await response.json() as UserProgress;
}

// Delete a saved tree path
export async function deleteTreePath(treePathId: string, token: string) {
  if (!token) {
    throw new Error('Authentication token required');
  }

  try {
    console.log('Deleting tree with ID:', treePathId);
    const response = await makeAuthenticatedRequest(`/tree-paths/${treePathId}`, {
      method: 'DELETE'
    }, token);

    console.log('Delete response status:', response.status);
    
    if (!response.ok) {
      const errorData = await response.json();
      console.error('Error deleting tree:', {
        status: response.status,
        statusText: response.statusText,
        error: errorData
      });
      throw new Error(errorData.detail || `Failed to delete tree path (${response.status})`);
    }

    return true;
  } catch (error) {
    console.error('Error in deleteTreePath:', error);
    throw error;
  }
}

// Get a saved tree by ID
export async function getTreePath(treeId: string, token: string) {
  if (!token) {
    throw new Error('Authentication token required');
  }

  try {
    const response = await makeAuthenticatedRequest(`/tree-paths/${treeId}`, {
      method: 'GET'
    }, token);

    if (!response.ok) {
      const errorData = await response.json();
      console.error('Error fetching tree:', errorData);
      throw new Error(errorData.detail || 'Failed to fetch tree path');
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error in getTreePath:', error);
    throw error;
  }
}