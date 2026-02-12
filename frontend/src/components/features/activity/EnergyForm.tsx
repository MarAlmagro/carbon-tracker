import { zodResolver } from '@hookform/resolvers/zod';
import { useForm } from 'react-hook-form';
import { useTranslation } from 'react-i18next';
import { z } from 'zod';
import { useCreateActivity, useEmissionFactors } from '@/hooks/useActivities';

const ENERGY_TYPES = ['electricity', 'natural_gas', 'heating_oil'] as const;

const energySchema = z.object({
  type: z.enum(ENERGY_TYPES),
  value: z.number().positive().max(100000),
  date: z.string(),
  notes: z.string().max(500).optional(),
});

type EnergyFormData = z.infer<typeof energySchema>;

interface EnergyFormProps {
  readonly onSuccess?: () => void;
}

export function EnergyForm({ onSuccess }: EnergyFormProps) {
  const { t } = useTranslation();
  const { data: emissionFactors, isLoading: factorsLoading } =
    useEmissionFactors('energy');
  const createActivity = useCreateActivity();

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors, isSubmitting },
    reset,
  } = useForm<EnergyFormData>({
    resolver: zodResolver(energySchema),
    defaultValues: {
      type: 'electricity',
      date: new Date().toISOString().split('T')[0],
      value: undefined,
      notes: '',
    },
  });

  const selectedType = watch('type');
  const selectedValue = watch('value');

  const onSubmit = async (data: EnergyFormData) => {
    try {
      await createActivity.mutateAsync({
        category: 'energy',
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

  const getEnergyIcon = (type: string) => {
    const icons: Record<string, string> = {
      electricity: '⚡',
      natural_gas: '🔥',
      heating_oil: '🛢️',
    };
    return icons[type] || '⚡';
  };

  const getUnitLabel = (type: string) => {
    if (type === 'heating_oil') {
      return t('activity.energy.units.liters');
    }
    return t('activity.energy.units.kwh');
  };

  // Calculate estimated CO2e
  const estimatedCo2e =
    selectedValue && emissionFactors
      ? selectedValue *
        (emissionFactors.find((f) => f.type === selectedType)?.factor || 0)
      : 0;

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div>
        <label htmlFor="energy-type" className="block text-sm font-medium mb-1">
          {t('activity.energy.type')}
        </label>
        <select
          id="energy-type"
          {...register('type')}
          className="w-full px-3 py-2 border rounded-md bg-background focus:outline-none focus:ring-2 focus:ring-primary"
          disabled={factorsLoading}
          data-testid="energy-type-select"
          aria-describedby={errors.type ? 'type-error' : undefined}
        >
          {ENERGY_TYPES.map((type) => (
            <option key={type} value={type}>
              {getEnergyIcon(type)} {t(`activity.energy.types.${type}`)}
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
        <label htmlFor="energy-amount" className="block text-sm font-medium mb-1">
          {t('activity.energy.amount')} ({getUnitLabel(selectedType)})
        </label>
        <input
          id="energy-amount"
          type="number"
          step="0.1"
          min="0"
          max="100000"
          {...register('value', { valueAsNumber: true })}
          className="w-full px-3 py-2 border rounded-md bg-background focus:outline-none focus:ring-2 focus:ring-primary"
          placeholder="350.0"
          data-testid="energy-amount-input"
          aria-describedby={errors.value ? 'value-error' : undefined}
        />
        {errors.value && (
          <p id="value-error" className="text-sm text-destructive mt-1" role="alert">
            {errors.value.message}
          </p>
        )}
      </div>

      <div>
        <label htmlFor="energy-date" className="block text-sm font-medium mb-1">
          {t('activity.date')}
        </label>
        <input
          id="energy-date"
          type="date"
          {...register('date')}
          className="w-full px-3 py-2 border rounded-md bg-background focus:outline-none focus:ring-2 focus:ring-primary"
          data-testid="energy-date-input"
          aria-describedby={errors.date ? 'date-error' : undefined}
        />
        {errors.date && (
          <p id="date-error" className="text-sm text-destructive mt-1" role="alert">
            {errors.date.message}
          </p>
        )}
      </div>

      <div>
        <label htmlFor="energy-notes" className="block text-sm font-medium mb-1">
          {t('activity.notes')}{' '}
          <span className="text-muted-foreground">({t('common.optional')})</span>
        </label>
        <input
          id="energy-notes"
          type="text"
          {...register('notes')}
          className="w-full px-3 py-2 border rounded-md bg-background focus:outline-none focus:ring-2 focus:ring-primary"
          placeholder={t('activity.notesPlaceholder')}
          data-testid="energy-notes-input"
          aria-describedby={errors.notes ? 'notes-error' : undefined}
        />
        {errors.notes && (
          <p id="notes-error" className="text-sm text-destructive mt-1" role="alert">
            {errors.notes.message}
          </p>
        )}
      </div>

      {selectedValue > 0 && estimatedCo2e > 0 && (
        <div className="bg-yellow-50 dark:bg-yellow-900/20 p-3 rounded-md">
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
          className="flex-1 px-4 py-2 bg-yellow-600 text-white rounded-md hover:bg-yellow-700 transition-colors disabled:opacity-50"
          data-testid="energy-submit-button"
        >
          {isSubmitting || createActivity.isPending
            ? t('common.loading')
            : t('activity.energy.logEnergy')}
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
