import React, { useState } from 'react';
import { Menu, Plus, Edit2, Check, X } from 'lucide-react';
import { Conversation, ChatMode } from '../types/chat.types';

interface ChatHeaderProps {
  conversation: Conversation | null;
  chatMode: ChatMode;
  onMenuClick: () => void;
  onNewChat: () => void;
  onUpdateTitle: (title: string) => Promise<void>;
  onModeChange: (mode: ChatMode) => void;
}

export const ChatHeader: React.FC<ChatHeaderProps> = ({
  conversation,
  chatMode,
  onMenuClick,
  onNewChat,
  onUpdateTitle,
  onModeChange
}) => {
  const [isEditingTitle, setIsEditingTitle] = useState(false);
  const [editingTitle, setEditingTitle] = useState('');

  const handleTitleEdit = () => {
    if (conversation) {
      setEditingTitle(conversation.title);
      setIsEditingTitle(true);
    }
  };

  const handleTitleSave = async () => {
    if (editingTitle.trim()) {
      await onUpdateTitle(editingTitle);
      setIsEditingTitle(false);
    }
  };

  const handleTitleCancel = () => {
    setIsEditingTitle(false);
    setEditingTitle('');
  };

  return (
    <div className="border-b bg-white px-4 py-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <button
            onClick={onMenuClick}
            className="rounded-lg p-2 hover:bg-gray-100 transition-colors"
          >
            <Menu size={20} />
          </button>
          
          {conversation && (
            <div className="flex items-center space-x-2">
              {isEditingTitle ? (
                <>
                  <input
                    type="text"
                    value={editingTitle}
                    onChange={(e) => setEditingTitle(e.target.value)}
                    className="rounded border px-2 py-1 text-sm focus:outline-none 
                             focus:ring-2 focus:ring-blue-500"
                    autoFocus
                  />
                  <button
                    onClick={handleTitleSave}
                    className="p-1 text-green-600 hover:text-green-700"
                  >
                    <Check size={16} />
                  </button>
                  <button
                    onClick={handleTitleCancel}
                    className="p-1 text-red-600 hover:text-red-700"
                  >
                    <X size={16} />
                  </button>
                </>
              ) : (
                <>
                  <h2 className="text-lg font-medium">
                    {conversation.title}
                  </h2>
                  <button
                    onClick={handleTitleEdit}
                    className="p-1 text-gray-500 hover:text-gray-700"
                  >
                    <Edit2 size={14} />
                  </button>
                </>
              )}
            </div>
          )}
        </div>

        <div className="flex items-center space-x-2">
          <ChatModeSelector
            currentMode={chatMode}
            onModeChange={onModeChange}
          />
          <button
            onClick={onNewChat}
            className="rounded-lg bg-blue-500 px-3 py-2 text-sm 
                     text-white hover:bg-blue-600 transition-colors
                     flex items-center space-x-1"
          >
            <Plus size={16} />
            <span>New Chat</span>
          </button>
        </div>
      </div>
    </div>
  );
};

interface ChatModeSelectorProps {
  currentMode: ChatMode;
  onModeChange: (mode: ChatMode) => void;
}

const ChatModeSelector: React.FC<ChatModeSelectorProps> = ({
  currentMode,
  onModeChange
}) => {
  const modes: { value: ChatMode; label: string; color: string }[] = [
    { value: 'default', label: 'Default', color: 'bg-blue-500' },
    { value: 'socratic', label: 'Socratic', color: 'bg-green-500' },
    { value: 'claude', label: 'Claude', color: 'bg-purple-500' }
  ];

  return (
    <select
      value={currentMode}
      onChange={(e) => onModeChange(e.target.value as ChatMode)}
      className="rounded-lg border border-gray-300 px-3 py-2 text-sm
                 focus:outline-none focus:ring-2 focus:ring-blue-500"
    >
      {modes.map(mode => (
        <option key={mode.value} value={mode.value}>
          {mode.label}
        </option>
      ))}
    </select>
  );
};