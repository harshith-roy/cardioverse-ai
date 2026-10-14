export function GlassPanel({ children, hover = false, className = '' }) {
  return (
    <div className={`glass-panel ${hover ? 'glass-panel-hover' : ''} ${className}`}>
      {children}
    </div>
  )
}
