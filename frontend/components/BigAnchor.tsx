import { Box, styled } from "@mui/material";
import { FC, ForwardedRef, forwardRef, HTMLProps } from "react";

const _BigAnchor: FC<HTMLProps<HTMLAnchorElement> & { ref?: ForwardedRef<HTMLAnchorElement> }> =
  forwardRef(function _BigAnchor(props, ref) {
    const { children, ...rest } = props;
    return (
      <Box position="relative">
        <a
          {...rest}
          ref={ref}
          style={{
            position: "absolute",
            display: "block",
            left: 1,
            right: 1,
            top: 0,
            bottom: 0,
            zIndex: 1,
          }}
        >
          <Box />
        </a>
        {children}
      </Box>
    );
  });

const BigAnchor = styled(_BigAnchor)({
  "&:hover": {
    backgroundColor: "rgba(0,0,0,0.1)",
  },
});

export default BigAnchor;
