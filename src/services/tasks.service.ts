/**
 * Tasks Service
 * API calls for task operations
 */

import apiClient from '@/lib/api-client';
import { Task, CreateTaskRequest } from '@/types';

export const tasksService = {
  /**
   * Get all tasks for user
   */
  getTasks: async (userId: string, filters?: {
    status?: string;
    milestone_id?: string;
    date?: string;
  }): Promise<Task[]> => {
    const params = new URLSearchParams({ user_id: userId, ...filters });
    const response = await apiClient.get(`/tasks?${params.toString()}`);
    return response.data;
  },

  /**
   * Get single task
   */
  getTask: async (taskId: string): Promise<Task> => {
    const response = await apiClient.get(`/tasks/${taskId}`);
    return response.data;
  },

  /**
   * Create new task
   */
  createTask: async (data: CreateTaskRequest): Promise<Task> => {
    const response = await apiClient.post('/tasks', data);
    return response.data;
  },

  /**
   * Update task
   */
  updateTask: async (taskId: string, data: Partial<Task>): Promise<Task> => {
    const response = await apiClient.patch(`/tasks/${taskId}`, data);
    return response.data;
  },

  /**
   * Delete task
   */
  deleteTask: async (taskId: string): Promise<void> => {
    await apiClient.delete(`/tasks/${taskId}`);
  },

  /**
   * Mark task as complete
   */
  completeTask: async (taskId: string): Promise<Task> => {
    const response = await apiClient.post(`/tasks/${taskId}/complete`);
    return response.data;
  },

  /**
   * Get today's tasks
   */
  getTodaysTasks: async (userId: string): Promise<Task[]> => {
    const response = await apiClient.get(`/tasks/today?user_id=${userId}`);
    return response.data;
  },

  /**
   * Reschedule task
   */
  rescheduleTask: async (taskId: string, newDate: string): Promise<Task> => {
    const response = await apiClient.post(`/tasks/${taskId}/reschedule`, {
      scheduled_at: newDate,
    });
    return response.data;
  },

  /**
   * Request task reallocation (difficulty adjustment)
   */
  requestReallocation: async (taskId: string, reason: string): Promise<Task> => {
    const response = await apiClient.post(`/tasks/${taskId}/reallocate`, { reason });
    return response.data;
  },
};
