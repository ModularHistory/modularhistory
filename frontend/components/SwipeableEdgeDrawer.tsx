import Box from "@mui/material/Box";
import { grey } from "@mui/material/colors";
import { styled } from "@mui/material/styles";
import { FC, ReactNode, useState } from "react";

const Root = styled("div")(({ theme }) => ({
  position: "sticky",
  width: "100%",
  top: 0,
  backgroundColor: theme.palette.mode === "light" ? grey[100] : theme.palette.background.default,
  // backgroundColor: theme.palette.mode === 'light' ? '#fff' : grey[800],
  zIndex: 100,
  transition: "max-height 0.3s ease",
  borderBottom: `2px solid ${theme.palette.mode === "light" ? grey[300] : theme.palette.divider}`,
}));

const Puller = styled(Box)(({ theme }) => ({
  width: 30,
  height: "0.25rem",
  // padding: 3,
  backgroundColor: theme.palette.mode === "light" ? grey[300] : grey[900],
  borderRadius: 3,
  left: "calc(50% - 15px)",
  cursor: "pointer",
}));

interface SwipeableEdgeDrawerProps {
  jutRem: number;
  jutContent: ReactNode;
  children: ReactNode;
}

const SwipeableEdgeDrawer: FC<SwipeableEdgeDrawerProps> = ({
  jutRem,
  jutContent,
  children,
}: SwipeableEdgeDrawerProps) => {
  const [open, setOpen] = useState(false);

  const toggleDrawer = (newOpen: boolean) => () => {
    setOpen(newOpen);
  };

  return (
    <Root sx={{ maxHeight: open ? "80vh" : `${jutRem}rem`, overflowY: open ? "scroll" : "hidden" }}>
      <Box padding={1}>{children}</Box>
      <Box
        position="sticky"
        bottom={0}
        display="flex"
        justifyContent="center"
        alignItems="center"
        bgcolor={"inherit"}
        zIndex={10}
      >
        <Box flex={1} display="flex" justifyContent="center">
          {jutContent}
        </Box>
        <Box flex={1} display="flex" justifyContent="center">
          <Puller onClick={open ? toggleDrawer(false) : toggleDrawer(true)} />
        </Box>
        <Box flex={1} />
      </Box>
    </Root>
  );
};

export default SwipeableEdgeDrawer;
