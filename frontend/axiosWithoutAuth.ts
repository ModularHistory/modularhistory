/**
 * Import axios from this module when making a POST request to the Django API.
 */

import axios from "axios";
import { DJANGO_CSRF_COOKIE_NAME } from "./auth";

// Include the CSRF token from the cookie supplied by Django.
// Create custom instance to avoid polluting global settings.
const axiosWithoutAuth = axios.create({
  xsrfHeaderName: "X-CSRFToken",
  xsrfCookieName: DJANGO_CSRF_COOKIE_NAME,
  withCredentials: false,
});

export default axiosWithoutAuth;
