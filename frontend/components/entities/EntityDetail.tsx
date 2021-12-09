import ModuleHTML from "@/components/details/ModuleHTML";
import { Entity } from "@/types/models";
import { FC } from "react";
import ImageCard from "../images/ImageCard";

interface EntityDetailProps {
  entity: Entity;
}

const EntityDetail: FC<EntityDetailProps> = ({ entity }: EntityDetailProps) => {
  const firstImage = entity.cachedImages?.[0];
  return (
    <>
      <h1 className="text-center card-title" dangerouslySetInnerHTML={{ __html: entity.name }} />
      {firstImage && (
        <div className="img-container" style={{ maxWidth: "44%", maxHeight: firstImage.height }}>
          <ImageCard image={firstImage} />
        </div>
      )}

      <ModuleHTML html={entity.description} />
    </>
  );
};

export default EntityDetail;
