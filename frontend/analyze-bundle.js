#!/usr/bin/env node

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

console.log('🔍 Analyzing Next.js Bundle Size...\n');

// Build the project with bundle analyzer
try {
  console.log('📦 Building production bundle...');
  execSync('ANALYZE=true npm run build', { stdio: 'inherit' });
} catch (error) {
  console.error('❌ Build failed:', error.message);
  process.exit(1);
}

// Check .next directory for bundle stats
const nextDir = path.join(__dirname, '.next');
const statsFile = path.join(nextDir, 'analyze', 'client.html');

if (fs.existsSync(statsFile)) {
  console.log('\n✅ Bundle analysis complete!');
  console.log(`📊 View report at: file://${statsFile}`);
  
  // Try to open in browser
  const platform = process.platform;
  const command = platform === 'darwin' ? 'open' : platform === 'win32' ? 'start' : 'xdg-open';
  
  try {
    execSync(`${command} ${statsFile}`);
  } catch (e) {
    console.log('💡 Open the HTML file above in your browser to view the bundle analysis.');
  }
} else {
  console.log('\n📊 Calculating bundle sizes...');
  
  // Get build output stats
  const buildOutput = execSync('du -sh .next/static/chunks/*.js', { encoding: 'utf-8' });
  console.log('\nChunk sizes:');
  console.log(buildOutput);
  
  // Calculate total bundle size
  const totalSize = execSync('du -sh .next', { encoding: 'utf-8' }).split('\t')[0];
  console.log(`\n📦 Total build size: ${totalSize}`);
  
  // Show optimization tips
  console.log('\n💡 Optimization Tips:');
  console.log('- Use dynamic imports for heavy components');
  console.log('- Implement route-based code splitting');
  console.log('- Tree shake unused exports');
  console.log('- Optimize images with next/image');
  console.log('- Use production builds for accurate measurements');
}