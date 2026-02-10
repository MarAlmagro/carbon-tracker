import { useTranslation } from 'react-i18next';
import type { Activity } from '@/hooks/useActivities';

interface ActivityCardProps {
  readonly activity: Activity;
}

export function ActivityCard({ activity }: ActivityCardProps) {
  const { t, i18n } = useTranslation();

  const getTransportIcon = (type: string) => {
    const icons: Record<string, string> = {
      car_petrol: '🚗',
      car_diesel: '🚗',
      car_electric: '⚡🚗',
      bus: '🚌',
      train: '🚆',
      bike: '🚲',
      walk: '🚶',
      plane_domestic: '✈️',
      plane_international: '✈️',
    };
    return icons[type] || '📊';
  };

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

  const getUnitLabel = (category: string) => {
    switch (category) {
      case 'transport':
        return 'km';
      case 'energy':
        return 'kWh';
      case 'food':
        return t('activity.food.servings', 'servings');
      default:
        return '';
    }
  };

  return (
    <li
      className="p-4 border rounded-lg bg-card hover:bg-muted/50 transition-colors list-none"
    >
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-3">
          <span className="text-2xl" aria-hidden="true">
            {getTransportIcon(activity.type)}
          </span>
          <div>
            <p className="font-medium">
              {getTypeLabel(activity.category, activity.type)} -{' '}
              {activity.value} {getUnitLabel(activity.category)}
            </p>
            <p className="text-sm text-muted-foreground">
              <span className="font-medium text-primary">
                {activity.co2e_kg.toFixed(2)} kg CO2e
              </span>
              {' | '}
              {formatDate(activity.date)}
            </p>
          </div>
        </div>
      </div>
      {activity.notes && (
        <p className="mt-2 text-sm text-muted-foreground pl-11">
          {activity.notes}
        </p>
      )}
    </li>
  );
}
