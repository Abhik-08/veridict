import { Outlet } from 'react-router-dom'
import { AnimatedBackground, GridBackground, GradientBlobs } from '@/components'
import { Navbar } from './Navbar'
import { Footer } from './Footer'

/**
 * Root layout — wraps every page with the ambient background layers,
 * sticky navbar, and footer.
 */
export function RootLayout() {
  return (
    <div className="relative min-h-screen flex flex-col">
      {/* Ambient background layers */}
      <AnimatedBackground />
      <GridBackground />
      <GradientBlobs />

      {/* Navigation */}
      <Navbar />

      {/* Page content */}
      <main className="relative z-10 flex-1 pt-16">
        <Outlet />
      </main>

      {/* Footer */}
      <Footer />
    </div>
  )
}
