# GramSehat — Layer 7 Database Deployment Guide (Supabase)

This directory contains the complete, idempotent SQL scripts for GramSehat's data layer.

---

## 📋 Execution Order in Supabase SQL Editor

Run the SQL files in the **Supabase Dashboard → SQL Editor** in the exact numerical sequence below:

### Step 1: Create Database Schema
📄 **File:** [`schema.sql`](file:///Users/aayushchaturvedi/Documents/ANTIGRAVITY/Gramsehat/backend/db/schema.sql)  
- **Action:** Creates all 7 tables (`patients`, `sessions`, `visits`, `hospitals`, `referrals`, `prealerts`, `ambulance_requests`) with UUID primary keys, check constraints, foreign keys, and indexes.
- **Verification Query:**
  ```sql
  SELECT table_name 
  FROM information_schema.tables 
  WHERE table_schema = 'public' 
  ORDER BY table_name;
  ```
  *Expected Output:* 7 tables listed.

---

### Step 2: Create Hospital Matching Function
📄 **File:** [`functions.sql`](file:///Users/aayushchaturvedi/Documents/ANTIGRAVITY/Gramsehat/backend/db/functions.sql)  
- **Action:** Installs the `match_hospitals(p_specialty, p_lat, p_lng, p_limit)` PL/pgSQL function using the Haversine formula and automated emergency fallback.
- **Verification Query:**
  ```sql
  SELECT routine_name, routine_type 
  FROM information_schema.routines 
  WHERE routine_name = 'match_hospitals';
  ```
  *Expected Output:* 1 row returned.

---

### Step 3: Seed Demo Hospital Network
📄 **File:** [`seed.sql`](file:///Users/aayushchaturvedi/Documents/ANTIGRAVITY/Gramsehat/backend/db/seed.sql)  
- **Action:** Populates 10 fictional demo hospitals with diverse specialties and bed counts spread around rural UP (`lat: 26.8467, lng: 80.9462`).
- **Customization:** You can modify `c_lat` and `c_lng` at lines 20-21 in `seed.sql` to re-center the simulated facilities around your hackathon demo target village!
- **Verification Query:**
  ```sql
  SELECT 
    name, 
    type, 
    specialties, 
    beds_available, 
    is_demo 
  FROM hospitals 
  ORDER BY name;
  ```
  *Expected Output:* 10 demo hospital rows.

- **Test Matching Query:**
  ```sql
  -- Match nearest eye hospital with beds available:
  SELECT * FROM match_hospitals('ophthalmology', 26.8467, 80.9462, 3);
  ```
  *Expected Output:* Returns `Drishti Rural Eye Institute (Demo)` with `fallback = false`, filtering out the 0-bed clinic.

---

### Step 4: Configure Supabase Realtime & Private Storage
📄 **File:** [`realtime_and_storage.sql`](file:///Users/aayushchaturvedi/Documents/ANTIGRAVITY/Gramsehat/backend/db/realtime_and_storage.sql)  
- **Action:** Adds `prealerts` and `ambulance_requests` to the `supabase_realtime` publication for live WebSocket streaming, and creates the private `patient-images` storage bucket.
- **Verification Queries:**
  ```sql
  -- Check realtime publication tables:
  SELECT pubname, tablename 
  FROM pg_publication_tables 
  WHERE pubname = 'supabase_realtime';
  ```
  *Expected Output:* `prealerts` and `ambulance_requests` present.

  ```sql
  -- Check storage bucket:
  SELECT id, name, public 
  FROM storage.buckets 
  WHERE id = 'patient-images';
  ```
  *Expected Output:* Bucket `patient-images` with `public = false`.

---

### Step 5: Enable Row Level Security (RLS)
📄 **File:** [`policies.sql`](file:///Users/aayushchaturvedi/Documents/ANTIGRAVITY/Gramsehat/backend/db/policies.sql)  
- **Action:** Enables RLS on all 7 tables. Configures read-only demo access for the frontend anon key on `prealerts`, `ambulance_requests`, and `hospitals`.
- **Verification Query:**
  ```sql
  SELECT tablename, rowsecurity 
  FROM pg_tables 
  WHERE schemaname = 'public';
  ```
  *Expected Output:* `rowsecurity = true` for all 7 tables.

---

## 🔐 Environment Variables

Ensure your backend `.env` file contains:
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-service-role-key-here
```
> **IMPORTANT:** The `SUPABASE_SERVICE_KEY` (service_role) has administrative privileges and bypasses RLS. Never commit it to git or bundle it in frontend code!
