/**
 * Import axios from this module when making a POST request to the Django API.
 */

import axios from "axios";

const djangoCsrfCookieName = "csrftoken";

// Include the CSRF token from the cookie supplied by Django.
axios.defaults.xsrfHeaderName = "X-CSRFToken";
axios.defaults.xsrfCookieName = djangoCsrfCookieName;
axios.defaults.withCredentials = true;

export default axios;
