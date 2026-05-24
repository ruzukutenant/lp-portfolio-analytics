import snapshotJson from "@/data/snapshot.json";
import positionsJson from "@/data/positions.json";
import cashProjectionJson from "@/data/cash_projection.json";
import fundamentalEvsJson from "@/data/fundamental_evs.json";
import type { CashProjection, FundamentalEv, Position, Snapshot } from "./types";

export const snapshot = snapshotJson as unknown as Snapshot;
export const positions = positionsJson as unknown as Position[];
export const cashProjection = cashProjectionJson as unknown as CashProjection;
export const fundamentalEvs = fundamentalEvsJson as unknown as Record<string, FundamentalEv>;

export function fmtUsd(n: number, opts?: { compact?: boolean; sign?: boolean }) {
  const abs = Math.abs(n);
  const sign = n < 0 ? "−" : opts?.sign ? "+" : "";
  if (opts?.compact && abs >= 1_000_000) return `${sign}$${(abs / 1_000_000).toFixed(2)}M`;
  if (opts?.compact && abs >= 10_000) return `${sign}$${Math.round(abs / 1000)}K`;
  if (opts?.compact && abs >= 1000) return `${sign}$${(abs / 1000).toFixed(1)}K`;
  return `${sign}$${abs.toLocaleString("en-US", { maximumFractionDigits: 0 })}`;
}

export function fmtPct(n: number, digits = 1) {
  return `${(n * 100).toFixed(digits)}%`;
}

export function fmtMultiple(n: number, digits = 2) {
  return `${n.toFixed(digits)}×`;
}

export function lookupFundamentalEv(company: string): FundamentalEv | undefined {
  const key = company.toLowerCase().replace(/\s+/g, "-");
  return fundamentalEvs[key];
}
