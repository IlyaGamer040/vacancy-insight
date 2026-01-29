export type CompanyInVacancy = {
  company_id: number;
  name: string;
};

export type ExperienceInVacancy = {
  experience_id: number;
  name: string;
};

export type WorkFormatInVacancy = {
  work_format_id: number;
  name: string;
};

export type WorkScheduleInVacancy = {
  work_schedule_id: number;
  name: string;
};

export type SkillInVacancy = {
  skill_id: number;
  name?: string | null;
  category?: string | null;
  is_mandatory: boolean;
};

export type VacancyBase = {
  title: string;
  description: string;
  salary_from?: number | null;
  salary_to?: number | null;
  currency?: string | null;
  location?: string | null;
  raw_address?: string | null;
  parsed_address?: string | null;
  source_url: string;
  published_date?: string | null;
  is_active: boolean;
};

export type VacancySimple = VacancyBase & {
  vacancy_id: number;
  company_id: number;
  experience_id: number;
  work_format_id: number;
  work_schedule_id: number;
};

export type VacancyWithCompany = VacancySimple & {
  company?: CompanyInVacancy | null;
  experience?: ExperienceInVacancy | null;
};

export type Vacancy = VacancySimple & {
  company?: CompanyInVacancy | null;
  experience?: ExperienceInVacancy | null;
  work_format?: WorkFormatInVacancy | null;
  work_schedule?: WorkScheduleInVacancy | null;
  skills: SkillInVacancy[];
};

export type VacancyFilters = {
  title?: string;
  location?: string;
  min_salary?: number;
  max_salary?: number;
  experience_id?: number;
  work_format_id?: number;
  work_schedule_id?: number;
  skill_ids?: number[];
  is_active?: boolean;
  offset?: number;
  limit?: number;
};
