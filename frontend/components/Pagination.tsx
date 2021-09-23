import { Breakpoint, useMediaQuery, useTheme } from "@mui/material";
import MuiPagination, { PaginationProps as MuiPaginationProps } from "@mui/material/Pagination";
import { styled } from "@mui/material/styles";
import { useRouter } from "next/router";
import { FC, useState } from "react";

const StyledPagination = styled(MuiPagination)(({ theme }) => ({
  // override bootstrap css
  "& button:focus": { outline: "none" },
  // center the pagination
  "& > *": {
    marginTop: theme.spacing(1),
    marginBottom: theme.spacing(1),
    justifyContent: "center",
    display: "flex",
  },
}));

function usePageState() {
  // This hook is used to trigger route changes
  // when a page button is clicked.
  const router = useRouter();
  const pageNum = Number(router.query["page"] || 1);
  const [loading, setLoading] = useState(false);

  const setPage: MuiPaginationProps["onChange"] = (event, newPageNum) => {
    // remove page query param when page=1
    const query = { ...router.query };
    if (newPageNum > 1) {
      query.page = String(newPageNum);
    } else {
      delete query.page;
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

  // increase pagination size based on viewport size
  const breakpoints: ReadonlyArray<Breakpoint> = ["sm", "md"];
  const sibCount = breakpoints
    // eslint-disable-next-line react-hooks/rules-of-hooks
    .map((breakpoint) => useMediaQuery(theme.breakpoints.up(breakpoint)))
    .reduce((sum, current) => sum + Number(current), 1);

  const { pageNum, setPage, loading } = usePageState();

  // https://material-ui.com/api/pagination/
  return (
    <StyledPagination
      count={count}
      page={pageNum}
      siblingCount={sibCount}
      onChange={setPage}
      disabled={loading}
      variant="outlined"
      shape="rounded"
      size={sibCount > 2 ? "large" : undefined}
    />
  );
};
export default Pagination;
