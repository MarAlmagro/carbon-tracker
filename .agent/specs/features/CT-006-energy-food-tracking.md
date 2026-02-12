# Feature: Energy & Food Tracking

## Metadata
- **ID**: CT-006
- **Priority**: MEDIUM
- **Estimated Effort**: 6-8 hours
- **Dependencies**: CT-000 (Project Foundation), CT-001 (Transport Logging), CT-003 (Dashboard - optional)

## Summary
Add energy (electricity, natural gas, heating oil) and food (beef, pork, poultry, fish, dairy, vegetables, vegan) tracking categories to complement transport emissions, enabling comprehensive personal carbon footprint monitoring.

## User Story
As a **Carbon Tracker user**, I want to **log my energy consumption and food choices** so that **I can track my complete carbon footprint beyond just transportation**.

## Acceptance Criteria
- [ ] AC1: Users can log electricity consumption in kWh
- [ ] AC2: Users can log natural gas consumption in kWh
- [ ] AC3: Users can log heating oil consumption in liters
- [ ] AC4: Users can log food consumption by type (beef, pork, poultry, fish, dairy, vegetables, vegan)
- [ ] AC5: Food logging measured in servings or meals
- [ ] AC6: Category selector switches between Transport, Energy, Food
- [ ] AC7: Dashboard shows breakdown by all three categories
- [ ] AC8: Emission factors seeded for all energy and food types
- [ ] AC9: All form validations work correctly
- [ ] AC10: All strings in i18n files (EN/ES)

## API Contract

### 1. Log Energy Activity
**Endpoint:** `POST /api/v1/activities`

**Request Body (Electricity):**
```json
{
  "category": "energy",
  "type": "electricity",
  "value": 350.0,
  "date": "2026-02-10",
  "notes": "Monthly electricity usage"
}
```

**Response (201 Created):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "category": "energy",
  "type": "electricity",
  "value": 350.0,
  "co2e_kg": 140.0,
  "date": "2026-02-10",
  "notes": "Monthly electricity usage",
  "user_id": null,
  "session_id": "abc-123",
  "created_at": "2026-02-10T14:30:00Z"
}
```

### 2. Log Food Activity
**Endpoint:** `POST /api/v1/activities`

**Request Body (Beef):**
```json
{
  "category": "food",
  "type": "beef",
  "value": 2,
  "date": "2026-02-10",
  "notes": "Steak dinner"
}
```

**Response (201 Created):**
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "category": "food",
  "type": "beef",
  "value": 2,
  "co2e_kg": 14.0,
  "date": "2026-02-10",
  "notes": "Steak dinner",
  "user_id": null,
  "session_id": "abc-123",
  "created_at": "2026-02-10T14:30:00Z"
}
```

## Emission Factors

### Energy Emission Factors (kg CO2e per unit)

| Energy Type | Factor | Unit | Notes |
|-------------|--------|------|-------|
| `electricity` | 0.40 | kg CO2e/kWh | Grid average (varies by region) |
| `natural_gas` | 0.20 | kg CO2e/kWh | Natural gas heating |
| `heating_oil` | 2.50 | kg CO2e/liter | Oil heating |

### Food Emission Factors (kg CO2e per serving)

| Food Type | Factor | Unit | Notes |
|-----------|--------|------|-------|
| `beef` | 7.0 | kg CO2e/serving | Red meat (150g serving) |
| `pork` | 3.5 | kg CO2e/serving | Pork (150g serving) |
| `poultry` | 1.5 | kg CO2e/serving | Chicken/turkey (150g serving) |
| `fish` | 2.0 | kg CO2e/serving | Fish/seafood (150g serving) |
| `dairy` | 1.0 | kg CO2e/serving | Dairy products (milk, cheese, yogurt) |
| `vegetables` | 0.2 | kg CO2e/serving | Plant-based foods |
| `vegan_meal` | 0.5 | kg CO2e/serving | Complete vegan meal |

Source: UK DEFRA 2023, FAO 2023

## UI/UX Requirements

### Category Selector

