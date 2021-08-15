import dynamic from "next/dynamic";
import { FC } from "react";

const ReactAdmin = dynamic(() => import("components/admin/Admin"), {
  ssr: false,
});

const HomePage: FC = () => <ReactAdmin />;

export default HomePage;
