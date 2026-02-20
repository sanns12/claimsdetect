export default function LIMEExplanation({ factors, loading }) {
  if (loading) {
    return (
      <div className="mt-4">
        <h3 className="text-sm font-medium mb-3">LIME Explanation</h3>
        <div className="animate-pulse space-y-3">
          <div className="h-4 bg-surface rounded w-3/4"></div>
          <div className="h-2 bg-surface rounded w-full"></div>
          <div className="h-2 bg-surface rounded w-5/6"></div>
        </div>
      </div>
    );
  }

  if (!factors || factors.length === 0) {
    return (
      <div className="mt-4">
        <h3 className="text-sm font-medium mb-3">LIME Explanation</h3>
        <p className="text-xs text-textSecondary">
          No explanation factors available for this claim.
        </p>
      </div>
    );
  }

  return (
    <div className="mt-4">
      <h3 className="text-sm font-medium mb-3">LIME Explanation</h3>
      <p className="text-xs text-textSecondary mb-3">
        This claim's risk score is influenced by:
      </p>
      <div className="space-y-3">
        {factors.map((factor, index) => (
          <div key={index}>
            <div className="flex justify-between text-xs mb-1">
              <span>{factor.name}</span>
              <span className={
                factor.impact > 30 ? 'text-danger' : 
                factor.impact > 15 ? 'text-warning' : 'text-success'
              }>
                {factor.impact}% influence
              </span>
            </div>
            <div className="w-full bg-background rounded-full h-1.5">
              <div 
                className={`h-1.5 rounded-full ${
                  factor.impact > 30 ? 'bg-danger' : 
                  factor.impact > 15 ? 'bg-warning' : 'bg-success'
                }`}
                style={{ width: `${factor.impact}%` }}
              ></div>
            </div>
            {factor.description && (
              <p className="text-xs text-textSecondary mt-1">{factor.description}</p>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