Add tabs or buttons to switch between categories:
```
┌─────────────────────────────────────────┐
│  [Transport] [Energy] [Food]            │
├─────────────────────────────────────────┤
│  (Form content based on selected tab)   │
└─────────────────────────────────────────┘
```

### Energy Form

```
┌─────────────────────────────────────────┐
│  Energy Type: [Electricity ▼]           │
│                                         │
│  Amount (kWh): [350.0]                  │
│                                         │
│  Date: [2026-02-10]                     │
│                                         │
│  Notes: [Monthly electricity usage]     │
│                                         │
│  Estimated CO2e: 140.0 kg              │
│                                         │
│  [Log Energy Activity]                  │
└─────────────────────────────────────────┘
```

**Energy Type Options:**
- Electricity (kWh)
- Natural Gas (kWh)
- Heating Oil (liters)

### Food Form

```
┌─────────────────────────────────────────┐
│  Food Type: [Beef ▼]                    │
│                                         │
│  Servings: [2]                          │
│                                         │
│  Date: [2026-02-10]                     │
│                                         │
│  Notes: [Steak dinner]                  │
│                                         │
│  Estimated CO2e: 14.0 kg               │
│                                         │
│  [Log Food Activity]                    │
└─────────────────────────────────────────┘
```

**Food Type Options:**
- Beef (red meat)
- Pork
- Poultry (chicken, turkey)
- Fish/Seafood
- Dairy (milk, cheese, yogurt)
- Vegetables
- Vegan Meal

### Activity Cards

**Energy Card:**
```
┌─────────────────────────────────────────┐
│  ⚡ Electricity                          │
│  350 kWh • 140.0 kg CO2e               │
│  Feb 10, 2026                           │
│  Monthly electricity usage              │
└─────────────────────────────────────────┘
```

**Food Card:**
```
┌─────────────────────────────────────────┐
│  🥩 Beef                                 │
│  2 servings • 14.0 kg CO2e             │
│  Feb 10, 2026                           │
│  Steak dinner                           │
└─────────────────────────────────────────┘
```

### Dashboard Updates

Category breakdown now shows 3 segments:
- Transport (blue)
- Energy (yellow)
- Food (green)

## Technical Design

### What's Already Done (CT-000/CT-001)

#### Backend
- ✓ Activity entity supports `category` field (transport, energy, food)
- ✓ EmissionFactor table stores factors for all categories
- ✓ LogActivityUseCase is category-agnostic (works for any category)
- ✓ POST /api/v1/activities endpoint accepts category parameter
- ✓ CalculationService calculates CO2e regardless of category
- ✓ Dashboard aggregation groups by category

#### Frontend
- ✓ TransportForm component structure (can be replicated)
- ✓ ActivityCard displays category icon dynamically
- ✓ useCreateActivity hook is category-agnostic
- ✓ i18n structure supports category strings

### What Needs to Be Built

#### Backend (NEW)

**1. Seed Energy Emission Factors** (`backend/scripts/seed_emission_factors.py`)

Update seeding script to add energy factors:
```python
energy_factors = [
    ("energy", "electricity", 0.40, "kg CO2e/kWh", "Grid average"),
    ("energy", "natural_gas", 0.20, "kg CO2e/kWh", "Natural gas heating"),
    ("energy", "heating_oil", 2.50, "kg CO2e/liter", "Oil heating"),
]

for category, type_name, factor, unit, source in energy_factors:
    client.table("emission_factors").insert({
        "category": category,
        "type": type_name,
        "factor": factor,
        "unit": unit,
        "source": source
    }).execute()
```

**2. Seed Food Emission Factors** (`backend/scripts/seed_emission_factors.py`)

```python
food_factors = [
    ("food", "beef", 7.0, "kg CO2e/serving", "UK DEFRA 2023"),
    ("food", "pork", 3.5, "kg CO2e/serving", "UK DEFRA 2023"),
    ("food", "poultry", 1.5, "kg CO2e/serving", "UK DEFRA 2023"),
    ("food", "fish", 2.0, "kg CO2e/serving", "FAO 2023"),
    ("food", "dairy", 1.0, "kg CO2e/serving", "FAO 2023"),
    ("food", "vegetables", 0.2, "kg CO2e/serving", "FAO 2023"),
    ("food", "vegan_meal", 0.5, "kg CO2e/serving", "FAO 2023"),
]

for category, type_name, factor, unit, source in food_factors:
    client.table("emission_factors").insert({
        "category": category,
        "type": type_name,
        "factor": factor,
        "unit": unit,
        "source": source
    }).execute()
```

