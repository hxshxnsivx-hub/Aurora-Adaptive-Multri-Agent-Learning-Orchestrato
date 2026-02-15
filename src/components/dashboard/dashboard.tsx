"use client"

import React from 'react'
import { motion } from 'framer-motion'
import { GlassyCard, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { GlassyProgress } from '@/components/ui/progress'
import { Badge } from '@/components/ui/badge'
import { Calendar, Clock, Target, TrendingUp, BookOpen, Award } from 'lucide-react'

interface DashboardProps {
  user?: {
    name: string
    currentStreak: number
    totalStudyTime: number
    completionRate: number
  }
}

export function Dashboard({ user }: DashboardProps) {
  const mockUser = user || {
    name: "Alex",
    currentStreak: 7,
    totalStudyTime: 1440, // minutes
    completionRate: 0.75
  }

  const upcomingTasks = [
    { id: 1, title: "Complete Python Basics Module", dueDate: "Today", priority: "high" },
    { id: 2, title: "Practice Algorithm Problems", dueDate: "Tomorrow", priority: "medium" },
    { id: 3, title: "Review Data Structures", dueDate: "Dec 28", priority: "low" }
  ]

  const recentAchievements = [
    { id: 1, title: "7-Day Streak", icon: "🔥", date: "Today" },
    { id: 2, title: "Python Fundamentals", icon: "🐍", date: "Yesterday" },
    { id: 3, title: "First Milestone", icon: "🎯", date: "2 days ago" }
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Welcome Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <h1 className="text-4xl font-bold text-white mb-2">
            Welcome back, {mockUser.name}! 👋
          </h1>
          <p className="text-white/70 text-lg">
            Ready to continue your learning journey?
          </p>
        </motion.div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
          >
            <GlassyCard className="p-6">
              <div className="flex items-center space-x-4">
                <div className="p-3 bg-orange-500/20 rounded-full">
                  <TrendingUp className="h-6 w-6 text-orange-400" />
                </div>
                <div>
                  <p className="text-white/70 text-sm">Current Streak</p>
                  <p className="text-2xl font-bold text-white">{mockUser.currentStreak} days</p>
                </div>
              </div>
            </GlassyCard>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            <GlassyCard className="p-6">
              <div className="flex items-center space-x-4">
                <div className="p-3 bg-blue-500/20 rounded-full">
                  <Clock className="h-6 w-6 text-blue-400" />
                </div>
                <div>
                  <p className="text-white/70 text-sm">Study Time</p>
                  <p className="text-2xl font-bold text-white">{Math.floor(mockUser.totalStudyTime / 60)}h {mockUser.totalStudyTime % 60}m</p>
                </div>
              </div>
            </GlassyCard>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
          >
            <GlassyCard className="p-6">
              <div className="flex items-center space-x-4">
                <div className="p-3 bg-green-500/20 rounded-full">
                  <Target className="h-6 w-6 text-green-400" />
                </div>
                <div>
                  <p className="text-white/70 text-sm">Completion Rate</p>
                  <p className="text-2xl font-bold text-white">{Math.round(mockUser.completionRate * 100)}%</p>
                </div>
              </div>
            </GlassyCard>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.4 }}
          >
            <GlassyCard className="p-6">
              <div className="flex items-center space-x-4">
                <div className="p-3 bg-purple-500/20 rounded-full">
                  <BookOpen className="h-6 w-6 text-purple-400" />
                </div>
                <div>
                  <p className="text-white/70 text-sm">Active Paths</p>
                  <p className="text-2xl font-bold text-white">3</p>
                </div>
              </div>
            </GlassyCard>
          </motion.div>
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Current Progress */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.5 }}
            className="lg:col-span-2"
          >
            <GlassyCard>
              <CardHeader>
                <CardTitle className="text-white flex items-center space-x-2">
                  <Target className="h-5 w-5" />
                  <span>Current Learning Path</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div>
                  <div className="flex justify-between items-center mb-2">
                    <h3 className="text-lg font-semibold text-white">Python Mastery Journey</h3>
                    <Badge variant="secondary" className="bg-blue-500/20 text-blue-300">
                      Intermediate
                    </Badge>
                  </div>
                  <p className="text-white/70 mb-4">
                    Master Python programming from fundamentals to advanced concepts
                  </p>
                  <GlassyProgress value={65} className="mb-2" />
                  <div className="flex justify-between text-sm text-white/70">
                    <span>Progress: 65%</span>
                    <span>3 of 5 milestones completed</span>
                  </div>
                </div>

                <div className="space-y-3">
                  <h4 className="font-medium text-white">Current Milestone: Data Structures & Algorithms</h4>
                  <div className="space-y-2">
                    {['Arrays and Lists', 'Hash Tables', 'Binary Trees'].map((topic, index) => (
                      <div key={index} className="flex items-center space-x-3">
                        <div className={`w-2 h-2 rounded-full ${index < 2 ? 'bg-green-400' : 'bg-white/30'}`} />
                        <span className={`text-sm ${index < 2 ? 'text-white' : 'text-white/70'}`}>
                          {topic}
                        </span>
                        {index < 2 && <Badge variant="outline" className="text-xs">Completed</Badge>}
                      </div>
                    ))}
                  </div>
                </div>
              </CardContent>
            </GlassyCard>
          </motion.div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Upcoming Tasks */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5, delay: 0.6 }}
            >
              <GlassyCard>
                <CardHeader>
                  <CardTitle className="text-white flex items-center space-x-2">
                    <Calendar className="h-5 w-5" />
                    <span>Upcoming Tasks</span>
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  {upcomingTasks.map((task) => (
                    <div key={task.id} className="flex items-center space-x-3 p-3 rounded-lg bg-white/5 hover:bg-white/10 transition-colors">
                      <div className={`w-2 h-2 rounded-full ${
                        task.priority === 'high' ? 'bg-red-400' : 
                        task.priority === 'medium' ? 'bg-yellow-400' : 'bg-green-400'
                      }`} />
                      <div className="flex-1">
                        <p className="text-sm font-medium text-white">{task.title}</p>
                        <p className="text-xs text-white/70">{task.dueDate}</p>
                      </div>
                    </div>
                  ))}
                </CardContent>
              </GlassyCard>
            </motion.div>

            {/* Recent Achievements */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5, delay: 0.7 }}
            >
              <GlassyCard>
                <CardHeader>
                  <CardTitle className="text-white flex items-center space-x-2">
                    <Award className="h-5 w-5" />
                    <span>Recent Achievements</span>
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  {recentAchievements.map((achievement) => (
                    <div key={achievement.id} className="flex items-center space-x-3 p-3 rounded-lg bg-white/5">
                      <span className="text-2xl">{achievement.icon}</span>
                      <div className="flex-1">
                        <p className="text-sm font-medium text-white">{achievement.title}</p>
                        <p className="text-xs text-white/70">{achievement.date}</p>
                      </div>
                    </div>
                  ))}
                </CardContent>
              </GlassyCard>
            </motion.div>
          </div>
        </div>
      </div>
    </div>
  )
}