export default function Button({ children, variant = "primary", size = "md", className = "", ...props }) {
  const baseClasses = "rounded-lg font-medium transition-all shadow-lg hover:opacity-90";

  const variants = {
    primary: "bg-primary text-white shadow-blue-500/30",
    secondary: "bg-surface text-white hover:bg-opacity-80",
    danger: "bg-danger text-white",
    success: "bg-success text-white",
  };

  const sizes = {
    sm: "px-3 py-1.5 text-sm",
    md: "px-4 py-2",
    lg: "px-6 py-3 text-lg",
  };

  return (
    <button
      className={`${baseClasses} ${variants[variant]} ${sizes[size]} ${className}`}
      {...props}
    >
      {children}
    </button>
  );
}