# Manual Testing Guide — Dashboard Charts (CT-003)

This guide walks through manually verifying the dashboard charts, period selectors, and calculations.

## Prerequisites

- Application running locally (`docker compose up -d` or manual start)
- Frontend: http://localhost:5173
- API: http://localhost:8000

## 1. Create Test Activities Spanning Multiple Weeks

Log activities across different dates and categories to generate meaningful chart data. Use the transport form on the dashboard or call the API directly.

### Via the UI

1. Navigate to http://localhost:5173/dashboard
2. Use the **Log Activity** form on the dashboard
3. Log at least 5–10 activities across different categories (car, bus, train, bike)

### Via the API (recommended for date control)

Use the API docs at http://localhost:8000/docs or `curl` to create activities with specific dates. Replace `<SESSION_ID>` with the value from your browser's `X-Session-ID` header (visible in DevTools → Network tab on any API request).

```bash
# Week 1 — transport activities
curl -X POST http://localhost:8000/api/v1/activities \
  -H "Content-Type: application/json" \
  -H "X-Session-ID: <SESSION_ID>" \
  -d '{"category": "transport", "activity_type": "car", "quantity": 50, "unit": "km", "date": "2026-01-26"}'

curl -X POST http://localhost:8000/api/v1/activities \
  -H "Content-Type: application/json" \
  -H "X-Session-ID: <SESSION_ID>" \
  -d '{"category": "transport", "activity_type": "bus", "quantity": 30, "unit": "km", "date": "2026-01-28"}'

# Week 2 — energy activities
curl -X POST http://localhost:8000/api/v1/activities \
  -H "Content-Type: application/json" \
  -H "X-Session-ID: <SESSION_ID>" \
  -d '{"category": "energy", "activity_type": "electricity", "quantity": 100, "unit": "kWh", "date": "2026-02-02"}'

curl -X POST http://localhost:8000/api/v1/activities \
  -H "Content-Type: application/json" \
  -H "X-Session-ID: <SESSION_ID>" \
  -d '{"category": "energy", "activity_type": "natural_gas", "quantity": 50, "unit": "kWh", "date": "2026-02-04"}'

# Week 3 — food activities
curl -X POST http://localhost:8000/api/v1/activities \
  -H "Content-Type: application/json" \
  -H "X-Session-ID: <SESSION_ID>" \
  -d '{"category": "food", "activity_type": "beef", "quantity": 2, "unit": "kg", "date": "2026-02-09"}'

curl -X POST http://localhost:8000/api/v1/activities \
  -H "Content-Type: application/json" \
  -H "X-Session-ID: <SESSION_ID>" \
  -d '{"category": "food", "activity_type": "chicken", "quantity": 3, "unit": "kg", "date": "2026-02-10"}'

# Current week — mixed
curl -X POST http://localhost:8000/api/v1/activities \
  -H "Content-Type: application/json" \
  -H "X-Session-ID: <SESSION_ID>" \
  -d '{"category": "transport", "activity_type": "train", "quantity": 120, "unit": "km", "date": "2026-02-12"}'

curl -X POST http://localhost:8000/api/v1/activities \
  -H "Content-Type: application/json" \
  -H "X-Session-ID: <SESSION_ID>" \
  -d '{"category": "energy", "activity_type": "electricity", "quantity": 80, "unit": "kWh", "date": "2026-02-12"}'
```

## 2. Test All Period Selectors

Navigate to the dashboard and click each period button. Verify the following for each:

| Period | Expected Behavior |
|---|---|
| **Today** | Shows only today's activities. Summary card shows 0 if nothing logged today. |
| **This Week** | Shows Mon–Sun of the current week. Trend chart has 7 data points. |
| **This Month** | Shows 1st to last day of current month. Trend chart has 28–31 data points. |
| **This Year** | Shows Jan 1 to Dec 31. Trend chart shows daily data for the full year. |
| **All Time** | Shows all activities ever logged. Widest date range. |

