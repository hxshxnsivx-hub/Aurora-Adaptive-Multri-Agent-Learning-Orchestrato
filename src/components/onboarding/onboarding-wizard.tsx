"use client"

import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { GlassyCard, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { GlassyProgress } from '@/components/ui/progress'
import { ChevronLeft, ChevronRight, Target, Brain, Calendar, Link, Sparkles } from 'lucide-react'

interface OnboardingStep {
  id: number
  title: string
  description: string
  icon: React.ReactNode
  component: React.ReactNode
}

export function OnboardingWizard() {
  const [currentStep, setCurrentStep] = useState(0)
  const [formData, setFormData] = useState({
    goals: [] as string[],
    skills: {} as Record<string, number>,
    availability: {} as Record<string, any>,
    integrations: [] as string[]
  })

  const steps: OnboardingStep[] = [
    {
      id: 1,
      title: "Welcome & Goals",
      description: "Let's start by understanding your learning objectives",
      icon: <Target className="h-6 w-6" />,
      component: <GoalsStep formData={formData} setFormData={setFormData} />
    },
    {
      id: 2,
      title: "Skill Assessment",
      description: "Help us understand your current skill levels",
      icon: <Brain className="h-6 w-6" />,
      component: <SkillsStep formData={formData} setFormData={setFormData} />
    },
    {
      id: 3,
      title: "Schedule Setup",
      description: "Configure your availability and study preferences",
      icon: <Calendar className="h-6 w-6" />,
      component: <ScheduleStep formData={formData} setFormData={setFormData} />
    },
    {
      id: 4,
      title: "Integrations",
      description: "Connect your productivity tools (optional)",
      icon: <Link className="h-6 w-6" />,
      component: <IntegrationsStep formData={formData} setFormData={setFormData} />
    },
    {
      id: 5,
      title: "Generate Path",
      description: "Create your personalized learning journey",
      icon: <Sparkles className="h-6 w-6" />,
      component: <GeneratePathStep formData={formData} />
    }
  ]

  const progress = ((currentStep + 1) / steps.length) * 100

  const nextStep = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1)
    }
  }

  const prevStep = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-6">
      <div className="max-w-4xl mx-auto">
        {/* Progress Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <div className="flex items-center justify-between mb-4">
            <h1 className="text-3xl font-bold text-white">Setup Your Learning Journey</h1>
            <span className="text-white/70">
              Step {currentStep + 1} of {steps.length}
            </span>
          </div>
          <GlassyProgress value={progress} className="h-2" />
        </motion.div>

        {/* Step Content */}
        <AnimatePresence mode="wait">
          <motion.div
            key={currentStep}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            transition={{ duration: 0.3 }}
          >
            <GlassyCard className="mb-8">
              <CardHeader>
                <CardTitle className="text-white flex items-center space-x-3">
                  <div className="p-2 bg-blue-500/20 rounded-lg">
                    {steps[currentStep].icon}
                  </div>
                  <div>
                    <h2 className="text-xl">{steps[currentStep].title}</h2>
                    <p className="text-white/70 text-sm font-normal">
                      {steps[currentStep].description}
                    </p>
                  </div>
                </CardTitle>
              </CardHeader>
              <CardContent>
                {steps[currentStep].component}
              </CardContent>
            </GlassyCard>
          </motion.div>
        </AnimatePresence>

        {/* Navigation */}
        <div className="flex justify-between">
          <Button
            variant="glassy"
            onClick={prevStep}
            disabled={currentStep === 0}
            className="flex items-center space-x-2"
          >
            <ChevronLeft className="h-4 w-4" />
            <span>Previous</span>
          </Button>

          <Button
            variant="glassy"
            onClick={nextStep}
            disabled={currentStep === steps.length - 1}
            className="flex items-center space-x-2"
          >
            <span>Next</span>
            <ChevronRight className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </div>
  )
}

