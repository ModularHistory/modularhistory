import BaseCard from "./BaseCard";

export default function QuoteCard({quote, ...childProps}) {
  return (
    <BaseCard module={quote} {...childProps}>
      <div className="card-text">
        <blockquote className="blockquote">
          <div dangerouslySetInnerHTML={{__html: quote["truncated_html"]}}/>
          <footer className="blockquote-footer"
                  dangerouslySetInnerHTML={{__html: quote["attributee_string"]}}/>
        </blockquote>
      </div>
    </BaseCard>
  );
}
