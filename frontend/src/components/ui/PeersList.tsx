'use client';

import React from 'react';
import styles from './PeersList.module.css';

interface Peer {
  id: number;
  name: string;
  avatarUrl: string;
  compatibility: number;
  description: string;
  skills?: string[];
}

interface PeersListProps {
  peers: Peer[];
  className?: string;
  onPeerClick?: (peer: Peer) => void;
}

const PeersList: React.FC<PeersListProps> = ({ peers, className = '', onPeerClick }) => {
  return (
    <div className={`${styles.peersContainer} ${className}`}>
      <h2 className={styles.title}>Top Peers</h2>
      <div className={styles.peersList}>
        {peers.map((peer) => (
          <div
            key={peer.id}
            className={styles.peerCard}
            onClick={() => onPeerClick?.(peer)}
          >
            <div className={styles.peerAvatar}>
              <img src={peer.avatarUrl} alt={peer.name} />
              <div className={styles.compatibilityBadge}>
                {Math.round(peer.compatibility * 100)}%
              </div>
            </div>
            <div className={styles.peerInfo}>
              <h3 className={styles.peerName}>{peer.name}</h3>
              <p className={styles.peerDescription}>{peer.description}</p>
              {peer.skills && peer.skills.length > 0 && (
                <div className={styles.peerSkills}>
                  {peer.skills.slice(0, 3).map((skill, index) => (
                    <span key={index} className={styles.skillTag}>
                      {skill}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default PeersList;