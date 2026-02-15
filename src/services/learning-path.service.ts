/**
 * Learning Path Service
 * API calls for learning path operations
 */

import apiClient from '@/lib/api-client';
import { LearningPath, Milestone, CreateLearningPathRequest } from '@/types';

export const learningPathService = {
  /**
   * Get all learning paths for user
   */
  getLearningPaths: async (userId: string): Promise<LearningPath[]> => {
    const response = await apiClient.get(`/learning-paths?user_id=${userId}`);
    return response.data;
  },

  /**
   * Get single learning path
   */
  getLearningPath: async (pathId: string): Promise<LearningPath> => {
    const response = await apiClient.get(`/learning-paths/${pathId}`);
    return response.data;
  },

  /**
   * Create new learning path
   */
  createLearningPath: async (data: CreateLearningPathRequest): Promise<LearningPath> => {
    const response = await apiClient.post('/learning-paths', data);
    return response.data;
  },

  /**
   * Update learning path
   */
  updateLearningPath: async (pathId: string, data: Partial<LearningPath>): Promise<LearningPath> => {
    const response = await apiClient.patch(`/learning-paths/${pathId}`, data);
    return response.data;
  },

  /**
   * Delete learning path
   */
  deleteLearningPath: async (pathId: string): Promise<void> => {
    await apiClient.delete(`/learning-paths/${pathId}`);
  },

  /**
   * Get milestones for learning path
   */
  getMilestones: async (pathId: string): Promise<Milestone[]> => {
    const response = await apiClient.get(`/learning-paths/${pathId}/milestones`);
    return response.data;
  },

  /**
   * Update milestone
   */
  updateMilestone: async (pathId: string, milestoneId: string, data: Partial<Milestone>): Promise<Milestone> => {
    const response = await apiClient.patch(`/learning-paths/${pathId}/milestones/${milestoneId}`, data);
    return response.data;
  },

  /**
   * Generate learning path (AI)
   */
  generateLearningPath: async (data: {
    topic: string;
    current_level: string;
    target_level: string;
    goals: string[];
    weekly_hours: number;
  }): Promise<LearningPath> => {
    const response = await apiClient.post('/learning-paths/generate', data);
    return response.data;
  },
};
