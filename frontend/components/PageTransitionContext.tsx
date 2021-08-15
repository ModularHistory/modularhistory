import { useRouter } from "next/router";
import React, { createContext, FC, ReactNode, useEffect, useState } from "react";

// Because `PageTransitionContext.Provider` is placed at the root
// of the application (pages/_app.tsx), any component can
// use this context (react/useContext) to respond to page
// transitions without creating additional event callbacks.
const PageTransitionContext = createContext(false);
export default PageTransitionContext;

export function usePageTransitionListener(): boolean {
  const router = useRouter();
  const [isLoading, setLoading] = useState(false);

  useEffect(() => {
    const setLoadingTrue = () => setLoading(true);
    const setLoadingFalse = () => setLoading(false);
    router.events.on("routeChangeStart", setLoadingTrue);
    router.events.on("routeChangeComplete", setLoadingFalse);
    router.events.on("routeChangeError", setLoadingFalse);
    return () => {
      router.events.off("routeChangeStart", setLoadingTrue);
      router.events.off("routeChangeComplete", setLoadingFalse);
      router.events.off("routeChangeError", setLoadingFalse);
    };
  }, [router.events]);

  return isLoading;
}

interface PageTransitionContextProviderProps {
  children: ReactNode;
}

export const PageTransitionContextProvider: FC<PageTransitionContextProviderProps> = ({
  children,
}: PageTransitionContextProviderProps) => {
  return (
    <PageTransitionContext.Provider value={usePageTransitionListener()}>
      {children}
    </PageTransitionContext.Provider>
  );
};
