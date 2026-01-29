import { useQuery } from "@tanstack/react-query";
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip } from "recharts";
import { getDashboard } from "../api/endpoints";
import StatCard from "../components/StatCard";

export default function Dashboard() {
  const { data, isLoading, isError } = useQuery({
    queryKey: ["dashboard"],
    queryFn: getDashboard,
  });

  if (isLoading) {
    return <div className="card">Загрузка дашборда...</div>;
  }

  if (isError || !data) {
    return <div className="card">Не удалось загрузить дашборд.</div>;
  }

  return (
    <div className="stack">
      <h2>Дашборд</h2>

      <div className="grid grid-4">
        <StatCard label="Всего вакансий" value={data.overview.total_vacancies} />
        <StatCard label="Активные вакансии" value={data.overview.active_vacancies} />
        <StatCard label="Компаний" value={data.overview.total_companies} />
        <StatCard label="Навыков" value={data.overview.total_skills} />
      </div>

      <div className="grid grid-2">
        <div className="card stack">
          <div style={{ fontWeight: 600 }}>Топ навыков</div>
          <div style={{ height: 280 }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.top_skills}>
                <XAxis dataKey="skill" tick={{ fontSize: 12 }} />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Bar dataKey="count" fill="#2563eb" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="card stack">
          <div style={{ fontWeight: 600 }}>Распределение по опыту</div>
          <div style={{ height: 280 }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.experience_distribution}>
                <XAxis dataKey="experience" tick={{ fontSize: 12 }} />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Bar dataKey="count" fill="#22c55e" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      <div className="grid grid-2">
        <StatCard
          label="Вакансий с зарплатой"
          value={data.salary.with_salary}
        />
        <StatCard
          label="Средняя зарплата"
          value={data.salary.average_salary ?? "Нет данных"}
        />
      </div>
    </div>
  );
}