**3. Update Activity Schema** (`backend/src/api/schemas/activity.py`)

Add validation for category field:
```python
class ActivityCreate(BaseModel):
    """Activity creation request."""
    category: str = Field(regex="^(transport|energy|food)$")
    type: str = Field(min_length=1)
    value: float = Field(gt=0)
    date: date
    notes: Optional[str] = None
    metadata: Optional[dict] = None
```

**No new backend code needed!** The existing LogActivityUseCase already handles all categories generically.

#### Frontend (NEW)

**1. Energy Form Component** (`frontend/src/components/features/activity/EnergyForm.tsx` - NEW)

```typescript
import { useForm } from 'react-hook-form';
import { useTranslation } from 'react-i18next';
import { useCreateActivity } from '@/hooks/useActivities';

interface EnergyFormData {
  type: string;
  value: number;
  date: string;
  notes: string;
}

const ENERGY_TYPES = [
  { value: 'electricity', unit: 'kWh', factor: 0.40 },
  { value: 'natural_gas', unit: 'kWh', factor: 0.20 },
  { value: 'heating_oil', unit: 'liters', factor: 2.50 }
];

export default function EnergyForm() {
  const { t } = useTranslation();
  const createMutation = useCreateActivity();

  const { register, handleSubmit, watch, formState: { errors } } = useForm<EnergyFormData>({
    defaultValues: {
      type: 'electricity',
      value: 0,
      date: new Date().toISOString().split('T')[0],
      notes: ''
    }
  });

  const selectedType = watch('type');
  const selectedValue = watch('value');

  const selectedEnergyType = ENERGY_TYPES.find(t => t.value === selectedType);
  const estimatedCo2e = selectedValue * (selectedEnergyType?.factor || 0);

  const onSubmit = async (data: EnergyFormData) => {
    await createMutation.mutateAsync({
      category: 'energy',
      type: data.type,
      value: data.value,
      date: data.date,
      notes: data.notes
    });

    // Reset form on success
    if (createMutation.isSuccess) {
      // Form reset handled by useCreateActivity
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div>
        <label className="block text-sm font-medium mb-1">
          {t('activity.energy.type')}
        </label>
        <select
          {...register('type', { required: true })}
          className="w-full px-3 py-2 border rounded-md"
        >
          {ENERGY_TYPES.map(({ value }) => (
            <option key={value} value={value}>
              {t(`activity.energy.types.${value}`)}
            </option>
          ))}
        </select>
      </div>

      <div>
        <label className="block text-sm font-medium mb-1">
          {t('activity.energy.amount')} ({selectedEnergyType?.unit})
        </label>
        <input
          type="number"
          step="0.1"
          {...register('value', { required: true, min: 0.01 })}
          className="w-full px-3 py-2 border rounded-md"
        />
        {errors.value && (
          <span className="text-red-600 text-sm">{t('errors.validation')}</span>
        )}
      </div>

      <div>
        <label className="block text-sm font-medium mb-1">
          {t('activity.date')}
        </label>
        <input
          type="date"
          {...register('date', { required: true })}
          className="w-full px-3 py-2 border rounded-md"
        />
      </div>

      <div>
        <label className="block text-sm font-medium mb-1">
          {t('activity.notes')}
        </label>
        <textarea
          {...register('notes')}
          placeholder={t('activity.notesPlaceholder')}
          className="w-full px-3 py-2 border rounded-md"
          rows={3}
        />
      </div>

      {selectedValue > 0 && (
        <div className="bg-blue-50 p-3 rounded">
          <div className="text-sm text-gray-700">
            {t('activity.estimatedCo2e')}: {estimatedCo2e.toFixed(2)} kg CO2e
          </div>
        </div>
      )}

      <button
        type="submit"
        disabled={createMutation.isPending}
        className="w-full py-2 px-4 bg-yellow-600 text-white rounded-md hover:bg-yellow-700 disabled:opacity-50"
      >
        {createMutation.isPending
          ? t('common.loading')
          : t('activity.energy.logEnergy')}
      </button>

      {createMutation.error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-3 py-2 rounded">
          {createMutation.error.message}
        </div>
      )}
    </form>
  );
}
```

