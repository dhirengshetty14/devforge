export type TemplateDefinition = {
  id: string;
  name: string;
  description: string;
  defaults: {
    accent: string;
    font: string;
  };
};

export type GenerationProgressEvent = {
  job_id: string;
  status: string;
  progress: number;
  step: string;
  url?: string;
  error?: string;
};
