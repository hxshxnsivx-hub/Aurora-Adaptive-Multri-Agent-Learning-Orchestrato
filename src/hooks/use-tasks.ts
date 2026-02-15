/**
 * Tasks Hooks
 * React Query hooks for task operations
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { tasksService } from '@/services/tasks.service';
import { Task, CreateTaskRequest } from '@/types';

// Query keys
export const taskKeys = {
  all: ['tasks'] as const,
  lists: () => [...taskKeys.all, 'list'] as const,
  list: (userId: string, filters?: any) => [...taskKeys.lists(), userId, filters] as const,
  details: () => [...taskKeys.all, 'detail'] as const,
  detail: (taskId: string) => [...taskKeys.details(), taskId] as const,
  today: (userId: string) => [...taskKeys.all, 'today', userId] as const,
};

/**
 * Get all tasks for user
 */
export function useTasks(
  userId: string,
  filters?: {
    status?: string;
    milestone_id?: string;
    date?: string;
  }
) {
  return useQuery({
    queryKey: taskKeys.list(userId, filters),
    queryFn: () => tasksService.getTasks(userId, filters),
    enabled: !!userId,
  });
}

/**
 * Get single task
 */
export function useTask(taskId: string) {
  return useQuery({
    queryKey: taskKeys.detail(taskId),
    queryFn: () => tasksService.getTask(taskId),
    enabled: !!taskId,
  });
}

/**
 * Get today's tasks
 */
export function useTodaysTasks(userId: string) {
  return useQuery({
    queryKey: taskKeys.today(userId),
    queryFn: () => tasksService.getTodaysTasks(userId),
    enabled: !!userId,
    // Refetch every 5 minutes
    refetchInterval: 5 * 60 * 1000,
  });
}

/**
 * Create task
 */
export function useCreateTask() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreateTaskRequest) => tasksService.createTask(data),
    onSuccess: (data) => {
      // Invalidate task lists
      queryClient.invalidateQueries({ queryKey: taskKeys.lists() });
      // Set the new task in cache
      queryClient.setQueryData(taskKeys.detail(data.id), data);
    },
  });
}

/**
 * Update task
 */
export function useUpdateTask() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ taskId, data }: { taskId: string; data: Partial<Task> }) =>
      tasksService.updateTask(taskId, data),
    onSuccess: (data, variables) => {
      // Update cache
      queryClient.setQueryData(taskKeys.detail(variables.taskId), data);
      // Invalidate lists
      queryClient.invalidateQueries({ queryKey: taskKeys.lists() });
      queryClient.invalidateQueries({ queryKey: taskKeys.today(data.user_id) });
    },
  });
}

/**
 * Delete task
 */
export function useDeleteTask() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (taskId: string) => tasksService.deleteTask(taskId),
    onSuccess: (_, taskId) => {
      // Remove from cache
      queryClient.removeQueries({ queryKey: taskKeys.detail(taskId) });
      // Invalidate lists
      queryClient.invalidateQueries({ queryKey: taskKeys.lists() });
    },
  });
}

/**
 * Complete task
 */
export function useCompleteTask() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (taskId: string) => tasksService.completeTask(taskId),
    onSuccess: (data, taskId) => {
      // Update cache
      queryClient.setQueryData(taskKeys.detail(taskId), data);
      // Invalidate lists
      queryClient.invalidateQueries({ queryKey: taskKeys.lists() });
      queryClient.invalidateQueries({ queryKey: taskKeys.today(data.user_id) });
      // Invalidate progress
      queryClient.invalidateQueries({ queryKey: ['progress'] });
    },
  });
}

/**
 * Reschedule task
 */
export function useRescheduleTask() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ taskId, newDate }: { taskId: string; newDate: string }) =>
      tasksService.rescheduleTask(taskId, newDate),
    onSuccess: (data, variables) => {
      // Update cache
      queryClient.setQueryData(taskKeys.detail(variables.taskId), data);
      // Invalidate lists
      queryClient.invalidateQueries({ queryKey: taskKeys.lists() });
      queryClient.invalidateQueries({ queryKey: taskKeys.today(data.user_id) });
    },
  });
}

/**
 * Request task reallocation
 */
export function useRequestReallocation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ taskId, reason }: { taskId: string; reason: string }) =>
      tasksService.requestReallocation(taskId, reason),
    onSuccess: (data, variables) => {
      // Update cache
      queryClient.setQueryData(taskKeys.detail(variables.taskId), data);
      // Invalidate lists
      queryClient.invalidateQueries({ queryKey: taskKeys.lists() });
    },
  });
}