**2. Food Form Component** (`frontend/src/components/features/activity/FoodForm.tsx` - NEW)

```typescript
import { useForm } from 'react-hook-form';
import { useTranslation } from 'react-i18next';
import { useCreateActivity } from '@/hooks/useActivities';

interface FoodFormData {
  type: string;
  value: number;
  date: string;
  notes: string;
}

const FOOD_TYPES = [
  { value: 'beef', factor: 7.0 },
  { value: 'pork', factor: 3.5 },
  { value: 'poultry', factor: 1.5 },
  { value: 'fish', factor: 2.0 },
  { value: 'dairy', factor: 1.0 },
  { value: 'vegetables', factor: 0.2 },
  { value: 'vegan_meal', factor: 0.5 }
];

export default function FoodForm() {
  const { t } = useTranslation();
  const createMutation = useCreateActivity();

  const { register, handleSubmit, watch, formState: { errors } } = useForm<FoodFormData>({
    defaultValues: {
      type: 'beef',
      value: 1,
      date: new Date().toISOString().split('T')[0],
      notes: ''
    }
  });

  const selectedType = watch('type');
  const selectedServings = watch('value');

  const selectedFoodType = FOOD_TYPES.find(t => t.value === selectedType);
  const estimatedCo2e = selectedServings * (selectedFoodType?.factor || 0);

  const onSubmit = async (data: FoodFormData) => {
    await createMutation.mutateAsync({
      category: 'food',
      type: data.type,
      value: data.value,
      date: data.date,
      notes: data.notes
    });
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div>
        <label className="block text-sm font-medium mb-1">
          {t('activity.food.type')}
        </label>
        <select
          {...register('type', { required: true })}
          className="w-full px-3 py-2 border rounded-md"
        >
          {FOOD_TYPES.map(({ value }) => (
            <option key={value} value={value}>
              {t(`activity.food.types.${value}`)}
            </option>
          ))}
        </select>
      </div>

      <div>
        <label className="block text-sm font-medium mb-1">
          {t('activity.food.servings')}
        </label>
        <input
          type="number"
          step="1"
          min="1"
          {...register('value', { required: true, min: 1 })}
          className="w-full px-3 py-2 border rounded-md"
        />
        {errors.value && (
          <span className="text-red-600 text-sm">{t('errors.validation')}</span>
        )}
      </div>

      <div>
        <label className="block text-sm font-medium mb-1">
          {t('activity.date')}
        </label>
        <input
          type="date"
          {...register('date', { required: true })}
          className="w-full px-3 py-2 border rounded-md"
        />
      </div>

      <div>
        <label className="block text-sm font-medium mb-1">
          {t('activity.notes')}
        </label>
        <textarea
          {...register('notes')}
          placeholder={t('activity.notesPlaceholder')}
          className="w-full px-3 py-2 border rounded-md"
          rows={3}
        />
      </div>

      {selectedServings > 0 && (
        <div className="bg-green-50 p-3 rounded">
          <div className="text-sm text-gray-700">
            {t('activity.estimatedCo2e')}: {estimatedCo2e.toFixed(2)} kg CO2e
          </div>
        </div>
      )}

      <button
        type="submit"
        disabled={createMutation.isPending}
        className="w-full py-2 px-4 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50"
      >
        {createMutation.isPending
          ? t('common.loading')
          : t('activity.food.logFood')}
      </button>

      {createMutation.error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-3 py-2 rounded">
          {createMutation.error.message}
        </div>
      )}
    </form>
  );
}
```

**3. Category Selector Component** (`frontend/src/components/features/activity/CategorySelector.tsx` - NEW)

