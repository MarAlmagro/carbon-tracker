import { useTranslation } from 'react-i18next';

interface CategorySelectorProps {
  value: string;
  onChange: (category: string) => void;
}

const CATEGORIES = ['transport', 'energy', 'food'] as const;

export default function CategorySelector({ value, onChange }: CategorySelectorProps) {
  const { t } = useTranslation();

  return (
    <div className="flex space-x-2 border-b border-gray-200 mb-6" data-testid="category-selector">
      {CATEGORIES.map((category) => (
        <button
          key={category}
          onClick={() => onChange(category)}
          data-testid={`category-tab-${category}`}
          className={`px-4 py-2 font-medium transition-colors ${
            value === category
              ? 'border-b-2 border-blue-600 text-blue-600'
              : 'text-gray-600 hover:text-gray-900'
          }`}
          aria-pressed={value === category}
          aria-label={t(`activity.categories.${category}`)}
        >
          {t(`activity.categories.${category}`)}
        </button>
      ))}
    </div>
  );
}
