# The canvas, row by row: the one list of every screen, its code and title, its width and its kind.
# layout.py places the artboards from it and map.py writes the map from it. Add a screen here first.
# item: (file stem, frame title, width, kind)  kind: page | sheet | phone | menu | doc | ref
P, S, PH, DOC, TV = 1440, 720, 390, 816, 1920
ROWS = [
 ("S", "Start here · the map of every screen and click, and the design system", [
   ("Map", "S1 · Every screen and where each click leads", 3360, "ref"),
   ("System", "S2 · Design system", P, "page")]),
 ("A", "A · Public site: home, discover, events, organizations", [
   ("Main", "A1 · Home", P, "page"), ("Discover", "A2 · Discover", P, "page"), ("Event", "A3 · Event", P, "page"), ("Gate", "A4 · Sign-in gate", S, "sheet"),
   ("Organizations", "A5 · Organizations", P, "page"), ("OrgProfile", "A6 · Organization profile", P, "page"), ("ContactOrg", "A7 · Message an organization", S, "sheet")]),
 ("A2", "A · Public site: Qur’an school, giving and zakah, for organizations, help, a coffee for the developer", [
   ("Program", "A8 · Weekend Qur’an School", P, "page"), ("Donate", "A9 · Donate", P, "page"), ("DonateDone", "A10 · Donation receipt", S, "sheet"),
   ("ForOrgs", "A11 · For organizations", P, "page"), ("Help", "A12 · Help", P, "page"), ("Zakah", "A20 · Give zakah", P, "page"), ("Coffee", "A18 · Buy the developer a coffee", S, "sheet")]),
 ("A3", "A · Public site: Friday prayers, Eid prayer, payment links, terms and privacy", [
   ("Friday", "A13 · Friday prayers", P, "page"), ("Eid", "A19 · Eid prayer", P, "page"), ("PayLink", "A14 · Payment link", P, "page"),
   ("Terms", "A15 · Terms of Service", P, "page"), ("Privacy", "A16 · Privacy Policy", P, "page"), ("OrgTerms", "A17 · Organization Terms", P, "page")]),
 ("B", "B · Accounts: sign in, recover, create a member account", [
   ("SignIn", "B1 · Sign in", P, "page"), ("CheckEmail", "B2 · Check your email", S, "sheet"), ("Workspaces", "B3 · Choose a space", S, "sheet"), ("Forgot", "B4 · Forgot password", S, "sheet"),
   ("ResetPassword", "B5 · New password", S, "sheet"), ("SignUp", "B6 · Create account: choose type", P, "page"), ("SignUpMember", "B7 · Member sign-up", P, "page"),
   ("Verify", "B8 · Verify email", S, "sheet"), ("Welcome", "B9 · Welcome", P, "page")]),
 ("B2", "B · Accounts: organization application, invitations, updated terms", [
   ("OrgApply1", "B10 · Organization application 1 of 4: you", P, "page"), ("OrgApply2", "B11 · Organization application 2 of 4: organization", P, "page"),
   ("OrgApply3", "B12 · Organization application 3 of 4: verification", P, "page"), ("OrgApply4", "B13 · Organization application 4 of 4: review", P, "page"),
   ("OrgPending", "B14 · Application status", P, "page"), ("Invite", "B15 · Team invitation", S, "sheet"),
   ("TermsUpdate", "B16 · Updated terms at sign-in", S, "sheet"), ("GuardianInvite", "B17 · Guardian invitation", S, "sheet"), ("Unsubscribe", "B18 · Unsubscribe from an email", S, "sheet")]),
 ("C", "C · Member and family: my week, saved, notifications, family, the home masjid banner", [
   ("MyHusna", "C1 · My week", P, "page"), ("RsvpSheet", "C2 · RSVP", S, "sheet"), ("Saved", "C3 · Saved and going", P, "page"), ("Notifications", "C4 · Notifications", P, "page"),
   ("Family", "C5 · My family", P, "page"), ("ChildForm", "C6 · Add a child", P, "page"), ("PrayerBar", "C20 · Home masjid banner, on top of every member page", P, "strip")]),
 ("C2", "C · Parent enrolls children in Weekend Qur’an School", [
   ("Enroll1", "C7 · Enroll 1 of 5: children", P, "page"), ("Enroll2", "C8 · Enroll 2 of 5: classes", P, "page"), ("Enroll3", "C9 · Enroll 3 of 5: family and safety", P, "page"),
   ("Enroll4", "C10 · Enroll 4 of 5: agreements", P, "page"), ("Enroll5", "C11 · Enroll 5 of 5: tuition", P, "page"), ("Enroll6", "C12 · Enrollment submitted", P, "page")]),
 ("C3", "C · During the term: child, absences, payments, account, messages, waitlist", [
   ("Child", "C13 · Child: class, attendance, progress", P, "page"), ("AbsenceSheet", "C14 · Report an absence", S, "sheet"), ("WithdrawSheet", "C15 · Withdraw from a class", S, "sheet"),
   ("Payments", "C16 · Payments and receipts", P, "page"), ("Account", "C17 · Account settings", P, "page"),
   ("Messages", "C18 · Messages", P, "page"), ("WaitlistOffer", "C19 · Waitlist place offered", S, "sheet")]),
 ("D", "D · Organization workspace: setup, overview, events, Friday and Eid prayers", [
   ("OrgSetup", "D1 · Setup guide", P, "page"), ("OrgHome", "D2 · Overview", P, "page"), ("OrgEvents", "D3 · Events", P, "page"), ("OrgEventEdit", "D4 · Create event", P, "page"),
   ("OrgEventManage", "D5 · Event RSVPs", P, "page"), ("OrgFriday", "D6 · Friday and Eid prayers", P, "page"), ("OrgServiceSheet", "D7 · Edit a Jumu’ah", S, "sheet"), ("OrgEidEdit", "D39 · Plan an Eid prayer", P, "page")]),
 ("D2", "D · Organization workspace: school programs, applications, rosters, attendance, teacher’s view", [
   ("OrgPrograms", "D8 · Programs", P, "page"), ("OrgNewTermSheet", "D24 · Start the next term", S, "sheet"), ("OrgProgramEdit", "D9 · Program setup", P, "page"),
   ("UnsavedSheet", "D23 · Leave without saving?", S, "sheet"), ("OrgApplications", "D10 · Applications", P, "page"), ("OrgDecisionSheet", "D11 · Decline or ask for info", S, "sheet"),
   ("OrgRoster", "D12 · Classes and rosters", P, "page"), ("OrgStudent", "D13 · Student record", P, "page"), ("OrgAttendance", "D14 · Take attendance", P, "page"), ("OrgAttendanceTerm", "D31 · Attendance for the term", P, "page"),
   ("TeacherHome", "D25 · Teacher’s workspace", P, "page")]),
 ("D3", "D · Organization workspace: money, announcements, inbox, team, profile, settings, activity", [
   ("OrgDonations", "D15 · Donations", P, "page"), ("OrgPayouts", "D16 · Tuition and payouts", P, "page"), ("OrgRefundSheet", "D26 · Refund a payment", S, "sheet"),
   ("OrgAnnouncements", "D17 · Announcements", P, "page"), ("OrgInbox", "D18 · Inbox", P, "page"), ("OrgTeam", "D19 · Team and roles", P, "page"), ("OrgInviteSheet", "D20 · Invite a teammate", S, "sheet"),
   ("OrgProfileEdit", "D21 · Public profile editor", P, "page"), ("OrgSettings", "D22 · Organization settings", P, "page"),
   ("OrgChangeSheet", "D27 · Change verified name or address", S, "sheet"), ("OrgTransferSheet", "D28 · Transfer ownership", S, "sheet"), ("OrgTransferAccept", "D29 · Accept ownership", S, "sheet"),
   ("OrgActivity", "D30 · Activity log", P, "page"), ("OrgCoffee", "D38 · Buy the developer a coffee, from an organization", S, "sheet")]),
 ("D4", "D · Organization workspace: prayer times and TV displays", [
   ("OrgPrayerTimes", "D32 · Prayer times", P, "page"), ("OrgDisplays", "D33 · TV displays", P, "page"), ("OrgDisplayPairSheet", "D34 · Pair a TV", S, "sheet"),
   ("OrgDisplayEdit", "D35 · Set up a TV display", P, "page"), ("OrgSlideSheet", "D36 · Add a slide", S, "sheet"), ("OrgDisplayMessageSheet", "D37 · Show a message now", S, "sheet")]),
 ("E", "E · Founder console: sign-in, overview, approvals, organizations", [
   ("FounderSignIn", "E1 · Founder sign-in", S, "sheet"), ("FounderCode", "E2 · Two-step code", S, "sheet"), ("Founder", "E3 · Founder overview", P, "page"), ("FounderApprovals", "E4 · Organization approvals", P, "page"),
   ("FounderDecisionSheet", "E5 · Reject or request info", S, "sheet"), ("FounderOrgs", "E6 · Organizations", P, "page"), ("FounderOrg", "E7 · Organization detail", P, "page"),
   ("FounderSuspendSheet", "E8 · Suspend organization", S, "sheet")]),
 ("E2", "E · Founder console: users, moderation, support, cities, fees, system status, audit, settings", [
   ("FounderUsers", "E9 · Users", P, "page"), ("FounderModeration", "E10 · Moderation", P, "page"), ("FounderSupport", "E15 · Support inbox", P, "page"), ("FounderCities", "E11 · Cities and content", P, "page"),
   ("FounderPayments", "E12 · Payments and coffee", P, "page"), ("FounderHealth", "E16 · System status", P, "page"), ("FounderAudit", "E13 · Audit log", P, "page"),
   ("FounderSettings", "E14 · Console settings", P, "page"), ("FounderLegalSheet", "E17 · Publish a legal version", S, "sheet"), ("FounderStaffSetup", "E18 · Staff invitation and two-step setup", S, "sheet")]),
 ("F", "F · System: empty and error states, every message sent, hand-offs to Stripe, printed documents", [
   ("States", "F1 · Empty and error states", P, "page"), ("Emails", "F2 · Emails and text messages", P, "page"), ("Stripe", "F3 · Hand-offs to Stripe", P, "page"),
   ("DocReceipt", "F4 · Tuition receipt (PDF)", DOC, "doc"), ("DocStatement", "F5 · Year-end giving statement (PDF)", DOC, "doc"),
   ("DocEnrollment", "F6 · Signed enrollment record (PDF)", DOC, "doc"), ("DocSignIn", "F7 · Class sign-in sheet (PDF)", DOC, "doc")]),
 ("G", "G · On a phone: visitor and parent", [
   ("PhoneMain", "G1 · Home", PH, "phone"), ("MenuVisitor", "G2 · Visitor menu", PH, "menu"), ("PhoneEvent", "G3 · Event", PH, "phone"), ("PhoneSignIn", "G4 · Sign in", PH, "phone"),
   ("PhoneMyHusna", "G5 · My week", PH, "phone"), ("MenuMember", "G6 · Member menu", PH, "menu"), ("PhoneEnroll2", "G7 · Enroll: classes", PH, "phone"), ("PhoneEnroll5", "G8 · Enroll: tuition", PH, "phone"),
   ("PhoneChild", "G9 · Child", PH, "phone"), ("PhoneAbsence", "G10 · Report an absence", PH, "phone"), ("PhoneMessages", "G11 · Messages", PH, "phone"), ("PhoneDonate", "G12 · Donate", PH, "phone"), ("PhoneEid", "G18 · Eid prayer", PH, "phone"), ("PhonePrayerBar", "G17 · Home masjid banner, moving", PH, "strip")]),
 ("G2", "G · On a phone: teacher and organization", [
   ("PhoneTeacher", "G13 · Teacher’s workspace", PH, "phone"), ("PhoneAttendance", "G14 · Take attendance", PH, "phone"), ("PhoneOrgHome", "G15 · Workspace overview", PH, "phone"), ("MenuOrg", "G16 · Workspace menu", PH, "menu")]),
 ("H", "H · On a TV in the masjid: pairing, the three layouts, and the minutes around a prayer", [
   ("TvPair", "H1 · A new TV: pairing code", TV, "tv"), ("TvMain", "H2 · Timetable layout", TV, "tv"), ("TvSlides", "H3 · Slides-first layout", TV, "tv"), ("TvFocus", "H4 · Focus layout", TV, "tv"),
   ("TvAdhan", "H5 · At the adhan", TV, "tv"), ("TvIqamah", "H6 · Countdown to the iqamah", TV, "tv"), ("TvPrayer", "H7 · During the prayer", TV, "tv")]),
 ("H2", "H · On a TV in the masjid: Fridays, Ramadan, Eid, a message from the office, no connection, a screen on its side", [
   ("TvFriday", "H8 · Friday board", TV, "tv"), ("TvRamadan", "H9 · Ramadan: countdown to iftar", TV, "tv"), ("TvMessage", "H10 · A message from the office", TV, "tv"),
   ("TvOffline", "H11 · No connection", TV, "tv"), ("TvEid", "H13 · Eid prayer, somewhere else", TV, "tv"), ("TvPortrait", "H12 · Portrait screen", 1080, "tv")]),
]
GROUPS = [("S", "Start here"), ("A", "Public site"), ("B", "Accounts"), ("C", "Member and family"), ("D", "Organization workspace"), ("E", "Founder console"), ("F", "System"), ("G", "On a phone"), ("H", "On a TV")]

def all_items():
    for key, title, items in ROWS:
        for stem, t, w, kind in items:
            yield key, stem, t, w, kind

def code_of(title):
    return title.split(' · ')[0]

def code_key(code):
    return (code[0], int(code[1:]))
