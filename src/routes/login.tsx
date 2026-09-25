import * as React from "react";
import { createFileRoute, Link, useRouter } from "@tanstack/react-router";
import { AuthCard, FormInput, AuthButton } from "@/components/auth/AuthComponents";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";

export const Route = createFileRoute("/login")({
  head: () => ({
    meta: [
      { title: "Log In — CrickSense" },
      { name: "description", content: "Log in to your CrickSense account to access your biomechanics analytics dashboard." },
    ],
  }),
  component: LoginPage,
});

function LoginPage() {
  const router = useRouter();
  const [formData, setFormData] = React.useState({
    identifier: "",
    password: "",
    rememberMe: false,
  });
  const [errors, setErrors] = React.useState<Record<string, string>>({});
  const [isLoading, setIsLoading] = React.useState(false);
  const [successMsg, setSuccessMsg] = React.useState("");

  // Input blur/change handlers for inline validation
  const validateField = (name: string, value: string) => {
    let err = "";
    if (name === "identifier") {
      const val = value.trim();
      if (!val) {
        err = "Email or Username is required";
      } else if (val.includes("@")) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(val)) {
          err = "Please enter a valid email address";
        }
      }
    } else if (name === "password") {
      if (!value) {
        err = "Password is required";
      } else if (value.length < 6) {
        err = "Password must be at least 6 characters";
      }
    }
    setErrors((prev) => ({ ...prev, [name]: err }));
    return !err;
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    if (errors[name]) {
      validateField(name, value);
    }
  };

  const handleBlur = (e: React.FocusEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    validateField(name, value);
  };

  const handleCheckboxChange = (checked: boolean) => {
    setFormData((prev) => ({ ...prev, rememberMe: checked }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    // Validate all fields before submission
    const isIdentifierValid = validateField("identifier", formData.identifier);
    const isPasswordValid = validateField("password", formData.password);

    if (!isIdentifierValid || !isPasswordValid) {
      return;
    }

    setIsLoading(true);
    setSuccessMsg("");

    // Simulate mock authentication delay of 1s
    setTimeout(() => {
      setIsLoading(false);
      console.log("Login data submitted successfully:", formData);
      setSuccessMsg("Logged in successfully! Redirecting...");

      setTimeout(() => {
        router.navigate({ to: "/profile-setup" });
      }, 1500);
    }, 1000);
  };

  return (
    <AuthCard title="Welcome Back" subtitle="Log in to analyze your technique.">
      <form onSubmit={handleSubmit} noValidate>
        {successMsg && (
          <div className="mb-4 rounded-lg bg-[#22C55E]/10 border border-[#22C55E]/20 p-3 text-sm text-[#22C55E] font-medium animate-in fade-in duration-200">
            {successMsg}
          </div>
        )}

        <FormInput
          label="Email or Username"
          name="identifier"
          id="identifier"
          type="text"
          placeholder="Enter your email or username"
          value={formData.identifier}
          onChange={handleChange}
          onBlur={handleBlur}
          error={errors.identifier}
          disabled={isLoading}
          autoComplete="username"
        />

        <FormInput
          label="Password"
          name="password"
          id="password"
          type="password"
          placeholder="••••••••"
          value={formData.password}
          onChange={handleChange}
          onBlur={handleBlur}
          error={errors.password}
          disabled={isLoading}
          autoComplete="current-password"
        />

        <div className="mb-6 flex items-center justify-between text-sm">
          <div className="flex items-center space-x-2">
            <Checkbox
              id="rememberMe"
              checked={formData.rememberMe}
              onCheckedChange={handleCheckboxChange}
              disabled={isLoading}
              className="border-white/20 data-[state=checked]:bg-[#00D9C0] data-[state=checked]:text-[#0A0E1A]"
            />
            <Label htmlFor="rememberMe" className="text-sm font-normal text-[#9CA3AF] cursor-pointer selection:bg-transparent">
              Remember me
            </Label>
          </div>
          <Link
            to="/forgot-password"
            className="text-xs font-semibold text-[#00D9C0] hover:underline"
          >
            Forgot Password?
          </Link>
        </div>

        <AuthButton type="submit" isLoading={isLoading}>
          Log In
        </AuthButton>

        {/* Divider */}
        <div className="my-6 flex items-center justify-center gap-3">
          <div className="h-px flex-1 bg-white/10"></div>
          <span className="text-xs text-[#9CA3AF] uppercase font-semibold tracking-wider">or continue with</span>
          <div className="h-px flex-1 bg-white/10"></div>
        </div>

        {/* OAuth mock buttons */}
        <div className="grid grid-cols-2 gap-3 mb-6">
          <button
            type="button"
            onClick={() => console.log("Google OAuth Clicked")}
            disabled={isLoading}
            className="h-10 flex items-center justify-center gap-2 rounded-lg border border-white/10 bg-[#1F2937] hover:bg-[#2D3748] transition-colors text-sm text-[#F9FAFB] cursor-pointer disabled:opacity-50"
          >
            <svg className="h-4 w-4" viewBox="0 0 24 24" fill="currentColor">
              <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
              <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
              <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z" fill="#FBBC05"/>
              <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z" fill="#EA4335"/>
            </svg>
            Google
          </button>
          <button
            type="button"
            onClick={() => console.log("Apple OAuth Clicked")}
            disabled={isLoading}
            className="h-10 flex items-center justify-center gap-2 rounded-lg border border-white/10 bg-[#1F2937] hover:bg-[#2D3748] transition-colors text-sm text-[#F9FAFB] cursor-pointer disabled:opacity-50"
          >
            <svg className="h-4 w-4" viewBox="0 0 24 24" fill="currentColor">
              <path d="M18.71 19.5c-.83 1.24-1.71 2.45-3.05 2.47-1.34.03-1.77-.79-3.29-.79-1.53 0-2 .77-3.27.82-1.31.05-2.3-1.32-3.14-2.53C4.25 17 2.94 12.45 4.7 9.39c.87-1.52 2.43-2.48 4.12-2.51 1.28-.02 2.5.87 3.29.87.78 0 2.26-1.07 3.81-.91.65.03 2.47.26 3.64 1.98-.09.06-2.17 1.28-2.15 3.81.03 3.02 2.65 4.03 2.68 4.04-.03.07-.42 1.44-1.38 2.83M15.97 4.17c.66-.81 1.11-1.93.99-3.06-1 .04-2.22.67-2.94 1.51-.62.71-1.16 1.85-1.01 2.96 1.11.09 2.27-.6 2.96-1.41z"/>
            </svg>
            Apple
          </button>
        </div>

        <p className="text-center text-sm text-[#9CA3AF]">
          Don't have an account?{" "}
          <Link
            to="/signup"
            className="font-semibold text-[#00D9C0] hover:underline"
          >
            Sign Up
          </Link>
        </p>
      </form>
    </AuthCard>
  );
}
