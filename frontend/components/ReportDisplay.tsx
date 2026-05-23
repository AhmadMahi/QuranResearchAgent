"use client";

import { useState } from "react";
import { Copy, Check, BookOpen, Clock, CloudSun, Globe } from "lucide-react";
import type { ResearchResult } from "@/lib/api";

interface Props {
  result: ResearchResult;
}

function renderMarkdown(md: string): string {
  return md
    .replace(/^## (.+)$/gm, '<h2>$1</h2>')
    .replace(/^### (.+)$/gm, '<h3>$1</h3>')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    .replace(/^- (.+)$/gm, '<li>$1</li>')
    .replace(/(<li>.*<\/li>\n?)+/g, (m) => `<ul>${m}</ul>`)
    .replace(/^\| (.+) \|$/gm, (row) => {
      const cells = row.split('|').filter(Boolean).map((c) => c.trim());
      return '<tr>' + cells.map((c) => `<td>${c}</td>`).join('') + '</tr>';
    })
    .replace(/(<tr>.*<\/tr>\n?)+/g, (m) => `<table>${m}</table>`)
    .replace(/\n{2,}/g, '</p><p>')
    .replace(/^(?!<[hultp])(.+)$/gm, '<p>$1</p>')
    .replace(/<p><\/p>/g, '');
}

export default function ReportDisplay({ result }: Props) {
  const [copied, setCopied] = useState(false);

  const copy = () => {
    navigator.clipboard.writeText(result.report);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const weather = result.weather_data as Record<string, unknown>;
  const prayer  = result.prayer_times;
  const refs    = result.quran_references.filter((r) => r.text);

  return (
    <div className="animate-fade-in space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-slate-100">Research Report</h2>
        <button onClick={copy} className="flex items-center gap-2 text-sm text-slate-400 hover:text-emerald-400 transition-colors">
          {copied ? <Check size={15} className="text-emerald-400" /> : <Copy size={15} />}
          {copied ? "Copied!" : "Copy"}
        </button>
      </div>

      {/* Stat pills */}
      <div className="flex flex-wrap gap-3">
        {refs.length > 0 && (
          <div className="glass-accent flex items-center gap-2 px-3 py-1.5 text-xs text-emerald-300">
            <BookOpen size={13} />
            {refs.length} Quranic reference{refs.length !== 1 ? "s" : ""}
          </div>
        )}
        {weather.temperature !== undefined && (
          <div className="glass flex items-center gap-2 px-3 py-1.5 text-xs text-sky-300"
            style={{ border: "1px solid rgba(56,189,248,0.25)" }}>
            <CloudSun size={13} />
            {String(weather.temperature)} °C · {String(weather.description ?? "")}
          </div>
        )}
        {Object.keys(prayer).length > 0 && !("error" in prayer) && (
          <div className="glass flex items-center gap-2 px-3 py-1.5 text-xs text-violet-300"
            style={{ border: "1px solid rgba(167,139,250,0.25)" }}>
            <Clock size={13} />
            Prayer times included
          </div>
        )}
        {result.web_results.length > 0 && (
          <div className="glass flex items-center gap-2 px-3 py-1.5 text-xs text-orange-300"
            style={{ border: "1px solid rgba(251,146,60,0.25)" }}>
            <Globe size={13} />
            {result.web_results.length} web source{result.web_results.length !== 1 ? "s" : ""}
          </div>
        )}
      </div>

      {/* Main report */}
      <div
        className="glass p-6 report-body"
        dangerouslySetInnerHTML={{ __html: renderMarkdown(result.report) }}
      />

      {/* Quran references sidebar */}
      {refs.length > 0 && (
        <div className="space-y-2">
          <h3 className="text-sm font-semibold text-slate-300 flex items-center gap-2">
            <BookOpen size={14} className="text-emerald-400" /> Quranic References
          </h3>
          {refs.slice(0, 3).map((r, i) => (
            <div key={i} className="glass-accent p-3 space-y-1">
              <p className="text-xs font-semibold text-emerald-300">{r.reference}</p>
              <p className="text-xs text-slate-300 leading-relaxed italic">"{r.text}"</p>
            </div>
          ))}
        </div>
      )}

      {/* Prayer times */}
      {Object.keys(prayer).length > 0 && !("error" in prayer) && (
        <div className="space-y-2">
          <h3 className="text-sm font-semibold text-slate-300 flex items-center gap-2">
            <Clock size={14} className="text-violet-400" /> Prayer Times
          </h3>
          <div className="glass grid grid-cols-3 gap-2 p-3">
            {Object.entries(prayer).map(([name, time]) => (
              <div key={name} className="text-center">
                <p className="text-xs text-slate-500">{name}</p>
                <p className="text-sm font-semibold text-violet-300">{time}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Web references */}
      {result.web_results.length > 0 && (
        <div className="space-y-2">
          <h3 className="text-sm font-semibold text-slate-300 flex items-center gap-2">
            <Globe size={14} className="text-orange-400" /> IslamQA References
          </h3>
          <div className="glass p-3 space-y-2">
            {result.web_results.slice(0, 5).map((r, i) => (
              <div key={i} className="text-xs text-slate-300 leading-relaxed">
                {r.url ? (
                  <a
                    href={r.url}
                    target="_blank"
                    rel="noreferrer"
                    className="text-orange-300 hover:text-orange-200 underline"
                  >
                    {r.title || r.url}
                  </a>
                ) : (
                  <span className="text-slate-400">{r.title}</span>
                )}
                {r.snippet && <p className="text-slate-400 mt-1">{r.snippet}</p>}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
