import Box from "@mui/material/Box";
import { grey } from "@mui/material/colors";
import { styled } from "@mui/material/styles";
import { FC, ReactNode, useState } from "react";

const Root = styled("div")(({ theme }) => ({
  position: "sticky",
  top: 0,
  backgroundColor: theme.palette.mode === "light" ? grey[100] : theme.palette.background.default,
  // backgroundColor: theme.palette.mode === 'light' ? '#fff' : grey[800],
  zIndex: 100,
  transition: "max-height 0.3s ease",
  padding: "1rem",
}));

const Puller = styled(Box)(({ theme }) => ({
  position: "absolute",
  bottom: 6,
  width: 30,
  height: "0.25rem",
  padding: 3,
  backgroundColor: theme.palette.mode === "light" ? grey[300] : grey[900],
  borderRadius: 3,
  left: "calc(50% - 15px)",
  cursor: "pointer",
}));

interface SwipeableEdgeDrawerProps {
  jutRem: number;
  children: ReactNode;
}

const SwipeableEdgeDrawer: FC<SwipeableEdgeDrawerProps> = ({
  jutRem,
  children,
}: SwipeableEdgeDrawerProps) => {
  const [open, setOpen] = useState(false);

  const toggleDrawer = (newOpen: boolean) => () => {
    setOpen(newOpen);
  };

  return (
    <Root
      sx={{
        maxHeight: open ? "80vh" : `${jutRem}rem`,
        overflowY: open ? "scroll" : "hidden",
      }}
    >
      {children}
      <Puller onClick={open ? toggleDrawer(false) : toggleDrawer(true)} />
    </Root>
  );
};

export default SwipeableEdgeDrawer;
