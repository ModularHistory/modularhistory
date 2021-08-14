import Layout from "@/components/Layout";
import React from "react";

export default function Success() {
  return (
    <Layout title="Success">
      <div className="pt-5">
        <p className="h1 mt-5">Donated Successfully.</p>
        <div className="mt-3 pt-5 h3">
          Thank you for your donation! Your patronage makes ModularHistory possible.
        </div>
      </div>
    </Layout>
  );
}
