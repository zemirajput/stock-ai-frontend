import { NavLink } from "react-router-dom";
import {
  LayoutDashboard,
  BrainCircuit,
  BarChart3,
  Info
} from "lucide-react";

function Sidebar() {

  return (

    <aside className="w-64 bg-slate-900 text-white min-h-screen p-6">

      <h1 className="text-2xl font-bold mb-10">
        📈 StockAI
      </h1>

      <nav className="space-y-3">

        <NavLink
          to="/"
          className={({ isActive }) =>
            `flex items-center gap-3 p-3 rounded-lg ${
              isActive
                ? "bg-blue-600"
                : "hover:bg-slate-800"
            }`
          }
        >
          <LayoutDashboard size={20} />
          Dashboard
        </NavLink>

        <NavLink
          to="/prediction"
          className={({ isActive }) =>
            `flex items-center gap-3 p-3 rounded-lg ${
              isActive
                ? "bg-blue-600"
                : "hover:bg-slate-800"
            }`
          }
        >
          <BrainCircuit size={20} />
          Prediction
        </NavLink>

        <NavLink
          to="/analytics"
          className={({ isActive }) =>
            `flex items-center gap-3 p-3 rounded-lg ${
              isActive
                ? "bg-blue-600"
                : "hover:bg-slate-800"
            }`
          }
        >
          <BarChart3 size={20} />
          Analytics
        </NavLink>

        <NavLink
          to="/about"
          className={({ isActive }) =>
            `flex items-center gap-3 p-3 rounded-lg ${
              isActive
                ? "bg-blue-600"
                : "hover:bg-slate-800"
            }`
          }
        >
          <Info size={20} />
          About
        </NavLink>

      </nav>

    </aside>

  );
}

export default Sidebar;