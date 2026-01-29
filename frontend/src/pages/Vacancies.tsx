import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import {
  getVacancies,
  getExperiences,
  getWorkFormats,
  getWorkSchedules,
  getSkills,
} from "../api/endpoints";
import type { VacancyFilters, VacancyWithCompany } from "../types/vacancy";

type FilterForm = {
  title: string;
  location: string;
  minSalary: string;
  maxSalary: string;
  experienceId: string;
  workFormatId: string;
  workScheduleId: string;
  activeOnly: boolean;
  skillIds: number[];
};

const PAGE_SIZE = 20;

function toNumber(value: string) {
  if (!value) return undefined;
  const num = Number(value);
  return Number.isNaN(num) ? undefined : num;
}

function formatSalary(vacancy: VacancyWithCompany) {
  const from = vacancy.salary_from ?? undefined;
  const to = vacancy.salary_to ?? undefined;
  const currency = vacancy.currency ?? "";
  if (from && to) return `${from} - ${to} ${currency}`.trim();
  if (from) return `от ${from} ${currency}`.trim();
  if (to) return `до ${to} ${currency}`.trim();
  return "Нет данных";
}

export default function Vacancies() {
  const [form, setForm] = useState<FilterForm>({
    title: "",
    location: "",
    minSalary: "",
    maxSalary: "",
    experienceId: "",
    workFormatId: "",
    workScheduleId: "",
    activeOnly: true,
    skillIds: [],
  });
  const [appliedForm, setAppliedForm] = useState(form);
  const [page, setPage] = useState(0);

  const { data: experiences } = useQuery({
    queryKey: ["experiences"],
    queryFn: getExperiences,
  });
  const { data: workFormats } = useQuery({
    queryKey: ["work-formats"],
    queryFn: getWorkFormats,
  });
  const { data: workSchedules } = useQuery({
    queryKey: ["work-schedules"],
    queryFn: getWorkSchedules,
  });
  const { data: skills } = useQuery({
    queryKey: ["skills"],
    queryFn: getSkills,
  });

  const filters = useMemo<VacancyFilters>(() => {
    return {
      title: appliedForm.title || undefined,
      location: appliedForm.location || undefined,
      min_salary: toNumber(appliedForm.minSalary),
      max_salary: toNumber(appliedForm.maxSalary),
      experience_id: toNumber(appliedForm.experienceId),
      work_format_id: toNumber(appliedForm.workFormatId),
      work_schedule_id: toNumber(appliedForm.workScheduleId),
      is_active: appliedForm.activeOnly,
      skill_ids: appliedForm.skillIds.length ? appliedForm.skillIds : undefined,
      offset: page * PAGE_SIZE,
      limit: PAGE_SIZE,
    };
  }, [appliedForm, page]);

  const {
    data: vacancies,
    isLoading,
    isError,
  } = useQuery({
    queryKey: ["vacancies", filters],
    queryFn: () => getVacancies(filters),
  });

  const toggleSkill = (skillId: number) => {
    setForm((prev) => {
      const exists = prev.skillIds.includes(skillId);
      return {
        ...prev,
        skillIds: exists
          ? prev.skillIds.filter((id) => id !== skillId)
          : [...prev.skillIds, skillId],
      };
    });
  };

  const applyFilters = () => {
    setAppliedForm(form);
    setPage(0);
  };

  const clearFilters = () => {
    const cleared: FilterForm = {
      title: "",
      location: "",
      minSalary: "",
      maxSalary: "",
      experienceId: "",
      workFormatId: "",
      workScheduleId: "",
      activeOnly: true,
      skillIds: [],
    };
    setForm(cleared);
    setAppliedForm(cleared);
    setPage(0);
  };

  return (
    <div className="stack">
      <h2>Вакансии</h2>

      <div className="card stack">
        <div className="row">
          <input
            className="input"
            placeholder="Ключевые слова"
            value={form.title}
            onChange={(e) => setForm({ ...form, title: e.target.value })}
          />
          <input
            className="input"
            placeholder="Локация"
            value={form.location}
            onChange={(e) => setForm({ ...form, location: e.target.value })}
          />
          <input
            className="input"
            placeholder="Мин. зарплата"
            value={form.minSalary}
            onChange={(e) => setForm({ ...form, minSalary: e.target.value })}
          />
          <input
            className="input"
            placeholder="Макс. зарплата"
            value={form.maxSalary}
            onChange={(e) => setForm({ ...form, maxSalary: e.target.value })}
          />
        </div>

        <div className="row">
          <select
            className="select"
            value={form.experienceId}
            onChange={(e) => setForm({ ...form, experienceId: e.target.value })}
          >
            <option value="">Опыт</option>
            {experiences?.map((exp) => (
              <option key={exp.experience_id} value={exp.experience_id}>
                {exp.name}
              </option>
            ))}
          </select>

          <select
            className="select"
            value={form.workFormatId}
            onChange={(e) => setForm({ ...form, workFormatId: e.target.value })}
          >
            <option value="">Формат работы</option>
            {workFormats?.map((fmt) => (
              <option key={fmt.work_format_id} value={fmt.work_format_id}>
                {fmt.name}
              </option>
            ))}
          </select>

          <select
            className="select"
            value={form.workScheduleId}
            onChange={(e) =>
              setForm({ ...form, workScheduleId: e.target.value })
            }
          >
            <option value="">График</option>
            {workSchedules?.map((schedule) => (
              <option
                key={schedule.work_schedule_id}
                value={schedule.work_schedule_id}
              >
                {schedule.name}
              </option>
            ))}
          </select>

          <label className="row" style={{ alignItems: "center" }}>
            <input
              type="checkbox"
              checked={form.activeOnly}
              onChange={(e) =>
                setForm({ ...form, activeOnly: e.target.checked })
              }
            />
            Только активные
          </label>
        </div>

        <div className="stack">
          <div className="muted">Навыки</div>
          <div className="row">
            {skills?.map((skill) => (
              <label key={skill.skill_id} className="row">
                <input
                  type="checkbox"
                  checked={form.skillIds.includes(skill.skill_id)}
                  onChange={() => toggleSkill(skill.skill_id)}
                />
                {skill.name}
              </label>
            ))}
          </div>
        </div>

        <div className="row">
          <button className="btn" onClick={applyFilters}>
            Применить
          </button>
          <button className="btn secondary" onClick={clearFilters}>
            Сбросить
          </button>
        </div>
      </div>

      {isLoading ? (
        <div className="card">Загрузка вакансий...</div>
      ) : isError ? (
        <div className="card">Не удалось загрузить вакансии.</div>
      ) : vacancies && vacancies.length ? (
        <div className="card">
          <table className="table">
            <thead>
              <tr>
                <th>Название</th>
                <th>Компания</th>
                <th>Локация</th>
                <th>Зарплата</th>
                <th>Опыт</th>
              </tr>
            </thead>
            <tbody>
              {vacancies.map((vacancy) => (
                <tr key={vacancy.vacancy_id}>
                  <td>
                    <Link to={`/vacancies/${vacancy.vacancy_id}`}>
                      {vacancy.title}
                    </Link>
                  </td>
                  <td>{vacancy.company?.name ?? "Нет данных"}</td>
                  <td>{vacancy.location ?? "Нет данных"}</td>
                  <td>{formatSalary(vacancy)}</td>
                  <td>{vacancy.experience?.name ?? "Нет данных"}</td>
                </tr>
              ))}
            </tbody>
          </table>
          <div className="row" style={{ marginTop: 12 }}>
            <button
              className="btn secondary"
              onClick={() => setPage((p) => Math.max(p - 1, 0))}
              disabled={page === 0}
            >
              Назад
            </button>
            <div className="muted">Страница {page + 1}</div>
            <button
              className="btn secondary"
              onClick={() => setPage((p) => p + 1)}
              disabled={vacancies.length < PAGE_SIZE}
            >
              Вперёд
            </button>
          </div>
        </div>
      ) : (
        <div className="card">Вакансии не найдены.</div>
      )}
    </div>
  );
}
