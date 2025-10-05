import type { NextConfig } from "next";

const target = process.env.FLASK_INTERNAL_ORIGIN || "http://ml:8000";
const nextConfig: NextConfig = {
  // distDir: "build",
  /* config options here */
  async rewrites() {
    return [
      {
        source: "/flask/:path*",
        destination: `${target}/:path*`,
      },
    ];
  },
};

export default nextConfig;
