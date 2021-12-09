import { Image } from "@/types/models";
import { FC } from "react";
import ImageCard from "./ImageCard";

interface ImageDetailProps {
  image: Image;
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
