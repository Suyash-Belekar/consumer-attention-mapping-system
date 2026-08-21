import React from "react";
import Sidebar from "./Sidebar";
import Topbar from "./Topbar";
import ErrorBoundary from "./ErrorBoundary";

export default function Layout({ children }) {
  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <Sidebar />
      <div className="lg:pl-64">
        <Topbar />
        <main className="mx-auto max-w-[1600px] px-4 py-5 sm:px-6 lg:px-8">
          <ErrorBoundary>
            {children}
          </ErrorBoundary>
        </main>
      </div>
    </div>
  );
}
