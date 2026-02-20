import { STATUS_COLORS } from '../utils/constants';

export default function StatusBadge({ status }) {
  return (
    <span
      className="px-3 py-1 rounded-full text-xs font-medium inline-block"
      style={{
        backgroundColor: STATUS_COLORS[status] + '20',
        color: STATUS_COLORS[status],
      }}
    >
      {status}
    </span>
  );
}