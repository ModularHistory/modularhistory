import BaseCard from "./BaseCard";

export default function ImageCard({image, ...childProps}) {
  // Mostly copied from `apps/images/templates/images/_card.html`
  const cardClass = "image-card";
  const cardStyles = {maxWidth: `${image["width"]}px`}

  const topStyles = {
    maxWidth: image["width"],
    maxHeight: image["height"],
  }
  const top = (
    <div className="view overlay" style={topStyles} {...childProps}>
      {/* TODO: add "alt" tag to img element */}
      <img className="card-img-top lazy"
           src={image['src_url']} />
      <a href="#" onClick={(e) => e.preventDefault()}>
        <div className="mask rgba-white-slight"/>
      </a>
    </div>
  );

  return (
    <BaseCard module={image} cardClass={cardClass} cardStyles={cardStyles} top={top}>
      {image['caption_html'] && (
        <div className="card-text">
          <div dangerouslySetInnerHTML={{__html: image['caption_html']}}/>
          {image['provider_string'] && (
            <div className="image-credit float-right">
              <p>
                {image['provider_string']}
              </p>
            </div>
          )}
        </div>
      )}
    </BaseCard>
  );
}
