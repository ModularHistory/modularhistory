import dynamic from "next/dynamic";
import { FC } from "react";

const Pdf = dynamic(() => import("@/components/sources/Pdf"), { ssr: false });

interface PdfProps {
  url: string | null;
  initialPageNumber: string | undefined;
}

const PdfViewer: FC<PdfProps> = (props: PdfProps) => {
  return <Pdf {...props} />;
};

export default PdfViewer;
