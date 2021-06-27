import { Breakpoint, Theme, useMediaQuery, useTheme } from "@material-ui/core";
import MuiPagination from "@material-ui/core/Pagination";
import { makeStyles } from "@material-ui/styles";
import { useRouter } from "next/router";
import { FC, useState } from "react";

const useStyles = makeStyles((theme: Theme) => ({
  root: {
    // override bootstrap css
    "& button:focus": { outline: "none" },
    // center the pagination
    "& > *": {
      marginTop: theme.spacing(1),
      marginBottom: theme.spacing(1),
      justifyContent: "center",
      display: "flex",
    },
  },
}));

function usePageState() {
  // This hook is used to trigger route changes
  // when a page button is clicked.
  const router = useRouter();
  const pageNum = Number(router.query["page"] || 1);
  const [loading, setLoading] = useState(false);

  const setPage = (event, newPageNum) => {
    // remove page query param when page=1
    const query = { ...router.query };
    if (newPageNum > 1) {
      query["page"] = newPageNum;
    } else {
      delete query["page"];
    }

    // `loading` is true during page transitions so the paginator
    // can be disabled until the transition completes.
    setLoading(true);
    router.push({ query }).then(() => setLoading(false));
  };

  return { pageNum, setPage, loading };
}

interface PaginationProps {
  count: number;
}

const Pagination: FC<PaginationProps> = ({ count }: PaginationProps) => {
  const theme = useTheme();
  const classes = useStyles(theme);

  // increase pagination size based on viewport size
  const breakpoints: Breakpoint[] = ["sm", "md"];
  const sibCount = breakpoints
    .map((breakpoint) => useMediaQuery(theme.breakpoints.up(breakpoint)))
    .reduce((sum, current) => sum + Number(current), 1);

  const { pageNum, setPage, loading } = usePageState();

  // https://material-ui.com/api/pagination/
  return (
    <MuiPagination
      count={count}
      page={pageNum}
      siblingCount={sibCount}
      onChange={setPage}
      disabled={loading}
      variant="outlined"
      shape="rounded"
      size={sibCount > 2 ? "large" : undefined}
      className={classes.root}
    />
  );
};
export default Pagination;
