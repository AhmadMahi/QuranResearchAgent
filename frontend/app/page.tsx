"use client";

import { useState, useRef } from "react";
import {
  Search, BookOpen, Sparkles, MapPin, Globe2, AlertCircle, RotateCcw,
} from "lucide-react";
import AgentProgress, { AgentStep } from "@/components/AgentProgress";
import ReportDisplay from "@/components/ReportDisplay";
import { streamResearch, ResearchResult } from "@/lib/api";

const EXAMPLE_TOPICS = [
  "Patience and perseverance in Islam",
  "Environmental stewardship and sustainability",
  "The pursuit of knowledge in Islamic tradition",
  "Gratitude and mindfulness",
];

export default function Home() {
  const [topic, setTopic]     = useState("");
  const [city, setCity]       = useState("London");
  const [country, setCountry] = useState("United Kingdom");
  const [loading, setLoading] = useState(false);
  const [steps, setSteps]     = useState<AgentStep[]>([]);
  const [result, setResult]   = useState<ResearchResult | null>(null);
  const [error, setError]     = useState("");

  const resultRef  = useRef<HTMLDivElement>(null);
  const abortRef   = useRef<AbortController | null>(null);

  const reset = () => {
    abortRef.current?.abort();
    setLoading(false);
    setSteps([]);
    setResult(null);
    setError("");
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!topic.trim() || loading) return;

    reset();
    setLoading(true);

    const ctrl = new AbortController();
    abortRef.current = ctrl;

    await streamResearch(
      { topic: topic.trim(), city, country },
      (s) => setSteps((prev) => [...prev, s]),
      (r) => {
        setResult(r);
        setLoading(false);
        setTimeout(() => resultRef.current?.scrollIntoView({ behavior: "smooth" }), 100);
      },
      (msg) => {
        setError(msg);
        setLoading(false);
      },
      ctrl.signal,
    );
  };

  return (
    <div className="page-bg min-h-screen">
      <div className="max-w-3xl mx-auto px-4 py-12 space-y-10">

        {/* ── Header ─────────────────────────────────────────────────────── */}
        <header className="text-center space-y-3">
          <div className="inline-flex items-center gap-2 glass-accent px-4 py-1.5 text-xs text-emerald-400 rounded-full mb-2">
            <Sparkles size={12} />
            Powered by GPT-4o-mini · LangGraph · ChromaDB
          </div>
          <h1 className="text-4xl font-bold tracking-tight">
            <span className="gradient-text">Islamic Research</span>
            <br />
            <span className="text-slate-100">Agent</span>
          </h1>
          <p className="text-slate-400 text-base max-w-lg mx-auto leading-relaxed">
            Enter any topic — the AI pipeline fetches Quranic references, current weather,
            prayer times and live web research, then synthesises a structured report.
          </p>
        </header>

        {/* ── Form ───────────────────────────────────────────────────────── */}
        <div className="glass p-6 space-y-5">
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Topic */}
            <div className="space-y-1.5">
              <label className="text-sm text-slate-300 flex items-center gap-1.5">
                <BookOpen size={13} className="text-emerald-400" /> Research Topic
              </label>
              <div className="relative">
                <input
                  className="input-field pr-12"
                  placeholder="e.g. Gratitude and mindfulness in Islam…"
                  value={topic}
                  onChange={(e) => setTopic(e.target.value)}
                  disabled={loading}
                  maxLength={500}
                />
                <Search size={16} className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 pointer-events-none" />
              </div>
            </div>

            {/* City / Country row */}
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1.5">
                <label className="text-sm text-slate-300 flex items-center gap-1.5">
                  <MapPin size={13} className="text-sky-400" /> City
                </label>
                <input
                  className="input-field"
                  placeholder="London"
                  value={city}
                  onChange={(e) => setCity(e.target.value)}
                  disabled={loading}
                />
              </div>
              <div className="space-y-1.5">
                <label className="text-sm text-slate-300 flex items-center gap-1.5">
                  <Globe2 size={13} className="text-sky-400" /> Country
                </label>
                <input
                  className="input-field"
                  placeholder="United Kingdom"
                  value={country}
                  onChange={(e) => setCountry(e.target.value)}
                  disabled={loading}
                />
              </div>
            </div>

            {/* Actions */}
            <div className="flex gap-3 pt-1">
              <button
                type="submit"
                className="btn-primary flex items-center gap-2 flex-1 justify-center"
                disabled={loading || !topic.trim()}
              >
                {loading ? (
                  <>
                    <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    Researching…
                  </>
                ) : (
                  <>
                    <Search size={15} /> Start Research
                  </>
                )}
              </button>
              {(loading || result || error) && (
                <button
                  type="button"
                  onClick={reset}
                  className="glass px-4 py-2 text-sm text-slate-300 hover:text-white transition-colors flex items-center gap-1.5 rounded-xl"
                >
                  <RotateCcw size={14} /> Reset
                </button>
              )}
            </div>
          </form>

          {/* Example topics */}
          {!loading && !result && (
            <div className="space-y-2">
              <p className="text-xs text-slate-500">Try an example:</p>
              <div className="flex flex-wrap gap-2">
                {EXAMPLE_TOPICS.map((t) => (
                  <button
                    key={t}
                    onClick={() => setTopic(t)}
                    className="text-xs px-3 py-1.5 rounded-full transition-colors"
                    style={{
                      background: "rgba(16,185,129,0.08)",
                      border: "1px solid rgba(16,185,129,0.2)",
                      color: "#a7f3d0",
                    }}
                  >
                    {t}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* ── Error ──────────────────────────────────────────────────────── */}
        {error && (
          <div className="glass flex items-start gap-3 p-4 animate-fade-in"
            style={{ borderColor: "rgba(239,68,68,0.3)", background: "rgba(239,68,68,0.06)" }}>
            <AlertCircle size={16} className="text-red-400 flex-shrink-0 mt-0.5" />
            <p className="text-sm text-red-300">{error}</p>
          </div>
        )}

        {/* ── Agent progress ──────────────────────────────────────────────── */}
        {loading && (
          <div className="glass p-5 animate-fade-in">
            <AgentProgress steps={steps} loading={loading} />
          </div>
        )}

        {/* ── Result ─────────────────────────────────────────────────────── */}
        {result && (
          <div ref={resultRef}>
            <ReportDisplay result={result} />
          </div>
        )}

        {/* ── Footer ─────────────────────────────────────────────────────── */}
        <footer className="text-center text-xs text-slate-600 pt-4">
          Quran API · Azan API · DuckDuckGo Search · OpenWeatherMap · LangSmith Tracing
        </footer>
      </div>
    </div>
  );
}
