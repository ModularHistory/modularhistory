import OccurrenceDetail from "./OccurrenceDetail";
import QuoteDetail from "./QuoteDetail";

export default function ModuleDetail({module}) {
  switch (module['model']) {
    case 'occurrences.occurrence':
      return <OccurrenceDetail occurrence={module} />;
    case 'quotes.quote':
      return <QuoteDetail quote={module} />;
    default:
      return <pre>{JSON.stringify(module)}</pre>
  }
}
