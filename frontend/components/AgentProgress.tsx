"use client";

import { BookOpen, Cloud, Globe, Database, FileText, CheckCircle2, Loader2, Circle } from "lucide-react";

export interface AgentStep {
  step: string;
  agent: string;
}

interface Props {
  steps: AgentStep[];
  loading: boolean;
}

const AGENTS = [
  { key: "quran_researcher", label: "Quran Research Agent", icon: BookOpen, color: "#a78bfa" },
  { key: "weather_reporter", label: "Weather & Prayer Agent", icon: Cloud, color: "#38bdf8" },
  { key: "web_searcher",     label: "Web Search Agent",      icon: Globe,  color: "#fb923c" },
  { key: "vector_storer",    label: "Knowledge Base Agent",  icon: Database, color: "#f472b6" },
  { key: "formatter",        label: "Report Formatter Agent", icon: FileText, color: "#10b981" },
];

type Status = "waiting" | "active" | "done";

export default function AgentProgress({ steps, loading }: Props) {
  const completedAgents = new Set(
    steps.filter((s) => s.step.startsWith("✓")).map((s) => s.agent)
  );
  const lastStep = steps[steps.length - 1];
  const activeAgent = loading && lastStep ? lastStep.agent : "";

  function getStatus(key: string): Status {
    if (completedAgents.has(key)) return "done";
    if (activeAgent === key) return "active";
    return "waiting";
  }

  return (
    <div className="space-y-3">
      <p className="text-sm text-slate-400 mb-4">Research pipeline running…</p>

      {AGENTS.map((agent) => {
        const status = getStatus(agent.key);
        const Icon = agent.icon;

        return (
          <div
            key={agent.key}
            className="glass flex items-center gap-4 px-4 py-3 animate-slide-up"
            style={{ opacity: status === "waiting" ? 0.45 : 1 }}
          >
            {/* Icon */}
            <div
              className="relative flex-shrink-0 w-9 h-9 rounded-full flex items-center justify-center"
              style={{ background: `${agent.color}18`, border: `1px solid ${agent.color}40` }}
            >
              <Icon size={16} style={{ color: agent.color }} />
              {status === "active" && (
                <span className="absolute inset-0 rounded-full animate-ping opacity-30"
                  style={{ background: agent.color }} />
              )}
            </div>

            {/* Label */}
            <span className="flex-1 text-sm font-medium text-slate-200">{agent.label}</span>

            {/* Status icon */}
            {status === "done" && <CheckCircle2 size={18} className="text-emerald-400 flex-shrink-0" />}
            {status === "active" && <Loader2 size={18} className="animate-spin flex-shrink-0" style={{ color: agent.color }} />}
            {status === "waiting" && <Circle size={18} className="text-slate-600 flex-shrink-0" />}
          </div>
        );
      })}

      {/* Live step log */}
      {steps.length > 0 && (
        <div className="mt-4 glass p-3 space-y-1 max-h-40 overflow-y-auto">
          {steps.map((s, i) => (
            <p key={i} className="text-xs text-slate-400 animate-fade-in">
              {s.step}
            </p>
          ))}
        </div>
      )}
    </div>
  );
}
