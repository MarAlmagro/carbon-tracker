import { useState, useEffect } from 'react';
import { zodResolver } from '@hookform/resolvers/zod';
import { useForm, Controller } from 'react-hook-form';
import { useTranslation } from 'react-i18next';
import { z } from 'zod';
import { useCreateActivity } from '@/hooks/useActivities';
import { Airport, apiClient, FlightCalculation } from '@/services/api';
import { AirportAutocomplete } from './AirportAutocomplete';

const flightSchema = z.object({
  origin: z.custom<Airport>((val) => val !== null, {
    message: 'Origin airport is required',
  }),
  destination: z.custom<Airport>((val) => val !== null, {
    message: 'Destination airport is required',
  }),
  date: z.string(),
  notes: z.string().max(500).optional(),
});

type FlightFormData = z.infer<typeof flightSchema>;

interface FlightFormProps {
  readonly onSuccess?: () => void;
}

export function FlightForm({ onSuccess }: FlightFormProps) {
  const { t } = useTranslation();
  const createActivity = useCreateActivity();
  const [flightCalc, setFlightCalc] = useState<FlightCalculation | null>(null);
  const [isCalculating, setIsCalculating] = useState(false);

  const {
    control,
    handleSubmit,
    watch,
    formState: { errors, isSubmitting },
    reset,
    register,
  } = useForm<FlightFormData>({
    resolver: zodResolver(flightSchema),
    defaultValues: {
      origin: null,
      destination: null,
      date: new Date().toISOString().split('T')[0],
      notes: '',
    },
  });

  const origin = watch('origin');
  const destination = watch('destination');

  // Calculate flight when both airports are selected
  useEffect(() => {
    const calculateFlight = async () => {
      if (!origin || !destination) {
        setFlightCalc(null);
        return;
      }

      setIsCalculating(true);
      try {
        const result = await apiClient.calculateFlight({
          origin_iata: origin.iata_code,
          destination_iata: destination.iata_code,
        });
        setFlightCalc(result);
      } catch (error) {
        console.error('Failed to calculate flight:', error);
        setFlightCalc(null);
      } finally {
        setIsCalculating(false);
      }
    };

    calculateFlight();
  }, [origin, destination]);

  const onSubmit = async (data: FlightFormData) => {
    if (!flightCalc) {
      return;
    }

    try {
      await createActivity.mutateAsync({
        category: 'transport',
        type: flightCalc.flight_type,
        value: flightCalc.distance_km,
        date: data.date,
        notes: data.notes || undefined,
        metadata: {
          origin_iata: data.origin.iata_code,
          origin_name: data.origin.name,
          origin_city: data.origin.city,
          destination_iata: data.destination.iata_code,
          destination_name: data.destination.name,
          destination_city: data.destination.city,
          distance_km: flightCalc.distance_km,
          flight_type: flightCalc.flight_type,
          is_domestic: flightCalc.is_domestic,
        },
      });
      reset();
      setFlightCalc(null);
      onSuccess?.();
    } catch (error) {
      console.error('Failed to create flight activity:', error);
    }
  };

  const getHaulTypeLabel = (haulType: string) => {
    const labels: Record<string, string> = {
      short: t('activity.flight.shortHaul'),
      medium: t('activity.flight.mediumHaul'),
      long: t('activity.flight.longHaul'),
    };
    return labels[haulType] || haulType;
  };

  return (
    <form
      onSubmit={handleSubmit(onSubmit)}
      className="space-y-4"
      data-testid="flight-form"
    >
      <Controller
        name="origin"
        control={control}
        render={({ field }) => (
          <AirportAutocomplete
            label={t('activity.flight.origin')}
            value={field.value}
            onChange={field.onChange}
            placeholder={t('activity.flight.searchOrigin')}
            error={errors.origin?.message}
            required
            dataTestId="origin-airport"
          />
        )}
      />

      <Controller
        name="destination"
        control={control}
        render={({ field }) => (
          <AirportAutocomplete
            label={t('activity.flight.destination')}
            value={field.value}
            onChange={field.onChange}
            placeholder={t('activity.flight.searchDestination')}
            error={errors.destination?.message}
            required
            dataTestId="destination-airport"
          />
        )}
      />

      {isCalculating && (
        <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
          <p className="text-sm text-blue-700 dark:text-blue-300">
            {t('activity.flight.calculating')}
          </p>
        </div>
      )}

      {flightCalc && !isCalculating && (
        <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4 space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
              {t('activity.flight.distance')}:
            </span>
            <span className="text-sm font-bold text-green-700 dark:text-green-300">
              {Math.round(flightCalc.distance_km).toLocaleString()} km
            </span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
              {t('activity.flight.type')}:
            </span>
            <span className="text-sm text-gray-600 dark:text-gray-400">
              {flightCalc.is_domestic
                ? t('activity.flight.domestic')
                : t('activity.flight.international')}{' '}
              • {getHaulTypeLabel(flightCalc.haul_type)}
            </span>
          </div>
        </div>
      )}

      <div>
        <label
          htmlFor="date"
          className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
        >
          {t('activity.date')} <span className="text-red-500">*</span>
        </label>
        <input
          type="date"
          id="date"
          {...register('date')}
          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
          data-testid="flight-date"
        />
        {errors.date && (
          <p className="mt-1 text-sm text-red-600 dark:text-red-400">
            {errors.date.message}
          </p>
        )}
      </div>

      <div>
        <label
          htmlFor="notes"
          className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
        >
          {t('activity.notes')}
        </label>
        <textarea
          id="notes"
          {...register('notes')}
          rows={3}
          placeholder={t('activity.notesPlaceholder')}
          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent dark:bg-gray-700 dark:text-white resize-none"
          data-testid="flight-notes"
        />
        {errors.notes && (
          <p className="mt-1 text-sm text-red-600 dark:text-red-400">
            {errors.notes.message}
          </p>
        )}
      </div>

      <button
        type="submit"
        disabled={isSubmitting || !flightCalc || isCalculating}
        className="w-full bg-green-600 text-white py-3 px-4 rounded-lg hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors font-medium"
        data-testid="flight-submit"
      >
        {isSubmitting ? t('activity.logging') : t('activity.logActivity')}
      </button>
    </form>
  );
}
