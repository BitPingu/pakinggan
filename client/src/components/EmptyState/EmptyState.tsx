import type { LucideIcon } from 'lucide-react'
import './EmptyState.css'

interface EmptyStateProps {
  icon?: LucideIcon
  title?: string
  description?: string
  message?: string
}

// Displays a consistent empty, loading, or error state.
function EmptyState({
  icon: Icon,
  title,
  description,
  message,
}: EmptyStateProps) {
  return (
    <div className="empty-state">
      {Icon && (
        <Icon
          className="empty-state-icon"
          size={30}
          strokeWidth={1.8}
          aria-hidden="true"
        />
      )}
      {title && <h3>{title}</h3>}
      {description && <p>{description}</p>}
      {message && <p>{message}</p>}
    </div>
  )
}

export default EmptyState
