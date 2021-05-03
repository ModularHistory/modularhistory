import { EntityModule } from "@/interfaces";
import { FC } from "react";
import ImageCard from "../cards/ImageCard";

interface EntityDetailProps {
  entity: EntityModule;
}

const EntityDetail: FC<EntityDetailProps> = ({ entity }: EntityDetailProps) => {
  const firstImage = entity["serializedImages"]?.[0];
  return (
    <>
      <h1 className="text-center card-title" dangerouslySetInnerHTML={{ __html: entity["name"] }} />
      <div className="card-text">
        {firstImage && (
          <div
            className="img-container"
            style={{ maxWidth: "44%", maxHeight: firstImage["height"] }}
          >
            <ImageCard image={firstImage} />
          </div>
          // <div className="img-container" style={{ maxWidth: "44%", maxHeight: firstImage["height"] }}>
          //   <ImageCard image={firstImage} />
          // </div>
        )}
        <div dangerouslySetInnerHTML={{ __html: entity["description"] }} />
      </div>
    </>
  );
};

export default EntityDetail;
