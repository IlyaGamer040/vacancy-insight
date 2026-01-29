export type DashboardStats = {
  overview: {
    total_vacancies: number;
    active_vacancies: number;
    total_companies: number;
    total_skills: number;
  };
  salary: {
    with_salary: number;
    average_salary: number | null;
  };
  top_skills: Array<{ skill: string; count: number }>;
  experience_distribution: Array<{ experience: string; count: number }>;
};
