'use client';
import { useEffect, useState, useRef } from 'react';
import Link from 'next/link';
import { useRouter, usePathname } from 'next/navigation';
import XPProgress from '../ui/XPProgress';
import DarkModeToggle from '../ui/DarkModeToggle';

// Composants pour les menus déroulants
const ProfileDropdown = ({ pathname }: { pathname: string | null }) => {
    const [profileMenuOpen, setProfileMenuOpen] = useState(false);
    const profileMenuRef = useRef<HTMLDivElement>(null);

    // Fermer le menu lorsqu'on clique en dehors
    useEffect(() => {
        function handleClickOutside(event: MouseEvent) {
            if (profileMenuRef.current && !profileMenuRef.current.contains(event.target as Node)) {
                setProfileMenuOpen(false);
            }
        }
        
        document.addEventListener("mousedown", handleClickOutside);
        return () => {
            document.removeEventListener("mousedown", handleClickOutside);
        };
    }, []);

    return (
        <div className="relative inline-block text-left" ref={profileMenuRef}>
            <button
                onClick={() => setProfileMenuOpen(!profileMenuOpen)}
                className={`px-4 py-2 text-sm font-medium rounded-md transition-colors duration-150 ease-in-out flex items-center
                    ${pathname === '/profile' || pathname?.startsWith('/profile/')
                        ? 'text-blue-700 bg-blue-50 dark:text-blue-400 dark:bg-gray-800'
                        : 'text-gray-700 hover:text-blue-600 hover:bg-gray-50 dark:text-gray-300 dark:hover:text-gray-100 dark:hover:bg-gray-800'
                    }`}
            >
                Profile
                <svg
                    className={`ml-1 h-4 w-4 transition-transform duration-200 ${profileMenuOpen ? 'rotate-180' : ''}`}
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
            </button>
            
            {profileMenuOpen && (
                <div className="absolute right-0 mt-2 w-48 rounded-md shadow-lg bg-light-background dark:bg-dark-background ring-1 ring-black ring-opacity-5 z-40">
                    <div className="py-1" role="menu" aria-orientation="vertical">
                        <Link
                            href="/profile"
                            onClick={() => setProfileMenuOpen(false)}
                            className={`block px-4 py-2 text-sm ${pathname === '/profile' ? 'bg-blue-50 text-blue-700 dark:bg-gray-800 dark:text-blue-400' : 'text-gray-700 hover:bg-gray-50 hover:text-blue-600 dark:text-gray-300 dark:hover:bg-gray-800 dark:hover:text-gray-100'}`}
                            role="menuitem"
                        >
                            Informations générales
                        </Link>
                        <Link
                            href="/profile/holland-results"
                            onClick={() => setProfileMenuOpen(false)}
                            className={`block px-4 py-2 text-sm ${pathname === '/profile/holland-results' ? 'bg-blue-50 text-blue-700 dark:bg-gray-800 dark:text-blue-400' : 'text-gray-700 hover:bg-gray-50 hover:text-blue-600 dark:text-gray-300 dark:hover:bg-gray-800 dark:hover:text-gray-100'}`}
                            role="menuitem"
                        >
                            Résultats RIASEC
                        </Link>
                    </div>
                </div>
            )}
        </div>
    );
};

