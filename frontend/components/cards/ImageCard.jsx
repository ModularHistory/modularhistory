import ModuleCard from "./ModuleCard";

export default function ImageCard({ image, ...childProps }) {
  const cardClass = "image-card";
  const cardStyles = { maxWidth: `${image["width"]}px` };
  return (
    <ModuleCard
      module={image}
      cardClass={cardClass}
      cardStyles={cardStyles}
      content={
        image["captionHtml"] && (
          <div className="card-text">
            <div dangerouslySetInnerHTML={{ __html: image["captionHtml"] }} />
            {image["providerString"] && (
              <div className="image-credit float-right">
                <p>{image["providerString"]}</p>
              </div>
            )}
          </div>
        )
      }
    />
  );
}
