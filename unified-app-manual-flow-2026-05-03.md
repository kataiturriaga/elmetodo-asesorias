# Plan: Unified App — Manual Flow in `elmetodo_app` (rev 2)

**Status**: Draft. Pending product sign-off on §13.
**Scope**: `elmetodo_app` (new Flutter app, Riverpod) + this API + `elmetodo-dashboard` (admin "purchase" UI) + SMS OTP integration.
**Owner**: TBD. Synthesised from 15 parallel agent sweeps on 2026-05-03.

---

## 1. Goal

Merge the manual / asesorias flow (today in the legacy `elmetodo` Flutter app) into the new `elmetodo_app` so a single mobile codebase serves both:

- **Automated users** (`is_automated=true`, V2 self-paced programs, IAP-billed) — already supported.
- **Manual users** (`is_automated=false`, coach-managed, 14-day review cycle, paid off-platform) — currently only in the legacy app.

Two product constraints fix the trust model:

1. **A self-registering user must never end up as `is_automated=false`.** Manual access is gated by a server-side record placed by sales/coach/admin, not by a client-controlled flag.
2. **The new "nuevos clientes" funnel keeps working.** Coaches still get a screen of unassigned manual users to claim.

This rev replaces an earlier email-based design (see §5) with a phone-anchored design that is robust to the failure modes the email-based one couldn't handle.

---

## 2. Non-goals

- Sunsetting the legacy `elmetodo` app. Lives until manual UX in the new app reaches parity. Sunset is a later plan.
- Bulk-migrating existing manual users at flag-flip time. They migrate organically (next login).
- Adding manual-flow support to `elmetodo-golds-auto`. Out of scope.
- Account deletion (App Store 5.1.1(v)) — separate plan.
- In-app payment surface for manual users. **Explicitly rejected** (Apple IAP §11.1).
- Forcing all existing users to verify phone on day 1. We layer phone in gradually.
- Replacing the SM cutover (`USE_REVIEW_STATE_MACHINE`). Assumes cutover ships first; see §10.

---

## 3. Current state (1-paragraph version)

Today, manual vs automated is decided by the `X-Client-ID` header (`elmetodo` | `golds`) plus a client-controlled `app_mode` field on `/auth/{google,apple,email}`. Both are spoofable in a unified app. The `_validate_mode_transition` guard (`app/services/social_auth_service.py:72-127`) stops *existing* users from flipping modes but does nothing for fresh signups. Manual users today have no API-side payment verification — a coach manually flips `subscription_status=active` after off-platform payment confirmation. Phone is collected at signup but **not verified**. SMS infrastructure does not exist. See `docs/plans/asesorias-social-login.md` and `docs/features/review-cycle-state-machine.md` for adjacent design.

---

## 4. Why email-based pre-registration is the wrong anchor

The boss's earlier proposal (and the previous rev of this plan) used **email** as the matching key: coach pre-registers email X; user signs up with email X; server matches. This breaks in seven realistic ways:

