import { Image } from "@/interfaces";
import { FC } from "react";
import HTMLEllipsis from "react-lines-ellipsis/lib/html";
import ModuleCard from "../cards/ModuleCard";

interface ImageCardProps {
  image: Image;
}

const ImageCard: FC<ImageCardProps> = ({ image, ...childProps }: ImageCardProps) => {
  const style = { width: `${image.width}px`, maxWidth: `100%` };
  return (
    <ModuleCard module={image} className={"image-card"} style={style} {...childProps}>
      {image.captionHtml && (
        <>
          <HTMLEllipsis unsafeHTML={image.captionHtml} maxLine="3" basedOn="words" />
          {image.providerString && (
            <div className="image-credit float-right">
              <p>{image.providerString}</p>
            </div>
          )}
        </>
      )}
    </ModuleCard>
  );
};

export default ImageCard;
