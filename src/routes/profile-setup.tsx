import * as React from "react";
import { createFileRoute, Link, useRouter } from "@tanstack/react-router";
import { AuthCard, AuthButton } from "@/components/auth/AuthComponents";
import { CardSelect, SegmentedSelect } from "@/components/profile/ProfileSetupComponents";

export const Route = createFileRoute("/profile-setup")({
  head: () => ({
    meta: [
      { title: "Profile Setup — CrickSense" },
      { name: "description", content: "Complete your CrickSense player profile setup before entering your dashboard." },
    ],
  }),
  component: ProfileSetupPage,
});

function ProfileSetupPage() {
  const router = useRouter();
  const [formData, setFormData] = React.useState({
    gender: "",
    ageCategory: "",
    dominantHand: "",
    bowlingStyle: "",
  });

  const [errors, setErrors] = React.useState<Record<string, string>>({});
  const [isLoading, setIsLoading] = React.useState(false);
  const [successMsg, setSuccessMsg] = React.useState("");

  const validateField = (name: keyof typeof formData, value: string) => {
    const err = value.trim() ? "" : `Please select your ${name}`;
    setErrors((prev) => ({ ...prev, [name]: err }));
    return !err;
  };

  const updateField = (name: keyof typeof formData, value: string) => {
    setFormData((prev) => ({ ...prev, [name]: value }));
    if (errors[name]) {
      validateField(name, value);
    }
  };

  const validateAll = () => {
    const nextErrors: Record<string, string> = {};

    (Object.keys(formData) as Array<keyof typeof formData>).forEach((key) => {
      if (!formData[key]) {
        nextErrors[key] = `Please select your ${key}`;
      }
    });

    setErrors(nextErrors);
    return Object.keys(nextErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    const isValid = validateAll();
    if (!isValid) {
      return;
    }

    setIsLoading(true);
    setSuccessMsg("");

    setTimeout(() => {
      setIsLoading(false);
      console.log("Profile Setup submitted successfully:", formData);
      setSuccessMsg("Profile saved successfully! Redirecting to your dashboard...");

      setTimeout(() => {
        router.navigate({ to: "/dashboard" });
      }, 1200);
    }, 700);
  };

  return (
    <AuthCard title="Player Profile Setup" subtitle="Tell us about your playing profile so we can personalize your analysis.">
      <form onSubmit={handleSubmit} noValidate>
        {successMsg && (
          <div className="mb-4 rounded-lg bg-[#22C55E]/10 border border-[#22C55E]/20 p-3 text-sm text-[#22C55E] font-medium animate-in fade-in duration-200">
            {successMsg}
          </div>
        )}

        <SegmentedSelect
          label="Gender"
          options={[
            { label: "Female", value: "female" },
            { label: "Male", value: "male" },
            { label: "Other", value: "other" },
          ]}
          value={formData.gender}
          onChange={(value) => updateField("gender", value)}
          required
          className="mb-4"
        />
        {errors.gender && (
          <p className="-mt-3 mb-4 text-xs text-[#EF4444] font-medium">{errors.gender}</p>
        )}

        <CardSelect
          label="Age Category"
          options={[
            { label: "U-19", value: "u19", helper: "Under 19" },
            { label: "U-23", value: "u23", helper: "Under 23" },
            { label: "U-25", value: "u25", helper: "Under 25" },
            { label: "Senior", value: "senior", helper: "25+" },
          ]}
          value={formData.ageCategory}
          onChange={(value) => updateField("ageCategory", value)}
          required
          columns={2}
        />
        {errors.ageCategory && (
          <p className="-mt-3 mb-4 text-xs text-[#EF4444] font-medium">{errors.ageCategory}</p>
        )}

        <SegmentedSelect
          label="Dominant Bowling Hand"
          options={[
            { label: "Right Hand", value: "right" },
            { label: "Left Hand", value: "left" },
          ]}
          value={formData.dominantHand}
          onChange={(value) => updateField("dominantHand", value)}
          required
          className="mb-4"
        />
        {errors.dominantHand && (
          <p className="-mt-3 mb-4 text-xs text-[#EF4444] font-medium">{errors.dominantHand}</p>
        )}

        <CardSelect
          label="Bowling Style"
          options={[
            { label: "Fast", value: "fast", helper: "Pace bowling" },
            { label: "Swing", value: "swing", helper: "Late movement" },
            { label: "Spin", value: "spin", helper: "Wrist / finger spin" },
            { label: "Seam", value: "seam", helper: "Conventional seam" },
          ]}
          value={formData.bowlingStyle}
          onChange={(value) => updateField("bowlingStyle", value)}
          required
          columns={2}
        />
        {errors.bowlingStyle && (
          <p className="-mt-3 mb-4 text-xs text-[#EF4444] font-medium">{errors.bowlingStyle}</p>
        )}

        <div className="mt-6">
          <AuthButton type="submit" isLoading={isLoading}>
            Save & Continue
          </AuthButton>
        </div>

        <div className="mt-4 text-center">
          <Link
            to="/dashboard"
            className="text-sm font-semibold text-[#00D9C0] hover:underline"
          >
            Skip for now
          </Link>
        </div>
      </form>
    </AuthCard>
  );
}
