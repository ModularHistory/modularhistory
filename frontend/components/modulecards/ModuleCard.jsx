import OccurrenceCard from "./OccurrenceCard";
import QuoteCard from "./QuoteCard";

export default function ModuleCard({module}) {
  switch (module['model']) {
    case 'occurrences.occurrence':
      return <OccurrenceCard occurrence={module}/>
    case 'quotes.quote':
      return <QuoteCard quote={module}/>
    default:
      return <pre>{JSON.stringify(module, null, 2)}</pre>
  }
}