import { FC, ReactNode } from "react";

interface PageHeaderProps {
  children: ReactNode;
}

const PageHeader: FC<PageHeaderProps> = ({ children }: PageHeaderProps) => {
  return (
    <>
      <h1 className="page-header text-center my-3">{children}</h1>
      <hr />
    </>
  );
};

export default PageHeader;
