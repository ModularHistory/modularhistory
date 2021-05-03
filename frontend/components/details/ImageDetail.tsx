import { ImageModule } from "@/interfaces";
import { FC } from "react";
import ImageCard from "../cards/ImageCard";

interface ImageDetailProps {
  image: ImageModule;
}

const ImageDetail: FC<ImageDetailProps> = ({ image }: ImageDetailProps) => {
  return (
    <>
      <h1
        className="text-center card-title"
        dangerouslySetInnerHTML={{ __html: image.captionHtml }}
      />
      <ImageCard image={image} />
      <div dangerouslySetInnerHTML={{ __html: image.description }} />
    </>
  );
};

export default ImageDetail;
