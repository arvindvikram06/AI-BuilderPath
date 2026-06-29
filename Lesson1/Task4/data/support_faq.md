# NeuraStack Technologies — Support & FAQ

## General Support

### How do I contact NeuraStack support?
- **Email:** support@neurastack.io (response within 48 hours for Pro, 4 hours for Enterprise)
- **Live Chat:** Available at https://neurastack.io/support (Pro and Enterprise plans only)
- **Community Forum:** https://community.neurastack.io (all plans)
- **Emergency Hotline (Enterprise only):** +1 (512) 800-NURA ext. 2

### What are support hours?
Standard support is available Monday to Friday, 9:00 AM – 6:00 PM CST. Enterprise customers receive 24/7 support for P1 and P2 incidents.

---

## Account & Billing

### How do I reset my API key?
1. Log in to your NeuraStack dashboard at https://app.neurastack.io.
2. Navigate to **Settings → API Keys**.
3. Click **Regenerate Key** next to the key you wish to reset.
4. Confirm the action — the old key is immediately invalidated.
5. Copy and save your new API key securely; it will not be shown again.

### How do I cancel my subscription?
1. Go to **Settings → Billing → Cancel Subscription**.
2. Select a reason and click **Confirm Cancellation**.
3. Your account will remain active until the end of the current billing period.
4. Data is retained for 30 days after cancellation, then permanently deleted.

### I was charged incorrectly. What should I do?
Email billing@neurastack.io with your invoice number and a description of the discrepancy. Billing disputes are resolved within 5 business days. Verified overcharges are refunded within 7–10 business days.

### Can I upgrade or downgrade my plan mid-cycle?
- **Upgrade:** Takes effect immediately; you are charged the prorated difference.
- **Downgrade:** Takes effect at the start of the next billing cycle.

---

## API Usage & Rate Limits

### What are the API rate limits?
| Plan | Requests per Minute | Requests per Day |
|---|---|---|
| Free | 10 req/min | 100 req/day |
| Pro | 100 req/min | 10,000 req/day |
| Enterprise | 1,000 req/min | Unlimited |

### What happens if I exceed the rate limit?
Requests exceeding the rate limit receive an **HTTP 429 Too Many Requests** response. The response includes a `Retry-After` header indicating when you can retry. Free and Pro accounts are automatically throttled; Enterprise accounts receive burst capacity of 2× the rate limit for up to 60 seconds.

### How do I authenticate API requests?
All API requests must include a Bearer token in the Authorization header:
```
Authorization: Bearer YOUR_API_KEY
```
API keys can be generated in **Settings → API Keys**. Each account can have up to 5 active API keys simultaneously.

---

## NeuraChat — Chatbot

### Why is my chatbot giving wrong answers?
The most common causes are:
1. **Outdated index:** Re-ingest your documents using the Rebuild Index button or `python ingest.py`.
2. **Poor chunking:** Try reducing chunk size to 500 characters for dense documents.
3. **Insufficient top-k:** Increase the number of retrieved chunks (top-k) to 7 or 8.
4. **Document quality:** Scanned PDFs without OCR may not extract text correctly.

### How do I upload documents to NeuraChat?
Documents can be uploaded in two ways:
1. **Admin Panel:** Go to Settings → Knowledge Base → Upload Documents (supported formats: PDF, DOCX, TXT, MD).
2. **Runtime Upload:** Use the sidebar file uploader in the NeuraChat UI for session-scoped uploads (temporary, not saved to base index).

### What file formats are supported?
NeuraChat supports: `.pdf`, `.docx`, `.txt`, `.md` (Markdown). Maximum file size is 50 MB per document on Pro and 200 MB on Enterprise.

### How do I rebuild the knowledge base index?
Run the following command from the project root:
```bash
python ingest.py
```
Or click the **🔄 Rebuild Index** button in the NeuraChat sidebar. Rebuilding typically takes 30–90 seconds depending on document volume.

---

## NeuraSearch — Search Engine

### Why are my search results irrelevant?
1. Ensure the document was successfully ingested (check the ingestion log).
2. Try rephrasing your query using natural language rather than keywords.
3. Verify the document is within your plan's document limit.
4. If using role-based access control, confirm the user has visibility to the target document.

### Can NeuraSearch index private GitHub repositories?
Yes. Connect your GitHub account via **Settings → Integrations → GitHub**. Grant read access to the repositories you want indexed. Indexing begins within 15 minutes of connection.

---

## NeuraPipeline — Workflows

### My pipeline is failing. How do I debug it?
1. Go to **Pipelines → [Your Pipeline] → Run History**.
2. Click the failed run to view logs for each node.
3. Check the error message and node type — most failures are due to misconfigured connector credentials.
4. Use the **Test Node** feature to isolate and re-run individual nodes.

### How do I roll back a pipeline to a previous version?
Go to **Pipelines → [Your Pipeline] → Version History**. Select the version you want to restore and click **Restore**. The restored version becomes the new active version; the previous one is saved in history.
