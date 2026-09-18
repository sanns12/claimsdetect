// Renders the SHAP explanation returned by the backend for a claim.
//
// `shap` is the object produced by backend/fraud_engine/shap_explainer.py:
//   { available, method, output_space, base_value, raw_margin,
//     features: [{ feature, value, shap_value, direction }] }
//
// Nothing is generated on the client. If the backend has no explanation for the
// claim (e.g. it was never scored, or the model was unavailable) an
// "unavailable" message is shown instead of placeholder factors.

const formatFeatureName = (name) =>
  String(name)
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (c) => c.toUpperCase());

const formatValue = (value) => {
  if (value === null || value === undefined) return 'not available';
  return Number.isInteger(value) ? value.toLocaleString() : Number(value.toFixed(3)).toString();
};

export default function SHAPExplanation({ shap = null, loading = false, maxFeatures = 8 }) {
  if (loading) {
    return (
      <div className="mt-4">
        <h3 className="text-sm font-medium mb-3">SHAP Explanation</h3>
        <div className="animate-pulse space-y-3">
          <div className="h-4 bg-surface rounded w-3/4"></div>
          <div className="space-y-2">
            <div className="h-2 bg-surface rounded w-full"></div>
            <div className="h-2 bg-surface rounded w-5/6"></div>
            <div className="h-2 bg-surface rounded w-4/6"></div>
          </div>
        </div>
      </div>
    );
  }

  const features = shap && shap.available && Array.isArray(shap.features) ? shap.features : [];

  if (features.length === 0) {
    return (
      <div className="mt-4">
        <h3 className="text-sm font-bold mb-2 flex items-center gap-2">
          <span className="w-1 h-4 bg-primary rounded-full"></span>
          SHAP Model Explanation
        </h3>
        <p className="text-xs text-textSecondary">
          {shap && shap.reason
            ? shap.reason
            : 'No model explanation is available for this claim.'}
        </p>
      </div>
    );
  }

  const shown = features.slice(0, maxFeatures);
  const maxMagnitude = Math.max(...shown.map((f) => Math.abs(f.shap_value)), 1e-9);

  return (
    <div className="mt-4">
      <h3 className="text-sm font-bold mb-3 flex items-center gap-2">
        <span className="w-1 h-4 bg-primary rounded-full"></span>
        SHAP Model Explanation
      </h3>

      <p className="text-xs text-textSecondary mb-4">
        Contribution of each input to the machine-learning score for this claim.
        Red pushes the score up, green pushes it down.
      </p>

      <div className="space-y-4">
        {shown.map((f) => {
          const increases = f.direction === 'increases_risk';
          const width = Math.max(4, Math.round((Math.abs(f.shap_value) / maxMagnitude) * 100));
          return (
            <div key={f.feature}>
              <div className="flex justify-between text-xs mb-1">
                <span className="font-medium">
                  {formatFeatureName(f.feature)}
                  <span className="text-textSecondary font-normal"> = {formatValue(f.value)}</span>
                </span>
                <span className={`font-mono ${increases ? 'text-danger' : 'text-success'}`}>
                  {increases ? '+' : ''}{f.shap_value.toFixed(3)}
                </span>
              </div>
              <div className="w-full bg-background rounded-full h-2">
                <div
                  className={`h-2 rounded-full ${increases ? 'bg-danger' : 'bg-success'}`}
                  style={{ width: `${width}%` }}
                ></div>
              </div>
            </div>
          );
        })}
      </div>

      <p className="text-[10px] text-textSecondary mt-4">
        Values are SHAP contributions in the model's log-odds space
        ({shap.method}). They explain the ML score only, not the other evidence layers.
      </p>
    </div>
  );
}
