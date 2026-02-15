/**
 * User Service
 * API calls for user-related operations
 */

import apiClient from '@/lib/api-client';
import { User, UserProfile, OnboardingData } from '@/types';

export const userService = {
  /**
   * Get current user
   */
  getCurrentUser: async (): Promise<User> => {
    const response = await apiClient.get('/users/me');
    return response.data;
  },

  /**
   * Get user profile
   */
  getUserProfile: async (userId: string): Promise<UserProfile> => {
    const response = await apiClient.get(`/users/${userId}/profile`);
    return response.data;
  },

  /**
   * Update user profile
   */
  updateUserProfile: async (userId: string, data: Partial<UserProfile>): Promise<UserProfile> => {
    const response = await apiClient.patch(`/users/${userId}/profile`, data);
    return response.data;
  },

  /**
   * Complete onboarding
   */
  completeOnboarding: async (data: OnboardingData): Promise<User> => {
    const response = await apiClient.post('/onboarding/complete', data);
    return response.data;
  },

  /**
   * Get user skills
   */
  getUserSkills: async (userId: string) => {
    const response = await apiClient.get(`/users/${userId}/skills`);
    return response.data;
  },

  /**
   * Update user skills
   */
  updateUserSkills: async (userId: string, skills: any[]) => {
    const response = await apiClient.put(`/users/${userId}/skills`, { skills });
    return response.data;
  },
};
