import { create } from 'zustand'
import { devtools, persist } from 'zustand/middleware'

// User state
interface UserState {
  user: User | null
  profile: UserProfile | null
  isAuthenticated: boolean
  setUser: (user: User | null) => void
  setProfile: (profile: UserProfile | null) => void
  logout: () => void
}

// Learning path state
interface LearningPathState {
  currentPath: LearningPath | null
  milestones: Milestone[]
  completedTasks: string[]
  upcomingTasks: Task[]
  progress: UserProgress | null
  setCurrentPath: (path: LearningPath | null) => void
  setMilestones: (milestones: Milestone[]) => void
  completeTask: (taskId: string) => void
  updateProgress: (progress: UserProgress) => void
}

// UI state
interface UIState {
  sidebarOpen: boolean
  currentView: string
  loading: boolean
  error: string | null
  setSidebarOpen: (open: boolean) => void
  setCurrentView: (view: string) => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
}

// Voice state
interface VoiceState {
  isListening: boolean
  isProcessing: boolean
  lastCommand: string | null
  sessionId: string | null
  setListening: (listening: boolean) => void
  setProcessing: (processing: boolean) => void
  setLastCommand: (command: string | null) => void
  setSessionId: (sessionId: string | null) => void
}

// Combined app state
interface AppState extends UserState, LearningPathState, UIState, VoiceState {}

// Types
interface User {
  id: string
  email: string
  name?: string
  picture?: string
}

interface UserProfile {
  id: string
  displayName: string
  skillLevels: Record<string, number>
  learningPreferences: {
    contentTypes: string[]
    learningPace: string
    sessionDuration: number
  }
  availabilitySchedule: Record<string, TimeSlot[]>
  timezone: string
  goals: Goal[]
}

interface TimeSlot {
  start: number
  end: number
}

interface Goal {
  id: string
  title: string
  description: string
  targetDate?: string
  priority: string
}

interface LearningPath {
  id: string
  title: string
  description: string
  difficultyLevel: string
  estimatedTotalHours: number
  status: string
  completionPercentage: number
  milestones: Milestone[]
  createdAt: string
}

interface Milestone {
  id: string
  title: string
  description: string
  orderIndex: number
  estimatedHours: number
  status: string
  dueDate?: string
  tasks: Task[]
}

interface Task {
  id: string
  title: string
  description: string
  taskType: string
  estimatedMinutes: number
  completionStatus: string
  scheduledAt?: string
}

interface UserProgress {
  id: string
  totalStudyTime: number
  streakDays: number
  completedMilestones: string[]
  completedTasks: string[]
  performanceMetrics: Record<string, any>
  lastActivity: string
}

export const useAppStore = create<AppState>()(
  devtools(
    persist(
      (set, get) => ({
        // User state
        user: null,
        profile: null,
        isAuthenticated: false,
        setUser: (user) => set({ user, isAuthenticated: !!user }),
        setProfile: (profile) => set({ profile }),
        logout: () => set({ user: null, profile: null, isAuthenticated: false }),

        // Learning path state
        currentPath: null,
        milestones: [],
        completedTasks: [],
        upcomingTasks: [],
        progress: null,
        setCurrentPath: (currentPath) => set({ currentPath }),
        setMilestones: (milestones) => set({ milestones }),
        completeTask: (taskId) => {
          const { completedTasks } = get()
          if (!completedTasks.includes(taskId)) {
            set({ completedTasks: [...completedTasks, taskId] })
          }
        },
        updateProgress: (progress) => set({ progress }),

        // UI state
        sidebarOpen: false,
        currentView: 'dashboard',
        loading: false,
        error: null,
        setSidebarOpen: (sidebarOpen) => set({ sidebarOpen }),
        setCurrentView: (currentView) => set({ currentView }),
        setLoading: (loading) => set({ loading }),
        setError: (error) => set({ error }),

        // Voice state
        isListening: false,
        isProcessing: false,
        lastCommand: null,
        sessionId: null,
        setListening: (isListening) => set({ isListening }),
        setProcessing: (isProcessing) => set({ isProcessing }),
        setLastCommand: (lastCommand) => set({ lastCommand }),
        setSessionId: (sessionId) => set({ sessionId }),
      }),
      {
        name: 'adaptive-learning-store',
        partialize: (state) => ({
          user: state.user,
          profile: state.profile,
          isAuthenticated: state.isAuthenticated,
          currentPath: state.currentPath,
          completedTasks: state.completedTasks,
        }),
      }
    )
  )
)

// Selectors for better performance
export const useUser = () => useAppStore((state) => state.user)
export const useProfile = () => useAppStore((state) => state.profile)
export const useCurrentPath = () => useAppStore((state) => state.currentPath)
export const useProgress = () => useAppStore((state) => state.progress)
export const useUIState = () => useAppStore((state) => ({
  sidebarOpen: state.sidebarOpen,
  currentView: state.currentView,
  loading: state.loading,
  error: state.error,
}))
export const useVoiceState = () => useAppStore((state) => ({
  isListening: state.isListening,
  isProcessing: state.isProcessing,
  lastCommand: state.lastCommand,
  sessionId: state.sessionId,
}))