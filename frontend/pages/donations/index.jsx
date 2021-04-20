import Link from "next/link";
import React from "react";
import Layout from "../../components/Layout";

export default function Donations() {
  return (
    <Layout>
      <div className="text-center">
        <div className="pt-5">
          <p className="h1">Donate</p>
        </div>
        <div className="pt-5 m-auto col-6">
          <p className="sm w-70">
            Modular history is a non-profit organization that helps people to learn about and understand history. 
            Donate to our cause because learning can't wait.
          </p>
        </div>
        <div className="pt-5 col-4 m-auto row">
          <Link href={'/donations/make'}>
            <button className="col btn btn-primary mr-3" type="button">Donate Now &nbsp;<i className="fa fa-dollar-sign"></i></button>
          </Link>
          {" "}
          <Link href={'/about/'}>
            <button className="col btn btn-primary ml-3" type="button">About &nbsp;<i className="fa fa-info-circle"></i></button>
          </Link>
        </div>
      </div>
    </Layout>
  );
}
