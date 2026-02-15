import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import { cn } from '@/lib/utils';
import { QueryProvider } from '@/lib/query-provider';
import { GraphQLProvider } from '@/lib/graphql-provider';

const inter = Inter({ 
  subsets: ['latin'],
  variable: '--font-inter',
  display: 'swap',
});

export const metadata: Metadata = {
  title: 'Adaptive Learning Platform',
  description: 'AI-powered learning orchestrator for technical learners',
  keywords: ['learning', 'AI', 'education', 'programming', 'adaptive'],
  authors: [{ name: 'Adaptive Learning Platform Team' }],
  creator: 'Adaptive Learning Platform',
  publisher: 'Adaptive Learning Platform',
  formatDetection: {
    email: false,
    address: false,
    telephone: false,
  },
  metadataBase: new URL(process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3000'),
  openGraph: {
    title: 'Adaptive Learning Platform',
    description: 'AI-powered learning orchestrator for technical learners',
    url: '/',
    siteName: 'Adaptive Learning Platform',
    locale: 'en_US',
    type: 'website',
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Adaptive Learning Platform',
    description: 'AI-powered learning orchestrator for technical learners',
  },
  verification: {
    google: process.env.GOOGLE_SITE_VERIFICATION,
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark" suppressHydrationWarning>
      <body 
        className={cn(
          'min-h-screen bg-background font-sans antialiased',
          inter.variable
        )}
      >
        <QueryProvider>
          <GraphQLProvider>
            <div className="relative flex min-h-screen flex-col">
              <div className="flex-1">{children}</div>
            </div>
          </GraphQLProvider>
        </QueryProvider>
      </body>
    </html>
  );
}