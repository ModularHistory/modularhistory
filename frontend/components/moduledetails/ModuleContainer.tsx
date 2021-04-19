import { OccurrenceModule, QuoteModule } from "@/interfaces";
import { FC } from "react";

import {Container} from "@material-ui/core";
import ModuleDetail from "@/components/moduledetails/ModuleDetail";
import {useMediaQuery} from "@material-ui/core";

interface ModuleContainerProps {
  module: OccurrenceModule | QuoteModule
}

/**
 * Wraps a module's HTML in a container, adding padding and centering the content.
 */
const ModuleContainer: FC<ModuleContainerProps> = ({module}: ModuleContainerProps) => {
  // check if the viewport width is less than 600px
  const isSmall = useMediaQuery("@media (max-width:600px)");

  return (
    <Container style={{padding: `20px ${isSmall ? "20px" : "80px"}`, maxWidth: "50rem"}}>
      <ModuleDetail module={module}/>
    </Container>
  );
}

export default ModuleContainer;