// Composant pour le menu déroulant du profil mobile
const MobileProfileMenu = ({
    pathname,
    setMoreMenuOpen,
    setCareerMenuOpen,
    setWorkspaceMenuOpen
}: {
    pathname: string | null;
    setMoreMenuOpen: (open: boolean) => void;
    setCareerMenuOpen: (open: boolean) => void;
    setWorkspaceMenuOpen: (open: boolean) => void;
}) => {
    const [profileMobileMenuOpen, setProfileMobileMenuOpen] = useState(false);
    const profileMobileMenuRef = useRef<HTMLDivElement>(null);
    const router = useRouter();
    
    // Fermer le menu lorsqu'on clique en dehors
    useEffect(() => {
        function handleClickOutside(event: MouseEvent) {
            if (profileMobileMenuRef.current && !profileMobileMenuRef.current.contains(event.target as Node)) {
                setProfileMobileMenuOpen(false);
            }
        }
        
        document.addEventListener("mousedown", handleClickOutside);
        return () => {
            document.removeEventListener("mousedown", handleClickOutside);
        };
    }, []);
    
    return (
        <div className="relative" ref={profileMobileMenuRef}>
            <button
                className={`flex flex-col items-center text-xs w-full ${pathname === '/profile' || pathname?.startsWith('/profile/') ? 'text-blue-600 dark:text-blue-400' : 'text-gray-600 dark:text-gray-400'}`}
                onClick={() => {
                    setMoreMenuOpen(false);
                    setCareerMenuOpen(false);
                    setWorkspaceMenuOpen(false);
                    setProfileMobileMenuOpen(!profileMobileMenuOpen);
                }}
            >
                <span className="material-icons-outlined">person</span>
                <span>Profile</span>
            </button>
            
            {/* Menu du profil pour mobile */}
            {profileMobileMenuOpen && (
                <div className="absolute bottom-full right-0 mb-2 w-48 bg-light-background dark:bg-dark-background rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
                    <div className="py-1">
                        <Link
                            href="/profile"
                            onClick={() => setProfileMobileMenuOpen(false)}
                            className={`flex items-center px-4 py-3 text-sm ${pathname === '/profile' ? 'bg-blue-50 text-blue-600 dark:bg-gray-800 dark:text-blue-400' : 'text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800'}`}
                        >
                            <span className="material-icons-outlined mr-2 text-gray-500 dark:text-gray-400">account_circle</span>
                            Informations générales
                        </Link>
                        <Link
                            href="/profile/holland-results"
                            onClick={() => setProfileMobileMenuOpen(false)}
                            className={`flex items-center px-4 py-3 text-sm ${pathname === '/profile/holland-results' ? 'bg-blue-50 text-blue-600 dark:bg-gray-800 dark:text-blue-400' : 'text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800'}`}
                        >
                            <span className="material-icons-outlined mr-2 text-gray-500 dark:text-gray-400">psychology</span>
                            Résultats RIASEC
                        </Link>
                    </div>
                </div>
            )}
        </div>
    );
};

