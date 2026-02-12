"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";

import { api } from "@/lib/api";
import { setAuthTokens } from "@/lib/auth";

type AuthTokens = {
  access_token: string;
  refresh_token: string;
  token_type: string;
};

export function AuthCallbackClient() {
  const params = useSearchParams();
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const code = params.get("code");
    const state = params.get("state");
    if (!code || !state) {
      setError("Missing OAuth callback parameters");
      return;
    }
    (async () => {
      try {
        const tokens = await api.get<AuthTokens>(
          `/api/auth/github/callback?code=${encodeURIComponent(code)}&state=${encodeURIComponent(state)}`,
          false,
        );
        setAuthTokens(tokens.access_token, tokens.refresh_token);
        router.replace("/dashboard");
      } catch (err) {
        setError(err instanceof Error ? err.message : "OAuth callback failed");
      }
    })();
  }, [params, router]);

  return (
    <div className="container py-16">
      <div className="glass rounded-2xl p-6">
        <h1 className="text-xl font-semibold">Authenticating</h1>
        {error ? (
          <p className="mt-3 text-red-600">{error}</p>
        ) : (
          <p className="mt-3 text-slate-600">Completing GitHub OAuth flow...</p>
        )}
      </div>
    </div>
  );
}
