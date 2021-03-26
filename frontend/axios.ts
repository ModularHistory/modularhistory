import axios from "axios";

const djangoCsrfCookieName = "csrftoken"

// Axios config for DRF requests
axios.defaults.xsrfHeaderName = "X-CSRFToken";
axios.defaults.xsrfCookieName = djangoCsrfCookieName;
axios.defaults.withCredentials = true;

export default axios;