// Step Components
function GoalsStep({ formData, setFormData }: any) {
  const commonGoals = [
    "Learn Python Programming",
    "Master Data Structures & Algorithms",
    "Prepare for Technical Interviews",
    "Build Full-Stack Applications",
    "Learn Machine Learning",
    "Prepare for Coding Competitions"
  ]

  const toggleGoal = (goal: string) => {
    const goals = formData.goals.includes(goal)
      ? formData.goals.filter((g: string) => g !== goal)
      : [...formData.goals, goal]
    setFormData({ ...formData, goals })
  }

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-white mb-4">What are your learning goals?</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {commonGoals.map((goal) => (
            <button
              key={goal}
              onClick={() => toggleGoal(goal)}
              className={`p-4 rounded-lg border text-left transition-all ${
                formData.goals.includes(goal)
                  ? 'bg-blue-500/20 border-blue-400 text-white'
                  : 'bg-white/5 border-white/20 text-white/70 hover:bg-white/10'
              }`}
            >
              {goal}
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}

function SkillsStep({ formData, setFormData }: any) {
  const skills = [
    "Python", "JavaScript", "Data Structures", "Algorithms", 
    "System Design", "Databases", "Web Development", "Machine Learning"
  ]

  const updateSkill = (skill: string, level: number) => {
    setFormData({
      ...formData,
      skills: { ...formData.skills, [skill]: level }
    })
  }

  return (
    <div className="space-y-6">
      <h3 className="text-lg font-semibold text-white mb-4">Rate your current skill levels</h3>
      <div className="space-y-4">
        {skills.map((skill) => (
          <div key={skill} className="space-y-2">
            <div className="flex justify-between">
              <span className="text-white">{skill}</span>
              <span className="text-white/70">
                {formData.skills[skill] ? `${formData.skills[skill]}/5` : '0/5'}
              </span>
            </div>
            <div className="flex space-x-2">
              {[1, 2, 3, 4, 5].map((level) => (
                <button
                  key={level}
                  onClick={() => updateSkill(skill, level)}
                  className={`w-8 h-8 rounded-full border transition-all ${
                    (formData.skills[skill] || 0) >= level
                      ? 'bg-blue-500 border-blue-400'
                      : 'bg-white/10 border-white/30 hover:bg-white/20'
                  }`}
                >
                  {level}
                </button>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

function ScheduleStep({ formData, setFormData }: any) {
  return (
    <div className="space-y-6">
      <h3 className="text-lg font-semibold text-white mb-4">When do you prefer to study?</h3>
      <div className="text-white/70">
        <p>Schedule configuration will be implemented here.</p>
        <p>This would include time slots, preferred session duration, etc.</p>
      </div>
    </div>
  )
}

function IntegrationsStep({ formData, setFormData }: any) {
  const integrations = [
    { name: "Google Calendar", description: "Sync your study schedule" },
    { name: "Notion", description: "Track progress and take notes" },
    { name: "GitHub", description: "Connect your coding projects" }
  ]

  return (
    <div className="space-y-6">
      <h3 className="text-lg font-semibold text-white mb-4">Connect your tools (optional)</h3>
      <div className="space-y-3">
        {integrations.map((integration) => (
          <div key={integration.name} className="flex items-center justify-between p-4 bg-white/5 rounded-lg">
            <div>
              <h4 className="text-white font-medium">{integration.name}</h4>
              <p className="text-white/70 text-sm">{integration.description}</p>
            </div>
            <Button variant="outline" size="sm">
              Connect
            </Button>
          </div>
        ))}
      </div>
    </div>
  )
}

function GeneratePathStep({ formData }: any) {
  return (
    <div className="space-y-6 text-center">
      <h3 className="text-lg font-semibold text-white mb-4">Ready to generate your learning path!</h3>
      <div className="text-white/70 space-y-2">
        <p>Goals: {formData.goals.length} selected</p>
        <p>Skills assessed: {Object.keys(formData.skills).length}</p>
      </div>
      <Button variant="glassy" size="lg" className="mt-6">
        Generate My Learning Path
      </Button>
    </div>
  )
}