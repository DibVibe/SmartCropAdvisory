// lib/config.js
import sharedConfig from "../shared-config.json";

const env = process.env.NODE_ENV || "development";
const config = sharedConfig[env];

export const API_BASE_URL = `${config.backend_url}/api/${config.api_version}`;
export const APP_NAME = sharedConfig.app.name;
