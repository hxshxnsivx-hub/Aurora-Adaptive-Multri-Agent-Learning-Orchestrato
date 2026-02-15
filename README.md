# Adaptive Learning Platform

An AI-powered web application that serves as an intelligent learning orchestrator for technical learners preparing for exams, hackathons, and interviews. The system uses a multi-agent AI architecture to generate personalized learning paths, curate resources, and dynamically adapt to user progress and feedback.

## 🚀 Features

- **Personalized Learning Paths**: AI-generated paths tailored to your skill level and goals
- **Multi-Agent AI System**: 12 specialized agents working together to optimize your learning
- **Dynamic Resource Curation**: Content from YouTube, GitHub, articles, courses, and PDFs
- **Real-time Adaptation**: Intelligent path adjustments based on progress and feedback
- **Calendar & Notion Integration**: Seamless workflow integration
- **Voice Assistant**: Natural language interaction with STT/TTS
- **Modern Glassy UI**: Dark-mode-first design with smooth animations

## 🛠️ Tech Stack

### Frontend
- **Next.js 14** with App Router
- **TypeScript** for type safety
- **Tailwind CSS** for styling
- **shadcn/ui** for components
- **TanStack Query** for server state
- **Zustand** for client state

### Backend
- **FastAPI** with async support
- **Strawberry GraphQL** for flexible APIs
- **LangGraph** for multi-agent workflows
- **PostgreSQL** for structured data
- **Redis** for caching and jobs
- **Pinecone** for vector search

### AI & Integrations
- **OpenAI GPT-4** for LLM capabilities
- **Google Calendar API** for scheduling
- **Notion API** for task management
- **YouTube Data API** for video resources
- **GitHub API** for code resources
- **ElevenLabs** for text-to-speech

## 📋 Prerequisites

- Node.js 18+ and npm/yarn
- Python 3.11+
- PostgreSQL 14+
- Redis 6+
- Docker (optional, for containerized development)

## 🚀 Quick Start

### 1. Clone and Setup Frontend

```bash
# Install dependencies
npm install

# Copy environment variables
cp .env.local.example .env.local

# Edit .env.local with your API keys and configuration
```

### 2. Development

```bash
# Start development server
npm run dev

# Run type checking
npm run type-check

# Run linting
npm run lint

# Run tests
npm run test
```

### 3. Build for Production

```bash
# Build the application
npm run build

# Start production server
npm start
```

## 📁 Project Structure

```
src/
├── app/                    # Next.js App Router pages
│   ├── globals.css        # Global styles
│   ├── layout.tsx         # Root layout
│   └── page.tsx           # Home page
├── components/            # Reusable UI components
├── hooks/                 # Custom React hooks
├── lib/                   # Utility functions
├── store/                 # Zustand stores
├── types/                 # TypeScript type definitions
└── utils/                 # Helper utilities
```

## 🎨 Design System

The platform uses a modern glassy aesthetic with:

- **Dark-mode-first** design
- **Glassmorphism** effects with backdrop blur
- **Smooth animations** and micro-interactions
- **Responsive design** for all devices
- **Accessibility-compliant** components

### Custom CSS Classes

```css
.glass              /* Basic glass effect */
.glass-card         /* Glass card with rounded corners */
.glass-button       /* Interactive glass button */
.gradient-text      /* Gradient text effect */
.animated-bg        /* Animated gradient background */
.shimmer           /* Loading shimmer effect */
```

## 🔧 Configuration

### Environment Variables

Key environment variables to configure:

```bash
# App
NEXT_PUBLIC_APP_URL=http://localhost:3000

# Auth0
AUTH0_SECRET=your-secret
AUTH0_CLIENT_ID=your-client-id

# APIs
OPENAI_API_KEY=your-openai-key
GOOGLE_CLIENT_ID=your-google-client-id
```

### Tailwind Configuration

The project includes custom Tailwind configuration for:
- Glass morphism utilities
- Custom color palette
- Animation keyframes
- Responsive breakpoints

## 🧪 Testing

```bash
# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm run test:coverage
```

## 📦 Deployment

### Vercel (Recommended)

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel --prod
```

### Docker

```bash
# Build image
docker build -t adaptive-learning-platform .

# Run container
docker run -p 3000:3000 adaptive-learning-platform
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

<<<<<<< Updated upstream

=======
>>>>>>> Stashed changes

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Check the documentation
- Join our community discussions

---

Built with ❤️ by the Adaptive Learning Platform Team
