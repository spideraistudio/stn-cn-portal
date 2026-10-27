import {caseNumberHistory, caseNumberLabel, type CaseNumberRecord} from "@/lib/case-numbers";

export function CaseNumberInfo({report}: {report: CaseNumberRecord}) {
  const history = caseNumberHistory(report.case_number_history);
  return <div className="space-y-2">
    <p><strong>{caseNumberLabel(report.case_number_type)}:</strong> {typeof report.case_number === "string" ? report.case_number : "Not provided"}</p>
    {history.length > 0 && <details className="text-xs">
      <summary className="cursor-pointer font-semibold">Previous case numbers ({history.length})</summary>
      <ul className="mt-2 space-y-2">{history.map((entry, index) => <li key={index}>
        {caseNumberLabel(entry.type)}: {entry.number} · Replaced {new Date(entry.replaced_at).toLocaleDateString("en-IN", {timeZone: "Asia/Kolkata"})}
      </li>)}</ul>
    </details>}
  </div>;
}
