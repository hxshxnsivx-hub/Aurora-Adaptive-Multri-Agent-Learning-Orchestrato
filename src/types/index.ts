// Core types for the Adaptive Learning Platform

export interface User {
  id: string;
  email: string;
  auth0Id: string;
  createdAt: Date;
  updatedAt: Date;
  isActive: boolean;
}

export interface UserProfile {
  id: string;
  userId: string;
  displayName: string;
  skillLevels: Record<string, SkillLevel>;
  learningPreferences: LearningPreferences;
  availabilitySchedule: Record<string, TimeSlot[]>;
  timezone: string;
  goals: LearningGoal[];
  integrations: IntegrationSettings;
}

export interface SkillLevel {
  level: number; // 0.0 to 1.0
  assessedAt: Date;
  confidence: number;
}

export interface LearningPreferences {
  preferredContentTypes: ContentType[];
  learningPace: LearningPace;
  difficultyPreference: DifficultyPreference;
  sessionDurationPreference: number; // minutes
}

export interface TimeSlot {
  start: number; // hour (0-23)
  end: number; // hour (0-23)
}

export interface LearningGoal {
  id: string;
  title: string;
  description: string;
  targetLevel: number;
  deadline?: Date;
  priority: Priority;
}

export interface IntegrationSettings {
  googleCalendar?: CalendarIntegration;
  notion?: NotionIntegration;
}

export interface CalendarIntegration {
  enabled: boolean;
  calendarId: string;
  syncPreferences: CalendarSyncPreferences;
}

export interface NotionIntegration {
  enabled: boolean;
  workspaceId: string;
  databaseId: string;
  syncPreferences: NotionSyncPreferences;
}

export interface CalendarSyncPreferences {
  createEvents: boolean;
  updateEvents: boolean;
  deleteEvents: boolean;
  eventPrefix: string;
}

export interface NotionSyncPreferences {
  createTasks: boolean;
  updateTasks: boolean;
  syncProgress: boolean;
  pageTemplate: string;
}

export interface LearningPath {
  id: string;
  userId: string;
  title: string;
  description: string;
  difficultyLevel: DifficultyLevel;
  estimatedTotalHours: number;
  milestones: Milestone[];
  status: PathStatus;
  createdAt: Date;
  updatedAt: Date;
  completionPercentage: number;
}

export interface Milestone {
  id: string;
  learningPathId: string;
  title: string;
  description: string;
  orderIndex: number;
  tasks: Task[];
  resources: Resource[];
  completionCriteria: string;
  estimatedHours: number;
  prerequisites: string[]; // milestone IDs
  status: MilestoneStatus;
  dueDate?: Date;
}

export interface Task {
  id: string;
  milestoneId: string;
  title: string;
  description: string;
  taskType: TaskType;
  estimatedMinutes: number;
  resources: Resource[];
  completionStatus: TaskStatus;
  scheduledAt?: Date;
  completedAt?: Date;
}

export interface Resource {
  id: string;
  title: string;
  description: string;
  resourceType: ResourceType;
  sourcePlatform: SourcePlatform;
  url: string;
  metadata: ResourceMetadata;
  difficultyLevel: DifficultyLevel;
  estimatedDuration: number; // minutes
  tags: string[];
  qualityScore: number; // 0-1
  createdAt: Date;
}

export interface ResourceMetadata {
  author?: string;
  publishedDate?: Date;
  viewCount?: number;
  rating?: number;
  language: string;
  fileSize?: number;
  thumbnailUrl?: string;
}

export interface UserProgress {
  id: string;
  userId: string;
  learningPathId: string;
  currentMilestoneId?: string;
  completedMilestones: string[];
  completedTasks: string[];
  totalStudyTime: number; // minutes
  streakDays: number;
  lastActivity: Date;
  performanceMetrics: PerformanceMetrics;
}

export interface PerformanceMetrics {
  completionRate: number; // percentage
  averageSessionDuration: number; // minutes
  preferredStudyTimes: number[]; // hours of day
  difficultyAdaptationScore: number;
  engagementScore: number;
}

export interface Reallocation {
  id: string;
  userId: string;
  learningPathId: string;
  triggerReason: ReallocationReason;
  originalMilestoneId: string;
  newMilestoneId?: string;
  changesMade: PathChange[];
  confidenceScore: number;
  userApproved?: boolean;
  createdAt: Date;
  appliedAt?: Date;
}

