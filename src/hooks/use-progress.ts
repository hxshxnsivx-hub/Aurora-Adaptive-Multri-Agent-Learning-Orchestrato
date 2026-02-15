/**
 * Progress Hooks
 * React Query hooks for progress tracking
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { progressService } from '@/services/progress.service';
import { Progress, ProgressStats } from '@/types';

// Query keys
export const progressKeys = {
  all: ['progress'] as const,
  user: (userId: string) => [...progressKeys.all, 'user', userId] as const,
  stats: (userId: string) => [...progressKeys.all, 'stats', userId] as const,
  path: (pathId: string) => [...progressKeys.all, 'path', pathId] as const,
  streak: (userId: string) => [...progressKeys.all, 'streak', userId] as const,
};

/**
 * Get user progress
 */
export function useUserProgress(userId: string) {
  return useQuery({
    queryKey: progressKeys.user(userId),
    queryFn: () => progressService.getUserProgress(userId),
    enabled: !!userId,
  });
}

/**
 * Get progress stats
 */
export function useProgressStats(userId: string) {
  return useQuery({
    queryKey: progressKeys.stats(userId),
    queryFn: () => progressService.getProgressStats(userId),
    enabled: !!userId,
  });
}

/**
 * Get learning path progress
 */
export function useLearningPathProgress(pathId: string) {
  return useQuery({
    queryKey: progressKeys.path(pathId),
    queryFn: () => progressService.getLearningPathProgress(pathId),
    enabled: !!pathId,
  });
}

/**
 * Get streak information
 */
export function useStreak(userId: string) {
  return useQuery({
    queryKey: progressKeys.streak(userId),
    queryFn: () => progressService.getStreak(userId),
    enabled: !!userId,
  });
}

/**
 * Update progress
 */
export function useUpdateProgress() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      userId,
      data,
    }: {
      userId: string;
      data: {
        task_id?: string;
        milestone_id?: string;
        completion_percentage?: number;
      };
    }) => progressService.updateProgress(userId, data),
    onSuccess: (data, variables) => {
      // Invalidate all progress queries
      queryClient.invalidateQueries({ queryKey: progressKeys.user(variables.userId) });
      queryClient.invalidateQueries({ queryKey: progressKeys.stats(variables.userId) });
      queryClient.invalidateQueries({ queryKey: progressKeys.streak(variables.userId) });
      
      // If milestone progress, invalidate path progress
      if (variables.data.milestone_id) {
        queryClient.invalidateQueries({ queryKey: progressKeys.all });
      }
    },
  });
}
