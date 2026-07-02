import { useAuth } from "../../hooks/useAuth";

export function StudioModule() {
  const { role } = useAuth();

  if (role !== "admin") {
    return (
      <div className="max-w-4xl mx-auto">
        <h2 className="text-2xl font-bold mb-4">Prompt Studio</h2>
        <div className="bg-red-50 rounded-xl p-8 text-center text-red-500">
          <p className="font-medium">เฉพาะ Admin เท่านั้น</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto">
      <h2 className="text-2xl font-bold mb-4">Prompt Studio</h2>
      <div className="bg-white rounded-xl p-8 shadow-sm text-center text-gray-400">
        <p className="text-4xl mb-3">⚙️</p>
        <p className="font-medium">Prompt Studio — Sprint 5</p>
        <p className="text-sm mt-1">Template editor + Golden Vault regression testing</p>
      </div>
    </div>
  );
}
