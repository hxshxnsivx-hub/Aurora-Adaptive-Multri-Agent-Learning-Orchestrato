/**
 * Resources Service
 * API calls for resource operations
 */

import apiClient from '@/lib/api-client';
import { Resource } from '@/types';

export const resourcesService = {
  /**
   * Get resources for milestone
   */
  getResources: async (milestoneId: string): Promise<Resource[]> => {
    const response = await apiClient.get(`/resources?milestone_id=${milestoneId}`);
    return response.data;
  },

  /**
   * Get single resource
   */
  getResource: async (resourceId: string): Promise<Resource> => {
    const response = await apiClient.get(`/resources/${resourceId}`);
    return response.data;
  },

  /**
   * Search resources
   */
  searchResources: async (query: string, filters?: {
    resource_type?: string;
    difficulty_level?: string;
    source_platform?: string;
  }): Promise<Resource[]> => {
    const params = new URLSearchParams({ query, ...filters });
    const response = await apiClient.get(`/resources/search?${params.toString()}`);
    return response.data;
  },

  /**
   * Get recommended resources
   */
  getRecommendedResources: async (userId: string, topic: string): Promise<Resource[]> => {
    const response = await apiClient.get(`/resources/recommended?user_id=${userId}&topic=${topic}`);
    return response.data;
  },

  /**
   * Mark resource as completed
   */
  markResourceCompleted: async (resourceId: string, userId: string): Promise<void> => {
    await apiClient.post(`/resources/${resourceId}/complete`, { user_id: userId });
  },

  /**
   * Rate resource
   */
  rateResource: async (resourceId: string, rating: number, userId: string): Promise<void> => {
    await apiClient.post(`/resources/${resourceId}/rate`, { rating, user_id: userId });
  },
};
