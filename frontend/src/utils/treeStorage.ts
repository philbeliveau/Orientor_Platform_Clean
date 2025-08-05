import { TreeNode } from './convertToFlowGraph';

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
export async function saveTreePath(tree: TreeNode, treeType: 'career' | 'skills') {
  const token = localStorage.getItem('access_token');
  if (!token) {
    throw new Error('Authentication required');
  }

  const response = await fetch(`${API_URL}/tree-paths/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
      tree_type: treeType,
      tree_json: tree
    })
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to save tree path');
  }

  return await response.json();
}

// Fetch all tree paths for the current user
export async function fetchUserTreePaths() {
  const token = localStorage.getItem('access_token');
  if (!token) {
    throw new Error('Authentication required');
  }

  const response = await fetch(`${API_URL}/tree-paths/`, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to fetch tree paths');
  }

  return await response.json() as TreePath[];
}

// Save a note for a node action
export async function saveNodeNote(nodeId: string, actionIndex: number, noteText: string) {
  const token = localStorage.getItem('access_token');
  if (!token) {
    throw new Error('Authentication required');
  }

  const response = await fetch(`${API_URL}/node-notes/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
      node_id: nodeId,
      action_index: actionIndex,
      note_text: noteText
    })
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to save note');
  }

  return await response.json();
}

// Fetch all notes for a specific node
export async function fetchNodeNotes(nodeId: string) {
  const token = localStorage.getItem('access_token');
  if (!token) {
    throw new Error('Authentication required');
  }

  const response = await fetch(`${API_URL}/node-notes/node/${nodeId}/`, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to fetch notes');
  }

  return await response.json() as NodeNote[];
}

// Update user XP when completing an action
export async function updateUserXP(nodeId: string, xpGained = 10, completedActions?: { [key: string]: boolean[] }) {
  const token = localStorage.getItem('access_token');
  if (!token) {
    throw new Error('Authentication required');
  }

  const response = await fetch(`${API_URL}/user-progress/update`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
      node_id: nodeId,
      xp_gained: xpGained,
      completed_actions: completedActions
    })
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to update XP');
  }

  return await response.json();
}

// Get user progress (XP, level)
export async function getUserProgress() {
  const token = localStorage.getItem('access_token');
  if (!token) {
    throw new Error('Authentication required');
  }

  const response = await fetch(`${API_URL}/user-progress/`, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to fetch user progress');
  }

  return await response.json() as UserProgress;
}

// Delete a saved tree path
export async function deleteTreePath(treePathId: string) {
  const token = localStorage.getItem('access_token');
  if (!token) {
    throw new Error('Authentication required');
  }

  try {
    console.log('Deleting tree with ID:', treePathId);
    const response = await fetch(`${API_URL}/tree-paths/${treePathId}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });

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
export async function getTreePath(treeId: string) {
  const token = localStorage.getItem('access_token');
  if (!token) {
    throw new Error('Authentication required');
  }

  try {
    const response = await fetch(`${API_URL}/tree-paths/${treeId}`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });

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