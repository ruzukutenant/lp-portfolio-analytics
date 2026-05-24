export interface Notice {
  status: "implemented" | "pending";
  headline: string;
  detail: string;
  methodology_link?: string;
}

export interface Snapshot {
  snapshot_date: string;
  fund_id: string;
  fund_name: string;
  fund_description: string;
  deployed_usd: number;
  paid_in_usd: number;
  fee_drag_usd: number;
  already_distributed_usd: number;
  future_p50_net_usd: number;
  total_p50_net_usd: number;
  after_tax_p50_usd: number;
  moic_on_paid_in: number;
  moic_after_tax: number;
  p10_net_pretax_usd: number;
  p90_net_pretax_usd: number;
  qsbs_coverage_pct: number;
  audit_notice: Notice;
  verification_notice: Notice;
}

export interface Position {
  company: string;
  entry_date: string;
  entry_round: string;
  status: string;
  cost_usd: number;
  gp_current_mark_usd: number;
  gp_multiple: number;
  dilution_adjusted_mark_usd: number | null;
  rounds_since_entry: number | null;
  cumulative_survival: number | null;
  expected_exit_usd: number | null;
  expected_multiple_on_cost: number | null;
  cohort: string;
  exit_year: number;
  qsbs_eligible: boolean;
  realized: boolean;
}

export interface CashProjection {
  paid_in_usd: number;
  p10_usd: number;
  p50_usd: number;
  p90_usd: number;
  p50_composition: {
    already_received_usd: number;
    principal_recovery_usd: number;
    profit_pretax_usd: number;
    carry_usd: number;
  };
  after_tax_p50_usd: number;
  tax_usd: number;
}

export interface Scenario {
  label: string;
  prob: number;
  mult: number;
  _anchor?: string;
}

export interface FundamentalEv {
  rank: number;
  company: string;
  cohort: string;
  cost_usd: number;
  dilution_adjusted_mark_usd: number;
  weighted_multiplier: number;
  df: number;
  expected_exit_usd: number;
  exit_year: number;
  realized: boolean;
  scenarios: Scenario[];
  expected_multiple_on_cost: number;
}
