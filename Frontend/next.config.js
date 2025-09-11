/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    appDir: true,
  },
  // Allow custom page extensions to handle uppercase files
  pageExtensions: ['tsx', 'ts', 'jsx', 'js'],
  // Custom webpack configuration
  webpack: (config, { isServer }) => {
    return config;
  },
  // Handle case sensitivity issues
  trailingSlash: false,
  reactStrictMode: true,
};

module.exports = nextConfig;