export interface PathChange {
  changeType: ChangeType;
  targetId: string; // milestone or task ID
  oldValue?: Record<string, any>;
  newValue: Record<string, any>;
  reasoning: string;
}

// Enums
export enum ContentType {
  VIDEO = 'video',
  ARTICLE = 'article',
  CODE = 'code',
  INTERACTIVE = 'interactive',
  BOOK = 'book',
  COURSE = 'course',
  PODCAST = 'podcast',
}

export enum LearningPace {
  SLOW = 'slow',
  MODERATE = 'moderate',
  FAST = 'fast',
}

export enum DifficultyPreference {
  GRADUAL = 'gradual',
  CHALLENGING = 'challenging',
  ADAPTIVE = 'adaptive',
}

export enum Priority {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  CRITICAL = 'critical',
}

export enum DifficultyLevel {
  BEGINNER = 'beginner',
  INTERMEDIATE = 'intermediate',
  ADVANCED = 'advanced',
  EXPERT = 'expert',
}

export enum PathStatus {
  ACTIVE = 'active',
  COMPLETED = 'completed',
  PAUSED = 'paused',
  ARCHIVED = 'archived',
}

export enum MilestoneStatus {
  NOT_STARTED = 'not_started',
  IN_PROGRESS = 'in_progress',
  COMPLETED = 'completed',
  BLOCKED = 'blocked',
}

export enum TaskType {
  READ = 'read',
  WATCH = 'watch',
  CODE = 'code',
  PRACTICE = 'practice',
  QUIZ = 'quiz',
  PROJECT = 'project',
  REVIEW = 'review',
}

export enum TaskStatus {
  NOT_STARTED = 'not_started',
  IN_PROGRESS = 'in_progress',
  COMPLETED = 'completed',
  SKIPPED = 'skipped',
}

export enum ResourceType {
  VIDEO = 'video',
  ARTICLE = 'article',
  REPOSITORY = 'repository',
  COURSE = 'course',
  PDF = 'pdf',
  DOCUMENTATION = 'documentation',
  TUTORIAL = 'tutorial',
}

export enum SourcePlatform {
  YOUTUBE = 'youtube',
  GITHUB = 'github',
  WEB = 'web',
  COURSERA = 'coursera',
  UDEMY = 'udemy',
  MEDIUM = 'medium',
  DEV_TO = 'dev_to',
  STACKOVERFLOW = 'stackoverflow',
}

export enum ReallocationReason {
  BEHIND_SCHEDULE = 'behind_schedule',
  TOO_EASY = 'too_easy',
  TOO_HARD = 'too_hard',
  USER_FEEDBACK = 'user_feedback',
  PERFORMANCE_BASED = 'performance_based',
}

export enum ChangeType {
  ADD_MILESTONE = 'add_milestone',
  REMOVE_MILESTONE = 'remove_milestone',
  MODIFY_RESOURCES = 'modify_resources',
  RESCHEDULE = 'reschedule',
  ADJUST_DIFFICULTY = 'adjust_difficulty',
}

// API Response types
export interface ApiResponse<T> {
  data: T;
  success: boolean;
  message?: string;
  errors?: string[];
}

export interface PaginatedResponse<T> {
  data: T[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
  };
}

// Component Props types
export interface BaseComponentProps {
  className?: string;
  children?: React.ReactNode;
}

// Form types
export interface OnboardingFormData {
  displayName: string;
  selectedTopics: string[];
  skillAssessments: Record<string, number>;
  learningGoals: Omit<LearningGoal, 'id'>[];
  availabilitySchedule: Record<string, TimeSlot[]>;
  preferences: LearningPreferences;
  integrations: {
    enableGoogleCalendar: boolean;
    enableNotion: boolean;
  };
}

// Voice Assistant types
export interface VoiceCommand {
  transcript: string;
  confidence: number;
  intent: string;
  entities: Record<string, any>;
}

export interface VoiceResponse {
  text: string;
  audioUrl?: string;
  actions?: VoiceAction[];
}

export interface VoiceAction {
  type: string;
  payload: Record<string, any>;
}