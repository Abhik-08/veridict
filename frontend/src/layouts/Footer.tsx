export function Footer() {
  return (
    <footer className="relative z-10 border-t border-border">
      <div className="section-container py-8 flex items-center justify-center">
        <p className="text-sm text-muted-foreground tracking-wide">
          Veridict &copy; {new Date().getFullYear()}
        </p>
      </div>
    </footer>
  )
}
