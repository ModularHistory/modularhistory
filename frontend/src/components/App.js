import React, { Component } from "react";
import { render } from "react-dom";
import * as Sentry from '@sentry/react';

Sentry.init({
    dsn: "https://054ccb00ec274cc292f2472140f8260c@o431037.ingest.sentry.io/5380934",
    environment: "production"  // TODO
});

class App extends Component {
    constructor(props) {
        super(props);
        this.state = {
            data: [],
            loaded: false,
            placeholder: "Loading"
        };
    }

    componentDidMount() {
        fetch("api/lead")
            .then(response => {
                if (response.status > 400) {
                    return this.setState(() => {
                        return { placeholder: "Something went wrong!" };
                    });
                }
                return response.json();
            })
            .then(data => {
                this.setState(() => {
                    return {
                        data,
                        loaded: true
                    };
                });
            });
    }

    render() {
        return (
            <ul>
                {this.state.data.map(contact => {
                    return (
                        <li key={contact.id}>
                            {contact.name} - {contact.email}
                        </li>
                    );
                })}
            </ul>
        );
    }
}

export default App;

const container = document.getElementById("app");
render(<App />, container);