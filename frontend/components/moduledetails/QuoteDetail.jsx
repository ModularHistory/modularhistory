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

  const firstImage = quote['serialized_images']?.[0];

  return (
    <div className="detail">
      <a className="edit-object-button float-right" target="_blank"
         href="{% url 'admin:quotes_quote_change' quote.pk %}">
        <i className="fa fa-edit"/>
      </a>

      <h2 className="text-center card-title"
          dangerouslySetInnerHTML={{
            __html: quote['attributee_html'] + (quote['date_html'] ? quote['date_html'] : "")
          }}
      />

      <div className="card-text">
        {firstImage && (
          <div className="img-container" style={{maxWidth: "44%"}}>
            {/*{{quote.serialized_images | first | get_html_for_view:"card"}}*/}
            {/* <ImageCard image={firstImage}/> */}
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
    </div>
  );
}