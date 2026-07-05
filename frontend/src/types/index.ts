/**
 * Global type definitions for Veridict design system.
 */

/** Navigation link shape */
export interface NavLink {
  label: string
  href: string
  icon?: React.ReactNode
}

/** Feature card data */
export interface FeatureItem {
  icon: React.ReactNode
  title: string
  description: string
}

/** Generic component props with className extension */
export interface BaseComponentProps {
  className?: string
  children?: React.ReactNode
}
