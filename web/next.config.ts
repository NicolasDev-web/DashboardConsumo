import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  outputFileTracingRoot: process.cwd(),
  outputFileTracingIncludes: {
    "/api/**/*": ["./data-generated/**/*"],
  },
  turbopack: {
    root: process.cwd(),
  },
};

export default nextConfig;
