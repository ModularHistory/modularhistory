import { CardContent } from "@material-ui/core";
import BaseCard from "./BaseCard";

export default function EntityCard({ entity, ...childProps }) {
  return (
    <BaseCard module={entity} {...childProps}>
      <CardContent
        className="text-center"
        dangerouslySetInnerHTML={{ __html: entity["truncated_description"] }}
      />
    </BaseCard>
  );
}
