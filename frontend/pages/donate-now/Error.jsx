import Link from "next/link";
import React from "react";
import Layout from "../../components/Layout";

class Error extends React.Component {
    render() {
        return (
          <Layout>
            <div className="pt-5">
                <p className="h1 mt-5">Oops, something went wrong.</p>
                <div className="mt-3 pt-5 h3">
                    Sorry for your donation <b>{localStorage.getItem("donor")}</b>. There are some issues with your donation.
                </div>
                <div className="row col-6 mt-5 mx-auto">
                    <div className="col-5 mt-5 mx-auto">
                        <Link to="/" className="btn btn-primary  btn-lg"><b><i className="fa fa-arrow-bar-left"></i>TO THE LANDING PAGE</b></Link>
                    </div>
                </div>
            </div>
          </Layout>
        );
    }
}

export default Error;