```typescript
import { useTranslation } from 'react-i18next';

interface CategorySelectorProps {
  value: string;
  onChange: (category: string) => void;
}

const CATEGORIES = ['transport', 'energy', 'food'] as const;

export default function CategorySelector({ value, onChange }: CategorySelectorProps) {
  const { t } = useTranslation();

  return (
    <div className="flex space-x-2 border-b border-gray-200 mb-6">
      {CATEGORIES.map((category) => (
        <button
          key={category}
          onClick={() => onChange(category)}
          className={`px-4 py-2 font-medium transition-colors ${
            value === category
              ? 'border-b-2 border-blue-600 text-blue-600'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          {t(`activity.categories.${category}`)}
        </button>
      ))}
    </div>
  );
}
```

**4. Update Dashboard Page** (`frontend/src/pages/DashboardPage.tsx`)

```typescript
import { useState } from 'react';
import CategorySelector from '@/components/features/activity/CategorySelector';
import TransportForm from '@/components/features/activity/TransportForm';
import EnergyForm from '@/components/features/activity/EnergyForm';
import FoodForm from '@/components/features/activity/FoodForm';

export default function DashboardPage() {
  const [selectedCategory, setSelectedCategory] = useState('transport');

  return (
    <div>
      {/* ... existing dashboard content ... */}

      <div className="mt-8">
        <h2 className="text-2xl font-bold mb-4">Log Activity</h2>

        <CategorySelector
          value={selectedCategory}
          onChange={setSelectedCategory}
        />

        {selectedCategory === 'transport' && <TransportForm />}
        {selectedCategory === 'energy' && <EnergyForm />}
        {selectedCategory === 'food' && <FoodForm />}
      </div>
    </div>
  );
}
```

**5. Update Activity Card** (`frontend/src/components/features/activity/ActivityCard.tsx`)

Add category-specific icons and formatting:
```typescript
const CATEGORY_ICONS: Record<string, string> = {
  transport: '🚗',
  energy: '⚡',
  food: '🍽️'
};

const TYPE_ICONS: Record<string, string> = {
  // Transport
  car_petrol: '🚗',
  bus: '🚌',
  train: '🚆',
  // Energy
  electricity: '⚡',
  natural_gas: '🔥',
  heating_oil: '🛢️',
  // Food
  beef: '🥩',
  pork: '🥓',
  poultry: '🍗',
  fish: '🐟',
  dairy: '🥛',
  vegetables: '🥗',
  vegan_meal: '🌱'
};

