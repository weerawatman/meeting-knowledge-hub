import { NavLink } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";

const NAV_ITEMS = [
  { to: "/meetings", label: "Meeting Knowledge", icon: "🎙️" },
  { to: "/live", label: "Live Capture", icon: "🔴" },
  { to: "/digest", label: "Executive Digest", icon: "📄" },
  { to: "/chat", label: "Knowledge Chat", icon: "💬" },
  { to: "/studio", label: "Prompt Studio", icon: "⚙️" },
];

export function Layout({ children }: { children: React.ReactNode }) {
  const { email, role, logout } = useAuth();

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Sidebar */}
      <aside className="w-64 bg-slate-900 text-white flex flex-col">
        <div className="px-6 py-5 border-b border-slate-700">
          <h1 className="text-lg font-bold">Meeting Hub</h1>
          <p className="text-xs text-slate-400 mt-0.5">Private AI Knowledge</p>
        </div>
        <nav className="flex-1 py-4 space-y-1 px-2">
          {NAV_ITEMS.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `flex items-center gap-3 px-4 py-2.5 rounded-lg text-sm transition-colors ${
                  isActive
                    ? "bg-blue-600 text-white"
                    : "text-slate-300 hover:bg-slate-700 hover:text-white"
                }`
              }
            >
              <span>{item.icon}</span>
              <span>{item.label}</span>
            </NavLink>
          ))}
        </nav>
        <div className="px-4 py-4 border-t border-slate-700">
          <p className="text-xs text-slate-400 truncate">{email}</p>
          <p className="text-xs text-slate-500">{role}</p>
          <button
            onClick={logout}
            className="mt-2 text-xs text-red-400 hover:text-red-300"
          >
            ออกจากระบบ
          </button>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-auto p-6">{children}</main>
    </div>
  );
}
