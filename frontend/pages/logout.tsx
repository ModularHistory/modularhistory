import Router from "next/router";
import React, { useEffect } from "react";
import { useAuth } from "../auth";
import Layout from "../components/layout";

const Logout = (): React.ReactElement => {
    // const { isAuthenticated, logout } = useAuth();
    const { loading, isAuthenticated, logout } = useAuth();


    useEffect(() => {
        logout();
    }, []);

    if (isAuthenticated) return null;
    if (!loading) Router.push("/entities");
    return (
        <Layout title="Logout" canonicalUrl="/logout/">
            <h1 className="text-xl pt-3 pb-5">You've been logged out</h1>
        </Layout>
    )
}

export default Logout;