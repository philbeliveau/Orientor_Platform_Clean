import React, { useState } from 'react';
import { Users, Sparkles, MessageCircle, UserPlus, Award, Target } from 'lucide-react';
import { SaveActionButton } from '../chat/SaveActionButton';
import { ComponentAction } from '../chat/MessageComponent';

interface PeerData {
  id: string;
  name: string;
  avatar?: string;
  role?: string;
  institution?: string;
  match_score?: number;
  match_reasons?: string[];
  common_interests?: string[];
  skills?: string[];
  goals?: string[];
  bio?: string;
  status?: 'online' | 'offline' | 'busy';
}

interface PeerCardMessageProps {
  data: PeerData | PeerData[];
  actions: ComponentAction[];
  onAction: (action: ComponentAction) => void;
  saved?: boolean;
  className?: string;
}

const PeerCard: React.FC<{ 
  peer: PeerData; 
  onConnect: () => void;
  onMessage: () => void;
  onSave: () => Promise<void>;
  saved?: boolean;
}> = ({ peer, onConnect, onMessage, onSave, saved }) => {
  const [showDetails, setShowDetails] = useState(false);

  const getStatusColor = (status?: string) => {
    switch (status) {
      case 'online': return 'bg-green-500';
      case 'busy': return 'bg-orange-500';
      default: return 'bg-gray-400';
    }
  };

  const getInitials = (name: string) => {
    return name
      .split(' ')
      .map(n => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  return (
    <div className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
      <div className="flex items-start gap-3">
        {/* Avatar */}
        <div className="relative flex-shrink-0">
          {peer.avatar ? (
            <img 
              src={peer.avatar} 
              alt={peer.name}
              className="w-12 h-12 rounded-full object-cover"
            />
          ) : (
            <div className="w-12 h-12 rounded-full bg-blue-100 flex items-center justify-center">
              <span className="text-blue-600 font-medium">{getInitials(peer.name)}</span>
            </div>
          )}
          {peer.status && (
            <div className={`absolute bottom-0 right-0 w-3 h-3 rounded-full border-2 border-white ${getStatusColor(peer.status)}`} />
          )}
        </div>

        {/* Main Content */}
        <div className="flex-1">
          <div className="flex items-start justify-between">
            <div>
              <h4 className="font-medium text-gray-900">{peer.name}</h4>
              {peer.role && <p className="text-sm text-gray-600">{peer.role}</p>}
              {peer.institution && <p className="text-xs text-gray-500">{peer.institution}</p>}
            </div>
            <SaveActionButton 
              onSave={onSave} 
              saved={saved} 
              size="sm" 
              variant="ghost" 
            />
          </div>

          {/* Match Score */}
          {peer.match_score && (
            <div className="mt-2 flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-yellow-500" />
              <span className="text-sm font-medium text-green-600">{peer.match_score}% match</span>
            </div>
          )}

          {/* Match Reasons */}
          {peer.match_reasons && peer.match_reasons.length > 0 && (
            <div className="mt-2">
              <p className="text-xs font-medium text-gray-600 mb-1">Why you match:</p>
              <ul className="text-xs text-gray-600 space-y-0.5">
                {peer.match_reasons.slice(0, 2).map((reason, idx) => (
                  <li key={idx} className="flex items-start gap-1">
                    <span className="text-green-500 mt-0.5">•</span>
                    <span>{reason}</span>
                  </li>
                ))}
              </ul>
              {peer.match_reasons.length > 2 && (
                <button
                  onClick={() => setShowDetails(!showDetails)}
                  className="text-xs text-blue-600 hover:text-blue-700 font-medium mt-1"
                >
                  {showDetails ? 'Show less' : `+${peer.match_reasons.length - 2} more reasons`}
                </button>
              )}
            </div>
          )}

          {/* Expanded Details */}
          {showDetails && (
            <div className="mt-3 p-3 bg-gray-50 rounded-lg space-y-2">
              {peer.bio && (
                <div>
                  <p className="text-xs font-medium text-gray-600">About:</p>
                  <p className="text-xs text-gray-700">{peer.bio}</p>
                </div>
              )}
              
              {peer.common_interests && peer.common_interests.length > 0 && (
                <div>
                  <p className="text-xs font-medium text-gray-600">Common Interests:</p>
                  <div className="flex flex-wrap gap-1 mt-1">
                    {peer.common_interests.map((interest, idx) => (
                      <span key={idx} className="text-xs px-2 py-0.5 bg-blue-100 text-blue-700 rounded">
                        {interest}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {peer.skills && peer.skills.length > 0 && (
                <div>
                  <p className="text-xs font-medium text-gray-600">Skills:</p>
                  <div className="flex flex-wrap gap-1 mt-1">
                    {peer.skills.map((skill, idx) => (
                      <span key={idx} className="text-xs px-2 py-0.5 bg-gray-100 text-gray-700 rounded">
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {peer.goals && peer.goals.length > 0 && (
                <div>
                  <p className="text-xs font-medium text-gray-600">Goals:</p>
                  <ul className="text-xs text-gray-700 space-y-0.5 mt-1">
                    {peer.goals.map((goal, idx) => (
                      <li key={idx} className="flex items-start gap-1">
                        <Target className="w-3 h-3 text-purple-500 mt-0.5 flex-shrink-0" />
                        <span>{goal}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}

          {/* Actions */}
          <div className="flex items-center gap-2 mt-3">
            <button
              onClick={onConnect}
              className="flex items-center gap-1 px-3 py-1.5 text-sm font-medium bg-blue-500 text-white hover:bg-blue-600 rounded-lg transition-colors"
            >
              <UserPlus className="w-3 h-3" />
              Connect
            </button>
            <button
              onClick={onMessage}
              className="flex items-center gap-1 px-3 py-1.5 text-sm font-medium text-gray-600 hover:bg-gray-50 rounded-lg transition-colors"
            >
              <MessageCircle className="w-3 h-3" />
              Message
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export const PeerCardMessage: React.FC<PeerCardMessageProps> = ({
  data,
  actions,
  onAction,
  saved,
  className = ""
}) => {
  const peers = Array.isArray(data) ? data : [data];
  const [savedPeers, setSavedPeers] = useState<Set<string>>(new Set());

  const handleSavePeer = async (peerId: string) => {
    const saveAction = actions.find(a => a.type === 'save');
    if (saveAction) {
      onAction({ ...saveAction, params: { peerId } });
      setSavedPeers(new Set(Array.from(savedPeers).concat(peerId)));
    }
  };

  const handleConnect = (peerId: string) => {
    const connectAction = actions.find(a => a.label === 'Connect' || a.type === 'start');
    if (connectAction) {
      onAction({ ...connectAction, params: { peerId } });
    }
  };

  const handleMessage = (peerId: string) => {
    const messageAction = actions.find(a => a.label === 'Message');
    if (messageAction) {
      onAction({ ...messageAction, params: { peerId } });
    }
  };

  return (
    <div className={`${className}`}>
      {/* Header for multiple peers */}
      {peers.length > 1 && (
        <div className="flex items-center gap-2 mb-4">
          <Users className="w-5 h-5 text-blue-600" />
          <h3 className="font-medium text-gray-900">
            Found {peers.length} compatible peers
          </h3>
        </div>
      )}

      {/* Peer Cards */}
      <div className="space-y-3">
        {peers.map((peer) => (
          <PeerCard
            key={peer.id}
            peer={peer}
            onConnect={() => handleConnect(peer.id)}
            onMessage={() => handleMessage(peer.id)}
            onSave={() => handleSavePeer(peer.id)}
            saved={savedPeers.has(peer.id) || saved}
          />
        ))}
      </div>

      {/* Aggregate Actions */}
      {peers.length > 1 && actions.some(a => a.label === 'Find More Peers') && (
        <div className="mt-4 pt-3 border-t border-gray-200 flex items-center gap-2">
          {actions.filter(a => a.type !== 'save').map((action, index) => (
            <button
              key={index}
              onClick={() => onAction(action)}
              className="px-3 py-1.5 text-sm font-medium text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
            >
              {action.label}
            </button>
          ))}
        </div>
      )}
    </div>
  );
};