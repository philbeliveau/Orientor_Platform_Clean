// Bundle optimization configuration for Next.js

module.exports = {
  // Split vendor chunks for better caching
  splitChunks: {
    chunks: 'all',
    cacheGroups: {
      default: false,
      vendors: false,
      // Split vendor libraries
      framework: {
        name: 'framework',
        chunks: 'all',
        test: /[\\/]node_modules[\\/](react|react-dom|next)[\\/]/,
        priority: 40,
        enforce: true,
      },
      mui: {
        name: 'mui',
        chunks: 'all',
        test: /[\\/]node_modules[\\/]@mui[\\/]/,
        priority: 30,
        enforce: true,
      },
      charts: {
        name: 'charts',
        chunks: 'all',
        test: /[\\/]node_modules[\\/](chart\.js|react-chartjs-2|recharts)[\\/]/,
        priority: 25,
        enforce: true,
      },
      lottie: {
        name: 'lottie',
        chunks: 'all',
        test: /[\\/]node_modules[\\/](lottie-react|@lottiefiles)[\\/]/,
        priority: 20,
        enforce: true,
      },
      commons: {
        name: 'commons',
        minChunks: 2,
        priority: 10,
        reuseExistingChunk: true,
      },
      lib: {
        test(module) {
          return module.size() > 160000 &&
            /node_modules[\\/]/.test(module.nameForCondition() || '');
        },
        name(module) {
          const hash = crypto.createHash('sha1');
          hash.update(module.nameForCondition() || '');
          return `lib-${hash.digest('hex').substring(0, 8)}`;
        },
        priority: 15,
        minChunks: 1,
        reuseExistingChunk: true,
      },
    },
  },
  
  // Minimize bundle size
  minimize: true,
  
  // Tree shake unused exports
  usedExports: true,
  
  // Enable module concatenation
  concatenateModules: true,
  
  // Optimize runtime chunk
  runtimeChunk: {
    name: 'runtime',
  },
};