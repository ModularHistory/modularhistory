import { Container, useMediaQuery } from "@mui/material";
import { FC, ReactNode } from "react";

interface ModuleContainerProps {
  children: ReactNode;
}

/**
 * Wraps a module's HTML in a container, adding padding and centering the content.
 */
const ModuleContainer: FC<ModuleContainerProps> = ({ children }: ModuleContainerProps) => {
  // check if the viewport width is less than 600px
  const isSmall = useMediaQuery("@media (max-width:600px)");

  return (
    <Container style={{ padding: `20px ${isSmall ? "20px" : "80px"}`, maxWidth: "50rem" }}>
      {children}
    </Container>
  );
};

export default ModuleContainer;
