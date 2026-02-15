/**
 * User Hooks
 * React Query hooks for user operations
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { userService } from '@/services/user.service';
import { User, UserProfile, OnboardingData } from '@/types';

// Query keys
export const userKeys = {
  all: ['users'] as const,
  current: () => [...userKeys.all, 'current'] as const,
  profile: (userId: string) => [...userKeys.all, 'profile', userId] as const,
  skills: (userId: string) => [...userKeys.all, 'skills', userId] as const,
};

/**
 * Get current user
 */
export function useCurrentUser() {
  return useQuery({
    queryKey: userKeys.current(),
    queryFn: userService.getCurrentUser,
  });
}

/**
 * Get user profile
 */
export function useUserProfile(userId: string) {
  return useQuery({
    queryKey: userKeys.profile(userId),
    queryFn: () => userService.getUserProfile(userId),
    enabled: !!userId,
  });
}

/**
 * Update user profile
 */
export function useUpdateUserProfile() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ userId, data }: { userId: string; data: Partial<UserProfile> }) =>
      userService.updateUserProfile(userId, data),
    onSuccess: (data, variables) => {
      // Invalidate and refetch
      queryClient.invalidateQueries({ queryKey: userKeys.profile(variables.userId) });
      queryClient.invalidateQueries({ queryKey: userKeys.current() });
    },
  });
}

/**
 * Complete onboarding
 */
export function useCompleteOnboarding() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: OnboardingData) => userService.completeOnboarding(data),
    onSuccess: () => {
      // Invalidate current user
      queryClient.invalidateQueries({ queryKey: userKeys.current() });
    },
  });
}

/**
 * Get user skills
 */
export function useUserSkills(userId: string) {
  return useQuery({
    queryKey: userKeys.skills(userId),
    queryFn: () => userService.getUserSkills(userId),
    enabled: !!userId,
  });
}

/**
 * Update user skills
 */
export function useUpdateUserSkills() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ userId, skills }: { userId: string; skills: any[] }) =>
      userService.updateUserSkills(userId, skills),
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({ queryKey: userKeys.skills(variables.userId) });
    },
  });
}
