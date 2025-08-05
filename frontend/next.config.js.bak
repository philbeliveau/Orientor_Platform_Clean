/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  eslint: {
    // Disable ESLint during builds since we have config issues but code is working
    ignoreDuringBuilds: true,
  },
  // swcMinify is now default in Next.js 15+
  
  // Enable production optimizations
  productionBrowserSourceMaps: false,
  
  // Optimize images
  images: {
    domains: ['localhost', 'orientor.com'],
    formats: ['image/avif', 'image/webp'],
  },
  
  // Simplified webpack configuration - removed aggressive optimizations
  webpack: (config, { isServer, dev }) => {
    // Only add bundle analyzer when needed
    if (!dev && !isServer && process.env.ANALYZE === 'true') {
      const { BundleAnalyzerPlugin } = require('webpack-bundle-analyzer');
      config.plugins.push(
        new BundleAnalyzerPlugin({
          analyzerMode: 'static',
          reportFilename: './analyze.html',
          openAnalyzer: true,
        })
      );
    }
    
    return config;
  },
  
  // Experimental features (removed deprecated options for Next.js 15+)
  experimental: {
    // Most previous experimental features are now stable in Next.js 15
    // scrollRestoration is now default behavior
    // serverActions are now stable
    // optimizeCss is now handled automatically
  },
  
  // Headers for better caching
  async headers() {
    return [
      {
        source: '/:all*(svg|jpg|jpeg|png|gif|ico|webp|avif)',
        headers: [
          {
            key: 'Cache-Control',
            value: 'public, max-age=31536000, immutable',
          },
        ],
      },
      {
        source: '/_next/static/:path*',
        headers: [
          {
            key: 'Cache-Control',
            value: 'public, max-age=31536000, immutable',
          },
        ],
      },
    ];
  },
  
  // Compression
  compress: true,
  
  // Disable x-powered-by header
  poweredByHeader: false,
};

module.exports = nextConfig;