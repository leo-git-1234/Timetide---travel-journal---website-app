# Trip Sharing System - Quick Start Guide

## 🚀 Server Status
✅ **Server Running**: http://127.0.0.1:8000

## 📋 Quick Test Walkthrough

### Step 1: Login to Sender Account
1. Navigate to http://127.0.0.1:8000/login
2. Use any existing test account (e.g., tripowner@example.com / password123)
3. Click "Log In"
4. ✅ You should see the dashboard

### Step 2: Navigate to Settings
1. Click the profile dropdown (top-right corner)
2. Click "Settings"
3. Scroll down to find **"Manage Trip Sharing"** section
4. ✅ You should see a list of your trips

### Step 3: Share a Trip
1. Click the **"Share"** button next to any trip
2. A modal dialog will appear
3. Enter recipient email: `tripreceiver@example.com`
4. Select permission level: `editor` (allows creating/editing entries)
5. Click **"Send Invite"**
6. ✅ You should see "Invite sent successfully"

### Step 4: View Sent Invites (Optional)
- In the "Manage Trip Sharing" section, you can see shared trips
- Click "View Shares" to see who it's shared with
- Click "Revoke" to remove access anytime

### Step 5: Login to Receiver Account
1. In a new incognito/private window OR different browser:
2. Navigate to http://127.0.0.1:8000/login
3. Login as: `tripreceiver@example.com` / `password123`
4. ✅ Dashboard loads

### Step 6: View Pending Invites
1. Click the profile dropdown (top-right)
2. Click **"Invites"**
3. A modal shows "Trip Invites"
4. ✅ You should see your pending invite with:
   - Trip title
   - Sender's email
   - Permission level (viewer/editor)

### Step 7: Accept the Invite
1. In the Invites modal, click the green **"Accept"** button
2. ✅ Invite list refreshes
3. ✅ You see confirmation: "Invite accepted! You can now access the trip."

### Step 8: Access Shared Trip
1. Click on "My Trips" in the navigation
2. ✅ The shared trip now appears in your trip list!
3. Click on the trip name to view it
4. ✅ You can see all the trip details and entries

### Step 9: Create Entry (Editor Only)
1. While viewing the shared trip, click "Add Entry"
2. Fill in the entry details (content, date, mood, etc.)
3. Click "Save"
4. ✅ Entry created successfully (if you have editor permission)
5. ❌ If viewer permission, you'll see "Cannot create entries on shared trips"

### Step 10: Revoke Access (Sender Only)
1. Login back as the original trip owner
2. Go to Settings > Manage Trip Sharing
3. Find the trip that was shared
4. Click **"View Shares"** 
5. Click **"Revoke"** next to the recipient
6. ✅ Recipient immediately loses access

---

## 🔍 What You Can Test

### Permission Levels

**Editor (Full Collaboration)**
- ✅ View trip and all entries
- ✅ Create new entries
- ✅ Edit own entries
- ✅ Trip appears in My Trips

**Viewer (Read-Only)**
- ✅ View trip and all entries
- ❌ Cannot create entries (blocked)
- ❌ Cannot edit entries (blocked)
- ✅ Trip appears in My Trips

### Invite States

| Action | Result |
|--------|--------|
| **Pending** | Shown in Invites modal, can't access trip yet |
| **Accept** | Status changes to "Accepted", trip becomes accessible |
| **Decline** | Status changes to "Declined", trip remains blocked |
| **Revoke** (by owner) | Invite deleted, access removed immediately |

### Email Validation

- ✅ Valid email: `tripreceiver@example.com`
- ❌ Invalid email: `invalid` → Error shown
- ❌ Non-existent user: `unknown@example.com` → "User not found" error
- ❌ Duplicate share: Sharing same trip twice → "Already shared" error

---

## 💡 Feature Highlights

✨ **Seamless Collaboration**
- No friction workflow: Share → Accept → Collaborate
- Real-time access control updates
- Granular permission management

🔒 **Security**
- Email validation (EmailStr)
- User verification
- Owner-only invite revocation
- Status-based access control

📱 **Responsive Design**
- Works on desktop and mobile
- Touch-friendly buttons
- Scrollable lists for many trips/invites

⚡ **Performance**
- Efficient database queries with joined loading
- Permission checks on all endpoints
- Cascade deletes prevent orphaned data

---

## 🐛 Troubleshooting

### "Invite not showing in modal"
- **Check**: Make sure you're logged in as the recipient
- **Check**: Look for "No pending invites" message
- **Try**: Refresh the page and click Invites again

### "Cannot create entry on shared trip"
- **Reason**: You have "viewer" permission, not "editor"
- **Solution**: Ask the trip owner to reshare with "editor" permission
- **Or**: They can revoke and reshare

### "Trip doesn't appear in My Trips after accepting"
- **Check**: Wait a few seconds and refresh the page
- **Check**: Click on "My Trips" in navigation
- **Try**: Clear browser cache and reload

### "Share button shows error"
- **Check**: Email must be registered in the system
- **Check**: Email format must be valid
- **Try**: Create the test account first: Settings > Admin (if available)

### "Invites link not visible"
- **Check**: Click profile dropdown - it's in the menu
- **Check**: You must be logged in
- **Try**: Refresh the page

---

## 📊 API Endpoints Available

All endpoints available at `http://127.0.0.1:8000/`:

```
POST   /sharing/trips/{trip_id}/share
       → Send invite to email

GET    /sharing/invites
       → Get grouped invites (pending/accepted/declined)

PUT    /sharing/invites/{invite_id}/accept
       → Accept an invite

PUT    /sharing/invites/{invite_id}/decline
       → Decline an invite

GET    /sharing/shared-trips
       → View trips shared with you

GET    /sharing/trips/{trip_id}/shared-with
       → View who trip is shared with (owner only)

DELETE /sharing/trips/{trip_id}/shared-with/{invite_id}
       → Revoke access (owner only)
```

---

## ✅ Testing Checklist

- [ ] Can share a trip with another user
- [ ] Recipient receives invite in their Invites modal
- [ ] Recipient can accept the invite
- [ ] Shared trip appears in recipient's My Trips
- [ ] Editor can create entries on shared trip
- [ ] Viewer cannot create entries (blocked)
- [ ] Owner can revoke access
- [ ] Revoked trip no longer accessible to recipient
- [ ] Email validation prevents invalid emails
- [ ] Error messages are helpful
- [ ] UI is responsive on mobile
- [ ] Permissions persist after page reload

---

## 🎯 Next Steps

1. **Run the test walkthrough** above with two browser windows
2. **Verify all features** work as expected
3. **Test edge cases** (invalid emails, revoke, etc.)
4. **Check the database** to see TripInvite records created
5. **Review the code** in SHARING_SYSTEM_COMPLETE.md
6. **Deploy when satisfied** ✅

---

**Status**: ✅ Ready for Testing
**Last Updated**: 2024-01-16
