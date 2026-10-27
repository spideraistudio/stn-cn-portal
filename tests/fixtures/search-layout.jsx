import React from 'react';
import {createRoot} from 'react-dom/client';
import {WorkspaceShell} from '../../components/workspace-shell';
import {MemberDashboard} from '../../components/member-dashboard';
import {SellerSearch} from '../../components/seller-search';
import {ReportShell} from '../../components/report-shell';
import {ThemeProvider} from '../../components/theme-provider';
import {ThemeToggle} from '../../components/theme-toggle';
import {LegalFooter} from '../../components/legal-footer';

// Synthetic browser-only responses. No production endpoint or stored user data.
window.searchCalls = [];
window.searchMode = 'results';
const seller = {
  firm_name: 'Sample seller for layout checks', taluka: 'Himatnagar', district: 'Sabarkantha', state: 'Gujarat',
  gstin: '27••••••••••••Z5', report_count: 16, average_rating: 8, reporting_companies: 3,
  disputes: 1, open_disputes: 1, resolved_disputes: 0, reported_amount_paise: 500000,
  resolved_amount_paise: 0, legal_count: 1, latest_reviewed_at: Date.UTC(2026, 9, 20), under_review: true,
};
const reports = Array.from({length: 16}, (_, index) => ({
  id: String(index), created_at: '2026-10-20', summary: `Sample approved experience ${index + 1}. A longer description checks wrapping and reading as the page scrolls.`,
  rating: 8, status: 'approved', dispute: index % 3 === 0, dispute_resolved: index % 2 === 0,
  dispute_type: 'payment_delay', amount_paise: 500000, legal: index === 0,
  case_number: 'SAMPLE-1', reporter_company: 'Sample reporting company',
}));
window.fetch = async (url, options) => {
  if (url !== '/api/seller-search') return Response.json({items: [], unread: 0});
  window.searchCalls.push(JSON.parse(options.body));
  if (window.searchMode === 'error') return Response.json({error: 'Sample service unavailable. Try again.'}, {status: 503});
  const data = window.searchMode === 'empty' ? {seller: null, reports: [], more: false} : {seller, reports, more: false};
  if (window.searchMode === 'delay') return new Promise(resolve => { window.resolveSearch = () => resolve(Response.json(data)); });
  return Response.json(data);
};
const profile = {
  companyName: 'Sample Crop Science Company', responsiblePersonName: 'Sample member',
  categoryLabel: 'Agriculture', searchEnabled: !location.search.includes('disabled'), isPilot: true,
};
const page = location.pathname === '/member/sellers'
  ? <ReportShell flow title="Search sellers" description="Search approved business experience reports within your assigned category."><SellerSearch categoryLabel="Agriculture"/></ReportShell>
  : <MemberDashboard profile={profile} preview={location.search.includes('preview')}/>;
createRoot(document.getElementById('root')).render(
  <ThemeProvider><div className="flex min-h-screen flex-col"><div id="main-content" className="flex-1">
    <WorkspaceShell>{page}</WorkspaceShell>
  </div><ThemeToggle/><LegalFooter/></div></ThemeProvider>
);
