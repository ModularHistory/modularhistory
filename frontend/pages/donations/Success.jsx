import Link from "next/link";
import React from "react";
import Layout from "../../components/Layout";

class Success extends React.Component {
    render() {
        return (
          <Layout>
              <div className="pt-5">
                  <p className="h1 mt-5">Donated Successfully.</p>
                  <div className="mt-3 pt-5 h3">
                      Great thanks for your donation <b>{localStorage.getItem("donor")}</b>.<br></br> We really appreciate for your contribution and hospitability.
                  </div>
                  <div className="row col-6 mt-5 mx-auto">
                      <div className="col-6 mt-5 mx-auto">
                          <Link to="/" className="btn btn-primary  btn-lg"><b><i className="fa fa-arrow-bar-left"></i>GO TO THE LANDING PAGE</b></Link>
                      </div>
                  </div>
              </div>
            </Layout>
        );
    }
}

export default Success;