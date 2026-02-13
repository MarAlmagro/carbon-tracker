import { useTranslation } from 'react-i18next';
import { useDeleteActivity, type Activity } from '@/hooks/useActivities';

interface DeleteConfirmDialogProps {
  readonly activity: Activity;
  readonly isOpen: boolean;
  readonly onClose: () => void;
}

export function DeleteConfirmDialog({ activity, isOpen, onClose }: DeleteConfirmDialogProps) {
  const { t, i18n } = useTranslation();
  const deleteActivity = useDeleteActivity();

  const handleDelete = async () => {
    try {
      await deleteActivity.mutateAsync(activity.id);
      onClose();
    } catch (error) {
      console.error('Failed to delete activity:', error);
    }
  };

  if (!isOpen) return null;

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString(i18n.language, {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  const getTypeLabel = (category: string, type: string) => {
    const key = `activity.${category}.types.${type}`;
    const translated = t(key);
    return translated === key ? type.replaceAll('_', ' ') : translated;
  };

  const getUnitLabel = () => {
    if (activity.category === 'transport') {
      return 'km';
    } else if (activity.category === 'energy') {
      return activity.type === 'heating_oil' ? t('activity.energy.units.liters') : t('activity.energy.units.kwh');
    } else if (activity.category === 'food') {
      const count = activity.value;
      return count === 1 ? t('activity.food.serving') : t('activity.food.servings');
    }
    return '';
  };

  return (
    <div
      className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
      onClick={onClose}
      role="dialog"
      aria-modal="true"
      aria-labelledby="delete-modal-title"
    >
      <div
        className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-md w-full p-6"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between mb-4">
          <h2 id="delete-modal-title" className="text-xl font-semibold text-red-600 dark:text-red-400">
            {t('activity.deleteConfirmTitle')}
          </h2>
          <button
            type="button"
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
            aria-label={t('common.close')}
          >
            ✕
          </button>
        </div>

        <p className="text-gray-700 dark:text-gray-300 mb-4">
          {t('activity.deleteConfirmMessage')}
        </p>

        {/* Activity Summary */}
        <div className="bg-gray-50 dark:bg-gray-700 rounded-md p-4 mb-4">
          <p className="font-medium text-gray-900 dark:text-gray-100">
            {getTypeLabel(activity.category, activity.type)} - {activity.value} {getUnitLabel()}
          </p>
          <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
            {formatDate(activity.date)}
          </p>
          <p className="text-sm font-medium text-blue-600 dark:text-blue-400 mt-2">
            {activity.co2e_kg.toFixed(2)} kg CO2e
          </p>
        </div>

        {/* Error Message */}
        {deleteActivity.isError && (
          <div className="bg-red-50 dark:bg-red-900/20 p-3 rounded-md mb-4">
            <p className="text-sm text-red-900 dark:text-red-100">
              {t('activity.errorDeleting')}
            </p>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex gap-3">
          <button
            type="button"
            onClick={onClose}
            className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md hover:bg-gray-50 dark:hover:bg-gray-700"
            disabled={deleteActivity.isPending}
          >
            {t('common.cancel')}
          </button>
          <button
            type="button"
            onClick={handleDelete}
            className="flex-1 px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 disabled:opacity-50"
            disabled={deleteActivity.isPending}
            data-testid="confirm-delete-button"
          >
            {deleteActivity.isPending ? t('common.loading') : t('common.delete')}
          </button>
        </div>
      </div>
    </div>
  );
}
