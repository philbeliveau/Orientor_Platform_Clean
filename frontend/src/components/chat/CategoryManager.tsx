import React, { useState, useEffect } from 'react';
import { 
  FolderIcon, 
  PlusIcon,
  PencilIcon,
  TrashIcon,
  XMarkIcon,
  CheckIcon
} from '@heroicons/react/24/outline';

interface Category {
  id: number;
  name: string;
  description: string | null;
  color: string | null;
  conversation_count: number;
  created_at: string;
}

interface CategoryManagerProps {
  selectedCategoryId?: number | null;
  onSelectCategory: (category: Category | null) => void;
  onClose?: () => void;
}

export default function CategoryManager({ 
  selectedCategoryId, 
  onSelectCategory,
  onClose
}: CategoryManagerProps) {
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);
  const [isCreating, setIsCreating] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    color: '#3B82F6'
  });

  const colors = [
    '#3B82F6', // blue
    '#10B981', // green
    '#F59E0B', // amber
    '#EF4444', // red
    '#8B5CF6', // violet
    '#EC4899', // pink
    '#6B7280', // gray
    '#06B6D4', // cyan
  ];

  useEffect(() => {
    fetchCategories();
  }, []);

  const fetchCategories = async () => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/chat/categories`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setCategories(data);
      }
    } catch (error) {
      console.error('Error fetching categories:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async () => {
    if (!formData.name.trim()) return;

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/chat/categories`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify(formData)
      });

      if (response.ok) {
        const newCategory = await response.json();
        setCategories([...categories, newCategory]);
        setIsCreating(false);
        setFormData({ name: '', description: '', color: '#3B82F6' });
      }
    } catch (error) {
      console.error('Error creating category:', error);
    }
  };

  const handleUpdate = async (id: number) => {
    const category = categories.find(c => c.id === id);
    if (!category || !formData.name.trim()) return;

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/chat/categories/${id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify(formData)
      });

      if (response.ok) {
        const updatedCategory = await response.json();
        setCategories(categories.map(c => c.id === id ? updatedCategory : c));
        setEditingId(null);
      }
    } catch (error) {
      console.error('Error updating category:', error);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this category?')) return;

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/chat/categories/${id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });

      if (response.ok) {
        setCategories(categories.filter(c => c.id !== id));
        if (selectedCategoryId === id) {
          onSelectCategory(null);
        }
      }
    } catch (error) {
      console.error('Error deleting category:', error);
    }
  };

  const startEditing = (category: Category) => {
    setEditingId(category.id);
    setFormData({
      name: category.name,
      description: category.description || '',
      color: category.color || '#3B82F6'
    });
  };

  const cancelEditing = () => {
    setEditingId(null);
    setFormData({ name: '', description: '', color: '#3B82F6' });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold flex items-center">
          <FolderIcon className="w-5 h-5 mr-2" />
          Categories
        </h3>
        <div className="flex items-center space-x-2">
          <button
            onClick={() => {
              setIsCreating(true);
              setFormData({ name: '', description: '', color: '#3B82F6' });
            }}
            className="p-2 text-primary hover:bg-primary/10 rounded-lg transition-colors"
          >
            <PlusIcon className="w-5 h-5" />
          </button>
          {onClose && (
            <button
              onClick={onClose}
              className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg"
            >
              <XMarkIcon className="w-5 h-5" />
            </button>
          )}
        </div>
      </div>

      {/* Category List */}
      <div className="space-y-2">
        {/* All Conversations Option */}
        <button
          onClick={() => onSelectCategory(null)}
          className={`w-full p-3 rounded-lg text-left transition-colors ${
            selectedCategoryId === null
              ? 'bg-primary/10 border-2 border-primary'
              : 'hover:bg-gray-100 dark:hover:bg-gray-800 border-2 border-transparent'
          }`}
        >
          <div className="flex items-center">
            <div className="w-4 h-4 rounded mr-3 bg-gray-400" />
            <span className="font-medium">All Conversations</span>
          </div>
        </button>

        {/* Create New Category Form */}
        {isCreating && (
          <div className="p-4 border-2 border-dashed border-gray-300 dark:border-gray-700 rounded-lg">
            <div className="space-y-3">
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="Category name"
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                autoFocus
              />
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                placeholder="Description (optional)"
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary resize-none"
                rows={2}
              />
              <div className="flex items-center space-x-2">
                <span className="text-sm font-medium">Color:</span>
                <div className="flex space-x-1">
                  {colors.map((color) => (
                    <button
                      key={color}
                      onClick={() => setFormData({ ...formData, color })}
                      className={`w-6 h-6 rounded-full border-2 ${
                        formData.color === color 
                          ? 'border-gray-900 dark:border-white' 
                          : 'border-transparent'
                      }`}
                      style={{ backgroundColor: color }}
                    />
                  ))}
                </div>
              </div>
              <div className="flex justify-end space-x-2">
                <button
                  onClick={() => {
                    setIsCreating(false);
                    setFormData({ name: '', description: '', color: '#3B82F6' });
                  }}
                  className="px-3 py-1 text-sm border border-gray-300 dark:border-gray-700 rounded hover:bg-gray-100 dark:hover:bg-gray-800"
                >
                  Cancel
                </button>
                <button
                  onClick={handleCreate}
                  disabled={!formData.name.trim()}
                  className="px-3 py-1 text-sm bg-primary text-white rounded hover:bg-primary-dark disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Create
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Existing Categories */}
        {categories.map((category) => (
          <div
            key={category.id}
            className={`p-3 rounded-lg border-2 transition-colors ${
              selectedCategoryId === category.id
                ? 'bg-primary/10 border-primary'
                : 'hover:bg-gray-100 dark:hover:bg-gray-800 border-transparent'
            }`}
          >
            {editingId === category.id ? (
              <div className="space-y-2">
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full px-2 py-1 bg-transparent border-b-2 border-primary focus:outline-none"
                  autoFocus
                />
                <div className="flex items-center justify-between">
                  <div className="flex space-x-1">
                    {colors.map((color) => (
                      <button
                        key={color}
                        onClick={() => setFormData({ ...formData, color })}
                        className={`w-5 h-5 rounded-full border-2 ${
                          formData.color === color 
                            ? 'border-gray-900 dark:border-white' 
                            : 'border-transparent'
                        }`}
                        style={{ backgroundColor: color }}
                      />
                    ))}
                  </div>
                  <div className="flex space-x-1">
                    <button
                      onClick={() => handleUpdate(category.id)}
                      className="p-1 text-green-600 hover:bg-green-100 dark:hover:bg-green-900/20 rounded"
                    >
                      <CheckIcon className="w-4 h-4" />
                    </button>
                    <button
                      onClick={cancelEditing}
                      className="p-1 text-gray-600 hover:bg-gray-100 dark:hover:bg-gray-800 rounded"
                    >
                      <XMarkIcon className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>
            ) : (
              <div className="flex items-center justify-between">
                <button
                  onClick={() => onSelectCategory(category)}
                  className="flex-1 flex items-center text-left"
                >
                  <div 
                    className="w-4 h-4 rounded mr-3"
                    style={{ backgroundColor: category.color || '#6B7280' }}
                  />
                  <div className="flex-1">
                    <div className="font-medium">{category.name}</div>
                    {category.description && (
                      <div className="text-xs text-gray-500">{category.description}</div>
                    )}
                    <div className="text-xs text-gray-400 mt-1">
                      {category.conversation_count} conversations
                    </div>
                  </div>
                </button>
                <div className="flex items-center space-x-1">
                  <button
                    onClick={() => startEditing(category)}
                    className="p-1 text-gray-400 hover:text-gray-600 hover:bg-gray-100 dark:hover:bg-gray-800 rounded"
                  >
                    <PencilIcon className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => handleDelete(category.id)}
                    className="p-1 text-gray-400 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 rounded"
                  >
                    <TrashIcon className="w-4 h-4" />
                  </button>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}