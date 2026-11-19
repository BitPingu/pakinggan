import './PageHeader.css'

interface PageHeaderProps {
  eyebrow: string
  title: string
  description: string
}

// Displays a consistent heading across application pages.
function PageHeader({ eyebrow, title, description }: PageHeaderProps) {
  return (
    <header className="page-header">
      <span className="page-eyebrow">{eyebrow}</span>
      <h1>{title}</h1>
      <p className="page-description">{description}</p>
    </header>
  )
}

export default PageHeader
