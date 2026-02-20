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
