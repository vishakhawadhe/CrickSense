import * as React from "react";
import { createFileRoute, Link, useRouter } from "@tanstack/react-router";
import { AuthCard, FormInput, AuthButton } from "@/components/auth/AuthComponents";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";

export const Route = createFileRoute("/signup")({
  head: () => ({
    meta: [
      { title: "Sign Up — CrickSense" },
      { name: "description", content: "Create your CrickSense account to start analyzing your cricket technique with AI." },
    ],
  }),
  component: SignupPage,
});

function SignupPage() {
  const router = useRouter();
  const [formData, setFormData] = React.useState({
    fullName: "",
    email: "",
    password: "",
    confirmPassword: "",
    role: "Player",
    agreeToTerms: false,
  });
  const [errors, setErrors] = React.useState<Record<string, string>>({});
  const [isLoading, setIsLoading] = React.useState(false);
  const [successMsg, setSuccessMsg] = React.useState("");

  const validateField = (name: string, value: string) => {
    let err = "";
    if (name === "fullName") {
      if (!value.trim()) {
        err = "Full Name is required";
      }
    } else if (name === "email") {
      const val = value.trim();
      if (!val) {
        err = "Email is required";
      } else {
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
    } else if (name === "confirmPassword") {
      if (!value) {
        err = "Confirm Password is required";
      } else if (value !== formData.password) {
        err = "Passwords do not match";
      }
    }
    setErrors((prev) => ({ ...prev, [name]: err }));
    return !err;
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    if (errors[name]) {
      validateField(name, value);
    }
    
    // Additional live-check if typing confirmPassword while password exists, or vice-versa
    if (name === "password" && formData.confirmPassword) {
      setErrors((prev) => ({
        ...prev,
        confirmPassword: value === formData.confirmPassword ? "" : "Passwords do not match",
      }));
    }
  };

  const handleBlur = (e: React.FocusEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    validateField(name, value);
  };

  const handleCheckboxChange = (checked: boolean) => {
    setFormData((prev) => ({ ...prev, agreeToTerms: checked }));
    if (errors.agreeToTerms && checked) {
      setErrors((prev) => ({ ...prev, agreeToTerms: "" }));
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    // Validate all fields
    const isFullNameValid = validateField("fullName", formData.fullName);
    const isEmailValid = validateField("email", formData.email);
    const isPasswordValid = validateField("password", formData.password);
    const isConfirmPasswordValid = validateField("confirmPassword", formData.confirmPassword);

    let agreeErr = "";
    if (!formData.agreeToTerms) {
      agreeErr = "You must agree to the Terms & Privacy Policy to sign up";
      setErrors((prev) => ({ ...prev, agreeToTerms: agreeErr }));
    }

    if (
      !isFullNameValid ||
      !isEmailValid ||
      !isPasswordValid ||
      !isConfirmPasswordValid ||
      agreeErr
    ) {
      return;
    }

    setIsLoading(true);
    setSuccessMsg("");

    // Simulate signup request delay of 1s
    setTimeout(() => {
      setIsLoading(false);
      console.log("Signup data submitted successfully:", formData);
      setSuccessMsg("Account created successfully! Redirecting to profile setup...");

      setTimeout(() => {
        router.navigate({ to: "/profile-setup" });
      }, 1500);
    }, 1000);
  };

  return (
    <AuthCard title="Create Your Account" subtitle="Join CrickSense to level up your technique.">
      <form onSubmit={handleSubmit} noValidate>
        {successMsg && (
          <div className="mb-4 rounded-lg bg-[#22C55E]/10 border border-[#22C55E]/20 p-3 text-sm text-[#22C55E] font-medium animate-in fade-in duration-200">
            {successMsg}
          </div>
        )}

        <FormInput
          label="Full Name"
          name="fullName"
          id="fullName"
          type="text"
          placeholder="Enter your full name"
          value={formData.fullName}
          onChange={handleChange}
          onBlur={handleBlur}
          error={errors.fullName}
          disabled={isLoading}
          autoComplete="name"
        />

        <FormInput
          label="Email Address"
          name="email"
          id="email"
          type="email"
          placeholder="you@example.com"
          value={formData.email}
          onChange={handleChange}
          onBlur={handleBlur}
          error={errors.email}
          disabled={isLoading}
          autoComplete="email"
        />

        {/* Dropdown Selection */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-[#9CA3AF] mb-1.5" htmlFor="role">
            I am a...
          </label>
          <select
            id="role"
            name="role"
            value={formData.role}
            onChange={handleChange}
            disabled={isLoading}
            className="w-full h-11 px-3.5 rounded-lg border border-white/10 bg-[#1F2937] text-[#F9FAFB] outline-none focus:border-[#00D9C0] focus:ring-1 focus:ring-[#00D9C0] text-sm hover:border-white/20 transition duration-200 cursor-pointer disabled:opacity-50"
          >
            <option value="Player" className="bg-[#1F2937] text-[#F9FAFB]">Player</option>
            <option value="Coach" className="bg-[#1F2937] text-[#F9FAFB]">Coach</option>
            <option value="Parent" className="bg-[#1F2937] text-[#F9FAFB]">Parent</option>
          </select>
        </div>

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
          autoComplete="new-password"
        />

        <FormInput
          label="Confirm Password"
          name="confirmPassword"
          id="confirmPassword"
          type="password"
          placeholder="••••••••"
          value={formData.confirmPassword}
          onChange={handleChange}
          onBlur={handleBlur}
          error={errors.confirmPassword}
          disabled={isLoading}
          autoComplete="new-password"
        />

        <div className="mb-6">
          <div className="flex items-start space-x-2">
            <Checkbox
              id="agreeToTerms"
              checked={formData.agreeToTerms}
              onCheckedChange={handleCheckboxChange}
              disabled={isLoading}
              className="mt-0.5 border-white/20 data-[state=checked]:bg-[#00D9C0] data-[state=checked]:text-[#0A0E1A]"
            />
            <Label htmlFor="agreeToTerms" className="text-sm font-normal text-[#9CA3AF] cursor-pointer leading-tight selection:bg-transparent">
              I agree to the{" "}
              <a href="#" onClick={(e) => e.preventDefault()} className="font-semibold text-[#00D9C0] hover:underline">
                Terms of Service
              </a>{" "}
              &{" "}
              <a href="#" onClick={(e) => e.preventDefault()} className="font-semibold text-[#00D9C0] hover:underline">
                Privacy Policy
              </a>
            </Label>
          </div>
          {errors.agreeToTerms && (
            <p className="mt-1.5 text-xs text-[#EF4444] font-medium animate-in fade-in slide-in-from-top-1 duration-200">
              {errors.agreeToTerms}
            </p>
          )}
        </div>

        <AuthButton type="submit" isLoading={isLoading}>
          Create Account
        </AuthButton>

        <p className="mt-6 text-center text-sm text-[#9CA3AF]">
          Already have an account?{" "}
          <Link
            to="/login"
            className="font-semibold text-[#00D9C0] hover:underline"
          >
            Log In
          </Link>
        </p>
      </form>
    </AuthCard>
  );
}
