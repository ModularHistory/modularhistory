import Container from '@material-ui/core/Container';
import Link from "next/link";
import Router from "next/router";
import React, { useState } from "react";
import { useAuth } from "../auth";
import Layout from "../components/layout";


const Login: React.FunctionComponent = (): React.ReactElement => {
    const [username, setUsername] = useState<string>("");
    const [password, setPassword] = useState<string>("");
    const [errorMessage, setErrorMessage] = useState<string>("");
    const { loading, isAuthenticated, login } = useAuth();

    const handleSubmit = async (
        event: React.FormEvent<HTMLFormElement>
    ): Promise<void> => {
        event.preventDefault();
        setErrorMessage("");
        try {
            const resp = await login(username, password);
            if (resp.status === 401) {
                setErrorMessage("Invalid login credentials");
            }
        } catch (error) {
            console.error(error);
            // TODO: actually parse api 400 error messages
            setErrorMessage(error.message);
        }
    };

    if (!loading && isAuthenticated) Router.push("/entities");

    if (isAuthenticated) {
        return (
            <Layout title="Login">
                <p>You are already logged in.</p>
            </Layout>
        );
    }

    return (
        <Layout title="Login">
            <Container>
                <form className="w-full max-w-sm pt-4" onSubmit={handleSubmit}>
                    <div className="md:flex md:items-center mb-6">
                        <div className="md:w-1/3">
                            <label
                                className="block font-bold md:text-right mb-1 md:mb-0 pr-4"
                                htmlFor="username"
                            >
                                Username
                            </label>
                        </div>
                        <div className="md:w-2/3">
                            <input
                                type="text"
                                className="bg-gray-200 appearance-none border-2 border-gray-200 rounded w-full py-2 px-4 text-gray-700 leading-tight focus:outline-none focus:bg-white focus:border-gray-500"
                                id="username"
                                name="username"
                                value={username}
                                onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                                    setUsername(e.target.value)
                                }
                            />
                        </div>
                    </div>
                    <div className="md:flex md:items-center mb-6">
                        <div className="md:w-1/3">
                            <label
                                className="block text-gray-500 font-bold md:text-right mb-1 md:mb-0 pr-4"
                                htmlFor="password"
                            >
                                Password
                        </label>
                        </div>
                        <div className="md:w-2/3">
                            <input
                                type="password"
                                className="bg-gray-200 appearance-none border-2 border-gray-200 rounded w-full py-2 px-4 text-gray-700 leading-tight focus:outline-none focus:bg-white focus:border-gray-500"
                                id="password"
                                name="password"
                                value={password}
                                onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                                    setPassword(e.target.value)
                                }
                            />
                        </div>
                    </div>
                    <div className="md:flex md:items-center">
                        <div className="md:w-1/3"></div>
                        <div className="md:w-2/3">
                            <button
                                className="shadow bg-teal-500 hover:bg-teal-400 focus:shadow-outline focus:outline-none text-white font-bold py-2 px-4 rounded"
                                type="submit"
                            >
                                Login
                        </button>
                        </div>
                    </div>
                    {errorMessage ? (
                        <div className="md:flex md:items-center">
                            <div className="md:w-1/3"></div>
                            <div className="md:w-2/3 pt-4">
                                <p className="text-red-400">Error: {errorMessage}</p>
                            </div>
                        </div>
                    ) : null}
                    <div className="md:flex md:items-center">
                        <div className="md:w-1/3"></div>
                        <div className="md:w-2/3 pt-4">
                            <p className="text-gray-700">
                                No account?{" "}
                                <Link href="/signup">
                                    <a>Sign up</a>
                                </Link>
                            .
                        </p>
                        </div>
                    </div>
                </form>
            </Container>
        </Layout>
    );
};

export default Login;
