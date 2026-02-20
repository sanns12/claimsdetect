export default function RiskScore({ score }) {
  const getColor = () => {
    if (score > 70) return '#EF4444';
    if (score > 40) return '#F59E0B';
    return '#10B981';
  };

  const getLabel = () => {
    if (score > 70) return 'High Risk';
    if (score > 40) return 'Medium Risk';
    return 'Low Risk';
  };

  const color = getColor();

  return (
    <div className="text-center">
      <div className="relative w-32 h-32 mx-auto">
        {/* Circular progress */}
        <svg className="w-full h-full transform -rotate-90">
          <circle
            cx="64"
            cy="64"
            r="56"
            stroke="#1E2025"
            strokeWidth="8"
            fill="none"
          />
          <circle
            cx="64"
            cy="64"
            r="56"
            stroke={color}
            strokeWidth="8"
            fill="none"
            strokeLinecap="round"
            strokeDasharray={`${2 * Math.PI * 56}`}
            strokeDashoffset={`${2 * Math.PI * 56 * (1 - score / 100)}`}
            style={{ transition: 'stroke-dashoffset 0.5s' }}
          />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          <span className="text-3xl font-bold font-mono" style={{ color }}>
            {score}
          </span>
        </div>
      </div>
      <p className="mt-2 font-medium" style={{ color }}>{getLabel()}</p>
    </div>
  );
}
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

  return (
    <div className="mt-4">
      <h3 className="text-sm font-medium mb-3">LIME Explanation</h3>
      <p className="text-xs text-textSecondary mb-3">
        This claim was flagged due to the following factors:
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