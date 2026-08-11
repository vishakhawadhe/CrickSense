import * as React from "react";
import { createFileRoute, Link } from "@tanstack/react-router";
import { AuthCard, FormInput, AuthButton } from "@/components/auth/AuthComponents";

export const Route = createFileRoute("/forgot-password")({
  head: () => ({
    meta: [
      { title: "Reset Password — CrickSense" },
      { name: "description", content: "Reset your CrickSense account password by receiving a secure verification link." },
    ],
  }),
  component: ForgotPasswordPage,
});

function ForgotPasswordPage() {
  const [email, setEmail] = React.useState("");
  const [error, setError] = React.useState("");
  const [isLoading, setIsLoading] = React.useState(false);
  const [successMsg, setSuccessMsg] = React.useState("");

  const validateEmail = (val: string) => {
    let err = "";
    const trimmed = val.trim();
    if (!trimmed) {
      err = "Email is required";
    } else {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(trimmed)) {
        err = "Please enter a valid email address";
      }
    }
    setError(err);
    return !err;
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { value } = e.target;
    setEmail(value);
    if (error) {
      validateEmail(value);
    }
  };

  const handleBlur = (e: React.FocusEvent<HTMLInputElement>) => {
    validateEmail(e.target.value);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    const isValid = validateEmail(email);
    if (!isValid) {
      return;
    }

    setIsLoading(true);
    setSuccessMsg("");

    // Simulate mock email dispatch delay of 1s
    setTimeout(() => {
      setIsLoading(false);
      console.log("Password reset link requested for email:", email.trim());
      setSuccessMsg("If an account exists for this email, a reset link has been sent.");
      setEmail(""); // clear input field
    }, 1000);
  };

  return (
    <AuthCard
      title="Reset Your Password"
      subtitle="Enter your email and we'll send you a link to reset your password."
    >
      <form onSubmit={handleSubmit} noValidate>
        {successMsg && (
          <div className="mb-6 rounded-lg bg-[#22C55E]/10 border border-[#22C55E]/20 p-3 text-sm text-[#22C55E] font-medium animate-in fade-in duration-200">
            {successMsg}
          </div>
        )}

        <FormInput
          label="Email Address"
          name="email"
          id="email"
          type="email"
          placeholder="you@example.com"
          value={email}
          onChange={handleChange}
          onBlur={handleBlur}
          error={error}
          disabled={isLoading}
          autoComplete="email"
        />

        <div className="mt-6 mb-6">
          <AuthButton type="submit" isLoading={isLoading}>
            Send Reset Link
          </AuthButton>
        </div>

        <p className="text-center text-sm text-[#9CA3AF]">
          <Link
            to="/login"
            className="font-semibold text-[#00D9C0] hover:underline"
          >
            Back to Login
          </Link>
        </p>
      </form>
    </AuthCard>
  );
}
