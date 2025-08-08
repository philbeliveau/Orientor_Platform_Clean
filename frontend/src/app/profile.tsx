// src/app/profile/page.tsx
'use client';
import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@clerk/nextjs';
import axios from 'axios';
// import { AxiosError } from 'axios';

const ProfilePage = () => {
    const router = useRouter();
    const { getToken, isLoaded, isSignedIn } = useAuth();
    const [activeTab, setActiveTab] = useState('basic');
    const [formData, setFormData] = useState({
        // Basic Info
        email: '',
        password: '',
        name: '',
        age: '',
        sex: '',
        country: '',
        state_province: '',
        
        // Academic Info
        major: '',
        year: '',
        gpa: '',
        learning_style: '',
        
        // Personal Info
        hobbies: '',
        unique_quality: '',
        story: '',
        favorite_movie: '',
        favorite_book: '',
        favorite_celebrities: '',
        
        // Career Info
        job_title: '',
        industry: '',
        years_experience: '',
        education_level: '',
        career_goals: '',
        skills: '',
        interests: ''
    });
    const [message, setMessage] = useState('');

    useEffect(() => {
        if (!isLoaded) return; // Wait for auth to load
        
        if (!isSignedIn) {
            router.push('/sign-in');
            return;
        }
    }, [isLoaded, isSignedIn, router]);

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));
    };

    const handleUpdate = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!isLoaded || !isSignedIn) return;
        
        try {
            const token = await getToken();
            if (!token) {
                router.push('/sign-in');
                return;
            }
            
            await axios.put( 
                'http://localhost:8000/users/update',
                formData,
                {
                    headers: {
                        Authorization: `Bearer ${token}`,
                        'Content-Type': 'application/json',
                    },
                }
            );
            setMessage('Profile updated successfully!');
        } catch (error: any) {
            console.error('Error updating profile:', error);
            if (error.response?.status === 401) {
                router.push('/sign-in');
                return;
            }
            const axiosError = error as { response?: { data?: { detail?: string } } };
            setMessage('Error updating profile: ' + (axiosError.response?.data?.detail || 'Unknown error'));
        }
    };

    const renderTabContent = () => {
        switch (activeTab) {
            case 'basic':
                return (
                    <div>
                        <div className="flex max-w-[480px] flex-wrap items-end gap-4 px-4 py-3">
                            <label className="flex flex-col min-w-40 flex-1">
                                <p className="text-[#0d1b13] text-base font-medium leading-normal pb-2">Preferred Name</p>
                                <input
                                    placeholder="Enter your preferred name"
                                    className="form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-xl text-[#0d1b13] focus:outline-0 focus:ring-0 border-none bg-[#e7f3ec] focus:border-none h-14 placeholder:text-[#4c9a6a] p-4 text-base font-normal leading-normal"
                                    name="name"
                                    value={formData.name}
                                    onChange={handleInputChange}
                                />
                            </label>
                        </div>
                        <div className="flex max-w-[480px] flex-wrap items-end gap-4 px-4 py-3">
                            <label className="flex flex-col min-w-40 flex-1">
                                <p className="text-[#0d1b13] text-base font-medium leading-normal pb-2">Short Bio</p>
                                <textarea
                                    placeholder="Tell us a bit about yourself"
                                    className="form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-xl text-[#0d1b13] focus:outline-0 focus:ring-0 border-none bg-[#e7f3ec] focus:border-none min-h-36 placeholder:text-[#4c9a6a] p-4 text-base font-normal leading-normal"
                                    name="story"
                                    value={formData.story}
                                    onChange={handleInputChange}
                                ></textarea>
                            </label>
                        </div>
                        <div className="flex max-w-[480px] flex-wrap items-end gap-4 px-4 py-3">
                            <label className="flex flex-col min-w-40 flex-1">
                                <p className="text-[#0d1b13] text-base font-medium leading-normal pb-2">Interests</p>
                                <input
                                    placeholder="What are you passionate about?"
                                    className="form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-xl text-[#0d1b13] focus:outline-0 focus:ring-0 border-none bg-[#e7f3ec] focus:border-none h-14 placeholder:text-[#4c9a6a] p-4 text-base font-normal leading-normal"
                                    name="interests"
                                    value={formData.interests}
                                    onChange={handleInputChange}
                                />
                            </label>
                        </div>
                        <div className="flex max-w-[480px] flex-wrap items-end gap-4 px-4 py-3">
                            <label className="flex flex-col min-w-40 flex-1">
                                <p className="text-[#0d1b13] text-base font-medium leading-normal pb-2">Major</p>
                                <select
                                    className="form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-xl text-[#0d1b13] focus:outline-0 focus:ring-0 border-none bg-[#e7f3ec] focus:border-none h-14 bg-[image:--select-button-svg] placeholder:text-[#4c9a6a] p-4 text-base font-normal leading-normal"
                                    name="major"
                                    value={formData.major}
                                    onChange={handleInputChange}
                                >
                                    <option value="">Select your major</option>
                                    <option value="Computer Science">Computer Science</option>
                                    <option value="Engineering">Engineering</option>
                                    <option value="Business">Business</option>
                                    <option value="Arts">Arts</option>
                                </select>
                            </label>
                        </div>
                        <div className="flex max-w-[480px] flex-wrap items-end gap-4 px-4 py-3">
                            <label className="flex flex-col min-w-40 flex-1">
                                <p className="text-[#0d1b13] text-base font-medium leading-normal pb-2">Age</p>
                                <select
                                    className="form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-xl text-[#0d1b13] focus:outline-0 focus:ring-0 border-none bg-[#e7f3ec] focus:border-none h-14 bg-[image:--select-button-svg] placeholder:text-[#4c9a6a] p-4 text-base font-normal leading-normal"
                                    name="age"
                                    value={formData.age}
                                    onChange={handleInputChange}
                                >
                                    <option value="">Select your age</option>
                                    <option value="18-24">18-24</option>
                                    <option value="25-34">25-34</option>
                                    <option value="35-44">35-44</option>
                                    <option value="45+">45+</option>
                                </select>
                            </label>
                        </div>
                        <div className="flex max-w-[480px] flex-wrap items-end gap-4 px-4 py-3">
                            <label className="flex flex-col min-w-40 flex-1">
                                <p className="text-[#0d1b13] text-base font-medium leading-normal pb-2">Sex</p>
                                <select
                                    className="form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-xl text-[#0d1b13] focus:outline-0 focus:ring-0 border-none bg-[#e7f3ec] focus:border-none h-14 bg-[image:--select-button-svg] placeholder:text-[#4c9a6a] p-4 text-base font-normal leading-normal"
                                    name="sex"
                                    value={formData.sex}
                                    onChange={handleInputChange}
                                >
                                    <option value="">Select your sex</option>
                                    <option value="Male">Male</option>
                                    <option value="Female">Female</option>
                                    <option value="Other">Other</option>
                                </select>
                            </label>
                        </div>
                        <div className="flex max-w-[480px] flex-wrap items-end gap-4 px-4 py-3">
                            <label className="flex flex-col min-w-40 flex-1">
                                <p className="text-[#0d1b13] text-base font-medium leading-normal pb-2">Favorite Movie</p>
                                <input
                                    placeholder="What's your favorite movie?"
                                    className="form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-xl text-[#0d1b13] focus:outline-0 focus:ring-0 border-none bg-[#e7f3ec] focus:border-none h-14 placeholder:text-[#4c9a6a] p-4 text-base font-normal leading-normal"
                                    name="favorite_movie"
                                    value={formData.favorite_movie}
                                    onChange={handleInputChange}
                                />
                            </label>
                        </div>
                        <div className="flex max-w-[480px] flex-wrap items-end gap-4 px-4 py-3">
                            <label className="flex flex-col min-w-40 flex-1">
                                <p className="text-[#0d1b13] text-base font-medium leading-normal pb-2">Favorite Book</p>
                                <input
                                    placeholder="What's your favorite book?"
                                    className="form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-xl text-[#0d1b13] focus:outline-0 focus:ring-0 border-none bg-[#e7f3ec] focus:border-none h-14 placeholder:text-[#4c9a6a] p-4 text-base font-normal leading-normal"
                                    name="favorite_book"
                                    value={formData.favorite_book}
                                    onChange={handleInputChange}
                                />
                            </label>
                        </div>
                    </div>
                );
            case 'academic':
                return (
                    <div>
                        <div className="flex max-w-[480px] flex-wrap items-end gap-4 px-4 py-3">
                            <label className="flex flex-col min-w-40 flex-1">
                                <p className="text-[#0d1b13] text-base font-medium leading-normal pb-2">Major</p>
                                <select
                                    className="form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-xl text-[#0d1b13] focus:outline-0 focus:ring-0 border-none bg-[#e7f3ec] focus:border-none h-14 bg-[image:--select-button-svg] placeholder:text-[#4c9a6a] p-4 text-base font-normal leading-normal"
                                    name="major"
                                    value={formData.major}
                                    onChange={handleInputChange}
                                >
                                    <option value="">Select your major</option>
                                    <option value="Computer Science">Computer Science</option>
                                    <option value="Engineering">Engineering</option>
                                    <option value="Business">Business</option>
                                    <option value="Arts">Arts</option>
                                </select>
                            </label>
                        </div>
                        <div className="flex max-w-[480px] flex-wrap items-end gap-4 px-4 py-3">
                            <label className="flex flex-col min-w-40 flex-1">
                                <p className="text-[#0d1b13] text-base font-medium leading-normal pb-2">Year</p>
                                <select
                                    className="form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-xl text-[#0d1b13] focus:outline-0 focus:ring-0 border-none bg-[#e7f3ec] focus:border-none h-14 bg-[image:--select-button-svg] placeholder:text-[#4c9a6a] p-4 text-base font-normal leading-normal"
                                    name="year"
                                    value={formData.year}
                                    onChange={handleInputChange}
                                >
                                    <option value="">Select your year</option>
                                    <option value="1">First Year</option>
                                    <option value="2">Second Year</option>
                                    <option value="3">Third Year</option>
                                    <option value="4">Fourth Year</option>
                                    <option value="5+">Fifth Year or Beyond</option>
                                </select>
                            </label>
                        </div>
                        <div className="flex max-w-[480px] flex-wrap items-end gap-4 px-4 py-3">
                            <label className="flex flex-col min-w-40 flex-1">
                                <p className="text-[#0d1b13] text-base font-medium leading-normal pb-2">GPA</p>
                                <input
                                    placeholder="Your GPA"
                                    className="form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-xl text-[#0d1b13] focus:outline-0 focus:ring-0 border-none bg-[#e7f3ec] focus:border-none h-14 placeholder:text-[#4c9a6a] p-4 text-base font-normal leading-normal"
                                    name="gpa"
                                    value={formData.gpa}
                                    onChange={handleInputChange}
                                    type="number"
                                    step="0.01"
                                    min="0"
                                    max="4.0"
                                />
                            </label>
                        </div>
                        <div className="flex max-w-[480px] flex-wrap items-end gap-4 px-4 py-3">
                            <label className="flex flex-col min-w-40 flex-1">
                                <p className="text-[#0d1b13] text-base font-medium leading-normal pb-2">Learning Style</p>
                                <select
                                    className="form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-xl text-[#0d1b13] focus:outline-0 focus:ring-0 border-none bg-[#e7f3ec] focus:border-none h-14 bg-[image:--select-button-svg] placeholder:text-[#4c9a6a] p-4 text-base font-normal leading-normal"
                                    name="learning_style"
                                    value={formData.learning_style}
                                    onChange={handleInputChange}
                                >
                                    <option value="">Select your learning style</option>
                                    <option value="Visual">Visual</option>
                                    <option value="Auditory">Auditory</option>
                                    <option value="Reading/Writing">Reading/Writing</option>
                                    <option value="Kinesthetic">Kinesthetic</option>
                                </select>
                            </label>
                        </div>
                    </div>
                );
            case 'personal':
                return (
                    <div>
                        <div className="flex max-w-[480px] flex-wrap items-end gap-4 px-4 py-3">
                            <label className="flex flex-col min-w-40 flex-1">
                                <p className="text-[#0d1b13] text-base font-medium leading-normal pb-2">Hobbies</p>
                                <textarea
                                    placeholder="Enter your hobbies, separated by commas"
                                    className="form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-xl text-[#0d1b13] focus:outline-0 focus:ring-0 border-none bg-[#e7f3ec] focus:border-none min-h-36 placeholder:text-[#4c9a6a] p-4 text-base font-normal leading-normal"
                                    name="hobbies"
                                    value={formData.hobbies}
                                    onChange={handleInputChange}
                                ></textarea>
                            </label>
                        </div>
                        <div className="flex max-w-[480px] flex-wrap items-end gap-4 px-4 py-3">
                            <label className="flex flex-col min-w-40 flex-1">
                                <p className="text-[#0d1b13] text-base font-medium leading-normal pb-2">Unique Quality</p>
                                <textarea
                                    placeholder="What makes you unique?"
                                    className="form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-xl text-[#0d1b13] focus:outline-0 focus:ring-0 border-none bg-[#e7f3ec] focus:border-none min-h-36 placeholder:text-[#4c9a6a] p-4 text-base font-normal leading-normal"
                                    name="unique_quality"
                                    value={formData.unique_quality}
                                    onChange={handleInputChange}
                                ></textarea>
                            </label>
                        </div>
                        <div className="flex max-w-[480px] flex-wrap items-end gap-4 px-4 py-3">
                            <label className="flex flex-col min-w-40 flex-1">
                                <p className="text-[#0d1b13] text-base font-medium leading-normal pb-2">Your Story</p>
                                <textarea
                                    placeholder="Tell us your story"
                                    className="form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-xl text-[#0d1b13] focus:outline-0 focus:ring-0 border-none bg-[#e7f3ec] focus:border-none min-h-36 placeholder:text-[#4c9a6a] p-4 text-base font-normal leading-normal"
                                    name="story"
                                    value={formData.story}
                                    onChange={handleInputChange}
                                ></textarea>
                            </label>
                        </div>
                        <div className="flex max-w-[480px] flex-wrap items-end gap-4 px-4 py-3">
                            <label className="flex flex-col min-w-40 flex-1">
                                <p className="text-[#0d1b13] text-base font-medium leading-normal pb-2">Favorite Movie</p>
                                <input
                                    placeholder="What's your favorite movie?"
                                    className="form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-xl text-[#0d1b13] focus:outline-0 focus:ring-0 border-none bg-[#e7f3ec] focus:border-none h-14 placeholder:text-[#4c9a6a] p-4 text-base font-normal leading-normal"
                                    name="favorite_movie"
                                    value={formData.favorite_movie}
                                    onChange={handleInputChange}
                                />
                            </label>
                        </div>
                        <div className="flex max-w-[480px] flex-wrap items-end gap-4 px-4 py-3">
                            <label className="flex flex-col min-w-40 flex-1">
                                <p className="text-[#0d1b13] text-base font-medium leading-normal pb-2">Favorite Book</p>
                                <input
                                    placeholder="What's your favorite book?"
                                    className="form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-xl text-[#0d1b13] focus:outline-0 focus:ring-0 border-none bg-[#e7f3ec] focus:border-none h-14 placeholder:text-[#4c9a6a] p-4 text-base font-normal leading-normal"
                                    name="favorite_book"
                                    value={formData.favorite_book}
                                    onChange={handleInputChange}
                                />
                            </label>
                        </div>
                        <div className="flex max-w-[480px] flex-wrap items-end gap-4 px-4 py-3">
                            <label className="flex flex-col min-w-40 flex-1">
                                <p className="text-[#0d1b13] text-base font-medium leading-normal pb-2">Favorite Celebrities</p>
                                <input
                                    placeholder="Enter names, separated by commas"
                                    className="form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-xl text-[#0d1b13] focus:outline-0 focus:ring-0 border-none bg-[#e7f3ec] focus:border-none h-14 placeholder:text-[#4c9a6a] p-4 text-base font-normal leading-normal"
                                    name="favorite_celebrities"
                                    value={formData.favorite_celebrities}
                                    onChange={handleInputChange}
                                />
                            </label>
                        </div>
                    </div>
                );
            case 'career':
                return (
                    <div>
                        <div className="flex max-w-[480px] flex-wrap items-end gap-4 px-4 py-3">
                            <label className="flex flex-col min-w-40 flex-1">
                                <p className="text-[#0d1b13] text-base font-medium leading-normal pb-2">Job Title</p>
                                <input
                                    placeholder="Your current or desired job title"
                                    className="form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-xl text-[#0d1b13] focus:outline-0 focus:ring-0 border-none bg-[#e7f3ec] focus:border-none h-14 placeholder:text-[#4c9a6a] p-4 text-base font-normal leading-normal"
                                    name="job_title"
                                    value={formData.job_title}
                                    onChange={handleInputChange}
                                />
                            </label>
                        </div>
                        <div className="flex max-w-[480px] flex-wrap items-end gap-4 px-4 py-3">
                            <label className="flex flex-col min-w-40 flex-1">
                                <p className="text-[#0d1b13] text-base font-medium leading-normal pb-2">Industry</p>
                                <input
                                    placeholder="Your industry"
                                    className="form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-xl text-[#0d1b13] focus:outline-0 focus:ring-0 border-none bg-[#e7f3ec] focus:border-none h-14 placeholder:text-[#4c9a6a] p-4 text-base font-normal leading-normal"
                                    name="industry"
                                    value={formData.industry}
                                    onChange={handleInputChange}
                                />
                            </label>
                        </div>
                        <div className="flex max-w-[480px] flex-wrap items-end gap-4 px-4 py-3">
                            <label className="flex flex-col min-w-40 flex-1">
                                <p className="text-[#0d1b13] text-base font-medium leading-normal pb-2">Years Experience</p>
                                <input
                                    placeholder="Years of experience"
                                    className="form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-xl text-[#0d1b13] focus:outline-0 focus:ring-0 border-none bg-[#e7f3ec] focus:border-none h-14 placeholder:text-[#4c9a6a] p-4 text-base font-normal leading-normal"
                                    name="years_experience"
                                    value={formData.years_experience}
                                    onChange={handleInputChange}
                                    type="number"
                                />
                            </label>
                        </div>
                        <div className="flex max-w-[480px] flex-wrap items-end gap-4 px-4 py-3">
                            <label className="flex flex-col min-w-40 flex-1">
                                <p className="text-[#0d1b13] text-base font-medium leading-normal pb-2">Education Level</p>
                                <select
                                    className="form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-xl text-[#0d1b13] focus:outline-0 focus:ring-0 border-none bg-[#e7f3ec] focus:border-none h-14 bg-[image:--select-button-svg] placeholder:text-[#4c9a6a] p-4 text-base font-normal leading-normal"
                                    name="education_level"
                                    value={formData.education_level}
                                    onChange={handleInputChange}
                                >
                                    <option value="">Select your education level</option>
                                    <option value="High School">High School</option>
                                    <option value="Associate's Degree">Associate's Degree</option>
                                    <option value="Bachelor's Degree">Bachelor's Degree</option>
                                    <option value="Master's Degree">Master's Degree</option>
                                    <option value="Doctorate">Doctorate</option>
                                </select>
                            </label>
                        </div>
                        <div className="flex max-w-[480px] flex-wrap items-end gap-4 px-4 py-3">
                            <label className="flex flex-col min-w-40 flex-1">
                                <p className="text-[#0d1b13] text-base font-medium leading-normal pb-2">Career Goals</p>
                                <textarea
                                    placeholder="What are your career goals?"
                                    className="form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-xl text-[#0d1b13] focus:outline-0 focus:ring-0 border-none bg-[#e7f3ec] focus:border-none min-h-36 placeholder:text-[#4c9a6a] p-4 text-base font-normal leading-normal"
                                    name="career_goals"
                                    value={formData.career_goals}
                                    onChange={handleInputChange}
                                ></textarea>
                            </label>
                        </div>
                        <div className="flex max-w-[480px] flex-wrap items-end gap-4 px-4 py-3">
                            <label className="flex flex-col min-w-40 flex-1">
                                <p className="text-[#0d1b13] text-base font-medium leading-normal pb-2">Skills</p>
                                <textarea
                                    placeholder="Enter your skills, separated by commas"
                                    className="form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-xl text-[#0d1b13] focus:outline-0 focus:ring-0 border-none bg-[#e7f3ec] focus:border-none min-h-36 placeholder:text-[#4c9a6a] p-4 text-base font-normal leading-normal"
                                    name="skills"
                                    value={formData.skills}
                                    onChange={handleInputChange}
                                ></textarea>
                            </label>
                        </div>
                        <div className="flex max-w-[480px] flex-wrap items-end gap-4 px-4 py-3">
                            <label className="flex flex-col min-w-40 flex-1">
                                <p className="text-[#0d1b13] text-base font-medium leading-normal pb-2">Interests</p>
                                <textarea
                                    placeholder="Enter your interests, separated by commas"
                                    className="form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-xl text-[#0d1b13] focus:outline-0 focus:ring-0 border-none bg-[#e7f3ec] focus:border-none min-h-36 placeholder:text-[#4c9a6a] p-4 text-base font-normal leading-normal"
                                    name="interests"
                                    value={formData.interests}
                                    onChange={handleInputChange}
                                ></textarea>
                            </label>
                        </div>
                    </div>
                );
            default:
                return null;
        }
    };

    return (
        <div className="relative flex size-full min-h-screen flex-col bg-[#f8fcf9] group/design-root overflow-x-hidden" style={{fontFamily: '"Space Grotesk", "Noto Sans", sans-serif'}}>
            <div className="layout-container flex h-full grow flex-col">
                <header className="flex items-center justify-between whitespace-nowrap border-b border-solid border-b-[#e7f3ec] px-10 py-3">
                    <div className="flex items-center gap-4 text-[#0d1b13]">
                        <div className="size-4">
                            <svg viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path
                                    d="M13.8261 17.4264C16.7203 18.1174 20.2244 18.5217 24 18.5217C27.7756 18.5217 31.2797 18.1174 34.1739 17.4264C36.9144 16.7722 39.9967 15.2331 41.3563 14.1648L24.8486 40.6391C24.4571 41.267 23.5429 41.267 23.1514 40.6391L6.64374 14.1648C8.00331 15.2331 11.0856 16.7722 13.8261 17.4264Z"
                                    fill="currentColor"
                                ></path>
                                <path
                                    fillRule="evenodd"
                                    clipRule="evenodd"
                                    d="M39.998 12.236C39.9944 12.2537 39.9875 12.2845 39.9748 12.3294C39.9436 12.4399 39.8949 12.5741 39.8346 12.7175C39.8168 12.7597 39.7989 12.8007 39.7813 12.8398C38.5103 13.7113 35.9788 14.9393 33.7095 15.4811C30.9875 16.131 27.6413 16.5217 24 16.5217C20.3587 16.5217 17.0125 16.131 14.2905 15.4811C12.0012 14.9346 9.44505 13.6897 8.18538 12.8168C8.17384 12.7925 8.16216 12.767 8.15052 12.7408C8.09919 12.6249 8.05721 12.5114 8.02977 12.411C8.00356 12.3152 8.00039 12.2667 8.00004 12.2612C8.00004 12.261 8 12.2607 8.00004 12.2612C8.00004 12.2359 8.0104 11.9233 8.68485 11.3686C9.34546 10.8254 10.4222 10.2469 11.9291 9.72276C14.9242 8.68098 19.1919 8 24 8C28.8081 8 33.0758 8.68098 36.0709 9.72276C37.5778 10.2469 38.6545 10.8254 39.3151 11.3686C39.9006 11.8501 39.9857 12.1489 39.998 12.236ZM4.95178 15.2312L21.4543 41.6973C22.6288 43.5809 25.3712 43.5809 26.5457 41.6973L43.0534 15.223C43.0709 15.1948 43.0878 15.1662 43.104 15.1371L41.3563 14.1648C43.104 15.1371 43.1038 15.1374 43.104 15.1371L43.1051 15.135L43.1065 15.1325L43.1101 15.1261L43.1199 15.1082C43.1276 15.094 43.1377 15.0754 43.1497 15.0527C43.1738 15.0075 43.2062 14.9455 43.244 14.8701C43.319 14.7208 43.4196 14.511 43.5217 14.2683C43.6901 13.8679 44 13.0689 44 12.2609C44 10.5573 43.003 9.22254 41.8558 8.2791C40.6947 7.32427 39.1354 6.55361 37.385 5.94477C33.8654 4.72057 29.133 4 24 4C18.867 4 14.1346 4.72057 10.615 5.94478C8.86463 6.55361 7.30529 7.32428 6.14419 8.27911C4.99695 9.22255 3.99999 10.5573 3.99999 12.2609C3.99999 13.1275 4.29264 13.9078 4.49321 14.3607C4.60375 14.6102 4.71348 14.8196 4.79687 14.9689C4.83898 15.0444 4.87547 15.1065 4.9035 15.1529C4.91754 15.1762 4.92954 15.1957 4.93916 15.2111L4.94662 15.223L4.95178 15.2312ZM35.9868 18.996L24 38.22L12.0131 18.996C12.4661 19.1391 12.9179 19.2658 13.3617 19.3718C16.4281 20.1039 20.0901 20.5217 24 20.5217C27.9099 20.5217 31.5719 20.1039 34.6383 19.3718C35.082 19.2658 35.5339 19.1391 35.9868 18.996Z"
                                    fill="currentColor"
                                ></path>
                            </svg>
                        </div>
                        <h2 className="text-[#0d1b13] text-lg font-bold leading-tight tracking-[-0.015em]">Navigo</h2>
                    </div>
                    <div className="flex flex-1 justify-end gap-8">
                        <div className="flex items-center gap-9">
                            <a className="text-[#0d1b13] text-sm font-medium leading-normal" href="#">Dashboard</a>
                            <a className="text-[#0d1b13] text-sm font-medium leading-normal" href="#">Explore</a>
                            <a className="text-[#0d1b13] text-sm font-medium leading-normal" href="#">Learn</a>
                            <a className="text-[#0d1b13] text-sm font-medium leading-normal" href="#">Network</a>
                        </div>
                        <button
                            className="flex max-w-[480px] cursor-pointer items-center justify-center overflow-hidden rounded-full h-10 bg-[#e7f3ec] text-[#0d1b13] gap-2 text-sm font-bold leading-normal tracking-[0.015em] min-w-0 px-2.5"
                        >
                            <div className="text-[#0d1b13]" data-icon="Peers" data-size="20px" data-weight="regular">
                                {/* <svg xmlns="http://www.w3.org/2000/svg" width="20px" height="20px" fill="currentColor" viewBox="0 0 256 256">
                                    <path
                                        d="M221.8,175.94C216.25,166.38,208,139.33,208,104a80,80,0,1,0-160,0c0,35.34-8.26,62.38-13.81,71.94A16,16,0,0,0,48,200H88.81a40,40,0,0,0,78.38,0H208a16,16,0,0,0,13.8-24.06ZM128,216a24,24,0,0,1-22.62-16h45.24A24,24,0,0,1,128,216ZM48,184c7.7-13.24,16-43.92,16-80a64,64,0,1,1,128,0c0,36.05,8.28,66.73,16,80Z"
                                    ></path>
                                </svg> */}
                                    <svg xmlns="http://www.w3.org/2000/svg" width="18px" height="18px" fill="currentColor" viewBox="0 0 256 256">
                                    <path 
                                        d="M128,120a48,48,0,1,0-48-48A48,48,0,0,0,128,120Zm0,16c-33.08,0-96,16.54-96,49.38V200a8,8,0,0,0,8,8H216a8,8,0,0,0,8-8v-14.62C224,152.54,161.08,136,128,136Z"
                                    ></path>
                                </svg>
                            </div>
                        </button>
                        <div
                            className="bg-center bg-no-repeat aspect-square bg-cover rounded-full size-10"
                            style={{backgroundImage: 'url("https://lh3.googleusercontent.com/aida-public/AB6AXuDG1setwA6v6owRLfDH-tliRn7h-UI7iRFFETno1LTpH66o2hUcdMla5XKStKxxh0xCHkK0vSOtHKrw6WTHvxqtYPxNk_2edo8lIB4rz1gSNTAdUlAZwmY3vKGeGbqixnWq9dzvkroKkUrJnJLBe7E4EU_QO00MiBrCeo1UmvmFMdwmo8FxtcttCFJ9RYSuM-qlpgJ-kRSrH3vPytAGJljcDubAV4Y5domafp38he3MPZsxPw-Binz24QZMLxo7EyFEkIdiwCMuFwN7")'}}
                        ></div>
                    </div>
                </header>
                <div className="px-40 flex flex-1 justify-center py-5">
                    <div className="layout-content-container flex flex-col max-w-[960px] flex-1">
                        <div className="flex flex-wrap justify-between gap-3 p-4">
                            <div className="flex min-w-72 flex-col gap-3">
                                <p className="text-[#0d1b13] tracking-light text-[32px] font-bold leading-tight">Profile Builder</p>
                                <p className="text-[#4c9a6a] text-sm font-normal leading-normal">Complete your profile to unlock personalized career recommendations and skill-building resources.</p>
                            </div>
                        </div>
                        <div className="flex flex-col gap-3 p-4">
                            <div className="flex gap-6 justify-between">
                                <p className="text-[#0d1b13] text-base font-medium leading-normal">Profile Completion</p>
                                <p className="text-[#0d1b13] text-sm font-normal leading-normal">25%</p>
                            </div>
                            <div className="rounded bg-[#cfe7d8]"><div className="h-2 rounded bg-[#10cf59]" style={{width: '25%'}}></div></div>
                        </div>
                        <div className="pb-3">
                            <div className="flex border-b border-[#cfe7d8] px-4 gap-8">
                                <a
                                    className={`flex flex-col items-center justify-center border-b-[3px] ${activeTab === 'basic' ? 'border-b-[#10cf59] text-[#0d1b13]' : 'border-b-transparent text-[#4c9a6a]'} pb-[13px] pt-4`}
                                    href="#"
                                    onClick={(e) => { e.preventDefault(); setActiveTab('basic'); }}
                                >
                                    <p className={`${activeTab === 'basic' ? 'text-[#0d1b13]' : 'text-[#4c9a6a]'} text-sm font-bold leading-normal tracking-[0.015em]`}>Basic Information</p>
                                </a>
                                <a
                                    className={`flex flex-col items-center justify-center border-b-[3px] ${activeTab === 'academic' ? 'border-b-[#10cf59] text-[#0d1b13]' : 'border-b-transparent text-[#4c9a6a]'} pb-[13px] pt-4`}
                                    href="#"
                                    onClick={(e) => { e.preventDefault(); setActiveTab('academic'); }}
                                >
                                    <p className={`${activeTab === 'academic' ? 'text-[#0d1b13]' : 'text-[#4c9a6a]'} text-sm font-bold leading-normal tracking-[0.015em]`}>Academic History</p>
                                </a>
                                <a
                                    className={`flex flex-col items-center justify-center border-b-[3px] ${activeTab === 'personal' ? 'border-b-[#10cf59] text-[#0d1b13]' : 'border-b-transparent text-[#4c9a6a]'} pb-[13px] pt-4`}
                                    href="#"
                                    onClick={(e) => { e.preventDefault(); setActiveTab('personal'); }}
                                >
                                    <p className={`${activeTab === 'personal' ? 'text-[#0d1b13]' : 'text-[#4c9a6a]'} text-sm font-bold leading-normal tracking-[0.015em]`}>Personality Traits</p>
                                </a>
                                <a
                                    className={`flex flex-col items-center justify-center border-b-[3px] ${activeTab === 'career' ? 'border-b-[#10cf59] text-[#0d1b13]' : 'border-b-transparent text-[#4c9a6a]'} pb-[13px] pt-4`}
                                    href="#"
                                    onClick={(e) => { e.preventDefault(); setActiveTab('career'); }}
                                >
                                    <p className={`${activeTab === 'career' ? 'text-[#0d1b13]' : 'text-[#4c9a6a]'} text-sm font-bold leading-normal tracking-[0.015em]`}>Career Aspirations</p>
                                </a>
                            </div>
                        </div>
                        
                        <form onSubmit={handleUpdate}>
                            {renderTabContent()}
                            
                            <div className="flex px-4 py-3 justify-end">
                                <button
                                    type="submit"
                                    className="flex min-w-[84px] max-w-[480px] cursor-pointer items-center justify-center overflow-hidden rounded-full h-10 px-4 bg-[#10cf59] text-[#0d1b13] text-sm font-bold leading-normal tracking-[0.015em]"
                                >
                                    <span className="truncate">Save &amp; Continue</span>
                                </button>
                            </div>
                            
                            {message && (
                                <p className={`mt-4 p-3 rounded ${
                                    message.includes('Error') ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'
                                }`}>
                                    {message}
                                </p>
                            )}
                        </form>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ProfilePage;