### What to check for each period

- [ ] **Summary Card** updates with correct total, activity count, and daily average
- [ ] **% change** arrow direction makes sense (↑ red = increase, ↓ green = decrease, → neutral = no change)
- [ ] **Pie chart** shows correct category proportions (hover to verify kg values)
- [ ] **Trend chart** shows data points for the correct date range
- [ ] **Loading state** appears briefly when switching periods
- [ ] Switching back to a previously viewed period loads instantly (cached)

## 3. Verify Calculations Match

Cross-check the dashboard numbers against the raw API responses.

### Step-by-step

1. Open browser DevTools → Network tab
2. Select "This Month" period on the dashboard
3. Find the three API calls:
   - `GET /api/v1/footprint/summary?period=month`
   - `GET /api/v1/footprint/breakdown?period=month`
   - `GET /api/v1/footprint/trend?period=month`
4. Click each response and verify:

| Check | API field | Dashboard element |
|---|---|---|
| Total emissions | `summary.total_co2e_kg` | Large number on Summary Card |
| Activity count | `summary.activity_count` | "Activities" row on Summary Card |
| Daily average | `summary.average_daily_co2e_kg` | "Avg Daily" row on Summary Card |
| Change % | `summary.change_percentage` | Arrow + percentage on Summary Card |
| Category totals | `breakdown.breakdown[].co2e_kg` | Pie chart tooltip values |
| Category %s | `breakdown.breakdown[].percentage` | Pie chart labels |
| Trend points | `trend.data_points[].co2e_kg` | Line chart Y-axis values |

### Sanity checks

- Sum of all `breakdown[].co2e_kg` should equal `summary.total_co2e_kg`
- Sum of all `breakdown[].percentage` should be ~100%
- Sum of all `trend.data_points[].co2e_kg` should equal `summary.total_co2e_kg`
- `average_daily_co2e_kg` ≈ `total_co2e_kg / number_of_days_in_period`

## 4. Test on Mobile Viewport

1. Open browser DevTools → Toggle Device Toolbar (Ctrl+Shift+M / Cmd+Shift+M)
2. Test at these viewports:

| Device | Width | What to verify |
|---|---|---|
| **iPhone SE** | 375px | Period buttons wrap, charts stack vertically, text readable |
| **iPhone 14** | 390px | Same as above |
| **iPad Mini** | 768px | Charts may show side-by-side, period buttons fit in one row |
| **Desktop** | 1280px | Full 2-column chart layout, all elements visible |

### Mobile checklist

- [ ] Period selector buttons wrap gracefully (no horizontal overflow)
- [ ] Summary card is full-width and readable
- [ ] Pie chart is centered and labels don't overlap
- [ ] Line chart axes are readable, X-axis labels don't overlap
- [ ] Scrolling is smooth, no horizontal scroll on the page
- [ ] Tap targets (period buttons) are large enough (~44px minimum)

## 5. Test Auto-Refresh After Logging

1. View the dashboard with "This Month" selected
2. Note the current total CO2e
3. Log a new activity using the form on the same page
4. Verify:
   - [ ] Summary card total increases
   - [ ] Pie chart updates with new proportions
   - [ ] Trend chart shows the new data point
   - [ ] Activity list shows the new entry

## 6. Test Empty State

1. Switch to "Today" period on a day with no activities
2. Verify:
   - [ ] Empty state illustration (🌱) is displayed
   - [ ] "No activities logged yet" message appears
   - [ ] "Start tracking your footprint" prompt is shown
   - [ ] Log Activity form is still accessible below

## 7. Test Authenticated vs Guest

### As guest (no account)
1. Open the app in an incognito window
2. Log activities and verify dashboard shows them
3. Close and reopen incognito → data should be gone (new session)

### As authenticated user
1. Sign in with an account
2. Log activities and verify dashboard shows them
3. Sign out and sign back in → data should persist
