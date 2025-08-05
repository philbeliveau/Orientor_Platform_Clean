import React from 'react';
import { CheckCircle, ExternalLink, Folder } from 'lucide-react';

interface SaveConfirmationData {
  item_type: string;
  item_title: string;
  save_location?: string;
  myspace_url?: string;
  timestamp?: string;
}

interface SaveConfirmationMessageProps {
  data: SaveConfirmationData;
  className?: string;
}

export const SaveConfirmationMessage: React.FC<SaveConfirmationMessageProps> = ({
  data,
  className = ""
}) => {
  return (
    <div className={`flex items-center gap-3 p-3 bg-green-50 border border-green-200 rounded-lg ${className}`}>
      <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0" />
      <div className="flex-1">
        <p className="text-sm text-green-800">
          <span className="font-medium">{data.item_title}</span> has been saved to your{' '}
          {data.save_location || 'My Space'}
        </p>
        {data.myspace_url && (
          <a
            href={data.myspace_url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1 mt-1 text-xs text-green-700 hover:text-green-800 font-medium"
          >
            <Folder className="w-3 h-3" />
            View in My Space
            <ExternalLink className="w-3 h-3" />
          </a>
        )}
      </div>
      {data.timestamp && (
        <span className="text-xs text-green-600">
          {new Date(data.timestamp).toLocaleTimeString()}
        </span>
      )}
    </div>
  );
};