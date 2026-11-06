import type { ReactNode } from "react";

/** Moldura de smartphone; em telas pequenas ocupa 100% da viewport. */
export function PhoneFrame({ children }: { children: ReactNode }) {
  return (
    <div className="flex min-h-screen w-full justify-center bg-surface sm:items-center sm:py-8">
      <div className="flex h-screen w-full max-w-[420px] flex-col overflow-hidden bg-background shadow-float sm:h-[860px] sm:rounded-[32px]">
        {children}
      </div>
    </div>
  );
}
