import { ImageModule } from "@/interfaces";
import { FC } from "react";
import ImageCard from "../cards/ImageCard";

interface ImageDetailProps {
  image: ImageModule;
}

const ImageDetail: FC<ImageDetailProps> = ({ image }: ImageDetailProps) => {
  const firstImage = image["serializedImages"]?.[0];
  return (
    <>
      <h1 className="text-center card-title" dangerouslySetInnerHTML={{ __html: image["name"] }} />
      <div className="card-text">
        {firstImage && (
          <div className="img-container" style={{ maxWidth: "44%" }}>
            <ImageCard image={firstImage} />
          </div>
        )}
        <div dangerouslySetInnerHTML={{ __html: image["description"] }} />
      </div>
    </>
  );
};

export default ImageDetail;
