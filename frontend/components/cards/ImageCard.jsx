import HTMLEllipsis from "react-lines-ellipsis/lib/html";
import ModuleCard from "./ModuleCard";

export default function ImageCard({ image, ...childProps }) {
  const style = { width: `${image.width}px`, maxWidth: `100%` };
  return (
    <ModuleCard module={image} className={"image-card"} style={style} {...childProps}>
      {image.captionHtml && (
        <>
          <HTMLEllipsis unsafeHTML={image.captionHtml} maxLine="3" basedOn="words" trimRight />
          {image.providerString && (
            <div className="image-credit float-right">
              <p>{image.providerString}</p>
            </div>
          )}
        </>
      )}
    </ModuleCard>
  );
}