export default function ActivityCard({ activity }: { activity: Activity }) {
  const icon = TYPE_ICONS[activity.type] || CATEGORY_ICONS[activity.category];

  // Different formatting based on category
  const getValueDisplay = () => {
    if (activity.category === 'transport') {
      return `${activity.value} km`;
    } else if (activity.category === 'energy') {
      const unit = activity.type === 'heating_oil' ? 'liters' : 'kWh';
      return `${activity.value} ${unit}`;
    } else if (activity.category === 'food') {
      return `${activity.value} serving${activity.value > 1 ? 's' : ''}`;
    }
    return `${activity.value}`;
  };

  return (
    <div className="activity-card">
      <div className="text-lg">
        {icon} {t(`activity.${activity.category}.types.${activity.type}`)}
      </div>
      <div className="text-sm text-gray-600">
        {getValueDisplay()} • {activity.co2e_kg.toFixed(2)} kg CO2e
      </div>
      {/* ... rest of card ... */}
    </div>
  );
}
```

**6. Update i18n Files**

Already complete in existing locale files (see CT-000 completion document).

## Implementation Steps

1. **Run Emission Factor Seeding**
   - Update `backend/scripts/seed_emission_factors.py`
   - Add energy factors (3 types)
   - Add food factors (7 types)
   - Run script: `python backend/scripts/seed_emission_factors.py`

2. **Create Energy Form Component**
   - Create `frontend/src/components/features/activity/EnergyForm.tsx`
   - Implement form with type dropdown, amount input, date, notes
   - Add CO2e estimation preview
   - Add validation

3. **Create Food Form Component**
   - Create `frontend/src/components/features/activity/FoodForm.tsx`
   - Implement form with type dropdown, servings input, date, notes
   - Add CO2e estimation preview
   - Add validation

4. **Create Category Selector Component**
   - Create `frontend/src/components/features/activity/CategorySelector.tsx`
   - Implement tab navigation for Transport/Energy/Food

5. **Update Dashboard Page**
   - Add CategorySelector component
   - Conditionally render form based on selected category
   - Ensure forms are properly integrated

6. **Update Activity Card**
   - Add category-specific icons
   - Add category-specific value formatting (km, kWh, servings)
   - Update display logic

7. **Update Activity Schema Validation**
   - Add category regex validation to ActivityCreate schema
   - Test validation with invalid categories

8. **Test Backend Emission Factors**
   - Integration test: POST activity with category=energy
   - Integration test: POST activity with category=food
   - Verify CO2e calculations are correct

9. **Test Energy Form**
   - Component test: EnergyForm renders correctly
   - Component test: Form validation works
   - Component test: CO2e preview calculates correctly
   - E2E test: Log electricity, natural gas, heating oil

10. **Test Food Form**
    - Component test: FoodForm renders correctly
    - Component test: Form validation works
    - Component test: CO2e preview calculates correctly
    - E2E test: Log all 7 food types

11. **Test Category Switching**
    - Component test: CategorySelector switches forms
    - E2E test: Switch between all categories and log activities

12. **Test Dashboard Integration**
    - E2E test: Verify all categories appear in breakdown chart
    - E2E test: Verify activities from all categories appear in list
    - Visual test: Check colors match (blue=transport, yellow=energy, green=food)

13. **Manual Testing**
    - Log activities from all 3 categories
    - Verify dashboard breakdown shows all 3 segments
    - Verify activity list displays all types correctly
    - Test on mobile viewport

14. **Update Documentation**
    - Add energy and food sections to README.md
    - Document emission factor sources
    - Add screenshots of new forms

## Test Requirements

### Backend Tests

**Integration Tests:**
- `test_create_energy_activity_electricity()` - Returns 201, correct CO2e
- `test_create_energy_activity_natural_gas()` - Returns 201, correct CO2e
- `test_create_food_activity_beef()` - Returns 201, correct CO2e
- `test_create_food_activity_vegan()` - Returns 201, correct CO2e
- `test_invalid_category()` - Returns 400 with validation error

### Frontend Tests

**Component Tests:**
- `EnergyForm.test.tsx` - Renders, validates, submits, shows CO2e preview
- `FoodForm.test.tsx` - Renders, validates, submits, shows CO2e preview
- `CategorySelector.test.tsx` - Switches categories correctly
- `ActivityCard.test.tsx` - Displays all category types correctly

**E2E Tests:**
- `energy-logging.spec.ts` - Log all 3 energy types, verify in dashboard
- `food-logging.spec.ts` - Log all 7 food types, verify in dashboard
- `multi-category.spec.ts` - Log activities from all categories, verify breakdown chart shows 3 segments

## Definition of Done

- [ ] Energy emission factors seeded (3 types)
- [ ] Food emission factors seeded (7 types)
- [ ] EnergyForm component created and functional
- [ ] FoodForm component created and functional
- [ ] CategorySelector component created and functional
- [ ] Dashboard integrates all 3 category forms
- [ ] Activity cards display all categories correctly
- [ ] Breakdown chart shows 3 segments (transport, energy, food)
- [ ] All backend tests pass (5 new integration tests)
- [ ] All frontend tests pass (4 component + 3 E2E tests)
- [ ] No TypeScript or Python errors
- [ ] Documentation updated with energy and food sections

## Out of Scope

- Energy bill upload/parsing (future: CT-006.1)
- Meal photo recognition (future: CT-006.2)
- Recipe carbon calculator (future: CT-006.3)
- Smart meter integration (future: CT-006.4)
- Food waste tracking (future: CT-006.5)
- Regional energy grid carbon intensity (use average for now)

## Related

- **Dependencies:** CT-000, CT-001
- **Enhances:** CT-003 (Dashboard shows all 3 categories)
- **Reuses:** LogActivityUseCase, CalculationService (no backend changes needed!)
- **Architecture:** Category-agnostic design pays off - minimal new code required
