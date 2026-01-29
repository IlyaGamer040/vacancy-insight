import { api, buildParams } from "./client";
import type { DashboardStats } from "../types/dashboard";
import type {
  Vacancy,
  VacancyWithCompany,
  VacancyFilters,
} from "../types/vacancy";
import type {
  Experience,
  WorkFormat,
  WorkSchedule,
  Skill,
  Company,
} from "../types/reference";

export async function getDashboard() {
  const { data } = await api.get<DashboardStats>("/stats/dashboard");
  return data;
}

export async function getVacancies(filters: VacancyFilters) {
  const params = buildParams(filters);
  const { data } = await api.get<VacancyWithCompany[]>("/vacancies", { params });
  return data;
}

export async function getVacancy(id: number) {
  const { data } = await api.get<Vacancy>(`/vacancies/${id}`);
  return data;
}

export async function getExperiences() {
  const { data } = await api.get<Experience[]>("/experiences");
  return data;
}

export async function getWorkFormats() {
  const { data } = await api.get<WorkFormat[]>("/work-formats");
  return data;
}

export async function getWorkSchedules() {
  const { data } = await api.get<WorkSchedule[]>("/work-schedules");
  return data;
}

export async function getSkills() {
  const { data } = await api.get<Skill[]>("/skills");
  return data;
}

export async function getCompanies() {
  const { data } = await api.get<Company[]>("/companies");
  return data;
}
