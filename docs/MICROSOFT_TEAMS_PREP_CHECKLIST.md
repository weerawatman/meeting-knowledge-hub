# Microsoft Teams Preparation Checklist
## SAT Secretary BOT

Last updated: 2026-07-02

Use this file to prepare the Microsoft 365 tenant, Entra app registration, Teams app package, and test meetings before we connect the real Teams integration.

---

## 1. Information To Prepare

| Item | Value |
| --- | --- |
| Microsoft 365 tenant ID | `TODO` |
| Primary admin contact | `TODO` |
| Public HTTPS base URL for this app | `TODO` |
| Public domain only, no protocol | `TODO` |
| Entra application/client ID | `TODO` |
| Entra client secret | `TODO - store in .env only, never commit` |
| Teams app ID | `TODO` |
| Bot ID / Microsoft App ID | `TODO` |
| Bot display name | `SAT Secretary BOT` |
| Test organizer account | `TODO` |
| Test internal participant account | `TODO` |
| Test external guest account | `TODO` |

---

## 2. Tenant/Admin Decisions

- [ ] Confirm that SAT Secretary BOT may be installed in the tenant.
- [ ] Confirm that the bot may appear as a visible participant in meetings.
- [ ] Confirm that meeting captions/transcription policies are enabled for test users.
- [ ] Confirm whether CART captions / real-time captions can be enabled in meeting options.
- [ ] Confirm whether post-meeting transcript access through Microsoft Graph is allowed.
- [ ] Confirm retention requirement: mixed raw audio 30 days, raw text permanent.
- [ ] Confirm external guest policy: guests can see subtitles and bot roster name only.

---

## 3. Entra App Registration

Create or prepare an Entra application for the backend integration.

Required values:

- Application/client ID
- Directory/tenant ID
- Client secret or certificate
- Redirect URI for local/dev if needed
- Application ID URI if Teams SSO is enabled later

Initial Graph/Teams permissions to review with the admin:

- Online meeting read/transcript permissions for post-meeting transcript import
- Calendar/meeting read permissions for calendar monitor
- Bot/Teams app permissions required by the selected bot implementation

Do not grant broad production permissions until the feasibility spikes confirm the exact integration path.

---

## 4. Teams App Package

Template location:

- `config/teams/manifest.template.json`

Before upload:

- [ ] Replace all `${...}` placeholders.
- [ ] Add `color.png` and `outline.png` icons.
- [ ] Confirm `validDomains` contains the public domain.
- [ ] Confirm side panel/config URLs are HTTPS and reachable.
- [ ] Upload through Teams Developer Portal or tenant app catalog.

---

## 5. Feasibility Spike Meetings

Create at least four test meetings:

| Meeting | Purpose | Required Participants |
| --- | --- | --- |
| SAT-M1 Native Captions | CART/native caption publishing | Organizer + internal participant |
| SAT-M1 Bot Roster | Confirm visible participant/lifecycle | Organizer + internal participant |
| SAT-M1 Audio Path | Validate live audio capture path | Organizer + 2 internal speakers |
| SAT-M1 External Guest | Validate guest restrictions | Organizer + internal + external guest |

Record the result in `docs/TASKS_Teams_Meeting_AI.md` under Phase 1.

---

## 6. Environment Variables

Copy `.env.example` to `.env` and fill these values:

```env
PUBLIC_BASE_URL=
PUBLIC_DOMAIN=
TEAMS_APP_ID=
TEAMS_BOT_ID=
ENTRA_TENANT_ID=
ENTRA_CLIENT_ID=
ENTRA_CLIENT_SECRET=
GRAPH_TRANSCRIPT_ENABLED=false
TEAMS_NATIVE_CAPTIONS_ENABLED=false
CART_CAPTION_SPIKE_URL=
```

Keep `.env` private.

---

## 7. References

- Microsoft 365 app manifest schema: https://learn.microsoft.com/en-us/microsoft-365/extensibility/schema/
- Teams meeting apps APIs and real-time captions: https://learn.microsoft.com/en-us/microsoftteams/platform/apps-in-teams-meetings/meeting-apps-apis
- Teams real-time media bots: https://learn.microsoft.com/en-us/microsoftteams/platform/bots/calls-and-meetings/real-time-media-concepts
- Application-hosted media bot considerations: https://learn.microsoft.com/en-us/microsoftteams/platform/bots/calls-and-meetings/requirements-considerations-application-hosted-media-bots
- Teams Graph transcript APIs overview: https://learn.microsoft.com/en-us/microsoftteams/platform/graph-api/meeting-transcripts/overview-transcripts
