import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import { ArrowRight, BarChart3, Leaf, TrendingDown } from 'lucide-react';

export function HomePage() {
  const { t } = useTranslation();

  return (
    <div className="max-w-4xl mx-auto">
      <div className="text-center py-12">
        <h1 className="text-4xl font-bold mb-4">
          {t('home.title', 'Track Your Carbon Footprint')}
        </h1>
        <p className="text-xl text-muted-foreground mb-8">
          {t(
            'home.subtitle',
            'Understand and reduce your environmental impact through daily activity tracking'
          )}
        </p>
        <Link
          to="/dashboard"
          className="inline-flex items-center gap-2 bg-primary text-primary-foreground px-6 py-3 rounded-md font-medium hover:bg-primary/90 transition-colors"
        >
          {t('home.getStarted', 'Get Started')}
          <ArrowRight className="w-4 h-4" />
        </Link>
      </div>

      <div className="grid md:grid-cols-3 gap-8 mt-16">
        <div className="text-center p-6">
          <div className="w-12 h-12 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
            <Leaf className="w-6 h-6 text-primary" />
          </div>
          <h3 className="font-semibold mb-2">
            {t('home.features.track', 'Track Activities')}
          </h3>
          <p className="text-sm text-muted-foreground">
            {t(
              'home.features.trackDesc',
              'Log transport, energy, and food activities'
            )}
          </p>
        </div>

        <div className="text-center p-6">
          <div className="w-12 h-12 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
            <BarChart3 className="w-6 h-6 text-primary" />
          </div>
          <h3 className="font-semibold mb-2">
            {t('home.features.visualize', 'Visualize Data')}
          </h3>
          <p className="text-sm text-muted-foreground">
            {t(
              'home.features.visualizeDesc',
              'See your carbon footprint trends over time'
            )}
          </p>
        </div>

        <div className="text-center p-6">
          <div className="w-12 h-12 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
            <TrendingDown className="w-6 h-6 text-primary" />
          </div>
          <h3 className="font-semibold mb-2">
            {t('home.features.reduce', 'Reduce Impact')}
          </h3>
          <p className="text-sm text-muted-foreground">
            {t(
              'home.features.reduceDesc',
              'Get insights to lower your emissions'
            )}
          </p>
        </div>
      </div>
    </div>
  );
}
