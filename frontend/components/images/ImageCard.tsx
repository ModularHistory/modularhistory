import { Image } from "@/types/models";
import { styled } from "@mui/material/styles";
import { FC } from "react";
import HTMLEllipsis from "react-lines-ellipsis/lib/html";
import ModuleCard from "../cards/ModuleCard";

interface ImageCardProps {
  image: Image;
}

const ImageCard: FC<ImageCardProps> = ({ image, ...childProps }: ImageCardProps) => {
  return (
    <ModuleCard module={image} className={"image-card"} {...childProps}>
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

export default styled(ImageCard)(({ image }) => ({ width: `${image.width}px`, maxWidth: `100%` }));
