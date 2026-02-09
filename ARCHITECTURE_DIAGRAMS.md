# 📊 Trip Sharing System - Architecture & Flow Diagrams

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    TIMETIDE APPLICATION                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────┐         ┌──────────────────────┐      │
│  │   Frontend       │◄───────►│  FastAPI Backend     │      │
│  ├──────────────────┤         ├──────────────────────┤      │
│  │ Settings Page    │         │ /sharing/* Routes    │      │
│  │ - Trip List      │         │ - POST /share        │      │
│  │ - Share Modal    │         │ - GET /invites       │      │
│  │ - Permission     │         │ - PUT /accept        │      │
│  │   Selector       │         │ - PUT /decline       │      │
│  │                  │         │ - GET /shared-trips  │      │
│  │ Navbar           │         │ - GET /shared-with   │      │
│  │ - Invites Link   │         │ - DELETE /revoke     │      │
│  │ - Invites Modal  │         │                      │      │
│  │ - Badge Counter  │         │ Permission Checks    │      │
│  └──────────────────┘         │ - trips.py           │      │
│                               │ - entries.py         │      │
│                               └──────────────────────┘      │
│                                        ▲                    │
│                                        │                    │
│                                        ▼                    │
│                               ┌──────────────────┐          │
│                               │  SQLAlchemy ORM  │          │
│                               │  - TripInvite    │          │
│                               │  - User          │          │
│                               │  - Trip          │          │
│                               └──────────────────┘          │
│                                        ▲                    │
│                                        │                    │
│                                        ▼                    │
│                               ┌──────────────────┐          │
│                               │  SQLite Database │          │
│                               │ - trip_invites   │          │
│                               │ - trips          │          │
│                               │ - users          │          │
│                               └──────────────────┘          │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 📈 Database Schema

```
┌──────────────────────────────────┐
│           users                  │
├──────────────────────────────────┤
│ id (PK)                          │
│ email                            │
│ name                             │
│ ◄─ sent_invites (relationship)   │
│ ◄─ received_invites (relationship)
└──────────────────────────────────┘
          ▲              ▲
          │              │
          │              │
          │ (inviter_id) │ (invitee_id)
          │              │
┌──────────────────────────────────────────────┐
│          trip_invites (NEW!)                 │
├──────────────────────────────────────────────┤
│ id (PK)                                      │
│ trip_id (FK) ────┐                           │
│ inviter_id (FK) ─┤─► users                   │
│ invitee_id (FK) ─┘                           │
│ status: pending/accepted/declined            │
│ permission_level: viewer/editor              │
│ created_at                                   │
│ updated_at                                   │
│ UNIQUE (trip_id, invitee_id)                │
└──────────────────────────────────────────────┘
          ▲
          │ (trip_id)
          │
┌──────────────────────────────────┐
│           trips                  │
├──────────────────────────────────┤
│ id (PK)                          │
│ owner_id (FK)                    │
│ title                            │
│ description                      │
│ ◄─ invites (relationship)        │
└──────────────────────────────────┘
```

---

## 🔄 Invite Workflow Sequence

```
USER A (Trip Owner)          DATABASE              USER B (Recipient)
      │                         │                         │
      │                         │                         │
      │─── 1. Share Trip ───►   │                         │
      │   (email: B)            │                         │
      │                    Create TripInvite              │
      │                    status='pending'               │
      │                    permission='editor'            │
      │                         │                         │
      │◄─── 2. Response ────    │                         │
      │    (invite created)     │                         │
      │                         │                         │
      │                         │◄─── 3. Open Invites ────┤
      │                         │                         │
      │                    Query pending                  │
      │                    invites for User B             │
      │                         │                         │
      │                         ├──► 4. Display ────────►│
      │                         │    Pending Invites     │
      │                         │                         │
      │                         │     5. Accept Invite ──►
      │                         │                         │
      │                    Update status to              │
      │                    'accepted'                    │
      │                         │                         │
      │                         ├──► 6. Trip Now ───────►│
      │                         │    Accessible          │
      │                         │                         │
      │◄─── 7. (Optional) ─┐    │                         │
      │   Check who has    │    │                         │
      │   access to trip   │    │                         │
      │                    └──► Query shared_with        │
      │                         │                         │
      │ (If needed)             │                         │
      │─── 8. Revoke Access ──►│                         │
      │                    Delete TripInvite             │
      │                         │                         │
      │                         ├──► 9. Lost Access ────►|
      │                         │                         │
```

---

## 🎯 Permission Matrix

```
┌─────────────────────┬───────────┬──────────┐
│   Action            │  Owner    │ Editor   │
├─────────────────────┼───────────┼──────────┤
│ View Trip           │    ✅     │    ✅    │
│ View Entries        │    ✅     │    ✅    │
│ Create Entry        │    ✅     │    ✅    │
│ Edit Own Entry      │    ✅     │    ✅    │
│ Edit Any Entry      │    ✅     │    ❌    │
│ Delete Entry        │    ✅     │    ❌    │
│ Share Trip          │    ✅     │    ❌    │
│ Revoke Access       │    ✅     │    ❌    │
│ See Trip in List    │    ✅     │    ✅    │
└─────────────────────┴───────────┴──────────┘

┌─────────────────────┬───────────┬──────────┐
│   Action            │  Viewer   │ Pending  │
├─────────────────────┼───────────┼──────────┤
│ View Trip           │    ✅     │    ❌    │
│ View Entries        │    ✅     │    ❌    │
│ Create Entry        │    ❌     │    ❌    │
│ Edit Own Entry      │    ❌     │    ❌    │
│ Edit Any Entry      │    ❌     │    ❌    │
│ Delete Entry        │    ❌     │    ❌    │
│ Share Trip          │    ❌     │    ❌    │
│ Revoke Access       │    ❌     │    ❌    │
│ See Trip in List    │    ✅     │    ❌    │
└─────────────────────┴───────────┴──────────┘
```

---

## 📡 API Flow Diagram

```
FRONTEND REQUEST          BACKEND PROCESSING         DATABASE RESPONSE
      │                         │                           │
      ├─ Share Trip ────►       │                           │
      │  {email, perm}          ├─ Verify Owner ───────────►│
      │                         │                    Check trip owner
      │                         │◄─ Owner OK ───────────────┤
      │                         │                           │
      │                         ├─ Find User ──────────────►│
      │                         │        by email            │
      │                         │◄─ User ID ────────────────┤
      │                         │                           │
      │                         ├─ Check Duplicate ────────►│
      │                         │   (trip_id, invitee_id)    │
      │                         │◄─ Unique OK ──────────────┤
      │                         │                           │
      │                         ├─ Create TripInvite ──────►│
      │                         │    status='pending'       │
      │                         │◄─ ID & Data ──────────────┤
      │                         │                           │
      │◄─ 201 Created ─────────┤                           │
      │  {invite_data}          │                           │
      │                         │                           │
      │                         │                           │
      ├─ Get Invites ───►       │                           │
      │                         ├─ Query TripInvites ──────►│
      │                         │  WHERE invitee = user     │
      │                         │◄─ Results Grouped ────────┤
      │                         │  by status                │
      │◄─ 200 OK ─────────────┤                           │
      │  {pending, accepted,    │                           │
      │   declined}             │                           │
      │                         │                           │
      │                         │                           │
      ├─ Accept Invite ──►      │                           │
      │  {invite_id}            ├─ Verify Invitee ────────►│
      │                         │                    Check invitee_id
      │                         │◄─ Invitee OK ─────────────┤
      │                         │                           │
      │                         ├─ Update Status ──────────►│
      │                         │  status='accepted'        │
      │                         │◄─ Updated ────────────────┤
      │                         │                           │
      │◄─ 200 OK ─────────────┤                           │
      │  {updated_invite}       │                           │
      │                         │                           │
```

---

## 🔐 Security Flow

```
USER REQUEST
     │
     ▼
┌──────────────────────────┐
│ Extract Cookie/Token     │
└──────────────────────────┘
     │
     ▼
┌──────────────────────────┐
│ Decode JWT Token         │
├──────────────────────────┤
│ Try core decoder         │
│ → Fallback to legacy     │
│ → Raise 401 if invalid   │
└──────────────────────────┘
     │
     ▼
┌──────────────────────────┐
│ Query User from Database │
├──────────────────────────┤
│ Find by user_id from token
│ → Raise 404 if not found │
└──────────────────────────┘
     │
     ▼
┌──────────────────────────┐
│ Route-Specific Checks    │
├──────────────────────────┤
│ • Owner check (for share)│
│ • Invitee check (for    │
│   accept/decline)        │
│ • Status validation      │
│ • Permission validation  │
│ → Raise 403 if denied    │
└──────────────────────────┘
     │
     ▼
┌──────────────────────────┐
│ Process Request          │
│ (Success Path)           │
└──────────────────────────┘
```

---

## 🎨 UI Component Hierarchy

```
SETTINGS PAGE
│
└─ Manage Trip Sharing Section
   │
   ├─ Trip List Container
   │  │
   │  └─ Trip Item (for each trip)
   │     │
   │     ├─ Trip Title
   │     ├─ Trip Date
   │     ├─ Share Button ──┐
   │     └─ Edit Button    │
   │                       │
   │                       ▼
   │            tripSharingModal
   │            ├─ Header: "Share Trip"
   │            ├─ Email Input Field
   │            ├─ Permission Level Dropdown
   │            │  ├─ Option: viewer
   │            │  └─ Option: editor
   │            ├─ Send Invite Button
   │            └─ Close Button
   │
   └─ (Shared Trips List)
      ├─ Shared Trip 1
      ├─ Shared Trip 2
      └─ View Details / Revoke

NAVBAR
│
└─ Profile Dropdown
   │
   ├─ Profile Link
   ├─ Settings Link
   ├─ Invites Link ──┐
   │                 │
   │                 ▼
   │       invitesModal
   │       ├─ Header: "Trip Invites"
   │       ├─ Invite List
   │       │  └─ Invite Item (for each)
   │       │     ├─ Trip Title
   │       │     ├─ From: Inviter Email
   │       │     ├─ Permission Level
   │       │     ├─ Accept Button (green)
   │       │     └─ Decline Button (gray)
   │       │
   │       └─ "No pending invites" (if empty)
   │
   └─ Sign Out Link
```

---

## 📊 Data Flow in GET /trips/

```
User Request: GET /trips/

     ▼
┌─────────────────────────────┐
│ get_trips() Function        │
└─────────────────────────────┘
     │
     ├──────────────────────────────┐
     │                              │
     ▼                              ▼
Query Owned Trips         Query Shared Trips
(owner_id = current_user) (TripInvite.invitee_id = user
                           AND status = 'accepted')
     │                              │
     ├──────────────┬───────────────┤
     │              │               │
     ▼              ▼               │
owned_trips   shared_trips[]  ◄────┘
     │              │
     └──────────┬───┘
                │
                ▼
         Merge Lists
    (owned + shared)
                │
                ▼
         Remove Duplicates
                │
                ▼
         Sort by updated_at
                │
                ▼
         Return Combined List
                │
                ▼
         Frontend Receives
      All Accessible Trips
```

---

## 🚀 Deployment Architecture

```
DEVELOPMENT                    PRODUCTION
─────────────────              ─────────────────
Local SQLite DB        ──>     PostgreSQL/MySQL
http://localhost:8000  ──>     https://api.domain.com
Hot Reload Enabled     ──>     ASGI Server (Gunicorn)
Debug = True           ──>     Debug = False
Single Process         ──>     Multi-worker
Console Logs           ──>     Structured Logging
                               
                        Authentication
                        ├─ SSL Certificates
                        ├─ JWT Secrets
                        ├─ CORS Configured
                        ├─ Rate Limiting
                        └─ Input Validation

                        Monitoring
                        ├─ Error Logs
                        ├─ Performance Metrics
                        ├─ User Analytics
                        └─ Uptime Monitoring
```

---

## 📋 Testing Matrix

```
┌──────────────────┬──────────┬──────────┬──────────┐
│ Feature          │ Unit     │ Integration │ E2E   │
├──────────────────┼──────────┼──────────┼──────────┤
│ Send Invite      │    ✅    │    ✅    │    ✅   │
│ Accept Invite    │    ✅    │    ✅    │    ✅   │
│ Decline Invite   │    ✅    │    ✅    │    ✅   │
│ Access Control   │    ✅    │    ✅    │    ✅   │
│ Entry Creation   │    ✅    │    ✅    │    ✅   │
│ Trip Visibility  │    ✅    │    ✅    │    ✅   │
│ Revoke Access    │    ✅    │    ✅    │    ✅   │
│ Permission Check │    ✅    │    ✅    │    ✅   │
└──────────────────┴──────────┴──────────┴──────────┘
```

---

## 🎯 Component Interaction Map

```
Settings Page          Navbar              Database         API Routes
    │                   │                    │                 │
    │                   │                    │                 │
    ├─ Load Trips ─────────────────────────►│◄──────── GET /trips/
    │                   │                    │
    │◄─ Trip List ──────────────────────────┤
    │                   │                    │
    ├─ Share Trip ────────────────────────────────────► POST /share
    │                   │                    │             │
    │                   │                    ├─ Create    │
    │                   │                    │ TripInvite  │
    │                   │                    │◄────────────┤
    │                   │                    │
    │                   ├─ Show Invites ────────────────► GET /invites
    │                   │                    │
    │                   │◄─ Pending List ────────────────┤
    │                   │                    │
    │                   ├─ Accept Invite ────────────────► PUT /accept
    │                   │                    │
    │                   │                    ├─ Update   │
    │                   │                    │ Status     │
    │                   │                    │◄────────────┤
    │                   │                    │
    ├─ Check Shared ────────────────────────────────────► GET /shared-with
    │                   │                    │
    ├─ Revoke ─────────────────────────────────────────► DELETE /revoke
    │                   │                    │
    │                   │                    ├─ Remove   │
    │                   │                    │ TripInvite │
    │                   │                    │◄────────────┤
```

---

## ✨ Feature Interaction Summary

```
TRIP OWNER
│
├─ Can send invites (Settings)
│  └─ Via email
│  └─ With permission level
│
├─ Can view who has access (Settings)
│  └─ See all recipients
│  └─ See permission levels
│
├─ Can revoke access (Settings)
│  └─ Removes recipient's access
│  └─ Immediately effective
│
└─ Always has full access
   ├─ View trip
   ├─ View entries
   ├─ Create entries
   └─ Edit entries

SHARED USER (Accepted)
│
├─ Can view shared trips (My Trips)
│  └─ Trip appears in list
│
├─ Can view trip details
│  └─ All trip information
│  └─ All entries
│
├─ Can create entries (Editor)
│  └─ Full collaboration
│  └─ Edit own entries
│
├─ Can view entries (Viewer)
│  └─ Read-only access
│  └─ Cannot modify
│
└─ Can reject access (Navbar)
   └─ Via Invites dropdown

INVITED USER (Pending)
│
├─ Can see invite (Navbar)
│  └─ In Invites dropdown
│  └─ Shows trip details
│
├─ Can accept invite
│  └─ Gains access immediately
│  └─ Trip appears in My Trips
│
└─ Can decline invite
   └─ Remains blocked from trip
```

---

**This diagram set provides a complete visual overview of the trip sharing system architecture, data flow, and user interactions.**
