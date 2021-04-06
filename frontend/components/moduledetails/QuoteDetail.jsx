import ImageCard from "../modulecards/ImageCard";

export default function QuoteDetail({quote}) {
  const superUserEditButton = (
    // TODO: implement condition render with NextAuth's useSession()
    undefined
    // {% if request.user.is_superuser %}
    //   <a className="edit-object-button float-right" style="margin-left: 1rem;"
    //   target="_blank" rel="noopener noreferrer" href="{{ quote|get_admin_url }}">
    //   <i className="fa fa-edit"></i>
    //   </a>
    // {% endif %}
  );

  let titleHtml = quote['attributee_html'];
  if (quote['date_html']) titleHtml += `, ${quote['date_html']}`;

  const firstImage = quote['serialized_images']?.[0];

  return (
    <>
      <a className="edit-object-button float-right" target="_blank"
         href="{% url 'admin:quotes_quote_change' quote.pk %}">
        <i className="fa fa-edit"/>
      </a>

      <h2 className="text-center card-title"
          dangerouslySetInnerHTML={{__html: titleHtml}}
      />

      <div className="card-text">
        {firstImage && (
          <div className="img-container" style={{maxWidth: "44%"}}>
            <ImageCard image={firstImage}/>
          </div>
        )}

        {superUserEditButton}
        <div dangerouslySetInnerHTML={{__html: quote['html']}}/>
        {superUserEditButton}

        {quote['tags_html'] && (
          <ul className="tags" dangerouslySetInnerHTML={{__html: quote['tags_html']}}/>
        )}

        <footer className="footer sources-footer">

          <ol className="citations">
            {quote['serialized_citations'].map((citation) => (
              <li className="source" id={`citation-${citation['pk']}`}
                  dangerouslySetInnerHTML={{__html: citation['html']}}/>
            ))}
          </ol>

        </footer>
      </div>
    </>
  );
}