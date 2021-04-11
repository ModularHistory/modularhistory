export default function BaseCard({module, cardClass, cardStyles, top, children}) {
  // BaseCard is extended by module-specific cards.
  // The code is mostly copied from the `_card.html` Django template.

  const isImage = module['model'] === 'images.Image';
  let bgImage;
  if (!isImage) {
    bgImage = module['serialized_images']?.[0];
  }

  return (
    <div className={`card m-2 ${cardClass || ""}`} style={cardStyles}>
      {top || module['verified'] || (
        <span style={{display: "inline-block", position: "absolute", top: "1px", right: "1px"}}>
          UNVERIFIED
        </span>
      )}

      {bgImage && (
        <div className="img-bg lazy-bg" data-img={bgImage['src_url']}
             style={{
               backgroundPosition: bgImage['bg_img_position'],
               backgroundImage: `url(${bgImage['src_url']})`
             }}>
        </div>
      )}

      <div className="card-body" style={{backgroundColor: "transparent", zIndex: "1"}}>
        {!isImage && module['date_html'] && (
          <p className="card-title text-center my-1">
            <small dangerouslySetInnerHTML={{__html: module['date_html']}}/>
          </p>
        )}

        {children}

      </div>
    </div>
  );
}
