import {createContext, useEffect, useState} from "react";
import {useRouter} from "next/router";

const PageTransitionContext = createContext(false);
export default PageTransitionContext;

export function usePageTransitionListener() {
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
    }
  }, []);

  return isLoading;
}

export function PageTransitionContextProvider({children}) {
  return (
    <PageTransitionContext.Provider value={usePageTransitionListener()}>
      {children}
    </PageTransitionContext.Provider>
  );
}
