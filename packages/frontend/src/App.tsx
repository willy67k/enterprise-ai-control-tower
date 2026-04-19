import React, { useState } from "react";
import { ChatPanel } from "./components/chat/ChatPanel";
import { DocumentsPanel } from "./components/documents/DocumentsPanel";
import { Layout } from "./components/layout/Layout";
import type { TabId } from "./components/layout/Sidebar";
import { OrchestratorPanel } from "./components/orchestrator/OrchestratorPanel";
import { SettingsPanel } from "./components/settings/SettingsPanel";

const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<TabId>("orchestrator");

  return (
    <Layout active={activeTab} onNavigate={setActiveTab}>
      {activeTab === "orchestrator" && <OrchestratorPanel />}
      {activeTab === "chat" && <ChatPanel />}
      {activeTab === "documents" && <DocumentsPanel />}
      {activeTab === "settings" && <SettingsPanel />}
    </Layout>
  );
};

export default App;
