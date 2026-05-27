# Stock Management System Feature Roadmap

This document lists suitable product features for the Stock Management System. The department-based stock transfer feature is intentionally excluded from this roadmap.

## Core inventory features

1. Product barcode and SKU search
   - Add fast product lookup by SKU, barcode, or product name.
   - Support barcode scanner input on product, purchase, and sale screens.

2. Low-stock alert dashboard
   - Show products that are at or below their configured minimum stock.
   - Highlight critical products on the dashboard and operations page.

3. Automatic reorder suggestions
   - Suggest reorder quantities using each product reorder rule.
   - Include preferred supplier information when available.

4. Product profile page
   - Show product details, stock quantity, pricing, purchase history, sale history, and profit summary.
   - Include stock movement history and batch/expiry information.

5. Category and unit management UI
   - Add frontend CRUD screens for product categories and units.
   - Use category and unit filters on the product list.

6. Immutable stock ledger
   - Keep stock movement history read-only after posting.
   - Use correction movements instead of editing previous ledger records.

7. Stock adjustment with approval
   - Allow users to request stock increases or decreases with a reason.
   - Require approval for sensitive adjustment reasons.

8. Physical stock count sessions
   - Create stock count sessions with expected system quantity and counted quantity.
   - Show differences and generate correction movements after review.

9. Batch and expiry tracking
   - Track product batch number, manufacture date, expiry date, and remaining quantity.
   - Show expired and near-expiry stock alerts.

10. FIFO, weighted-average, and batch-specific costing
   - Let administrators select the costing method used for profit and valuation reports.
   - Preserve costing configuration history for auditability.

## Purchase and supplier features

11. Supplier profile pages
   - Show supplier contact details, purchase history, payments, returns, and ledger balance.

12. Purchase order workflow
   - Create purchase batches with supplier, currency, invoice number, reference number, and notes.
   - Add purchase items with piece or pack quantity support.

13. Purchase receiving screen
   - Post received purchase items into the stock ledger automatically.
   - Show received, remaining, and cost values per purchase line.

14. Supplier return workflow
   - Record supplier returns with return reason, returned items, and status.
   - Adjust stock and supplier ledger after approval/posting.

15. Purchase payment tracking
   - Link purchase payments to finance accounts and transactions.
   - Show paid, unpaid, and outstanding purchase balances.

## Sales and customer features

16. Customer profile pages
   - Show customer contact details, sales history, payments, returns, and ledger balance.

17. Sales invoice workflow
   - Create sales with customer, currency, invoice number, discount, totals, and notes.
   - Add product lines and calculate cost, gross profit, and profit margin.

18. Sale item stock validation
   - Prevent selling more stock than is available in the selected batch or stock ledger.
   - Show available quantity while selecting sale items.

19. Service charges on sales
   - Add service lines such as delivery, installation, repair, support, or setup fees.
   - Include service totals in sale totals and invoices.

20. Customer return workflow
   - Record customer returns with returned products, quantity, unit price, reason, and status.
   - Adjust stock and customer ledger after approval/posting.

21. Sale payment tracking
   - Link sale payments to finance accounts and transactions.
   - Show paid, unpaid, and outstanding sale balances.

## Finance and reporting features

22. Finance account dashboard
   - Show account balances by currency.
   - Summarize deposits, withdrawals, sale payments, purchase payments, and expenses.

23. Party ledger
   - Track debit, credit, balance, and reference numbers for suppliers and customers.
   - Link ledger entries to sales, purchases, payments, returns, and adjustments.

24. Profit and loss report
   - Show revenue, cost of goods sold, service revenue, discounts, expenses, gross profit, and net profit.

25. Stock valuation report
   - Calculate inventory value using the selected costing method.
   - Group valuation by product, category, supplier, or batch.

26. Sales history report
   - Filter sales by date, customer, product, category, invoice number, and payment status.
   - Show totals, cost, profit, and margin.

27. Purchase history report
   - Filter purchases by date, supplier, product, batch, invoice number, and payment status.
   - Show quantities, costs, paid amounts, and remaining balances.

28. Supplier performance report
   - Compare suppliers by purchase volume, return rate, average cost, and delivery reliability.

29. Export center
   - Export products, sales, purchases, stock movements, and reports as CSV, Excel, or PDF.
   - Track export status as queued, running, completed, or failed.

30. Business document center
   - Upload and link sale invoices, purchase invoices, receipts, and attachments to business records.

## User, security, and operations features

31. Approval workflow center
   - Review purchase, sale, stock adjustment, and return approval requests.
   - Support approve, reject, pending, posted, and draft states.

32. Role and permission management UI
   - Add frontend screens for assigning permissions and reviewing user access.

33. Activity audit trail
   - Show created by, updated by, timestamps, and authorization activity logs on important records.

34. Operations dashboard
   - Summarize low stock, pending approvals, open returns, queued exports, expiry alerts, and recent stock activity.

35. Notification center
   - Notify users about low stock, pending approvals, failed exports, near-expiry batches, and overdue payments.

36. Global search
   - Search products, parties, purchases, sales, returns, documents, and reports from one search box.

37. Advanced filters and saved views
   - Add reusable filters to product, purchase, sale, stock, finance, and report pages.
   - Allow users to save common views.

38. Dashboard widgets
   - Add customizable cards for sales, purchases, profit, low stock, outstanding balances, and pending approvals.

39. Data import tools
   - Import products, parties, opening stock, and price lists from CSV or Excel.
   - Validate data before saving.

40. Backup and restore guidance
   - Add administrator documentation for database backup, media backup, and restore procedures.

## Suggested implementation priority

1. Barcode/SKU search
2. Low-stock dashboard
3. Product profile page
4. Purchase receiving screen
5. Sales invoice workflow
6. Payment tracking
7. Approval workflow center
8. Stock adjustment workflow
9. Batch and expiry alerts
10. Reports and export center
