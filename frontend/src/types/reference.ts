export type Company = {
  company_id: number;
  name: string;
  website?: string | null;
  description?: string | null;
};

export type Experience = {
  experience_id: number;
  name: string;
  order: number;
};

export type WorkFormat = {
  work_format_id: number;
  name: string;
};

export type WorkSchedule = {
  work_schedule_id: number;
  name: string;
};

export type Skill = {
  skill_id: number;
  name: string;
  category?: string | null;
};
