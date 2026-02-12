export type AuthUser = {
  id: string;
  github_username: string;
  email?: string | null;
  avatar_url?: string | null;
};

export type Portfolio = {
  id: string;
  user_id: string;
  subdomain: string;
  custom_domain?: string | null;
  template_id: string;
  theme_config: Record<string, unknown>;
  is_published: boolean;
  last_generated_at?: string | null;
  view_count: number;
  created_at: string;
  updated_at: string;
};

export type GenerationJob = {
  id: string;
  user_id: string;
  portfolio_id: string;
  status: "pending" | "processing" | "completed" | "failed";
  progress_percentage: number;
  current_step?: string | null;
  error_message?: string | null;
  started_at: string;
  completed_at?: string | null;
};
