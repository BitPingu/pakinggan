interface EmptyStateProps {
  icon?: string
  title?: string
  description?: string
  message?: string
}

// Displays a consistent empty, loading, or error state.
function EmptyState({ icon, title, description, message }: EmptyStateProps) {
  return (
    <div className="empty-state">
      {icon && <span className="empty-state-icon">{icon}</span>}
      {title && <h3>{title}</h3>}
      {description && <p>{description}</p>}
      {message && <p>{message}</p>}
    </div>
  )
}

export default EmptyState
