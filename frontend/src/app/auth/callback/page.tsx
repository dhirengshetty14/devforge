import { Suspense } from "react";

import { AuthCallbackClient } from "@/app/auth/callback/AuthCallbackClient";

export const dynamic = "force-dynamic";

export default function AuthCallbackPage() {
  return (
    <Suspense fallback={<div className="container py-16 text-slate-600">Loading auth callback...</div>}>
      <AuthCallbackClient />
    </Suspense>
  );
}