export default function MainLayout({ 
    children, 
    showNav = true 
}: { 
    children: React.ReactNode, 
    showNav?: boolean 
}) {
    const [isLoggedIn, setIsLoggedIn] = useState(false);
    const [isLoading, setIsLoading] = useState(true);
    const [moreMenuOpen, setMoreMenuOpen] = useState(false);
    const [careerMenuOpen, setCareerMenuOpen] = useState(false);
    const [workspaceMenuOpen, setWorkspaceMenuOpen] = useState(false);
    const moreMenuRef = useRef<HTMLDivElement>(null);
    const careerMenuRef = useRef<HTMLDivElement>(null);
    const workspaceMenuRef = useRef<HTMLDivElement>(null);
    const router = useRouter();
    const pathname = usePathname();

    // Public routes that don't require authentication
    const publicRoutes = ['/login', '/register', '/test-page'];
    const isPublicRoute = pathname ? publicRoutes.includes(pathname) : false;

    useEffect(() => {
        // Check if user is logged in
        const token = localStorage.getItem('access_token') || '';
        console.log('Auth check - Token:', token ? 'Found' : 'Not found', 'Pathname:', pathname);
        
        // Désactivé temporairement pour le développement
        // if (!token && !isPublicRoute && showNav) {
        //     console.log('No token found, redirecting to login');
        //     router.push('/login');
        //     return;
        // }
        
        // Pour le développement, considérer l'utilisateur comme connecté
        const loggedIn = true; // !!token;
        console.log('Setting isLoggedIn to:', loggedIn);
        setIsLoggedIn(loggedIn);
        setIsLoading(false);
    }, [router, isPublicRoute, showNav, pathname]);

    // Close menus when clicking outside
    useEffect(() => {
        function handleClickOutside(event: MouseEvent) {
            if (moreMenuRef.current && !moreMenuRef.current.contains(event.target as Node)) {
                setMoreMenuOpen(false);
            }
            if (careerMenuRef.current && !careerMenuRef.current.contains(event.target as Node)) {
                setCareerMenuOpen(false);
            }
            if (workspaceMenuRef.current && !workspaceMenuRef.current.contains(event.target as Node)) {
                setWorkspaceMenuOpen(false);
            }
        }
        
        document.addEventListener("mousedown", handleClickOutside);
        return () => {
            document.removeEventListener("mousedown", handleClickOutside);
        };
    }, []);

    // Close mobile menus when route changes
    useEffect(() => {
        console.log('Route changed to:', pathname);
        setMoreMenuOpen(false);
        setCareerMenuOpen(false);
        setWorkspaceMenuOpen(false);
    }, [pathname]);

    const handleLogout = () => {
        console.log('Logging out user');
        localStorage.removeItem('access_token');
        router.push('/login');
    };

    const toggleCareerDropdown = () => {
        console.log('Toggling career dropdown');
        setCareerMenuOpen(!careerMenuOpen);
        if (workspaceMenuOpen) setWorkspaceMenuOpen(false);
    };

    const toggleWorkspaceDropdown = () => {
        console.log('Toggling workspace dropdown, current state:', workspaceMenuOpen);
        setWorkspaceMenuOpen(!workspaceMenuOpen);
        if (careerMenuOpen) setCareerMenuOpen(false);
    };

    // For public routes, render immediately without checking auth
    if (isPublicRoute) {
        return (
            <div className="min-h-screen flex flex-col">
                <main className="flex-1 w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
                    {children}
                </main>
            </div>
        );
    }

    // Show loading state while checking authentication
    if (isLoading) {
        return (
            <div className="min-h-screen flex items-center justify-center">
                <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
            </div>
        );
    }

    // Check if current path is in career path section
    const isCareerPath = ['/vector-search', '/find-your-way', '/cv', '/tree'].includes(pathname || '');

    console.log('Rendering layout with isLoggedIn:', isLoggedIn);

    return (
        <div className="min-h-screen flex flex-col bg-stitch-primary text-stitch-sage">
            {/* Desktop Navigation Bar - Only visible on larger screens */}
            {isLoggedIn && (
                <header className="fixed top-0 left-0 right-0 w-full z-50 bg-stitch-primary/90 backdrop-blur-md border-b border-stitch-border shadow-sm hidden md:block font-departure header">
                    <div className="layout-container mx-auto">
                        <div className="flex justify-between py-3">
                            {/* Left Side - Logo and Primary Navigation */}
                            <div className="flex items-center space-x-8">
                                {/* Logo */}
                                <Link href="/" className="flex-shrink-0 flex items-center">
                                    <span className="text-xl font-bold tracking-tight text-stitch-accent font-departure">
                                        Navigo
                                    </span>
                                </Link>
                                
                                {/* Primary Navigation */}
                                <div className="flex items-center space-x-1">
                                    <Link 
                                        href="/chat" 
                                        className={`px-4 py-2 text-sm font-bold rounded-md transition-colors duration-150 ease-in-out font-departure
                                            ${pathname === '/chat'
                                                ? 'text-stitch-accent bg-stitch-primary/50'
                                                : 'text-stitch-sage hover:text-stitch-accent hover:bg-stitch-primary/30'
                                            }`}
                                    >
                                        Mentor
                                    </Link>
                                    
                                    <Link 
                                        href="/peers" 
                                        className={`px-4 py-2 text-sm font-bold rounded-md transition-colors duration-150 ease-in-out font-departure
                                            ${pathname === '/peers'
                                                ? 'text-stitch-accent bg-stitch-primary/50'
                                                : 'text-stitch-sage hover:text-stitch-accent hover:bg-stitch-primary/30'
                                            }`}
                                    >
                                        Network
                                    </Link>


                                    {/* Career Path Dropdown */}
                                    <div className="relative" ref={careerMenuRef}>
                                        <button 
                                            onClick={toggleCareerDropdown}
                                            className={`group px-4 py-2 text-sm font-bold rounded-md transition-colors duration-150 ease-in-out flex items-center font-departure
                                                ${isCareerPath
                                                    ? 'text-stitch-accent bg-stitch-primary/50'
                                                    : 'text-stitch-sage hover:text-stitch-accent hover:bg-stitch-primary/30'
                                                }`}
                                        >
                                            Career Growth
                                            <svg className={`ml-1 h-4 w-4 transition-transform duration-200 ${careerMenuOpen ? 'rotate-180' : ''}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                                            </svg>
                                        </button>
                                        
                                        {careerMenuOpen && (
                                            <div className="absolute left-0 mt-2 w-56 rounded-md shadow-lg bg-stitch-primary border border-stitch-border ring-1 ring-black ring-opacity-5 z-40">
                                                <div className="py-1" role="menu" aria-orientation="vertical">
                                                    <Link
                                                        href="/vector-search"
                                                        className={`block px-4 py-2 text-sm font-departure ${pathname === '/vector-search' ? 'bg-stitch-primary/50 text-stitch-accent' : 'text-stitch-sage hover:bg-stitch-primary/30 hover:text-stitch-accent'}`}
                                                        role="menuitem"
                                                    >
                                                        Career Insights
                                                    </Link>
                                                    <Link
                                                        href="/find-your-way"
                                                        className={`block px-4 py-2 text-sm font-departure ${pathname === '/find-your-way' ? 'bg-stitch-primary/50 text-stitch-accent' : 'text-stitch-sage hover:bg-stitch-primary/30 hover:text-stitch-accent'}`}
                                                        role="menuitem"
                                                    >
                                                        Pathway Explorer
                                                    </Link>
                                                    <Link
                                                        href="/career"
                                                        className={`block px-4 py-2 text-sm font-departure ${pathname === '/career' ? 'bg-stitch-primary/50 text-stitch-accent' : 'text-stitch-sage hover:bg-stitch-primary/30 hover:text-stitch-accent'}`}
                                                        role="menuitem"
                                                    >
                                                        Career Explorer
                                                    </Link>
                                                    <Link
                                                        href="/enhanced-skills"
                                                        className={`block px-4 py-2 text-sm font-departure ${pathname === '/enhanced-skills' ? 'bg-stitch-primary/50 text-stitch-accent' : 'text-stitch-sage hover:bg-stitch-primary/30 hover:text-stitch-accent'}`}
                                                        role="menuitem"
                                                    >
                                                        Enhanced Skills Path
                                                    </Link>
                                                    <Link
                                                        href="/holland-test"
                                                        className={`block px-4 py-2 text-sm font-departure ${pathname === '/holland-test' ? 'bg-stitch-primary/50 text-stitch-accent' : 'text-stitch-sage hover:bg-stitch-primary/30 hover:text-stitch-accent'}`}
                                                        role="menuitem"
                                                    >
                                                        Test Holland (RIASEC)
                                                    </Link>
                                                    <Link
                                                        href="/case-study-journey"
                                                        className={`block px-4 py-2 text-sm font-departure ${pathname === '/case-study-journey' ? 'bg-stitch-primary/50 text-stitch-accent' : 'text-stitch-sage hover:bg-stitch-primary/30 hover:text-stitch-accent'}`}
                                                    >
                                                        Étude de Cas Navigo
                                                    </Link>
                                                    {/* Resume Studio Link - Commented out for AWS deployment
                                                    <Link
                                                        href="/cv"
                                                        className={`block px-4 py-2 text-sm ${pathname === '/cv' ? 'bg-blue-50 text-blue-700 dark:bg-gray-800 dark:text-blue-400' : 'text-gray-700 hover:bg-gray-50 hover:text-blue-600 dark:text-gray-300 dark:hover:bg-gray-800 dark:hover:text-gray-100'}`}
                                                        role="menuitem"
                                                    >
                                                        Resume Studio
                                                    </Link>
                                                    */}
                                                </div>
                                            </div>
                                        )}
                                    </div>

                                    {/* Workspace Dropdown */}
                                    <div className="relative inline-block text-left" ref={workspaceMenuRef}>
                                        <button
                                            type="button"
                                            onClick={() => setWorkspaceMenuOpen(!workspaceMenuOpen)}
                                            className="inline-flex justify-center w-full px-4 py-2 text-sm font-bold text-stitch-sage hover:text-stitch-accent hover:bg-stitch-primary/30 rounded-md transition-colors duration-150 ease-in-out font-departure"
                                        >
                                            Workspace
                                            <svg
                                            className={`ml-2 h-4 w-4 transition-transform duration-200 ${workspaceMenuOpen ? 'rotate-180' : ''}`}
                                            xmlns="http://www.w3.org/2000/svg"
                                            viewBox="0 0 20 20"
                                            fill="currentColor"
                                            aria-hidden="true"
                                            >
                                            <path
                                                fillRule="evenodd"
                                                d="M5.23 7.21a.75.75 0 011.06.02L10 10.94l3.71-3.71a.75.75 0 111.06 1.06l-4.25 4.25a.75.75 0 01-1.06 0L5.21 8.27a.75.75 0 01.02-1.06z"
                                                clipRule="evenodd"
                                            />
                                            </svg>
                                        </button>

                                        <div className={`absolute z-10 mt-2 w-44 origin-top-right rounded-md bg-stitch-primary border border-stitch-border shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none ${workspaceMenuOpen ? 'block' : 'hidden'}`}>
                                            <div className="py-1">
                                            <Link
                                                href="/space"
                                                className={`block px-4 py-2 text-sm rounded-md transition-colors duration-150 ease-in-out font-departure
                                                ${pathname === '/space'
                                                    ? 'text-stitch-accent bg-stitch-primary/50'
                                                    : 'text-stitch-sage hover:text-stitch-accent hover:bg-stitch-primary/30'
                                                }`}
                                            >
                                                Space
                                            </Link>
                                            <Link
                                                href="/tree-path"
                                                className={`block px-4 py-2 text-sm rounded-md transition-colors duration-150 ease-in-out font-departure
                                                ${pathname === '/tree-path'
                                                    ? 'text-stitch-accent bg-stitch-primary/50'
                                                    : 'text-stitch-sage hover:text-stitch-accent hover:bg-stitch-primary/30'
                                                }`}
                                            >
                                                Tree Path
                                            </Link>
                                            </div>
                                        </div>
                                        </div>
                                </div>
                            </div>

                            
                            
                            {/* Right Side - XP Progress, Dark Mode Toggle, User Profile & Logout */}
                            <div className="flex items-center space-x-4">
                                {/* XP Progress Bar */}
                                <XPProgress className="mr-2" />
                                
                                {/* Dark Mode Toggle - Added to the left of Profile */}
                                <DarkModeToggle />
                                
                                <ProfileDropdown pathname={pathname} />
                                
                                <button 
                                    onClick={handleLogout}
                                    className="px-4 py-2 text-sm font-bold rounded-md text-stitch-sage hover:text-red-500 hover:bg-stitch-primary/30 transition-colors duration-150 ease-in-out font-departure"
                                >
                                    Sign Out
                                </button>
                            </div>
                        </div>
                    </div>
                </header>
            )}

            {/* Main content area */}
            <main className={`flex-1 layout-container mx-auto ${isLoggedIn ? 'pt-0 md:pt-20 pb-16 md:pb-8' : 'py-8'}`}>
                {children}
            </main>

            {/* Mobile Bottom Navigation (only visible on smaller screens) */}
            {isLoggedIn && (
                <div className="fixed bottom-0 left-0 right-0 w-full bg-stitch-primary border-t border-stitch-border md:hidden z-50 font-departure">
                    <div className="grid grid-cols-5 py-2">
                        <Link 
                            href="/chat" 
                            className={`flex flex-col items-center text-xs font-departure ${pathname === '/chat' ? 'text-stitch-accent' : 'text-stitch-sage'}`}
                        >
                            <span className="material-icons-outlined">chat</span>
                            <span>Chat</span>
                        </Link>
                        <Link 
                            href="/peers" 
                            className={`flex flex-col items-center text-xs font-departure ${pathname === '/peers' ? 'text-stitch-accent' : 'text-stitch-sage'}`}
                        >
                            <span className="material-icons-outlined">people</span>
                            <span>Peers</span>
                        </Link>
                        
                        {/* More menu button */}
                        <div className="relative">
                            <button 
                                className="flex flex-col items-center w-full text-xs text-stitch-sage font-departure"
                                onClick={() => setMoreMenuOpen(!moreMenuOpen)}
                                aria-label="More options"
                            >
                                <span className="material-icons-outlined">more_horiz</span>
                                <span>More</span>
                            </button>
                            
                            {/* More dropdown menu */}
                            {moreMenuOpen && (
                                <div 
                                    ref={moreMenuRef}
                                    className="absolute bottom-full left-1/2 transform -translate-x-1/2 w-56 mb-2 bg-stitch-primary rounded-lg shadow-lg border border-stitch-border overflow-hidden"
                                >
                                    <div className="py-1">
                                        {/* Dropdown menu items with dark mode styles */}
                                        <Link 
                                            href="/vector-search" 
                                            className={`flex items-center px-4 py-3 text-sm ${pathname === '/vector-search' ? 'bg-stitch-primary/50 text-stitch-accent' : 'text-stitch-sage hover:bg-stitch-primary/30 hover:text-stitch-accent'}`}
                                        >
                                            <span className="material-icons-outlined mr-2 text-stitch-sage">trending_up</span>
                                            Career Recommendation
                                        </Link>
                                        <Link 
                                            href="/find-your-way" 
                                            className={`flex items-center px-4 py-3 text-sm ${pathname === '/find-your-way' ? 'bg-stitch-primary/50 text-stitch-accent' : 'text-stitch-sage hover:bg-stitch-primary/30 hover:text-stitch-accent'}`}
                                        >
                                            <span className="material-icons-outlined mr-2 text-stitch-sage">explore</span>
                                            Pathway Explorer
                                        </Link>
                                        <Link 
                                            href="/career" 
                                            className={`flex items-center px-4 py-3 text-sm ${pathname === '/career' ? 'bg-stitch-primary/50 text-stitch-accent' : 'text-stitch-sage hover:bg-stitch-primary/30 hover:text-stitch-accent'}`}
                                        >
                                            <span className="material-icons-outlined mr-2 text-stitch-sage">business</span>
                                            Career Explorer
                                        </Link>
                                        <Link 
                                            href="/enhanced-skills" 
                                            className={`flex items-center px-4 py-3 text-sm ${
                                                pathname === '/enhanced-skills'
                                                    ? 'bg-stitch-primary/50 text-stitch-accent font-bold'
                                                    : 'text-stitch-sage hover:bg-stitch-primary/30 hover:text-stitch-accent'
                                            }`}
                                        >
                                            <span className="material-icons-outlined mr-2 text-stitch-sage">school</span>
                                            Enhanced Skills Path
                                        </Link>
                                        <Link
                                            href="/holland-test"
                                            className={`flex items-center px-4 py-3 text-sm ${
                                                pathname === '/holland-test'
                                                    ? 'bg-stitch-primary/50 text-stitch-accent font-bold'
                                                    : 'text-stitch-sage hover:bg-stitch-primary/30 hover:text-stitch-accent'
                                            }`}
                                        >
                                            <span className="material-icons-outlined mr-2 text-stitch-sage">psychology</span>
                                            Test Holland (RIASEC)
                                        </Link>
                                        <div className="border-t border-stitch-border mt-1"></div>
                                        
                                        {/* Dark mode toggle in mobile menu */}
                                        <div className="flex items-center justify-between w-full px-4 py-3 text-sm text-stitch-sage">
                                            <div className="flex items-center">
                                                <span className="material-icons-outlined mr-2 text-stitch-sage">
                                                    {/* Icon will be determined by the dark mode state */}
                                                    dark_mode
                                                </span>
                                                Dark Mode
                                            </div>
                                            <DarkModeToggle className="p-1" />
                                        </div>
                                        
                                        <button 
                                            onClick={handleLogout}
                                            className="flex items-center w-full px-4 py-3 text-sm text-red-500 hover:bg-stitch-primary/30"
                                        >
                                            <span className="material-icons-outlined mr-2">logout</span>
                                            Logout
                                        </button>
                                    </div>
                                </div>
                            )}
                        </div>
                        
                        <div className="relative">
                            <Link
                                href="/space"
                                className={`flex flex-col items-center w-full text-xs ${
                                    pathname === '/space' || pathname === '/tree-path'
                                        ? 'text-stitch-accent'
                                        : 'text-stitch-sage'
                                }`}
                                onClick={(e) => {
                                    e.preventDefault();
                                    setWorkspaceMenuOpen(!workspaceMenuOpen);
                                }}
                            >
                                <span className="material-icons-outlined">folder</span>
                                <span>Workspace</span>
                            </Link>
                            
                        {/* Mobile Workspace Dropdown Menu */}
                        {workspaceMenuOpen && (
                            <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 w-56 mb-2 bg-stitch-primary rounded-lg shadow-lg border border-stitch-border overflow-hidden">
                                <div className="py-1">
                                    <Link 
                                        href="/space"
                                        onClick={() => setWorkspaceMenuOpen(false)}
                                        className={`block px-4 py-2 text-sm rounded-md transition-colors duration-150 ease-in-out
                                            ${pathname === '/space'
                                                ? 'text-stitch-accent bg-stitch-primary/50'
                                                : 'text-stitch-sage hover:text-stitch-accent hover:bg-stitch-primary/30'
                                            }`}
                                    >
                                        <span className="material-icons-outlined mr-2 text-stitch-sage">space_dashboard</span>
                                        Space
                                    </Link>
                                    <Link 
                                        href="/tree-path"
                                        onClick={() => setWorkspaceMenuOpen(false)}
                                        className={`block px-4 py-2 text-sm rounded-md transition-colors duration-150 ease-in-out
                                            ${pathname === '/tree-path'
                                                ? 'text-stitch-accent bg-stitch-primary/50'
                                                : 'text-stitch-sage hover:text-stitch-accent hover:bg-stitch-primary/30'
                                            }`}
                                    >
                                        <span className="material-icons-outlined mr-2 text-stitch-sage">account_tree</span>
                                        Tree Path
                                    </Link>
                                </div>
                            </div>
                        )}
                        </div>
                        <MobileProfileMenu
                            pathname={pathname}
                            setMoreMenuOpen={setMoreMenuOpen}
                            setCareerMenuOpen={setCareerMenuOpen}
                            setWorkspaceMenuOpen={setWorkspaceMenuOpen}
                        />
                    </div>
                </div>
            )}
        </div>
    );
}