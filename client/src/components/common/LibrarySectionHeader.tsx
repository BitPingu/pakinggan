interface LibrarySectionHeaderProps {
  title: string
  count: string
}

// Displays a library section title and its item count.
function LibrarySectionHeader({ title, count }: LibrarySectionHeaderProps) {
  return (
    <div className="library-section-header">
      <h2>{title}</h2>
      <span className="library-count">{count}</span>
    </div>
  )
}

export default LibrarySectionHeader
