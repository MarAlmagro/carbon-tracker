import { useTranslation } from 'react-i18next';

interface PeriodSelectorProps {
  readonly value: string;
  readonly onChange: (period: string) => void;
  readonly options?: readonly string[];
}

const DEFAULT_PERIODS = ['day', 'week', 'month', 'year', 'all'] as const;

export function PeriodSelector({ value, onChange, options }: PeriodSelectorProps) {
  const { t } = useTranslation();
  const periods = options ?? DEFAULT_PERIODS;

  return (
    <div className="flex flex-wrap gap-1 border-b border-border pb-1">
      {periods.map((period) => (
        <button
          key={period}
          type="button"
          onClick={() => onChange(period)}
          className={`px-4 py-2 text-sm font-medium rounded-t-md transition-colors ${
            value === period
              ? 'border-b-2 border-primary text-primary bg-primary/5'
              : 'text-muted-foreground hover:text-foreground hover:bg-muted/50'
          }`}
        >
          {t(`dashboard.period.${period}`)}
        </button>
      ))}
    </div>
  );
}
