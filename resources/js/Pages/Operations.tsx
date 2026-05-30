import React from 'react';
import AppLayout from '../Layouts/AppLayout';
import { Badge, Card, EmptyState, TableShell } from '../Components/UI';

type Props = Record<string, any>;

function MiniTable({ title, rows, columns }: { title: string; rows: any[]; columns: Array<[string, string]> }) {
  return (
    <Card className="p-0">
      <div className="border-b border-slate-100 p-5"><h3 className="font-semibold text-slate-900">{title}</h3></div>
      {rows?.length ? <TableShell><thead className="bg-slate-50 text-slate-600"><tr>{columns.map(([key, label]) => <th key={key} className="px-4 py-3">{label}</th>)}</tr></thead><tbody className="divide-y divide-slate-100">{rows.map((row, index) => <tr key={row.id ?? index} className="hover:bg-slate-50">{columns.map(([key]) => <td key={key} className="px-4 py-3 text-slate-700">{String(row[key] ?? '—')}</td>)}</tr>)}</tbody></TableShell> : <div className="p-5"><EmptyState title={`No ${title.toLowerCase()}`} description="Records will appear here after you create them from admin or workflow screens." /></div>}
    </Card>
  );
}

export default function Operations(props: Props) {
  const summary = props.summary || {};
  const cards = [
    ['Low stock alerts', summary.lowStock ?? 0, 'Products at or below reorder level'],
    ['Pending approvals', summary.pendingApprovals ?? 0, 'Purchase, transfer, sale, adjustment approvals'],
    ['Open returns', summary.openReturns ?? 0, 'Customer, supplier, and damaged returns'],
    ['Queued exports', summary.queuedExports ?? 0, 'CSV, Excel, and PDF export jobs'],
  ];
  return (
    <AppLayout title="Operations" subtitle="Feature center for alerts, approvals, returns, stock counts, expiry tracking, reports, exports, invoices, and ledgers.">
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">{cards.map(([title, value, description]) => <Card key={title as string}><p className="text-sm font-medium text-slate-500">{title}</p><p className="mt-2 text-3xl font-bold text-slate-900">{value as any}</p><p className="mt-2 text-xs text-slate-500">{description}</p></Card>)}</div>
      <div className="mt-6 grid gap-4 lg:grid-cols-3"><Card><Badge tone="success">Implemented</Badge><h3 className="mt-3 font-semibold">Reorder + low-stock alerts</h3><p className="mt-1 text-sm text-slate-500">Track product minimum stock, preferred supplier, and reorder quantity.</p></Card><Card><Badge tone="info">Implemented</Badge><h3 className="mt-3 font-semibold">Approval workflows</h3><p className="mt-1 text-sm text-slate-500">Model purchase, stock, adjustment, return, and sale approval requests.</p></Card><Card><Badge tone="neutral">Implemented</Badge><h3 className="mt-3 font-semibold">Exports and reports</h3><p className="mt-1 text-sm text-slate-500">Queue exports and advanced reports for CSV, Excel, and PDF workflows.</p></Card></div>
      <div className="mt-6 grid gap-6 xl:grid-cols-2">
        <MiniTable title="Low stock rules" rows={props.lowStockRules || []} columns={[["product", "Product"], ["current", "Current"], ["minimum", "Minimum"], ["reorderQuantity", "Reorder"], ["supplier", "Supplier"]]} />
        <MiniTable title="Approvals" rows={props.approvals || []} columns={[["workflow_type", "Workflow"], ["status", "Status"], ["title", "Title"], ["reference_number", "Reference"]]} />
        <MiniTable title="Documents and invoices" rows={props.documents || []} columns={[["document_type", "Type"], ["title", "Title"], ["reference_number", "Reference"], ["issued_at", "Issued"]]} />
        <MiniTable title="Party ledger" rows={props.partyLedger || []} columns={[["party__name", "Party"], ["entry_type", "Type"], ["debit", "Debit"], ["credit", "Credit"]]} />
        <MiniTable title="Returns" rows={props.returns || []} columns={[["return_number", "Return #"], ["return_type", "Type"], ["status", "Status"], ["return_date", "Date"]]} />
        <MiniTable title="Stock adjustment reasons" rows={props.stockReasons || []} columns={[["name", "Reason"], ["requires_approval", "Approval required"]]} />
        <MiniTable title="Stock counts" rows={props.stockCounts || []} columns={[["count_number", "Count #"], ["status", "Status"], ["scheduled_date", "Scheduled"]]} />
        <MiniTable title="Batch and expiry tracking" rows={props.batchTracking || []} columns={[["product", "Product"], ["batchNumber", "Batch"], ["expiryDate", "Expiry"], ["quantity", "Qty"], ["expired", "Expired"]]} />
        <MiniTable title="Costing configuration" rows={props.costing || []} columns={[["name", "Name"], ["method", "Method"], ["is_default", "Default"]]} />
        <MiniTable title="Advanced reports" rows={props.advancedReports || []} columns={[["report_type", "Type"], ["title", "Title"], ["date_from", "From"], ["date_to", "To"]]} />
        <MiniTable title="Export jobs" rows={props.exports || []} columns={[["export_type", "Type"], ["file_format", "Format"], ["status", "Status"], ["created_at", "Created"]]} />
      </div>
    </AppLayout>
  );
}
