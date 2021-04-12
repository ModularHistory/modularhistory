/**
 * Import axios from this module when making a POST request to the Django API.
 */

import axios from "axios";

const djangoCsrfCookieName = "csrftoken";

// Include the CSRF token from the cookie supplied by Django.
// Create custom instance to avoid polluting global settings.
const authAxios = axios.create({
  xsrfHeaderName: "X-CSRFToken",
  xsrfCookieName: djangoCsrfCookieName,
  withCredentials: true,
});

export default authAxios;
