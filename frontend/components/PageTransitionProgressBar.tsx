import { Box, Fade, LinearProgress } from "@mui/material";
import { useRouter } from "next/router";
import { FC, useEffect, useRef, useState } from "react";

export const constants = {
  fadeOutDelay: 1000,
  incrementDelay: 500,
  incrementValue: 5,
  initialValue: 20,
  finalIncompleteValue: 80,
  finalCompleteValue: 100,
} as const;

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
      setLoadingProgress(constants.initialValue);

      // every 500ms, increase progress by 5, until we reach 80.
      timerIDRef.current = window.setInterval(() => {
        setLoadingProgress((currentProgress) => {
          if (currentProgress >= constants.finalIncompleteValue) {
            clearProgressInterval();
            return currentProgress;
          }
          return currentProgress + constants.incrementValue;
        });
      }, constants.incrementDelay);
    };

    const handleRouteChangeComplete = () => {
      clearProgressInterval();
      setLoadingProgress(constants.finalCompleteValue);
      timerIDRef.current = window.setTimeout(() => setLoadingProgress(0), constants.fadeOutDelay);
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
      <Fade
        in={![0, constants.finalCompleteValue].includes(loadingProgress)}
        timeout={{ exit: constants.fadeOutDelay }}
      >
        <LinearProgress variant={"determinate"} value={loadingProgress} />
      </Fade>
    </Box>
  );
};

export default PageTransitionProgressBar;
