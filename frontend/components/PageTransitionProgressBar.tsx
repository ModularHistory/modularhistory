import { Box, Fade, LinearProgress } from "@mui/material";
import { useRouter } from "next/router";
import { FC, useEffect, useRef, useState } from "react";

const PageTransitionProgressBar: FC = () => {
  const { events } = useRouter();
  const [loadingProgress, setLoadingProgress] = useState(0);

  // We use this ref to track the last active interval/timeout
  // so we can cancel it when a transition is interrupted.
  const timerIDRef = useRef<number>();

  useEffect(() => {
    const clearProgressInterval = () => {
      if (timerIDRef.current) clearInterval(timerIDRef.current);
    };

    const handleRouteChangeStart = () => {
      clearProgressInterval();
      setLoadingProgress(20);

      // every 500ms, increase progress by 5, until we reach 80.
      timerIDRef.current = window.setInterval(() => {
        setLoadingProgress((currentProgress) => {
          if (currentProgress === 75) {
            clearProgressInterval();
          }
          return currentProgress + 5;
        });
      }, 500);
    };

    const handleRouteChangeComplete = () => {
      clearProgressInterval();
      setLoadingProgress(100);
      timerIDRef.current = window.setTimeout(() => setLoadingProgress(0), 1e3);
    };

    events.on("routeChangeStart", handleRouteChangeStart);
    events.on("routeChangeComplete", handleRouteChangeComplete);

    return () => {
      events.off("routeChangeStart", handleRouteChangeStart);
      events.off("routeChangeComplete", handleRouteChangeComplete);
    };
  }, [events]);

  return (
    <Box position={"fixed"} width={"100%"} top={-1} left={0} zIndex={10}>
      <Fade in={![0, 100].includes(loadingProgress)} timeout={{ exit: 1e3 }}>
        <LinearProgress variant={"determinate"} value={loadingProgress} />
      </Fade>
    </Box>
  );
};

export default PageTransitionProgressBar;
