# Next.js Upgrade Plan: 13.5.11 → 15.x

## 🚨 Current Critical Issues
- **Next.js 13.5.11** is severely outdated (latest: 15.4.5)
- **Webpack errors**: `TypeError: Cannot read properties of undefined (reading 'call')`
- **Hydration failures**: Server-client mismatch causing blank screen
- **JavaScript runtime errors**: 20+ errors per page load

## 📋 Upgrade Strategy

### Phase 1: Dependency Updates
```bash
# Update core packages
npm install next@latest react@latest react-dom@latest eslint-config-next@latest

# Current versions:
# next: ^13.5.11 → 15.4.5
# react: 18.2.0 → 19.0.0  
# react-dom: 18.2.0 → 19.0.0
```

### Phase 2: Breaking Changes to Address

#### 1. **Dynamic APIs (cookies, headers) - Now Async**
```typescript
// BEFORE (Next.js 13)
import { cookies } from 'next/headers'
const cookieStore = cookies()
const token = cookieStore.get('token')

// AFTER (Next.js 15)
import { cookies } from 'next/headers'
const cookieStore = await cookies()
const token = cookieStore.get('token')
```

#### 2. **Font Imports Update**
```typescript
// BEFORE
import { Inter } from '@next/font/google'

// AFTER  
import { Inter } from 'next/font/google'
```

#### 3. **Config Updates**
```javascript
// next.config.js updates needed:
const nextConfig = {
  // REMOVE deprecated experimental features
  experimental: {
    optimizeCss: true,        // Remove - now stable
    scrollRestoration: true,  // Remove - now default
    serverActions: true,      // Remove - now stable
  },

  // ADD new stable features
  serverExternalPackages: [], // Renamed from experimental.serverComponentsExternalPackages
  bundlePagesRouterDependencies: true, // Renamed from experimental.bundlePagesExternals
}
```

### Phase 3: TypeScript Updates
```bash
# Update TypeScript types for React 19
npm install -D @types/react@19.0.0 @types/react-dom@19.0.0
```

## 🔧 Execution Steps

### Step 1: Automated Upgrade (Recommended)
```bash
cd frontend
npx @next/codemod@latest upgrade latest
```

### Step 2: Manual Upgrade (Alternative)
```bash
cd frontend
npm install next@latest react@latest react-dom@latest eslint-config-next@latest
npm install -D @types/react@19.0.0 @types/react-dom@19.0.0
```

### Step 3: Fix Configuration Issues
1. **Update next.config.js** - Remove deprecated experimental features
2. **Fix font imports** - Update @next/font to next/font
3. **Update middleware** - Handle new async patterns
4. **Fix webpack config** - Resolve custom webpack optimizations

### Step 4: Handle Component Updates
1. **Server Components** - Ensure async/await patterns
2. **Client Components** - Add 'use client' directive where needed
3. **Image optimization** - Verify next/image compatibility
4. **Dynamic imports** - Update dynamic component loading

## 🛠️ Potential Issues & Solutions

### Issue 1: Webpack Configuration Conflicts
**Problem**: Custom webpack config may conflict with Next.js 15
**Solution**: Simplify webpack config, remove deprecated options

### Issue 2: React 19 Breaking Changes
**Problem**: Some components may not work with React 19
**Solution**: Update component patterns, handle new React features

### Issue 3: CSS/Styling Issues
**Problem**: TailwindCSS or custom styles may break
**Solution**: Update PostCSS config, verify Tailwind compatibility

### Issue 4: Third-party Dependencies  
**Problem**: Some packages may not support React 19
**Solution**: Update dependencies or find alternatives

## 📊 Expected Improvements

### Performance Gains
- **Bundle size**: 15-20% reduction with better tree shaking
- **Build time**: 25-30% faster with improved compilation
- **Runtime**: Better hydration, fewer client-side errors
- **Developer experience**: Faster hot reload, better error messages

### New Features Available
- **Enhanced App Router**: Better routing and layouts
- **Improved Server Components**: More efficient SSR
- **Better Caching**: Automatic request deduplication
- **Enhanced Image Optimization**: Better performance and formats

## 🧪 Testing Plan

### 1. Development Testing
```bash
# After upgrade
npm run dev
# Test: http://localhost:3000
```

### 2. Build Testing
```bash
npm run build
npm run start
# Verify production build works
```

### 3. Feature Testing
- [ ] Homepage loads without errors
- [ ] Authentication flow works
- [ ] Chat interface functions
- [ ] Skill tree visualization renders
- [ ] Mobile responsiveness maintained
- [ ] All routes accessible

### 4. Performance Testing
```bash
npm run build:analyze
# Check bundle sizes and performance
```

## 🚨 Rollback Plan

If upgrade fails:
```bash
# Restore backups
cp package.json.backup package.json
cp next.config.js.backup next.config.js

# Reinstall original dependencies
npm install

# Restart development
npm run dev
```

## ✅ Success Criteria

- [ ] No webpack errors in console
- [ ] Application loads without JavaScript errors  
- [ ] All routes render correctly
- [ ] No hydration mismatches
- [ ] Build completes successfully
- [ ] Performance maintained or improved
- [ ] All tests pass

---

**Priority**: CRITICAL - Blocking all frontend functionality
**Estimated Time**: 2-4 hours with testing
**Risk Level**: Medium (backup and rollback plan ready)