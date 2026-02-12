import { zodResolver } from '@hookform/resolvers/zod';
import { useForm } from 'react-hook-form';
import { useTranslation } from 'react-i18next';
import { z } from 'zod';
import { useCreateActivity, useEmissionFactors } from '@/hooks/useActivities';

const FOOD_TYPES = [
  'beef',
  'pork',
  'poultry',
  'fish',
  'dairy',
  'vegetables',
  'vegan_meal',
] as const;

const foodSchema = z.object({
  type: z.enum(FOOD_TYPES),
  value: z.number().positive().int().max(100),
  date: z.string(),
  notes: z.string().max(500).optional(),
});

type FoodFormData = z.infer<typeof foodSchema>;

interface FoodFormProps {
  readonly onSuccess?: () => void;
}

export function FoodForm({ onSuccess }: FoodFormProps) {
  const { t } = useTranslation();
  const { data: emissionFactors, isLoading: factorsLoading } =
    useEmissionFactors('food');
  const createActivity = useCreateActivity();

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors, isSubmitting },
    reset,
  } = useForm<FoodFormData>({
    resolver: zodResolver(foodSchema),
    defaultValues: {
      type: 'beef',
      date: new Date().toISOString().split('T')[0],
      value: 1,
      notes: '',
    },
  });

  const selectedType = watch('type');
  const selectedServings = watch('value');

  const onSubmit = async (data: FoodFormData) => {
    try {
      await createActivity.mutateAsync({
        category: 'food',
        type: data.type,
        value: data.value,
        date: data.date,
        notes: data.notes || undefined,
      });
      reset();
      onSuccess?.();
    } catch (error) {
      console.error('Failed to create activity:', error);
    }
  };

  const getFoodIcon = (type: string) => {
    const icons: Record<string, string> = {
      beef: '🥩',
      pork: '🥓',
      poultry: '🍗',
      fish: '🐟',
      dairy: '🥛',
      vegetables: '🥗',
      vegan_meal: '🌱',
    };
    return icons[type] || '🍽️';
  };

  // Calculate estimated CO2e
  const estimatedCo2e =
    selectedServings && emissionFactors
      ? selectedServings *
        (emissionFactors.find((f) => f.type === selectedType)?.factor || 0)
      : 0;

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div>
        <label htmlFor="food-type" className="block text-sm font-medium mb-1">
          {t('activity.food.type')}
        </label>
        <select
          id="food-type"
          {...register('type')}
          className="w-full px-3 py-2 border rounded-md bg-background focus:outline-none focus:ring-2 focus:ring-primary"
          disabled={factorsLoading}
          data-testid="food-type-select"
          aria-describedby={errors.type ? 'type-error' : undefined}
        >
          {FOOD_TYPES.map((type) => (
            <option key={type} value={type}>
              {getFoodIcon(type)} {t(`activity.food.types.${type}`)}
            </option>
          ))}
        </select>
        {errors.type && (
          <p id="type-error" className="text-sm text-destructive mt-1" role="alert">
            {errors.type.message}
          </p>
        )}
      </div>

      <div>
        <label htmlFor="food-servings" className="block text-sm font-medium mb-1">
          {t('activity.food.servings')}
        </label>
        <input
          id="food-servings"
          type="number"
          step="1"
          min="1"
          max="100"
          {...register('value', { valueAsNumber: true })}
          className="w-full px-3 py-2 border rounded-md bg-background focus:outline-none focus:ring-2 focus:ring-primary"
          placeholder="1"
          data-testid="food-servings-input"
          aria-describedby={errors.value ? 'value-error' : undefined}
        />
        {errors.value && (
          <p id="value-error" className="text-sm text-destructive mt-1" role="alert">
            {errors.value.message}
          </p>
        )}
      </div>

      <div>
        <label htmlFor="food-date" className="block text-sm font-medium mb-1">
          {t('activity.date')}
        </label>
        <input
          id="food-date"
          type="date"
          {...register('date')}
          className="w-full px-3 py-2 border rounded-md bg-background focus:outline-none focus:ring-2 focus:ring-primary"
          data-testid="food-date-input"
          aria-describedby={errors.date ? 'date-error' : undefined}
        />
        {errors.date && (
          <p id="date-error" className="text-sm text-destructive mt-1" role="alert">
            {errors.date.message}
          </p>
        )}
      </div>

      <div>
        <label htmlFor="food-notes" className="block text-sm font-medium mb-1">
          {t('activity.notes')}{' '}
          <span className="text-muted-foreground">({t('common.optional')})</span>
        </label>
        <input
          id="food-notes"
          type="text"
          {...register('notes')}
          className="w-full px-3 py-2 border rounded-md bg-background focus:outline-none focus:ring-2 focus:ring-primary"
          placeholder={t('activity.notesPlaceholder')}
          data-testid="food-notes-input"
          aria-describedby={errors.notes ? 'notes-error' : undefined}
        />
        {errors.notes && (
          <p id="notes-error" className="text-sm text-destructive mt-1" role="alert">
            {errors.notes.message}
          </p>
        )}
      </div>

      {selectedServings > 0 && estimatedCo2e > 0 && (
        <div className="bg-green-50 dark:bg-green-900/20 p-3 rounded-md">
          <div className="text-sm text-gray-700 dark:text-gray-300">
            {t('activity.estimatedCo2e')}: <strong>{estimatedCo2e.toFixed(2)} kg CO2e</strong>
          </div>
        </div>
      )}

      <div className="flex gap-2 pt-2">
        <button
          type="button"
          onClick={() => reset()}
          className="flex-1 px-4 py-2 border rounded-md hover:bg-muted transition-colors"
        >
          {t('common.cancel')}
        </button>
        <button
          type="submit"
          disabled={isSubmitting || createActivity.isPending}
          className="flex-1 px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors disabled:opacity-50"
          data-testid="food-submit-button"
        >
          {isSubmitting || createActivity.isPending
            ? t('common.loading')
            : t('activity.food.logFood')}
        </button>
      </div>

      {createActivity.isError && (
        <p className="text-sm text-destructive text-center" role="alert">
          {t('errors.generic')}
        </p>
      )}

      {createActivity.isSuccess && (
        <output className="text-sm text-primary text-center block">
          {t('activity.logged')}
        </output>
      )}
    </form>
  );
}
