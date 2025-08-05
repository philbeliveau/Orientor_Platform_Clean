'use client';
import React, { useState, useEffect } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { fetchUserTreePaths, deleteTreePath } from '../../utils/treeStorage';
import { format } from 'date-fns';
import Link from 'next/link';
import XPProgress from '../../components/ui/XPProgress';
import MainLayout from '@/components/layout/MainLayout';

interface TreePath {
  id: number; // Changed from string to number to match the API response
  tree_type: string;
  tree_json: any;
  created_at: string;
}

export default function TreePathPage() {
  const [treePaths, setTreePaths] = useState<TreePath[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    console.log('Tree Path page mounted, pathname:', pathname);
  }, [pathname]);

  // Load tree paths on component mount
  useEffect(() => {
    const loadTreePaths = async () => {
      try {
        const paths = await fetchUserTreePaths();
        setTreePaths(paths);
      } catch (err: any) {
        console.error('Error loading tree paths:', err);
        setError(err.message || 'Failed to load your saved trees');
      } finally {
        setLoading(false);
      }
    };

    loadTreePaths();
  }, []);

  // Handle deleting a tree path
  const handleDeleteTreePath = async (id: number) => { // Changed from string to number
    if (window.confirm('Are you sure you want to delete this saved tree?')) {
      try {
        await deleteTreePath(id.toString()); // Convert id to string for the API call
        setTreePaths(treePaths.filter(path => path.id !== id));
      } catch (err: any) {
        console.error('Error deleting tree path:', err);
        alert('Failed to delete tree: ' + (err.message || 'Unknown error'));
      }
    }
  };

  // Generate a preview image for the tree (simplified)
  const generateTreePreview = (treeType: string) => {
    const iconPath = treeType === 'career' 
      ? '/images/career_tree_icon.svg' 
      : '/images/skills_tree_icon.svg';
    
    // Fallback to a generic tree icon
    return (
      <div className="bg-gray-100 rounded-lg flex items-center justify-center h-40">
        <svg 
          className={`w-16 h-16 ${treeType === 'career' ? 'text-blue-500' : 'text-green-500'}`} 
          xmlns="http://www.w3.org/2000/svg" 
          viewBox="0 0 24 24" 
          fill="none" 
          stroke="currentColor" 
          strokeWidth="2" 
          strokeLinecap="round" 
          strokeLinejoin="round"
        >
          <path d="M12 22V6" />
          <path d="M9 18H15" />
          <path d="M5 12H19" />
          <path d="M4 7a1 1 0 0 1 1-1h14a1 1 0 0 1 1 1v12a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V7Z" />
          <path d="M7 10a1 1 0 0 1 1-1h8a1 1 0 0 1 1 1v2a1 1 0 0 1-1 1H8a1 1 0 0 1-1-1v-2Z" />
        </svg>
      </div>
    );
  };

  if (loading) {
    return (
      <MainLayout>
        <div className="min-h-screen py-12 px-4 sm:px-6 lg:px-8 flex flex-col items-center">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100">My Tree Paths</h1>
            <p className="mt-2 text-lg text-gray-600 dark:text-gray-300">Loading your saved trees...</p>
          </div>
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
        </div>
      </MainLayout>
    );
  }

  if (error) {
    return (
      <MainLayout>
        <div className="min-h-screen py-12 px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-gray-900">My Tree Paths</h1>
            <p className="mt-2 text-lg text-red-600">{error}</p>
            <button
              onClick={() => router.push('/')}
              className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
            >
              Return Home
            </button>
          </div>
        </div>
      </MainLayout>
    );
  }

  return (
    <MainLayout>
      <div className="min-h-screen py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          {/* Header */}
          <div className="flex justify-between items-center mb-8">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">My Tree Paths</h1>
              <p className="mt-2 text-lg text-gray-600">
                {treePaths.length > 0 
                  ? `You have ${treePaths.length} saved ${treePaths.length === 1 ? 'tree' : 'trees'}`
                  : 'You have no saved trees yet'}
              </p>
            </div>
            
            {/* XP Progress */}
            <XPProgress />
          </div>
          
          {/* If no tree paths */}
          {treePaths.length === 0 && (
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm p-8 text-center">
              <svg 
                className="w-16 h-16 text-gray-400 dark:text-gray-500 mx-auto mb-4" 
                xmlns="http://www.w3.org/2000/svg" 
                viewBox="0 0 24 24" 
                fill="none" 
                stroke="currentColor" 
                strokeWidth="2" 
                strokeLinecap="round" 
                strokeLinejoin="round"
              >
                <path d="M12 22V6M9 18H15M5 12H19M4 7a1 1 0 0 1 1-1h14a1 1 0 0 1 1 1v12a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V7Z" />
              </svg>
              <h2 className="text-xl font-medium text-gray-800 dark:text-gray-100 mb-2">No Saved Trees</h2>
              <p className="text-gray-600 dark:text-gray-300 mb-6">
                Visit the Career Explorer or Enhanced Skills Path to create and save trees
              </p>
              <div className="flex justify-center space-x-4">
                <Link
                  href="/career"
                  className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                >
                  Career Explorer
                </Link>
                <Link
                  href="/enhanced-skills"
                  className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                >
                  Skills Path
                </Link>
              </div>
            </div>
          )}
          
          {/* Tree Path Grid */}
          {treePaths.length > 0 && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {treePaths.map((path) => (
                <div key={path.id} className="bg-white dark:bg-gray-800 rounded-xl shadow-sm overflow-hidden border border-gray-100 dark:border-gray-700">
                  {/* Preview */}
                  {generateTreePreview(path.tree_type)}
                  
                  {/* Content */}
                  <div className="p-4">
                    <div className="flex justify-between items-start">
                      <div>
                        <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100">
                          {path.tree_type === 'career' ? 'Career Path' : 'Skills Path'}
                        </h3>
                        <p className="text-sm text-gray-500 dark:text-gray-400">
                          Saved on {format(new Date(path.created_at), 'MMMM d, yyyy')}
                        </p>
                      </div>
                      
                      {/* Tree type badge */}
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        path.tree_type === 'career' 
                          ? 'bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200' 
                          : 'bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200'
                      }`}>
                        {path.tree_type}
                      </span>
                    </div>
                    
                    {/* Path stats (simplified) */}
                    <div className="mt-4 text-sm text-gray-600 dark:text-gray-300">
                      <div className="flex items-center">
                        <svg className="w-4 h-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                        </svg>
                        <span>
                          {path.tree_json.children?.length || 0} main nodes
                        </span>
                      </div>
                    </div>
                    
                    {/* Actions */}
                    <div className="mt-4 flex justify-between">
                      <Link
                        href={{
                          pathname: path.tree_type === 'career' ? '/career' : '/enhanced-skills',
                          query: { treeId: path.id }
                        }}
                        className="text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 text-sm font-medium"
                      >
                        View {path.tree_type} tree
                      </Link>
                      <button
                        onClick={() => handleDeleteTreePath(path.id)}
                        className="text-red-600 dark:text-red-400 hover:text-red-800 dark:hover:text-red-300 text-sm font-medium"
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </MainLayout>
  );
} 