import { useState } from 'react';
import { zodResolver } from '@hookform/resolvers/zod';
import { useForm } from 'react-hook-form';
import { useTranslation } from 'react-i18next';
import { z } from 'zod';
import { useCreateActivity, useEmissionFactors } from '@/hooks/useActivities';
import { FlightForm } from './FlightForm';

const TRANSPORT_TYPES = [
  'car_petrol',
  'car_diesel',
  'car_electric',
  'bus',
  'train',
  'bike',
  'walk',
] as const;

const transportSchema = z.object({
  type: z.enum(TRANSPORT_TYPES),
  value: z.number().positive().max(10000),
  date: z.string(),
  notes: z.string().max(500).optional(),
});

type TransportFormData = z.infer<typeof transportSchema>;

interface TransportFormProps {
  readonly onSuccess?: () => void;
}

type TransportMode = 'ground' | 'flight';

export function TransportForm({ onSuccess }: TransportFormProps) {
  const { t } = useTranslation();
  const { isLoading: factorsLoading } = useEmissionFactors('transport');
  const createActivity = useCreateActivity();
  const [mode, setMode] = useState<TransportMode>('ground');

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    reset,
  } = useForm<TransportFormData>({
    resolver: zodResolver(transportSchema),
    defaultValues: {
      type: 'car_petrol',
      date: new Date().toISOString().split('T')[0],
      value: undefined,
      notes: '',
    },
  });

  const onSubmit = async (data: TransportFormData) => {
    try {
      await createActivity.mutateAsync({
        category: 'transport',
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

  const getTransportIcon = (type: string) => {
    const icons: Record<string, string> = {
      car_petrol: '🚗',
      car_diesel: '🚗',
      car_electric: '⚡🚗',
      bus: '🚌',
      train: '🚆',
      bike: '🚲',
      walk: '🚶',
    };
    return icons[type] || '🚗';
  };

  return (
    <div className="space-y-4">
      {/* Mode Tabs */}
      <div className="flex gap-2 p-1 bg-gray-100 dark:bg-gray-800 rounded-lg">
        <button
          type="button"
          onClick={() => setMode('ground')}
          className={`flex-1 px-4 py-2 rounded-md transition-colors font-medium ${
            mode === 'ground'
              ? 'bg-white dark:bg-gray-700 text-green-600 dark:text-green-400 shadow-sm'
              : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
          }`}
          data-testid="ground-transport-tab"
        >
          🚗 {t('activity.transport.ground')}
        </button>
        <button
          type="button"
          onClick={() => setMode('flight')}
          className={`flex-1 px-4 py-2 rounded-md transition-colors font-medium ${
            mode === 'flight'
              ? 'bg-white dark:bg-gray-700 text-green-600 dark:text-green-400 shadow-sm'
              : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
          }`}
          data-testid="flight-transport-tab"
        >
          ✈️ {t('activity.transport.flight')}
        </button>
      </div>

      {/* Ground Transport Form */}
      {mode === 'ground' && (
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div>
            <label
              htmlFor="transport-type"
              className="block text-sm font-medium mb-1"
            >
              {t('activity.type')}
            </label>
            <select
              id="transport-type"
              {...register('type')}
              className="w-full px-3 py-2 border rounded-md bg-background focus:outline-none focus:ring-2 focus:ring-primary"
              disabled={factorsLoading}
              aria-describedby={errors.type ? 'type-error' : undefined}
            >
              {TRANSPORT_TYPES.map((type) => (
                <option key={type} value={type}>
                  {getTransportIcon(type)} {t(`activity.transport.types.${type}`)}
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
            <label
              htmlFor="transport-distance"
              className="block text-sm font-medium mb-1"
            >
              {t('activity.transport.distance')}
            </label>
            <input
              id="transport-distance"
              type="number"
              step="0.1"
              min="0"
              max="10000"
              {...register('value', { valueAsNumber: true })}
              className="w-full px-3 py-2 border rounded-md bg-background focus:outline-none focus:ring-2 focus:ring-primary"
              placeholder="25.5"
              aria-describedby={errors.value ? 'value-error' : undefined}
            />
            {errors.value && (
              <p id="value-error" className="text-sm text-destructive mt-1" role="alert">
                {errors.value.message}
              </p>
            )}
          </div>

          <div>
            <label
              htmlFor="transport-date"
              className="block text-sm font-medium mb-1"
            >
              {t('activity.date')}
            </label>
            <input
              id="transport-date"
              type="date"
              {...register('date')}
              className="w-full px-3 py-2 border rounded-md bg-background focus:outline-none focus:ring-2 focus:ring-primary"
              aria-describedby={errors.date ? 'date-error' : undefined}
            />
            {errors.date && (
              <p id="date-error" className="text-sm text-destructive mt-1" role="alert">
                {errors.date.message}
              </p>
            )}
          </div>

          <div>
            <label
              htmlFor="transport-notes"
              className="block text-sm font-medium mb-1"
            >
              {t('activity.notes')}{' '}
              <span className="text-muted-foreground">({t('common.optional')})</span>
            </label>
            <input
              id="transport-notes"
              type="text"
              {...register('notes')}
              className="w-full px-3 py-2 border rounded-md bg-background focus:outline-none focus:ring-2 focus:ring-primary"
              placeholder={t('activity.notesPlaceholder')}
              aria-describedby={errors.notes ? 'notes-error' : undefined}
            />
            {errors.notes && (
              <p id="notes-error" className="text-sm text-destructive mt-1" role="alert">
                {errors.notes.message}
              </p>
            )}
          </div>

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
              className="flex-1 px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors disabled:opacity-50"
            >
              {isSubmitting || createActivity.isPending
                ? t('common.loading')
                : t('activity.log')}
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
      )}

      {/* Flight Form */}
      {mode === 'flight' && <FlightForm onSuccess={onSuccess} />}
    </div>
  );
}
