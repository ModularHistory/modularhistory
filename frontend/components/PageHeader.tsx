import { FC, ReactNode } from "react";

interface PageHeaderProps {
  children: ReactNode;
}

const PageHeader: FC<PageHeaderProps> = ({ children }: PageHeaderProps) => {
  return (
    <h1
      className="page-header text-center my-3"
      style={{ padding: "0.5rem", margin: "0 15%", borderBottom: "1px solid lightgray" }}
    >
      {children}
    </h1>
  );
};

export default PageHeader;
