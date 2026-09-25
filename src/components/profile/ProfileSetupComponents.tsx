import * as React from "react";

export interface SegmentedOption {
  label: string;
  value: string;
}

export function SegmentedSelect({
  label,
  options,
  value,
  onChange,
  required = false,
  className = "",
}: {
  label?: string;
  options: SegmentedOption[];
  value: string;
  onChange: (value: string) => void;
  required?: boolean;
  className?: string;
}) {
  return (
    <div className={`mb-5 ${className}`.trim()}>
      {label && (
        <div className="mb-2 flex items-center justify-between">
          <span className="text-sm font-semibold text-[#F9FAFB]">
            {label}
            {required && <span className="ml-1 text-[#EF4444]">*</span>}
          </span>
        </div>
      )}
      <div className="grid grid-cols-2 gap-2 rounded-2xl border border-white/10 bg-[#1F2937] p-2">
        {options.map((option) => {
          const isSelected = value === option.value;
          return (
            <button
              key={option.value}
              type="button"
              onClick={() => onChange(option.value)}
              className={`h-11 rounded-xl px-4 text-sm font-semibold transition-all duration-200 ${
                isSelected
                  ? "bg-[#00D9C0] text-[#0A0E1A] shadow-sm"
                  : "text-[#9CA3AF] hover:bg-white/5 hover:text-[#F9FAFB]"
              }`}
            >
              {option.label}
            </button>
          );
        })}
      </div>
    </div>
  );
}

export interface CardSelectOption {
  label: string;
  value: string;
  icon?: React.ReactNode;
  helper?: string;
}

export function CardSelect({
  label,
  options,
  value,
  onChange,
  required = false,
  columns = 3,
}: {
  label?: string;
  options: CardSelectOption[];
  value: string;
  onChange: (value: string) => void;
  required?: boolean;
  columns?: number;
}) {
  const gridColumns = columns === 2 ? "grid-cols-2" : columns === 4 ? "grid-cols-4" : "grid-cols-3";

  return (
    <div className="mb-5">
      {label && (
        <div className="mb-2 flex items-center justify-between">
          <span className="text-sm font-semibold text-[#F9FAFB]">
            {label}
            {required && <span className="ml-1 text-[#EF4444]">*</span>}
          </span>
        </div>
      )}
      <div className={`grid ${gridColumns} gap-3`}>
        {options.map((option) => {
          const isSelected = value === option.value;
          return (
            <button
              key={option.value}
              type="button"
              onClick={() => onChange(option.value)}
              className={`min-h-[92px] rounded-2xl border p-4 text-left transition-all duration-200 ${
                isSelected
                  ? "border-[#00D9C0] bg-[#00D9C0]/15 shadow-sm shadow-[#00D9C0]/10"
                  : "border-white/10 bg-[#1F2937] hover:border-white/30 hover:bg-white/5"
              }`}
            >
              <div className="flex items-center gap-2">
                {option.icon && (
                  <span className={`grid h-8 w-8 place-items-center rounded-lg ${isSelected ? "bg-[#00D9C0]/20 text-[#00D9C0]" : "bg-white/5 text-[#9CA3AF]"}`}>{option.icon}</span>
                )}
                <span className="text-sm font-semibold text-[#F9FAFB]">{option.label}</span>
              </div>
              {option.helper && (
                <p className="mt-2 text-[11px] leading-5 text-[#9CA3AF]">{option.helper}</p>
              )}
            </button>
          );
        })}
      </div>
    </div>
  );
}
