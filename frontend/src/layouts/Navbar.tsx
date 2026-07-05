import logoSrc from '@/assets/logo.png'

export function Navbar() {
  return (
    <header className="fixed top-0 left-0 right-0 z-50">
      {/* Backdrop blur bar */}
      <div className="absolute inset-0 bg-background/60 backdrop-blur-2xl border-b border-border" />

      <nav className="relative section-container flex items-center justify-between h-[72px]">
        {/* Left: Logo (1.5x larger, 3.6rem) + Title + Subtitle */}
        <a href="/" className="flex items-center gap-3.5 group">
          <img
            src={logoSrc}
            alt="Veridict Logo"
            className="h-[3.6rem] w-[3.6rem] object-contain rounded-md transition-transform duration-300 group-hover:scale-105"
          />
          <div className="flex flex-col">
            <span className="font-display text-xl font-bold tracking-tight text-text-primary leading-tight">
              Veridict
            </span>
            <span className="text-[11px] text-muted-foreground tracking-wide leading-tight hidden sm:block">
              AI Response Quality Evaluator
            </span>
          </div>
        </a>

        {/* Right side is completely clean and minimal */}
        <div className="hidden md:flex items-center" />
      </nav>
    </header>
  )
}
