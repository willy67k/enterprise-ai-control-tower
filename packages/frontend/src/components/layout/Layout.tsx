import React from "react";
import { Sidebar, type TabId } from "./Sidebar";

interface LayoutProps {
  active: TabId;
  onNavigate: (_tab: TabId) => void;
  children: React.ReactNode;
}

export const Layout: React.FC = ({ active, onNavigate, children }) => {
  return (
    <div className="flex h-screen w-full overflow-hidden bg-gray-50">
      <Sidebar active={active} onNavigate={onNavigate} />
      <main className="flex flex-1 flex-col overflow-hidden">{children}</main>
    </div>
  );
};
