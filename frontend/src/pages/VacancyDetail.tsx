import { useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { getVacancy } from "../api/endpoints";

export default function VacancyDetail() {
  const params = useParams();
  const vacancyId = Number(params.id);

  const { data, isLoading, isError } = useQuery({
    queryKey: ["vacancy", vacancyId],
    queryFn: () => getVacancy(vacancyId),
    enabled: Number.isFinite(vacancyId),
  });

  if (!Number.isFinite(vacancyId)) {
    return <div className="card">Некорректный id вакансии.</div>;
  }

  if (isLoading) {
    return <div className="card">Загрузка вакансии...</div>;
  }

  if (isError || !data) {
    return <div className="card">Не удалось загрузить вакансию.</div>;
  }

  return (
    <div className="stack">
      <h2>{data.title}</h2>
      <div className="card stack">
        <div>
          <strong>Компания:</strong> {data.company?.name ?? "Нет данных"}
        </div>
        <div>
          <strong>Локация:</strong> {data.location ?? "Нет данных"}
        </div>
        <div>
          <strong>Опыт:</strong> {data.experience?.name ?? "Нет данных"}
        </div>
        <div>
          <strong>Формат работы:</strong> {data.work_format?.name ?? "Нет данных"}
        </div>
        <div>
          <strong>График работы:</strong> {data.work_schedule?.name ?? "Нет данных"}
        </div>
        <div>
          <strong>Зарплата:</strong>{" "}
          {data.salary_from || data.salary_to
            ? `${data.salary_from ?? ""} - ${data.salary_to ?? ""} ${
                data.currency ?? ""
              }`.trim()
            : "Нет данных"}
        </div>
        <div>
          <strong>Источник:</strong>{" "}
          <a href={data.source_url} target="_blank" rel="noreferrer">
            {data.source_url}
          </a>
        </div>
        <div>
          <strong>Описание:</strong>
          <div className="muted" style={{ marginTop: 6 }}>
            {data.description || "Нет данных"}
          </div>
        </div>
        <div>
          <strong>Навыки:</strong>
          <div className="row">
            {data.skills?.length
              ? data.skills.map((skill) => (
                  <span key={skill.skill_id} className="muted">
                    {skill.name ?? `Навык ${skill.skill_id}`}
                  </span>
                ))
              : "Нет данных"}
          </div>
        </div>
      </div>
    </div>
  );
}
