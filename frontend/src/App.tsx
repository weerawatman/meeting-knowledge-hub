import { Routes, Route, Navigate } from "react-router-dom";
import { Layout } from "./components/Layout";
import { LoginPage } from "./modules/auth/LoginPage";
import { MeetingsModule } from "./modules/meetings/MeetingsModule";
import { LiveModule } from "./modules/live/LiveModule";
import { DigestModule } from "./modules/digest/DigestModule";
import { ChatModule } from "./modules/chat/ChatModule";
import { StudioModule } from "./modules/studio/StudioModule";
import { useAuth } from "./hooks/useAuth";

export default function App() {
  const { isAuthenticated } = useAuth();

  if (!isAuthenticated) {
    return <LoginPage />;
  }

  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Navigate to="/meetings" replace />} />
        <Route path="/meetings/*" element={<MeetingsModule />} />
        <Route path="/live" element={<LiveModule />} />
        <Route path="/digest" element={<DigestModule />} />
        <Route path="/chat" element={<ChatModule />} />
        <Route path="/studio" element={<StudioModule />} />
      </Routes>
    </Layout>
  );
}
