import { FC } from "react";
import { ManyToOneFieldProps } from "../types";
import ManyToOneField from "./ManyToOneField";

const LocationsField: FC<ManyToOneFieldProps> = (props: ManyToOneFieldProps) => {
  return <ManyToOneField {...props} />;
};

export default LocationsField;
