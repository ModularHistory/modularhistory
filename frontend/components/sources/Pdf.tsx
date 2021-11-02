import { Skeleton } from "@mui/material";
import { FC } from "react";

export interface PdfProps {
  url: string | null;
  initialPageNumber: string | undefined;
}

const Pdf: FC<PdfProps> = (props: PdfProps) => {
  const { url, initialPageNumber } = props;
  return (
    <div>
      {url ? (
        <embed
          style={{
            width: "100%",
            height: "100vh",
          }}
          type="application/pdf"
          src={`${url}#page=${initialPageNumber}`}
        />
      ) : (
        <Skeleton
          variant={"rectangular"}
          sx={{ width: "inherit", minWidth: "50vw", height: "40vw" }}
        />
      )}
    </div>
  );
};

export default Pdf;
