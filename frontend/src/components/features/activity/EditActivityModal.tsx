import { useEffect } from 'react';
import { zodResolver } from '@hookform/resolvers/zod';
import { useForm } from 'react-hook-form';
import { useTranslation } from 'react-i18next';
import { z } from 'zod';
import { useUpdateActivity, useEmissionFactors, type Activity } from '@/hooks/useActivities';

const editActivitySchema = z.object({
  type: z.string().min(1).max(100),
  value: z.number().positive().max(100000),
  date: z.string(),
  notes: z.string().max(500).optional(),
});

type EditActivityFormData = z.infer<typeof editActivitySchema>;

interface EditActivityModalProps {
  readonly activity: Activity;
  readonly isOpen: boolean;
  readonly onClose: () => void;
}

export function EditActivityModal({ activity, isOpen, onClose }: EditActivityModalProps) {
  const { t } = useTranslation();
  const updateActivity = useUpdateActivity();
  const { data: emissionFactors } = useEmissionFactors(activity.category);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    reset,
    watch,
  } = useForm<EditActivityFormData>({
    resolver: zodResolver(editActivitySchema),
    defaultValues: {
      type: activity.type,
      value: activity.value,
      date: activity.date,
      notes: activity.notes || '',
    },
  });

  // Reset form when activity changes
  useEffect(() => {
    reset({
      type: activity.type,
      value: activity.value,
      date: activity.date,
      notes: activity.notes || '',
    });
  }, [activity, reset]);

  const selectedType = watch('type');
  const selectedValue = watch('value');

  // Calculate preview CO2e
  const previewCO2e = (() => {
    const factor = emissionFactors?.find((f) => f.type === selectedType);
    if (!factor || !selectedValue) return null;
    return (selectedValue * factor.factor).toFixed(2);
  })();

  const onSubmit = async (data: EditActivityFormData) => {
    try {
      await updateActivity.mutateAsync({
        id: activity.id,
        input: {
          type: data.type,
          value: data.value,
          date: data.date,
          notes: data.notes || undefined,
        },
      });
      onClose();
    } catch (error) {
      console.error('Failed to update activity:', error);
    }
  };

  const handleClose = () => {
    reset();
    onClose();
  };

  if (!isOpen) return null;

  const categoryTypes = emissionFactors?.filter((f) => f.category === activity.category) || [];

  const getTypeLabel = (type: string) => {
    const key = `activity.${activity.category}.types.${type}`;
    const translated = t(key);
    return translated === key ? type.replaceAll('_', ' ') : translated;
  };

  const getUnitLabel = () => {
    if (activity.category === 'transport') {
      return 'km';
    } else if (activity.category === 'energy') {
      return selectedType === 'heating_oil' ? t('activity.energy.units.liters') : t('activity.energy.units.kwh');
    } else if (activity.category === 'food') {
      return t('activity.food.servings');
    }
    return '';
  };

  return (
    <div
      className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
      onClick={handleClose}
      role="dialog"
      aria-modal="true"
      aria-labelledby="edit-modal-title"
    >
      <div
        className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-md w-full p-6"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between mb-4">
          <h2 id="edit-modal-title" className="text-xl font-semibold">
            {t('activity.editActivity')}
          </h2>
          <button
            type="button"
            onClick={handleClose}
            className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
            aria-label={t('common.close')}
          >
            ✕
          </button>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          {/* Type Selection */}
          <div>
            <label htmlFor="type" className="block text-sm font-medium mb-1">
              {t('activity.type')}
            </label>
            <select
              id="type"
              {...register('type')}
              className="w-full px-3 py-2 border rounded-md dark:bg-gray-700 dark:border-gray-600"
              data-testid="edit-type-select"
            >
              {categoryTypes.map((factor) => (
                <option key={factor.type} value={factor.type}>
                  {getTypeLabel(factor.type)}
                </option>
              ))}
            </select>
            {errors.type && (
              <p className="text-sm text-red-600 mt-1">{errors.type.message}</p>
            )}
          </div>

          {/* Value Input */}
          <div>
            <label htmlFor="value" className="block text-sm font-medium mb-1">
              {t('activity.value')} ({getUnitLabel()})
            </label>
            <input
              id="value"
              type="number"
              step="0.1"
              {...register('value', { valueAsNumber: true })}
              className="w-full px-3 py-2 border rounded-md dark:bg-gray-700 dark:border-gray-600"
              data-testid="edit-value-input"
            />
            {errors.value && (
              <p className="text-sm text-red-600 mt-1">{errors.value.message}</p>
            )}
          </div>

          {/* Date Input */}
          <div>
            <label htmlFor="date" className="block text-sm font-medium mb-1">
              {t('activity.date')}
            </label>
            <input
              id="date"
              type="date"
              {...register('date')}
              className="w-full px-3 py-2 border rounded-md dark:bg-gray-700 dark:border-gray-600"
              data-testid="edit-date-input"
            />
            {errors.date && (
              <p className="text-sm text-red-600 mt-1">{errors.date.message}</p>
            )}
          </div>

          {/* Notes Input */}
          <div>
            <label htmlFor="notes" className="block text-sm font-medium mb-1">
              {t('activity.notes')}
            </label>
            <textarea
              id="notes"
              {...register('notes')}
              rows={3}
              placeholder={t('activity.notesPlaceholder')}
              className="w-full px-3 py-2 border rounded-md dark:bg-gray-700 dark:border-gray-600"
              data-testid="edit-notes-input"
            />
            {errors.notes && (
              <p className="text-sm text-red-600 mt-1">{errors.notes.message}</p>
            )}
          </div>

          {/* Preview CO2e */}
          {previewCO2e && (
            <div className="bg-blue-50 dark:bg-blue-900/20 p-3 rounded-md">
              <p className="text-sm text-blue-900 dark:text-blue-100">
                <span className="font-medium">New CO2e:</span> {previewCO2e} kg
              </p>
            </div>
          )}

          {/* Error Message */}
          {updateActivity.isError && (
            <div className="bg-red-50 dark:bg-red-900/20 p-3 rounded-md">
              <p className="text-sm text-red-900 dark:text-red-100">
                {t('activity.errorUpdating')}
              </p>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex gap-3 pt-2">
            <button
              type="button"
              onClick={handleClose}
              className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md hover:bg-gray-50 dark:hover:bg-gray-700"
              disabled={isSubmitting}
            >
              {t('common.cancel')}
            </button>
            <button
              type="submit"
              className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
              disabled={isSubmitting}
              data-testid="save-changes-button"
            >
              {isSubmitting ? t('activity.editing') : t('activity.saveChanges')}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
