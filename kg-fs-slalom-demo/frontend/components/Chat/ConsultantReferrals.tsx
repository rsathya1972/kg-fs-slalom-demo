/**
 * Consultant referral cards — displayed alongside chat responses when
 * the RAG system identifies relevant Slalom consultants.
 */

import type { ConsultantReferral } from "@/lib/types";

interface ConsultantReferralsProps {
  referrals: ConsultantReferral[];
}

function getInitials(name: string): string {
  return name
    .split(" ")
    .map((part) => part[0])
    .join("")
    .toUpperCase()
    .slice(0, 2);
}

export default function ConsultantReferrals({
  referrals,
}: ConsultantReferralsProps) {
  if (referrals.length === 0) return null;

  return (
    <div>
      <p className="text-[10px] font-semibold text-slate-400 uppercase tracking-wide mb-2">
        Relevant Consultants
      </p>
      <div className="space-y-2">
        {referrals.map((referral) => (
          <div
            key={referral.consultant_id}
            className="flex items-start gap-3 bg-white border border-slate-200 rounded-xl px-3 py-2.5 shadow-sm"
          >
            {/* Avatar with initials */}
            <div className="w-8 h-8 rounded-full bg-[#00A3AD] flex items-center justify-center flex-shrink-0">
              <span className="text-white text-xs font-semibold">
                {getInitials(referral.name)}
              </span>
            </div>

            {/* Info */}
            <div className="flex-1 min-w-0">
              <p className="text-sm font-semibold text-slate-900 truncate">
                {referral.name}
              </p>
              {referral.title && (
                <p className="text-xs text-slate-500 truncate">{referral.title}</p>
              )}
              <div className="flex items-center gap-3 mt-0.5">
                <span className="text-[10px] text-slate-400">
                  {referral.utility_experience_years}y utility exp.
                </span>
                <span className="text-[10px] text-slate-400">
                  {referral.relevant_engagements.length} relevant engagement
                  {referral.relevant_engagements.length !== 1 ? "s" : ""}
                </span>
              </div>
            </div>

            {/* Contact link */}
            {referral.contact_email && (
              <a
                href={`mailto:${referral.contact_email}`}
                className="text-[10px] text-[#00A3AD] hover:underline flex-shrink-0"
              >
                Contact
              </a>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
