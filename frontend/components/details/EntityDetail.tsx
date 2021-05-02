import { EntityModule } from "@/interfaces";
import { FC } from "react";
import ImageCard from "../cards/ImageCard";

interface EntityDetailProps {
  entity: EntityModule;
}

const EntityDetail: FC<EntityDetailProps> = ({ entity }: EntityDetailProps) => {
  let titleHtml = entity["name"];
  const firstImage = JSON.parse(entity["serializedImages"])?.[0];
  const firstImageCard = (
    <>
      <div dangerouslySetInnerHTML={{ __html: module["caption_html"] }} />
      {module["provider_string"] && (
        <div className="image-credit float-right">
          <p>{module["provider_string"]}</p>
        </div>
      )}
    </>
  );
  return (
    <>
      <h1 className="text-center card-title" dangerouslySetInnerHTML={{ __html: titleHtml }} />
      <div className="card-text">
        {firstImage && (
          <div className="img-container" style={{ maxWidth: "44%" }}>
            <ImageCard image={firstImage} />
          </div>
        )}
        <div dangerouslySetInnerHTML={{ __html: entity["description"] }} />
      </div>
    </>
  );
};

export default EntityDetail;
