import { NavLink } from "react-router-dom";
import React from "react";

type LayoutProps = {
  children: React.ReactNode;
};

export default function Layout({ children }: LayoutProps) {
  return (
    <>
      <header
        style={{
          borderBottom: "1px solid #e2e8f0",
          background: "#ffffff",
        }}
      >
        <div className="container row" style={{ justifyContent: "space-between" }}>
          <div style={{ fontWeight: 700 }}>Аналитика вакансий</div>
          <nav className="row">
            <NavLink to="/" end>
              Дашборд
            </NavLink>
            <NavLink to="/vacancies">Вакансии</NavLink>
          </nav>
        </div>
      </header>
      <main className="container">{children}</main>
    </>
  );
}
