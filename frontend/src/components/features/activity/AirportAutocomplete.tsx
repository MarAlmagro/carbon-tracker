import { useState, useRef, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { Airport } from '@/services/api';
import { useAirportSearch } from '@/hooks/useAirportSearch';

interface AirportAutocompleteProps {
  readonly label: string;
  readonly value: Airport | null;
  readonly onChange: (airport: Airport | null) => void;
  readonly placeholder?: string;
  readonly error?: string;
  readonly required?: boolean;
  readonly dataTestId?: string;
}

export function AirportAutocomplete({
  label,
  value,
  onChange,
  placeholder,
  error,
  required = false,
  dataTestId = 'airport-autocomplete',
}: AirportAutocompleteProps) {
  const { t } = useTranslation();
  const [inputValue, setInputValue] = useState(value?.name || '');
  const [isOpen, setIsOpen] = useState(false);
  const wrapperRef = useRef<HTMLDivElement>(null);

  const { airports, isLoading } = useAirportSearch(inputValue);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (wrapperRef.current && !wrapperRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value;
    setInputValue(newValue);
    setIsOpen(true);

    // Clear selection if input doesn't match
    if (value && !newValue) {
      onChange(null);
    }
  };

  const handleSelectAirport = (airport: Airport) => {
    setInputValue(`${airport.name} (${airport.iata_code})`);
    onChange(airport);
    setIsOpen(false);
  };

  const handleFocus = () => {
    setIsOpen(true);
  };

  return (
    <div ref={wrapperRef} className="relative" data-testid={dataTestId}>
      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
        {label}
        {required && <span className="text-red-500 ml-1">*</span>}
      </label>

      <div className="relative">
        <input
          type="text"
          value={inputValue}
          onChange={handleInputChange}
          onFocus={handleFocus}
          placeholder={placeholder || t('activity.flight.searchAirport')}
          className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent dark:bg-gray-700 dark:text-white dark:border-gray-600 ${
            error ? 'border-red-500' : 'border-gray-300'
          }`}
          data-testid={`${dataTestId}-input`}
          autoComplete="off"
        />

        {isLoading && (
          <div className="absolute right-3 top-2.5">
            <div className="animate-spin h-5 w-5 border-2 border-green-500 border-t-transparent rounded-full" />
          </div>
        )}
      </div>

      {error && (
        <p className="mt-1 text-sm text-red-600 dark:text-red-400" data-testid={`${dataTestId}-error`}>
          {error}
        </p>
      )}

      {isOpen && airports.length > 0 && (
        <ul
          className="absolute z-10 w-full mt-1 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg shadow-lg max-h-60 overflow-auto"
          data-testid={`${dataTestId}-dropdown`}
        >
          {airports.map((airport) => (
            <li
              key={airport.iata_code}
              onClick={() => handleSelectAirport(airport)}
              className="px-3 py-2 hover:bg-gray-100 dark:hover:bg-gray-700 cursor-pointer transition-colors"
              data-testid={`${dataTestId}-option-${airport.iata_code}`}
            >
              <div className="flex items-center justify-between">
                <div>
                  <div className="font-medium text-gray-900 dark:text-white">
                    {airport.name}
                  </div>
                  <div className="text-sm text-gray-500 dark:text-gray-400">
                    {airport.city}, {airport.country}
                  </div>
                </div>
                <div className="text-sm font-mono bg-gray-200 dark:bg-gray-700 px-2 py-1 rounded">
                  {airport.iata_code}
                </div>
              </div>
            </li>
          ))}
        </ul>
      )}

      {isOpen && !isLoading && inputValue.length >= 2 && airports.length === 0 && (
        <div className="absolute z-10 w-full mt-1 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg shadow-lg p-3">
          <p className="text-sm text-gray-500 dark:text-gray-400 text-center">
            {t('activity.flight.noAirportsFound')}
          </p>
        </div>
      )}
    </div>
  );
}
