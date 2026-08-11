import * as React from "react";
import { Link } from "@tanstack/react-router";
import { Activity, Eye, EyeOff, Loader2 } from "lucide-react";

// AuthCard Component: Centers the form in a premium card styled with custom design tokens.
export function AuthCard({
  children,
  title,
  subtitle,
}: {
  children: React.ReactNode;
  title: string;
  subtitle?: string;
}) {
  return (
    <div className="flex min-h-screen items-center justify-center bg-[#0A0E1A] px-4 py-12 font-sans text-[#F9FAFB]">
      <div className="w-full max-w-md rounded-2xl border border-white/10 bg-[#111827] p-8 shadow-lg shadow-black/40 animate-in fade-in zoom-in-95 duration-300">
        <div className="mb-8 flex flex-col items-center text-center">
          <Link to="/" className="mb-4 flex items-center gap-2 hover:opacity-90">
            <span className="grid h-9 w-9 place-items-center rounded-lg bg-[#00D9C0] text-[#0A0E1A]">
              <Activity className="h-5 w-5" strokeWidth={2.5} />
            </span>
            <span className="text-xl font-bold tracking-tight text-[#F9FAFB]">CrickSense</span>
          </Link>
          <h2 className="text-2xl font-bold tracking-tight text-[#F9FAFB]">{title}</h2>
          {subtitle && <p className="mt-2 text-sm text-[#9CA3AF]">{subtitle}</p>}
        </div>
        {children}
      </div>
    </div>
  );
}

// FormInputProps Interface
interface FormInputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label: string;
  error?: string;
  name: string;
}

// FormInput Component: Text input with support for validation error message and password visibility toggling.
export const FormInput = React.forwardRef<HTMLInputElement, FormInputProps>(
  ({ label, error, type = "text", className = "", ...props }, ref) => {
    const [showPassword, setShowPassword] = React.useState(false);
    const isPassword = type === "password";
    const inputType = isPassword ? (showPassword ? "text" : "password") : type;

    return (
      <div className="mb-4">
        <label className="block text-sm font-medium text-[#9CA3AF] mb-1.5" htmlFor={props.name}>
          {label}
        </label>
        <div className="relative">
          <input
            ref={ref}
            type={inputType}
            className={`w-full h-11 px-3.5 rounded-lg border bg-[#1F2937] text-[#F9FAFB] placeholder-[#6B7280] transition duration-200 outline-none focus:border-[#00D9C0] focus:ring-1 focus:ring-[#00D9C0] text-sm ${
              error ? "border-[#EF4444]" : "border-white/10 hover:border-white/20"
            } ${isPassword ? "pr-10" : ""} ${className}`}
            {...props}
          />
          {isPassword && (
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-[#9CA3AF] hover:text-[#F9FAFB] transition-colors focus:outline-none"
            >
              {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
            </button>
          )}
        </div>
        {error && (
          <p className="mt-1.5 text-xs text-[#EF4444] font-medium animate-in fade-in slide-in-from-top-1 duration-200">
            {error}
          </p>
        )}
      </div>
    );
  }
);
FormInput.displayName = "FormInput";

// AuthButtonProps Interface
interface AuthButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  isLoading?: boolean;
}

// AuthButton Component: Premium action button with loading spinner state support.
export function AuthButton({ children, isLoading, className = "", disabled, ...props }: AuthButtonProps) {
  return (
    <button
      disabled={isLoading || disabled}
      className={`w-full h-11 flex items-center justify-center gap-2 rounded-lg bg-[#00D9C0] text-[#0A0E1A] font-semibold text-sm transition-all duration-200 hover:bg-[#00c5ae] active:scale-[0.99] disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer ${className}`}
      {...props}
    >
      {isLoading && <Loader2 className="h-4 w-4 animate-spin" />}
      {children}
    </button>
  );
}
