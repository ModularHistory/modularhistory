import { Button, CircularProgress } from "@material-ui/core";

import { useEffect, useContext } from "react";
import { useRouter } from "next/router";

import PageTransitionContext from "../PageTransitionContext";

export default function SearchButton(props) {
  // A button with "Search" label.
  // The label changes to "Loading" with a circular progress indicator when a page transition occurs.
  // All props are passed along to the Mui Button.

  const router = useRouter();
  const isLoading = useContext(PageTransitionContext);

  // asynchronously download JS for the search page
  useEffect(() => {
    router.prefetch("/search");
  }, []);

  let buttonText;
  if (isLoading) {
    buttonText = (
      <span>
        <CircularProgress size={12} style={{ marginRight: "10px" }} />
        Loading
      </span>
    );
  } else {
    buttonText = "Search";
  }

  return (
    <Button variant={"contained"} color={"primary"} size={"large"} disabled={isLoading} {...props}>
      {buttonText}
    </Button>
  );
}
