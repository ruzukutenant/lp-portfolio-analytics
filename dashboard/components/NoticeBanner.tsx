import type { Notice } from "@/lib/types";

interface NoticeBannerProps {
  notice: Notice;
  variant: "audit" | "verification";
}

export function NoticeBanner({ notice, variant }: NoticeBannerProps) {
  const colorClass =
    variant === "audit"
      ? "border-amber-300 bg-amber-50"
      : "border-emerald-300 bg-emerald-50";
  const labelColor =
    variant === "audit" ? "text-amber-900" : "text-emerald-900";
  const statusBadge =
    notice.status === "implemented"
      ? "bg-emerald-100 text-emerald-800 border-emerald-300"
      : "bg-amber-100 text-amber-800 border-amber-300";

  return (
    <div className={`border rounded-lg p-4 ${colorClass}`}>
      <div className="flex items-center gap-3 mb-2">
        <span className={`text-xs font-semibold uppercase tracking-wider ${labelColor}`}>
          {variant === "audit" ? "Audit" : "Verification"}
        </span>
        <span
          className={`text-xs px-2 py-0.5 rounded-full border font-medium ${statusBadge}`}
        >
          {notice.status}
        </span>
      </div>
      <div className="font-semibold text-gray-900 mb-1">{notice.headline}</div>
      <div className="text-sm text-gray-700 leading-relaxed">{notice.detail}</div>
      {notice.methodology_link && (
        <div className="text-xs text-gray-500 mt-2">
          See <code className="bg-white px-1 py-0.5 rounded border">{notice.methodology_link}</code>
        </div>
      )}
    </div>
  );
}
