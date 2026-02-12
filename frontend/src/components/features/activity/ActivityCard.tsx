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
      flight_domestic_short: '✈️',
      flight_domestic_medium: '✈️',
      flight_domestic_long: '✈️',
      flight_international_short: '✈️',
      flight_international_medium: '✈️',
      flight_international_long: '✈️',
    };
    return icons[type] || '📊';
  };

  const isFlightType = (type: string) => {
    return type.startsWith('flight_');
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

  const renderFlightInfo = () => {
    if (!isFlightType(activity.type) || !activity.metadata) {
      return null;
    }

    const { origin_iata, origin_city, destination_iata, destination_city } =
      activity.metadata as {
        origin_iata?: string;
        origin_city?: string;
        destination_iata?: string;
        destination_city?: string;
      };

    if (!origin_iata || !destination_iata) {
      return null;
    }

    return (
      <div className="mt-2 pl-11 text-sm text-muted-foreground">
        <span className="font-mono bg-gray-100 dark:bg-gray-800 px-2 py-0.5 rounded">
          {origin_iata}
        </span>
        {origin_city && (
          <span className="ml-1">({origin_city})</span>
        )}
        <span className="mx-2">→</span>
        <span className="font-mono bg-gray-100 dark:bg-gray-800 px-2 py-0.5 rounded">
          {destination_iata}
        </span>
        {destination_city && (
          <span className="ml-1">({destination_city})</span>
        )}
      </div>
    );
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
              {isFlightType(activity.type)
                ? t('activity.flight.label')
                : getTypeLabel(activity.category, activity.type)}{' '}
              -{' '}
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
      {renderFlightInfo()}
      {activity.notes && (
        <p className="mt-2 text-sm text-muted-foreground pl-11">
          {activity.notes}
        </p>
      )}
    </li>
  );
}
