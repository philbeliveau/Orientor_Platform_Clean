import React from 'react';
import Link from 'next/link';
import styles from './NewSidebar.module.css';

interface NavItem {
  name: string;
  icon: string;
  path: string;
}

interface NewSidebarProps {
  navItems: NavItem[];
  isChatMode?: boolean;
}

const NewSidebar: React.FC<NewSidebarProps> = ({ navItems, isChatMode = false }) => {
  return (
    <div className={`${styles.sidebar} ${isChatMode ? styles.chatMode : ''}`}>
      <div className={styles.navContainer}>
        {navItems.map((item, index) => (
          <Link href={item.path} key={index} className={styles.navItem}>
            <div className={styles.iconWrapper}>
              {item.icon === 'Dashboard' && (
                <svg xmlns="http://www.w3.org/2000/svg" width="24px" height="24px" fill="currentColor" viewBox="0 0 256 256">
                  <path d="M218.83,103.77l-80-75.48a1.14,1.14,0,0,1-.11-.11,16,16,0,0,0-21.53,0l-.11.11L37.17,103.77A8,8,0,0,0,32,110.62V208a16,16,0,0,0,16,16H208a16,16,0,0,0,16-16V110.62A8,8,0,0,0,218.83,103.77ZM208,208H160V160a8,8,0,0,0-8-8H104a8,8,0,0,0-8,8v48H48V115.55l80-75.48,80,75.48Z"></path>
                </svg>
              )}
              {item.icon === 'Classes' && (
                <svg xmlns="http://www.w3.org/2000/svg" width="24px" height="24px" fill="currentColor" viewBox="0 0 256 256">
                  <path d="M225.86,102.82c-.03-.07-.07-.13-.11-.2L208,80.51V56a8,8,0,0,0-8-8H56a8,8,0,0,0-8,8V80.51L30.25,102.62c0,.07-.08.13-.11.2A8,8,0,0,0,32,112v96a8,8,0,0,0,8,8H64a8,8,0,0,0,8-8V176h48v32a8,8,0,0,0,8,8h24a8,8,0,0,0,8-8V176h48v32a8,8,0,0,0,8,8h24a8,8,0,0,0,8-8V112A8,8,0,0,0,225.86,102.82ZM64,64H192V158.3l-16-16V104a8,8,0,0,0-8-8H88a8,8,0,0,0-8,8v38.3l-16,16Zm32,48h64v38.3l-32-32Z"></path>
                </svg>
              )}
              {item.icon === 'Education' && (
                <svg xmlns="http://www.w3.org/2000/svg" width="24px" height="24px" fill="currentColor" viewBox="0 0 256 256">
                  <path d="M208,24H72A32,32,0,0,0,40,56V224a8,8,0,0,0,8,8H192a8,8,0,0,0,0-16H56a16,16,0,0,1,16-16H208a8,8,0,0,0,8-8V32A8,8,0,0,0,208,24Zm-8,160H72a31.82,31.82,0,0,0-16,4.29V56A16,16,0,0,1,72,40H200Z"></path>
                </svg>
              )}
              {item.icon === 'Chat' && (
                <svg xmlns="http://www.w3.org/2000/svg" width="24px" height="24px" fill="currentColor" viewBox="0 0 256 256">
                  <path d="M216,48H40A16,16,0,0,0,24,64V224a15.84,15.84,0,0,0,9.25,14.5A16.05,16.05,0,0,0,40,240a15.89,15.89,0,0,0,10.25-3.78.69.69,0,0,0,.13-.11L82.5,208H216a16,16,0,0,0,16-16V64A16,16,0,0,0,216,48ZM40,224V64H216V192H82.5a16,16,0,0,0-10.25,3.78L40,224Z"></path>
                </svg>
              )}
              {item.icon === 'Peers' && (
                <svg xmlns="http://www.w3.org/2000/svg" width="24px" height="24px" fill="currentColor" viewBox="0 0 256 256">
                  <path d="M128,120a48,48,0,1,0-48-48A48,48,0,0,0,128,120Zm0,16c-33.08,0-96,16.54-96,49.38V200a8,8,0,0,0,8,8H216a8,8,0,0,0,8-8v-14.62C224,152.54,161.08,136,128,136Z"></path>
                </svg>
              )}
              {item.icon === 'Personality' && (
                <svg xmlns="http://www.w3.org/2000/svg" width="24px" height="24px" fill="currentColor" viewBox="0 0 256 256">
                  <path d="M232,128a104,104,0,1,0-193.55,58.25C41.62,187.2,40,191.43,40,196v20a12,12,0,0,0,12,12H88a12,12,0,0,0,12-12V204h8a8,8,0,0,0,8-8V168a40.05,40.05,0,0,0,40-40v-8a8,8,0,0,0-8-8H139.75a40,40,0,0,0-75.5,0H56a8,8,0,0,0,0,16h80a24,24,0,0,1,24,24v8a8,8,0,0,0,8,8h8a12,12,0,0,0,12-12V196c0-4.57-1.62-8.8-4.45-12.25ZM128,24A88,88,0,1,1,40,112,88.1,88.1,0,0,1,128,24Z"></path>
                </svg>
              )}
              {item.icon === 'Bookmark' && (
                <svg xmlns="http://www.w3.org/2000/svg" width="24px" height="24px" fill="currentColor" viewBox="0 0 256 256">
                  <path d="M184,32H72A16,16,0,0,0,56,48V224a8,8,0,0,0,12.24,6.78L128,193.43l59.77,37.35A8,8,0,0,0,200,224V48A16,16,0,0,0,184,32Zm0,177.57-51.77-32.35a8,8,0,0,0-8.48,0L72,209.57V48H184Z"></path>
                </svg>
              )}
              {item.icon === 'Trophy' && (
                <svg xmlns="http://www.w3.org/2000/svg" width="24px" height="24px" fill="currentColor" viewBox="0 0 256 256">
                  <path d="M232,64H208V56a16,16,0,0,0-16-16H64A16,16,0,0,0,48,56v8H24A16,16,0,0,0,8,80V96a40,40,0,0,0,40,40h3.65A80.13,80.13,0,0,0,120,191.61V216H96a8,8,0,0,0,0,16h64a8,8,0,0,0,0-16H136V191.58c31.94-3.23,58.44-25.64,68.08-55.58H208a40,40,0,0,0,40-40V80A16,16,0,0,0,232,64ZM48,120A24,24,0,0,1,24,96V80H48v32q0,4,.39,8Zm144-8.9c0,35.52-28.49,64.64-63.51,64.9H128a64,64,0,0,1-64-64V56H192ZM232,96a24,24,0,0,1-24,24h-.5a81.81,81.81,0,0,0,.5-8.9V80h24Z"></path>
                </svg>
              )}
              {item.icon === 'Note' && (
                <svg xmlns="http://www.w3.org/2000/svg" width="24px" height="24px" fill="currentColor" viewBox="0 0 256 256">
                  <path d="M216,40H40A16,16,0,0,0,24,56V200a16,16,0,0,0,16,16H216a16,16,0,0,0,16-16V56A16,16,0,0,0,216,40ZM40,56H216v96H176a16,16,0,0,0-16,16v48H40Zm152,144V168h24v32Z"></path>
                </svg>
              )}
              {item.icon === 'Case Study' && (
                <svg xmlns="http://www.w3.org/2000/svg" width="24px" height="24px" fill="currentColor" viewBox="0 0 256 256">
                  <path d="M128,16A112,112,0,1,0,240,128,112.13,112.13,0,0,0,128,16Zm0,208a96,96,0,1,1,96-96A96.11,96.11,0,0,1,128,224Z"></path>
                </svg>
              )}
              {item.icon === 'Tree' && (
                <svg xmlns="http://www.w3.org/2000/svg" width="24px" height="24px" fill="currentColor" viewBox="0 0 256 256">
                  <path d="M198.1,62.6a76,76,0,0,0-140.2,0A72.27,72.27,0,0,0,16,127.8C15.89,166.62,47.36,199,86.14,200A71.68,71.68,0,0,0,120,192.49V232a8,8,0,0,0,16,0V192.49A71.45,71.45,0,0,0,168,200l1.86,0c38.78-1,70.25-33.36,70.14-72.18A72.26,72.26,0,0,0,198.1,62.6ZM169.45,184a55.61,55.61,0,0,1-32.52-9.4q-.47-.3-.93-.57V132.94l43.58-21.78a8,8,0,1,0-7.16-14.32L136,115.06V88a8,8,0,0,0-16,0v51.06L83.58,120.84a8,8,0,1,0-7.16,14.32L120,156.94V174q-.47.27-.93.57A55.7,55.7,0,0,1,86.55,184a56,56,0,0,1-22-106.86,15.9,15.9,0,0,0,8.05-8.33,60,60,0,0,1,110.7,0,15.9,15.9,0,0,0,8.05,8.33,56,56,0,0,1-22,106.86Z"></path>
                </svg>
              )}
              {item.icon === 'Swipe' && (
                <svg xmlns="http://www.w3.org/2000/svg" width="24px" height="24px" fill="currentColor" viewBox="0 0 256 256">
                  <path d="M216,64H176V56a16,16,0,0,0-16-16H136V24a8,8,0,0,0-16,0V40H96A16,16,0,0,0,80,56v8H40A16,16,0,0,0,24,80V200a16,16,0,0,0,16,16H216a16,16,0,0,0,16-16V80A16,16,0,0,0,216,64ZM96,56h64v8H96ZM216,200H40V80H216V200ZM128,96a12,12,0,1,0,12,12A12,12,0,0,0,128,96Zm0,48a12,12,0,1,0,12,12A12,12,0,0,0,128,144Zm40-24a12,12,0,1,0,12,12A12,12,0,0,0,168,120ZM88,120a12,12,0,1,0,12,12A12,12,0,0,0,88,120Z"></path>
                </svg>
              )}
            </div>
            <span className={styles.tooltip}>{item.name}</span>
          </Link>
        ))}
      </div>
      
      {/* Profile Icon at Bottom */}
      <div className={styles.profileContainer}>
        <Link href="/profile" className={styles.navItem}>
          <div className={styles.iconWrapper}>
            <svg xmlns="http://www.w3.org/2000/svg" width="24px" height="24px" fill="currentColor" viewBox="0 0 256 256">
              <path d="M128,24A104,104,0,1,0,232,128,104.11,104.11,0,0,0,128,24ZM74.08,197.5a64,64,0,0,1,107.84,0,87.83,87.83,0,0,1-107.84,0ZM96,120a32,32,0,1,1,32,32A32,32,0,0,1,96,120Zm97.76,66.41a79.66,79.66,0,0,0-36.06-28.75,48,48,0,1,0-59.4,0,79.66,79.66,0,0,0-36.06,28.75,88,88,0,1,1,131.52,0Z"></path>
            </svg>
          </div>
          <span className={styles.tooltip}>Profile</span>
        </Link>
      </div>
    </div>
  );
};

export default NewSidebar; 