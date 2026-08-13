"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Phone, CheckCircle, XCircle, TrendingUp, RefreshCw, ShieldCheck, ArrowLeft, Wrench } from "lucide-react";

interface CallRecord {
  call_id: string;
  user_id: string;
  customer_name: string;
  channel: string;
  status: "successful" | "failed";
  outcome_reason: string;
  tools_used: string[];
  duration_seconds: number;
  started_at: string;
}

interface AnalyticsData {
  total_calls: number;
  successful_calls: number;
  failed_calls: number;
  success_rate: number;
  recent_calls: CallRecord[];
}

export default function DashboardPage() {
  const [data, setData] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [filter, setFilter] = useState<"all" | "successful" | "failed">("all");

  const fetchAnalytics = async () => {
    setLoading(true);
    try {
      const res = await fetch("/api/analytics");
      const json = await res.json();
      setData(json);
    } catch (e) {
      console.error("Failed to fetch analytics:", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalytics();
    const interval = setInterval(fetchAnalytics, 4000);
    return () => clearInterval(interval);
  }, []);

  const filteredCalls = (data?.recent_calls || []).filter((call) => {
    if (filter === "successful") return call.status === "successful";
    if (filter === "failed") return call.status === "failed";
    return true;
  });

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-6 md:p-10">
      <div className="max-w-6xl mx-auto space-y-8">
        {/* Top Navbar */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-6">
          <div>
            <div className="flex items-center gap-3">
              <Link
                href="/"
                className="text-xs text-indigo-400 hover:text-indigo-300 flex items-center gap-1 bg-slate-900 border border-slate-800 px-3 py-1.5 rounded-lg transition"
              >
                <ArrowLeft className="w-3.5 h-3.5" /> Back to Agent UI
              </Link>
              <span className="text-xs font-semibold px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span> Live SQLite Data
              </span>
            </div>
            <h1 className="text-3xl font-bold tracking-tight text-white mt-2">
              📊 DukaanSaathi — Call Analytics Dashboard
            </h1>
            <p className="text-slate-400 text-sm mt-1">
              Real-time performance metrics, success tracking, and call history for Sharma General Store Voice Assistant.
            </p>
          </div>

          <button
            onClick={fetchAnalytics}
            disabled={loading}
            className="flex items-center justify-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-sm px-4 py-2.5 rounded-xl shadow-lg shadow-indigo-600/20 transition disabled:opacity-50 cursor-pointer"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
            Refresh Analytics
          </button>
        </div>

        {/* Metrics Cards Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
          {/* Card 1: Total Calls */}
          <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl shadow-sm relative overflow-hidden">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">Total Calls</span>
              <div className="p-2.5 bg-indigo-500/10 text-indigo-400 rounded-xl border border-indigo-500/20">
                <Phone className="w-5 h-5" />
              </div>
            </div>
            <div className="mt-4 flex items-baseline gap-2">
              <span className="text-4xl font-extrabold text-white">{data?.total_calls ?? 0}</span>
              <span className="text-xs text-slate-500">all channels</span>
            </div>
            <p className="text-xs text-slate-400 mt-2">Combined Browser WebRTC & Outbound SIP calls</p>
          </div>

          {/* Card 2: Successful Calls */}
          <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl shadow-sm relative overflow-hidden">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold uppercase tracking-wider text-emerald-400">Successful Calls</span>
              <div className="p-2.5 bg-emerald-500/10 text-emerald-400 rounded-xl border border-emerald-500/20">
                <CheckCircle className="w-5 h-5" />
              </div>
            </div>
            <div className="mt-4 flex items-baseline gap-2">
              <span className="text-4xl font-extrabold text-emerald-400">{data?.successful_calls ?? 0}</span>
              <span className="text-xs text-emerald-500/80">completed</span>
            </div>
            <p className="text-xs text-slate-400 mt-2">Inquiries, price lookups, bills, tickets completed</p>
          </div>

          {/* Card 3: Failed Calls */}
          <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl shadow-sm relative overflow-hidden">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold uppercase tracking-wider text-rose-400">Failed Calls</span>
              <div className="p-2.5 bg-rose-500/10 text-rose-400 rounded-xl border border-rose-500/20">
                <XCircle className="w-5 h-5" />
              </div>
            </div>
            <div className="mt-4 flex items-baseline gap-2">
              <span className="text-4xl font-extrabold text-rose-400">{data?.failed_calls ?? 0}</span>
              <span className="text-xs text-rose-500/80">unresolved</span>
            </div>
            <p className="text-xs text-slate-400 mt-2">Early disconnects or uncompleted inquiries</p>
          </div>

          {/* Card 4: Success Rate */}
          <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl shadow-sm relative overflow-hidden">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold uppercase tracking-wider text-indigo-400">Success Rate</span>
              <div className="p-2.5 bg-indigo-500/10 text-indigo-400 rounded-xl border border-indigo-500/20">
                <TrendingUp className="w-5 h-5" />
              </div>
            </div>
            <div className="mt-4 flex items-baseline gap-2">
              <span className="text-4xl font-extrabold text-white">{data?.success_rate ?? 0}%</span>
            </div>
            <div className="w-full bg-slate-800 h-2 rounded-full mt-3 overflow-hidden">
              <div
                className="bg-indigo-500 h-full rounded-full transition-all duration-500"
                style={{ width: `${Math.min(data?.success_rate ?? 0, 100)}%` }}
              ></div>
            </div>
          </div>
        </div>

        {/* Privacy Assurance Alert */}
        <div className="bg-slate-900/60 border border-indigo-500/20 p-4 rounded-xl flex items-center gap-3 text-xs text-slate-300">
          <ShieldCheck className="w-5 h-5 text-indigo-400 shrink-0" />
          <span>
            <strong className="text-white">Privacy Guard Active:</strong> No passwords, PINs, OTPs, bank numbers, or raw voice transcripts are displayed or logged in compliance with Day 8 safety guidelines.
          </span>
        </div>

        {/* Call History Section */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <h2 className="text-lg font-semibold text-white">Call Logs & Outcome History</h2>
              <p className="text-xs text-slate-400">Real-time log of calls connected to DukaanSaathi voice agent</p>
            </div>

            {/* Filter Buttons */}
            <div className="flex items-center gap-1 bg-slate-950 p-1 rounded-xl border border-slate-800 text-xs">
              <button
                onClick={() => setFilter("all")}
                className={`px-3 py-1.5 rounded-lg font-medium transition cursor-pointer ${
                  filter === "all" ? "bg-indigo-600 text-white" : "text-slate-400 hover:text-white"
                }`}
              >
                All ({data?.recent_calls?.length ?? 0})
              </button>
              <button
                onClick={() => setFilter("successful")}
                className={`px-3 py-1.5 rounded-lg font-medium transition cursor-pointer ${
                  filter === "successful" ? "bg-emerald-600 text-white" : "text-slate-400 hover:text-white"
                }`}
              >
                Successful ({data?.successful_calls ?? 0})
              </button>
              <button
                onClick={() => setFilter("failed")}
                className={`px-3 py-1.5 rounded-lg font-medium transition cursor-pointer ${
                  filter === "failed" ? "bg-rose-600 text-white" : "text-slate-400 hover:text-white"
                }`}
              >
                Failed ({data?.failed_calls ?? 0})
              </button>
            </div>
          </div>

          {/* Table */}
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-300">
              <thead className="bg-slate-950/80 text-slate-400 uppercase tracking-wider text-[11px] border-b border-slate-800">
                <tr>
                  <th className="py-3 px-4">Call ID</th>
                  <th className="py-3 px-4">Caller / Customer</th>
                  <th className="py-3 px-4">Channel</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4">Outcome & Tools Used</th>
                  <th className="py-3 px-4">Duration</th>
                  <th className="py-3 px-4">Time</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {filteredCalls.length === 0 ? (
                  <tr>
                    <td colSpan={7} className="py-8 text-center text-slate-500">
                      No calls recorded yet. Make a test call on http://localhost:3000 to view live metrics!
                    </td>
                  </tr>
                ) : (
                  filteredCalls.map((call) => (
                    <tr key={call.call_id} className="hover:bg-slate-800/30 transition">
                      <td className="py-3.5 px-4 font-mono text-slate-400">{call.call_id}</td>
                      <td className="py-3.5 px-4 font-medium text-white">{call.customer_name}</td>
                      <td className="py-3.5 px-4">
                        <span className="inline-flex items-center gap-1 text-[11px] px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
                          {call.channel === "sip_outbound" ? "📞 SIP Outbound" : "🌐 Browser WebRTC"}
                        </span>
                      </td>
                      <td className="py-3.5 px-4">
                        {call.status === "successful" ? (
                          <span className="inline-flex items-center gap-1 text-[11px] font-semibold px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                            <CheckCircle className="w-3 h-3" /> SUCCESSFUL
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-1 text-[11px] font-semibold px-2.5 py-1 rounded-full bg-rose-500/10 text-rose-400 border border-rose-500/20">
                            <XCircle className="w-3 h-3" /> FAILED
                          </span>
                        )}
                      </td>
                      <td className="py-3.5 px-4 max-w-xs">
                        <div className="space-y-1">
                          <p className="text-slate-300 truncate">{call.outcome_reason}</p>
                          {call.tools_used.length > 0 && (
                            <div className="flex flex-wrap gap-1 mt-1">
                              {call.tools_used.map((tool) => (
                                <span
                                  key={tool}
                                  className="text-[10px] bg-indigo-500/10 text-indigo-300 border border-indigo-500/20 px-1.5 py-0.5 rounded flex items-center gap-1"
                                >
                                  <Wrench className="w-2.5 h-2.5" /> {tool}
                                </span>
                              ))}
                            </div>
                          )}
                        </div>
                      </td>
                      <td className="py-3.5 px-4 text-slate-400">{call.duration_seconds}s</td>
                      <td className="py-3.5 px-4 text-slate-400 font-mono text-[11px]">
                        {new Date(call.started_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" })}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
