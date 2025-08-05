import React, { useState } from 'react';
import { 
  XMarkIcon, 
  DocumentTextIcon,
  DocumentIcon,
  DocumentChartBarIcon,
  ArrowDownTrayIcon
} from '@heroicons/react/24/outline';

interface ConversationExportDialogProps {
  conversationId: number;
  conversationTitle: string;
  onClose: () => void;
}

export default function ConversationExportDialog({ 
  conversationId, 
  conversationTitle,
  onClose 
}: ConversationExportDialogProps) {
  const [selectedFormat, setSelectedFormat] = useState<'json' | 'txt' | 'pdf'>('txt');
  const [exporting, setExporting] = useState(false);

  const formatOptions = [
    {
      format: 'txt' as const,
      name: 'Plain Text',
      description: 'Simple text format, easy to read',
      icon: DocumentTextIcon
    },
    {
      format: 'json' as const,
      name: 'JSON',
      description: 'Structured data format for developers',
      icon: DocumentIcon
    },
    {
      format: 'pdf' as const,
      name: 'PDF',
      description: 'Formatted document for printing',
      icon: DocumentChartBarIcon
    }
  ];

  const handleExport = async () => {
    setExporting(true);
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/chat/conversations/${conversationId}/export`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify({ format: selectedFormat })
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${conversationTitle.replace(/[^a-z0-9]/gi, '_')}.${selectedFormat}`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        onClose();
      }
    } catch (error) {
      console.error('Error exporting conversation:', error);
    } finally {
      setExporting(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white dark:bg-gray-900 rounded-lg w-full max-w-md p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold">Export Conversation</h2>
          <button
            onClick={onClose}
            className="p-1 hover:bg-gray-100 dark:hover:bg-gray-800 rounded"
          >
            <XMarkIcon className="w-5 h-5" />
          </button>
        </div>

        <div className="space-y-3 mb-6">
          {formatOptions.map((option) => (
            <label
              key={option.format}
              className={`flex items-start p-4 border rounded-lg cursor-pointer transition-colors ${
                selectedFormat === option.format
                  ? 'border-primary bg-primary/5'
                  : 'border-gray-300 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800'
              }`}
            >
              <input
                type="radio"
                name="format"
                value={option.format}
                checked={selectedFormat === option.format}
                onChange={(e) => setSelectedFormat(e.target.value as typeof selectedFormat)}
                className="sr-only"
              />
              <option.icon className={`w-6 h-6 mr-3 ${
                selectedFormat === option.format ? 'text-primary' : 'text-gray-400'
              }`} />
              <div className="flex-1">
                <div className="font-medium">{option.name}</div>
                <div className="text-sm text-gray-500">{option.description}</div>
              </div>
            </label>
          ))}
        </div>

        <button
          onClick={handleExport}
          disabled={exporting}
          className="w-full py-2 bg-primary text-white rounded-lg hover:bg-primary-dark disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
        >
          <ArrowDownTrayIcon className="w-5 h-5" />
          <span>{exporting ? 'Exporting...' : 'Export Conversation'}</span>
        </button>

        {selectedFormat === 'pdf' && (
          <p className="mt-3 text-xs text-gray-500 text-center">
            Note: PDF export requires additional dependencies to be installed
          </p>
        )}
      </div>
    </div>
  );
}