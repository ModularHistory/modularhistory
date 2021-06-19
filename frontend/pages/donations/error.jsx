import Layout from "@/components/Layout";
import React from "react";

export default function Error() {
  return (
    <Layout>
      <div className="pt-5">
        <p className="h1 mt-5">Oops, something went wrong.</p>
        <div className="mt-3 pt-5 h3">Sorry, there were some issues with your donation.</div>
      </div>
    </Layout>
  );
}