| Failure mode | Frequency | What happens |
|---|---|---|
| Typo at sale ("juann@gmail.com") | Common | Customer locked out forever; needs support to fix |
| Apple Private Relay | Every iOS user using Sign in with Apple with relay enabled | Email seen by API ≠ email coach registered |
| Customer has multiple emails (work/personal) | Very common | Pays from one, signs up with another |
| Customer uses social login but registered email | Common | Apple ID email differs from coach-registered email |
| Customer changes email between purchase and signup | Occasional | Match fails |
| Capitalisation / whitespace ("Juan@Gmail.com" vs "juan@gmail.com") | Sporadic | Solvable but adds normalisation surface |
| Customer gives wrong email at sale (gives husband's by mistake) | Sporadic | Hard to diagnose |

Each one produces the same support ticket: *"I paid but the app says I'm a regular user."* Email is a label, not an identity.

**Phone with SMS OTP** fails fewer ways:
- One canonical format (E.164).
- Users know their own phone number.
- SMS OTP proves possession of the SIM, not just knowledge of the string.
- Doesn't break across Google/Apple/email login providers.
- Already collected by marketing for WhatsApp follow-up.
- The customer's phone is the same thing they text the sales team from — natural matching.

It's not perfect (porting attacks exist, SMS costs money, deliverability varies internationally) but it's an order of magnitude more reliable than email for this funnel.

---

## 5. Recommended architecture

### 5.1 Identity model

Going forward, **the user has one immutable trust anchor: their verified phone number.** Email becomes a secondary label (still useful for login, communication, recovery).

- New column: `users.phone_e164` (canonical E.164 format, indexed, unique within `app_name`).
- New column: `users.phone_verified_at` (timestamp; null = unverified).
- Existing `users.phone` becomes a free-text "what they typed" field (kept for back-compat).

Phone verification uses SMS OTP via a new provider integration (Twilio Verify is the obvious choice; alternatives: AWS SNS, MessageBird, regional providers for LatAm volume).

### 5.2 Data model: the `asesorias_purchases` table

The trust signal for "this person has paid for asesorias" lives in a new table:

```sql
CREATE TABLE asesorias_purchases (
  id            BIGSERIAL PRIMARY KEY,
  phone_e164    TEXT NOT NULL,                 -- matching key, NOT FK to users
  app_name      TEXT NOT NULL DEFAULT 'elmetodo',
  purchased_at  TIMESTAMPTZ NOT NULL,
  starts_at     DATE NOT NULL,                 -- when manual flow activates
  ends_at       DATE,                          -- null = ongoing/recurring
  amount        NUMERIC(10,2),
  currency      TEXT,
  payment_method TEXT NOT NULL,                -- 'manual_transfer'|'mercadopago'|'stripe'|'cash'|'other'
  payment_reference TEXT,                      -- transfer ID, processor txn, free text
  status        TEXT NOT NULL DEFAULT 'active', -- 'active'|'refunded'|'cancelled'|'pending'
  notes         TEXT,                          -- coach scratchpad
  created_by_coach_id INT REFERENCES coaches(id) NOT NULL,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_asesorias_purchases_phone ON asesorias_purchases(phone_e164, app_name) WHERE status = 'active';
CREATE INDEX idx_asesorias_purchases_coach ON asesorias_purchases(created_by_coach_id);
```

Key properties:
- **Keyed on phone, not user_id.** A purchase can exist before the user account does.
- **Multiple purchases per phone allowed.** Renewals = new rows. Audit trail preserved.
- **Coach attribution mandatory.** Every row knows who entered it. Enables suspicious-pattern detection ("Coach X has 50% refund rate").
- **`status` enables refund/cancellation flow.** Refund flips status → next ticker run downgrades user to `subscription_status=cancelled`.
- **Payment method generalises.** Today: `manual_transfer`. Tomorrow: payment processor webhook writes the row directly (see §9).

### 5.3 The signup flow (one diagram, all paths)

```
User opens app → "Continúa con Google / Apple / Email"
  │
  ▼
Auth provider returns identity (Google/Apple/email+pw)
  │
  ▼
"Verifica tu teléfono"  → SMS OTP → phone_verified_at set
  │
  ▼
Server lookup: SELECT * FROM asesorias_purchases
                WHERE phone_e164 = ? AND status = 'active'
                ORDER BY starts_at DESC LIMIT 1
  │
  ┌────────────────────────────────┴─────────────────────────────────┐
  ▼ no purchase                                                       ▼ purchase exists
User is automated. Create user with                              starts_at <= today?
  is_automated=true,                                                  │
  registered_as_automated=true.                       ┌───────────────┴───────────────┐
Standard automated onboarding.                        ▼ no                            ▼ yes
                                                Create user with             Create user with
                                                  is_automated=true,           is_automated=false,
                                                  registered_as_automated=false,  registered_as_automated=false,
                                                  tier=consultancy,            subscription_status=active,
                                                  asesorias_starts_at=...      coach_id=null (queued for assignment)
                                                Show "warm-up" home          Manual onboarding
                                                with banner "Tu asesoría     (questionnaire if missing →
                                                empieza el <date>".          waiting screen → coach assigns →
                                                On starts_at: ticker         push notification → manual home).
                                                flips is_automated=false.
```

Three properties this gives us:

1. **The only path to `is_automated=false` is matching an `asesorias_purchases` row.** Spoofing `app_mode=manual` does literally nothing.
2. **The "warm-up" window is a free product enhancement.** Customer pays Monday, coach sets `starts_at=Friday` → customer plays with the automated app for 4 days as `tier=consultancy` (full content unlocked) while their coach prepares their plan. Banner explains it. No idle time, no "I paid but got nothing" complaint.
3. **No purchase = automated, full stop.** A scammer cannot self-promote.

### 5.4 The login flow

A returning user has `phone_verified_at` set; we trust it.

```
User logs in (Google/Apple/email)
  │
  ▼
Server resolves user row.
  │
  ▼
Periodic re-check (e.g. on /users/me, or once a day):
  SELECT * FROM asesorias_purchases
   WHERE phone_e164 = ? AND status='active'
   ORDER BY starts_at DESC LIMIT 1
  │
  ▼
Compare with current is_automated state. Three transitions possible:
  1. No change                       → return UserResponse as today.
  2. Purchase appeared since last login + starts_at <= today
                                     → propose upgrade (see §5.6).
  3. Purchase refunded/expired       → propose downgrade (see §5.6).
```

The login response includes `is_automated`, `tier`, `subscription_status`, `pending_purchase_offer` (if any). The Flutter client picks the right shell.

### 5.5 Existing user migration

Three populations to migrate:

**(a) Existing manual users (legacy elmetodo app)**
- They have `is_automated=false` already. Trust signal is preserved.
- On first login to the new app, prompt phone verify. Once verified, **synthesise a backfill `asesorias_purchases` row** with `payment_method='legacy_pre_phone_anchor'`, `purchased_at=user.created_at`, `starts_at=user.created_at`. This makes the trust chain complete without disrupting access.
- Until they verify phone, they keep working via the legacy `is_automated` flag (we accept the partial trust during the migration window).

**(b) Existing automated users (current elmetodo_app users)**
- They have `is_automated=true`. No change to access.
- Phone verification prompted on next login. Once verified, server checks `asesorias_purchases` — if the customer recently paid for asesorias and the coach already entered the row, the upgrade-to-manual offer fires. Otherwise nothing changes.

**(c) Existing Gold's users**
- Out of scope. Phone verification not required by this plan; their trust anchor is Resamania, not phone.

### 5.6 Mode transitions

Currently, `automated → manual` is blocked by `_validate_mode_transition` except via env-var whitelist. We replace that env-var fallback with a data-driven rule:

```python
def can_transition_to_manual(user, asesorias_purchases) -> bool:
    return any(
        p.phone_e164 == user.phone_e164
        and p.status == 'active'
        and p.starts_at <= today()
        for p in asesorias_purchases
    )
```

Symmetric for `manual → automated`: only allowed when no active purchase remains (e.g., refund or non-renewal). The transition fires with full audit logging:
- `users.mode_switched_at`
- New `user_mode_transitions` audit table: `(user_id, from_is_automated, to_is_automated, reason, triggered_by, created_at)`.

The `MODE_SWITCH_WHITELIST_EMAILS` env-var stays as a dev-team escape hatch.

---

## 6. Edge case matrix

Every edge case I could think of, and how the system handles it.

| # | Edge case | Resolution |
|---|---|---|
| 1 | User pays asesorias, signs up with **wrong email** | Phone match works regardless of email. ✅ |
| 2 | User pays asesorias, signs up with **Apple Private Relay** | Phone match ignores email entirely. ✅ |
| 3 | User pays asesorias, **never installs the app** | Stays in `asesorias_purchases`. Dashboard view "Compras sin app" lets coach follow up via WhatsApp. ✅ |
| 4 | User installs app, signs up automated, **never pays** | Stays automated. Cannot self-promote. ✅ |
| 5 | User signs up automated **before** paying, pays later | Coach adds purchase row. On next `/users/me`, server detects purchase + offers upgrade. User confirms → mode flipped. ✅ |
| 6 | User pays asesorias, signs up but **enters wrong phone number** | SMS OTP fails (different SIM) OR succeeds (typo on a number they own). If it succeeds, they're automated; coach notices in queue, contacts via WhatsApp, fixes phone in dashboard. Add a "claim purchase" support flow as backup. ⚠ |
| 7 | User shares OTP code with a friend | Friend doesn't have the SIM → can't receive OTP → fails. Phone is the trust anchor. ✅ |
| 8 | User changes phone number | Support flow: in-app "change phone" with re-verify on new number. Migrates `phone_e164`. Audit log. ✅ |
| 9 | Existing manual user installs new app, hasn't verified phone yet | Logs in via legacy email+password → server returns `is_automated=false` (preserved from legacy flag) → manual UX. Prompts phone verify but doesn't block. ✅ |
| 10 | Existing manual user verifies phone, but no `asesorias_purchases` row | Auto-create backfill row with `payment_method='legacy_pre_phone_anchor'`. Trust chain restored. ✅ |
| 11 | Apple Sign in with Apple → email is private relay → user's first launch | Email is just a label. Phone OTP creates the trust anchor. ✅ |
| 12 | User installs the app, refuses to verify phone | Cannot complete signup. Same gate as today's questionnaire requirement — phone is mandatory. ⚠ design choice |
| 13 | SMS OTP undeliverable (international, bad signal) | Fall back to WhatsApp OTP (same Twilio Verify supports it) or voice call. Last resort: support claim flow. ⚠ |
| 14 | User's purchase is refunded | Coach sets `status='refunded'`. Next ticker tick: user's `subscription_status` flips to `cancelled` and they lose manual access (ticker already does this for the subscription_status=cancelled case). User downgrades to automated. ✅ |
| 15 | User's purchase expires (`ends_at` passed, no renewal) | Same as #14 but flagged "expired" instead of "refunded". ✅ |
| 16 | Coach renews a purchase | New row inserted with later `ends_at`. Aggregation query takes `MAX(ends_at)` across active rows. ✅ |
| 17 | User signs up with phone X, then later changes account email | Phone unchanged → asesorias status unchanged. Email change is cosmetic. ✅ |
| 18 | Two physical people share one phone (rare: families) | First user signs up, claims purchase. Second user can't sign up with same phone (unique constraint). Edge case: dashboard manual override to allow second account on same phone with a tagged note. ⚠ |
| 19 | User uninstalls and reinstalls the app | Same phone → same account. SMS OTP re-establishes session. ✅ |
| 20 | User logs in on a second device | Phone OTP on second device verifies it's still them. ✅ |
| 21 | Coach enters wrong phone in dashboard | Customer can't claim purchase. Standard support: coach edits the phone field in the row. Audit log captures who changed it. ✅ |
| 22 | User signs up automated with phone +X, later marketing creates purchase row with phone +Y for the same person | Two separate identities by design. Marketing must align phones. Support flow can merge accounts. ⚠ |
| 23 | iOS user has IAP automated subscription AND pays for asesorias | `tier=consultancy` outranks `tier=premium` in the existing resolver. They get manual flow + their IAP keeps renewing in parallel. We should refund the IAP automatically (App Store Connect API supports this for refunds). ⚠ requires policy decision |
| 24 | User on warm-up window cancels their purchase before `starts_at` | Coach refunds. Status flips. User stays automated. ✅ |
| 25 | Phone verification provider outage | Block all signups during outage. Show retry screen. Critical-path dependency — ensure provider has SLA. ⚠ |

15 ✅ "fully handled", 8 ⚠ "needs explicit product decision or has acceptable trade-off", 0 unresolved.

---

## 7. Why this beats the alternatives

| Approach | Trust source | Robust to email mismatch | Robust to user error | Anti-scam | Operational cost |
|---|---|---|---|---|---|
| Boss's email pre-registration | Coach-created email | ❌ | ❌ | ✅ | Low |
| Boss's magic-link token | Single-use token | ✅ | ✅ if not shared | ✅ | Low |
| Self-select + coach approval | Coach reviews queue | N/A | ✅ | ⚠ relies on coach diligence | High (coach time) |
| Build flavors (two binaries) | Bundle ID | N/A | ✅ | ✅ | High (two release pipelines, iOS distribution problem) |
| Deep-link with signed JWT | Crypto token + install referrer | ✅ | ⚠ iOS deferred-link gap | ✅ | Medium (Branch/Adjust SaaS or build it) |
| **Phone-anchored purchase records (this plan)** | Phone + SMS OTP + dashboard purchase row | ✅ | ✅ | ✅ | Medium (SMS provider, sales process change) |

Why this wins:
- **Robust to all email pathologies** (the user's specific complaint).
- **Phone is the natural identifier** in the existing sales funnel (WhatsApp).
- **Multi-purchase model handles renewals, refunds, future payment integration** without redesign.
- **Sub-flows for existing users** are clean (phone verify → backfill row).
- **Anti-scam guarantee** is server-side and binary: no purchase row, no manual mode.
- **Apple-safe** — no in-app payment surface for manual users.

The magic-link token (boss's Option B) is a complementary UX layer on top, not an alternative. After this plan ships, the dashboard could have a "Send WhatsApp invite" button that bundles the customer's phone + a deep link in one tap.

---

## 8. The dashboard changes

Three changes to the dashboard:

### 8.1 New "Compras de asesorías" admin section

Coaches/admins create rows in `asesorias_purchases`. Form fields:
- Phone number (required, E.164 format with country picker)
- Customer name (free text — for the coach's reference)
- Purchase date
- Start date (defaults today, can be future for warm-up)
- End date (optional)
- Payment method (dropdown)
- Payment reference (free text)
- Notes

### 8.2 "Nuevos clientes" screen extends

Today: shows users with `coach_id IS NULL AND is_automated=False`.
After: same, but with two pieces of context per row:
- The matching `asesorias_purchases` row (purchase date, payment method, notes)
- Phone (verified ✅ or unverified ⚠)
- Optional second tab: "Compras sin cuenta" — purchases where no user has signed up yet for that phone. Coach can WhatsApp the customer and remind them.

### 8.3 User detail page extends

Add a "Asesorías" panel showing all purchases for that phone with status, total paid, and a button to add a renewal. This becomes the audit trail for billing disputes.

---

## 9. Phase 2 (future): payment processor integration

This plan is designed so a payment processor webhook **writes the same `asesorias_purchases` row** with no behaviour change downstream. When the team is ready:

- Mercado Pago / Stripe Checkout link in Instagram bio.
- Customer enters phone + pays in browser.
- Webhook → `POST /api/webhooks/{processor}/purchase` → row created with `payment_method='mercadopago'`, `payment_reference=<txn_id>`, `status='active'`.
- Customer downloads app, enters their phone, OTP, gets matched to the purchase. Same flow.

Effects:
- Removes coach manual data entry.
- Automatic refund webhooks → automatic `status='refunded'`.
- Recurring subscriptions (Mercado Pago Subscriptions, Stripe Recurring) → automatic renewal rows.
- Apple-safe because the checkout is web, outside the app, not deep-linked from inside it.

This is a meaningful operational win but **does not block** the unified-app rollout. Phase 1 ships with manual coach-entered rows.

---

## 10. Sequencing

| Phase | Deliverable | Blocks |
|---|---|---|
| 0 | SM cutover (`USE_REVIEW_STATE_MACHINE=true`, per shadow-soak plan) | Everything below |
| 1a | Phone verification: SMS provider integration, `phone_verified_at` column, `/users/me/verify-phone` endpoints, OTP send/check | 1b |
| 1b | `asesorias_purchases` table, dashboard "Compras de asesorías" admin form, audit log | 1c |
| 1c | Auth flow refactor: signup checks purchases, `_validate_mode_transition` data-driven | 2, 3 |
| 2 | `subscription_status` (paused/cancelled) UI in `elmetodo_app` + AuthUser exposes `is_automated`, `tier` | 4 |
| 3 | Manual-flow UX port (review submission, progress graph, diet/routine display, questionnaire, manual home) | 4 |
| 4 | Login-flow routing: read `is_automated` → render correct shell | Public rollout |
| 5 | Existing-user migration: phone-verify prompt, legacy backfill row | Public rollout |
| 6 | (Optional) Magic-link "WhatsApp invite" button in dashboard | — |
| 7 | (Optional) Payment processor webhook integration | — |

Phase 0 is the only hard prerequisite outside this plan. Phase 1 is mostly backend + dashboard. Phase 2–4 is the bulk of Flutter work. Phase 5 covers migration.

---

## 11. Risks

### 11.1 Apple IAP guideline 3.1.1

Same as before. The legacy flow is Apple-safe because **the app contains zero payment surface for manual users**. The unified app must preserve this:

- ❌ No "Subscribe / Become a member / Upgrade to coach" CTA visible to manual-mode users.
- ❌ No deep-link from the app to a web checkout for asesorias.
- ✅ Automated-mode IAP unchanged (`app/api/routes/mobile/subscription.py:178`).
- ✅ Future payment-processor checkout (Phase 2) initiated **outside the app** (Instagram ad → browser, never from inside the app).

If a user sees IAP banners in automated mode and then transitions to manual mode, the manual-mode UI must hide all "upgrade" surfaces. Same pattern as Gold's "Upselling VIP" — text only, no purchase action.

### 11.2 SMS provider dependency

Phone verification becomes a critical-path dependency. Outages = no signups. Mitigations:
- Provider with high SLA (Twilio Verify is 99.95%).
- Backup channel: WhatsApp OTP (same Twilio Verify product supports it) and voice fallback.
- Async retry: if SMS fails, allow user to wait and retry without losing form state.
- Status page monitoring + Sentry alert on OTP send failure rate.

### 11.3 Coach data-entry quality

If a coach enters the wrong phone, the customer can't claim. Mitigations:
- Phone field has E.164 validation + country picker (no free-text).
- Dashboard shows "matched X users with this phone" preview before save.
- Daily anomaly job: purchases without a matching signed-up user after 7 days flagged for follow-up.
- Audit log on every row change.

### 11.4 Cost of SMS at scale

Twilio Verify is ~$0.05–$0.10 per verification depending on region. At 1000 signups/month: ~$50–$100/mo. Cheap. At 100k signups/month: ~$5k–$10k/mo. Plan budget if Instagram ads scale.

### 11.5 International deliverability

LatAm SMS deliverability is uneven (Mexico OK, Argentina mediocre, some countries spotty). WhatsApp fallback covers most gaps in this market. Test with real customer cohort before declaring victory.

### 11.6 Two trust signals during migration

While existing manual users haven't yet phone-verified, they exist on the legacy `is_automated=false` flag alone. During this window, that flag is the trust anchor. Risk: a previously-deleted manual user's email could be hijacked if their account was soft-deleted but not hard-deleted. Mitigations:
- Cap migration window: at +6 months, force phone verify on next login or block.
- Audit log on `is_automated` changes.

### 11.7 SMS OTP phishing

Standard SMS OTP phishing risk. Mitigations: short code expiry (5 min), rate limiting, lockout after 5 failures, OTP message wording "Nunca compartas este código."

---

## 12. References

- `docs/plans/asesorias-social-login.md` — earlier email-pre-registration design (this plan supersedes the matching-key part; the social-login UX still applies).
- `docs/plans/state-machine-shadow-mode-soak-2026-04-30.md` — blocking prerequisite (SM cutover).
- `docs/features/review-cycle-state-machine.md` — manual-user SM scope.
- `docs/features/feature-flags.md` — flag mechanism for staged rollout.
- `docs/platform-review-2026-04-25/findings/app-old-auto/30-iap-payments.md` — confirms manual flow's "no in-app payment surface" model.
- `docs/platform-review-2026-04-25/findings/app-new-auto/09-iap-subscriptions.md` — current IAP flow + known gaps.
- `app/services/social_auth_service.py:72-127` — existing mode-switch guard (to be replaced with data-driven version).
- `app/services/subscription_service.py:54-80` — tier resolver (`consultancy > premium > free`).
- `app/repositories/user_repository.py:40-57` — current new-clients query (extended in §8.2).
- Twilio Verify documentation: <https://www.twilio.com/docs/verify> (SMS + WhatsApp OTP).

---

## 13. Decisions to lock in before implementation

The boss needs to answer these before any code is written. They are ordered most-impactful first.

1. **§5.2 — Are we OK with `asesorias_purchases` as the data anchor and phone as the matching key?** This is the core architectural decision. Rest of the plan flows from yes.
2. **§11.4 — SMS provider budget.** OK to spend $50–$200/month on SMS verification (current scale)?
3. **§5.3 / §11.1 — Warm-up UX confirmation.** During the warm-up window (purchase exists, `starts_at` future), do we let users use the full automated app with `tier=consultancy`, or a stripped-down "your plan starts X" screen?
4. **#23 in matrix — IAP collision policy.** If a user has an active automated IAP subscription AND becomes manual, do we (a) auto-refund the IAP, (b) let it run to end-of-period, (c) require manual support intervention?
5. **#12 in matrix — Phone verification mandatory at signup?** I recommend yes (no opt-out). Boss confirms.
6. **#13 in matrix — WhatsApp OTP fallback.** OK to use Twilio's WhatsApp Verify channel as backup? Requires WhatsApp Business onboarding (~2 weeks lead time).
7. **§5.5(a) — Migration policy for legacy manual users without phones in DB.** Block their next login until phone verified, or allow soft migration with N-day grace?
8. **§9 — Phase 2 payment processor.** Mercado Pago, Stripe, both, neither?
9. **Sales-process change** — confirmed that every paying manual customer must have a `asesorias_purchases` row created (no exceptions, no informal "I'll add it later")?
