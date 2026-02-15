/**
 * Learning Path Hooks
 * React Query hooks for learning path operations
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { learningPathService } from '@/services/learning-path.service';
import { LearningPath, Milestone, CreateLearningPathRequest } from '@/types';

// Query keys
export const learningPathKeys = {
  all: ['learning-paths'] as const,
  lists: () => [...learningPathKeys.all, 'list'] as const,
  list: (userId: string) => [...learningPathKeys.lists(), userId] as const,
  details: () => [...learningPathKeys.all, 'detail'] as const,
  detail: (pathId: string) => [...learningPathKeys.details(), pathId] as const,
  milestones: (pathId: string) => [...learningPathKeys.detail(pathId), 'milestones'] as const,
};

/**
 * Get all learning paths for user
 */
export function useLearningPaths(userId: string) {
  return useQuery({
    queryKey: learningPathKeys.list(userId),
    queryFn: () => learningPathService.getLearningPaths(userId),
    enabled: !!userId,
  });
}

/**
 * Get single learning path
 */
export function useLearningPath(pathId: string) {
  return useQuery({
    queryKey: learningPathKeys.detail(pathId),
    queryFn: () => learningPathService.getLearningPath(pathId),
    enabled: !!pathId,
  });
}

/**
 * Create learning path
 */
export function useCreateLearningPath() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreateLearningPathRequest) => learningPathService.createLearningPath(data),
    onSuccess: (data) => {
      // Invalidate lists
      queryClient.invalidateQueries({ queryKey: learningPathKeys.lists() });
      // Set the new path in cache
      queryClient.setQueryData(learningPathKeys.detail(data.id), data);
    },
  });
}

/**
 * Update learning path
 */
export function useUpdateLearningPath() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ pathId, data }: { pathId: string; data: Partial<LearningPath> }) =>
      learningPathService.updateLearningPath(pathId, data),
    onSuccess: (data, variables) => {
      // Update cache
      queryClient.setQueryData(learningPathKeys.detail(variables.pathId), data);
      // Invalidate lists
      queryClient.invalidateQueries({ queryKey: learningPathKeys.lists() });
    },
  });
}

/**
 * Delete learning path
 */
export function useDeleteLearningPath() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (pathId: string) => learningPathService.deleteLearningPath(pathId),
    onSuccess: (_, pathId) => {
      // Remove from cache
      queryClient.removeQueries({ queryKey: learningPathKeys.detail(pathId) });
      // Invalidate lists
      queryClient.invalidateQueries({ queryKey: learningPathKeys.lists() });
    },
  });
}

/**
 * Get milestones for learning path
 */
export function useMilestones(pathId: string) {
  return useQuery({
    queryKey: learningPathKeys.milestones(pathId),
    queryFn: () => learningPathService.getMilestones(pathId),
    enabled: !!pathId,
  });
}

/**
 * Update milestone
 */
export function useUpdateMilestone() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      pathId,
      milestoneId,
      data,
    }: {
      pathId: string;
      milestoneId: string;
      data: Partial<Milestone>;
    }) => learningPathService.updateMilestone(pathId, milestoneId, data),
    onSuccess: (data, variables) => {
      // Invalidate milestones
      queryClient.invalidateQueries({ queryKey: learningPathKeys.milestones(variables.pathId) });
      // Invalidate path details
      queryClient.invalidateQueries({ queryKey: learningPathKeys.detail(variables.pathId) });
    },
  });
}

/**
 * Generate learning path with AI
 */
export function useGenerateLearningPath() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: {
      topic: string;
      current_level: string;
      target_level: string;
      goals: string[];
      weekly_hours: number;
    }) => learningPathService.generateLearningPath(data),
    onSuccess: (data) => {
      // Invalidate lists
      queryClient.invalidateQueries({ queryKey: learningPathKeys.lists() });
      // Set the new path in cache
      queryClient.setQueryData(learningPathKeys.detail(data.id), data);
    },
  });
}
