/**
 * Progress Service
 * API calls for progress tracking
 */

import apiClient from '@/lib/api-client';
import { Progress, ProgressStats } from '@/types';

export const progressService = {
  /**
   * Get user progress
   */
  getUserProgress: async (userId: string): Promise<Progress> => {
    const response = await apiClient.get(`/users/${userId}/progress`);
    return response.data;
  },

  /**
   * Get progress stats
   */
  getProgressStats: async (userId: string): Promise<ProgressStats> => {
    const response = await apiClient.get(`/users/${userId}/progress/stats`);
    return response.data;
  },

  /**
   * Get progress for learning path
   */
  getLearningPathProgress: async (pathId: string): Promise<Progress> => {
    const response = await apiClient.get(`/learning-paths/${pathId}/progress`);
    return response.data;
  },

  /**
   * Update progress
   */
  updateProgress: async (userId: string, data: {
    task_id?: string;
    milestone_id?: string;
    completion_percentage?: number;
  }): Promise<Progress> => {
    const response = await apiClient.post(`/users/${userId}/progress`, data);
    return response.data;
  },

  /**
   * Get streak information
   */
  getStreak: async (userId: string): Promise<{
    current_streak: number;
    longest_streak: number;
    last_activity_date: string;
  }> => {
    const response = await apiClient.get(`/users/${userId}/streak`);
    return response.data;
  },
};
