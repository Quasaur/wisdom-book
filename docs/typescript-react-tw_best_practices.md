I'll provide comprehensive best practices for optimizing TypeScript code in Django web app frontends, with detailed implementation steps for each.

## 1. Build Optimization with Vite

### Configure Production Build Settings
**Purpose**: Minimize bundle size and optimize loading performance.

**Step-by-step:**
1. Update `vite.config.ts` with production optimizations:
   ```typescript
   import { defineConfig } from 'vite'
   import react from '@vitejs/plugin-react'
   import path from 'path'

   export default defineConfig({
     plugins: [react()],
     build: {
       minify: 'terser',
       terserOptions: {
         compress: {
           drop_console: true,  // Remove console.logs in production
           drop_debugger: true,
         },
       },
       rollupOptions: {
         output: {
           manualChunks: {
             vendor: ['react', 'react-dom'],
             utils: ['lodash', 'date-fns'],
           },
         },
       },
       chunkSizeWarningLimit: 1000,
       sourcemap: false,  // Disable in production for smaller builds
     },
     server: {
       proxy: {
         '/api': {
           target: 'http://localhost:8000',
           changeOrigin: true,
         },
       },
     },
   })
   ```

2. Install terser if not already present:
   ```bash
   npm install -D terser
   ```

3. Create separate configs for dev/production:
   ```typescript
   // vite.config.ts
   export default defineConfig(({ mode }) => ({
     plugins: [react()],
     define: {
       __DEV__: mode === 'development',
     },
     build: mode === 'production' ? productionConfig : devConfig,
   }))
   ```

### Implement Code Splitting
**Purpose**: Load only necessary code for each route.

**Step-by-step:**
1. Use dynamic imports for route components:
   ```typescript
   // App.tsx
   import { lazy, Suspense } from 'react'
   import { BrowserRouter, Routes, Route } from 'react-router-dom'

   // Lazy load route components
   const QuoteList = lazy(() => import('./pages/QuoteList'))
   const QuoteDetail = lazy(() => import('./pages/QuoteDetail'))
   const TopicExplorer = lazy(() => import('./pages/TopicExplorer'))

   function App() {
     return (
       <BrowserRouter>
         <Suspense fallback={<LoadingSpinner />}>
           <Routes>
             <Route path="/" element={<QuoteList />} />
             <Route path="/quote/:id" element={<QuoteDetail />} />
             <Route path="/topics" element={<TopicExplorer />} />
           </Routes>
         </Suspense>
       </BrowserRouter>
     )
   }
   ```

2. Create a loading component:
   ```typescript
   // components/LoadingSpinner.tsx
   export const LoadingSpinner = () => (
     <div className="flex items-center justify-center min-h-screen">
       <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500" />
     </div>
   )
   ```

3. Split large components:
   ```typescript
   // Instead of importing everything
   import { HeavyComponent } from './HeavyComponent'

   // Use dynamic import
   const HeavyComponent = lazy(() => import('./HeavyComponent'))
   ```

### Optimize Bundle Analysis
**Purpose**: Identify and eliminate bloat.

**Step-by-step:**
1. Install bundle analyzer:
   ```bash
   npm install -D rollup-plugin-visualizer
   ```

2. Add to `vite.config.ts`:
   ```typescript
   import { visualizer } from 'rollup-plugin-visualizer'

   export default defineConfig({
     plugins: [
       react(),
       visualizer({
         open: true,
         gzipSize: true,
         brotliSize: true,
       }),
     ],
   })
   ```

3. Build and analyze:
   ```bash
   npm run build
   # Opens stats.html in browser automatically
   ```

4. Identify large dependencies and consider alternatives:
   ```typescript
   // Bad: Import entire lodash
   import _ from 'lodash'

   // Good: Import specific functions
   import debounce from 'lodash/debounce'
   import throttle from 'lodash/throttle'
   ```

---

## 2. React Performance Optimization

### Implement Proper Memoization
**Purpose**: Prevent unnecessary re-renders.

**Step-by-step:**
1. Use `React.memo` for functional components:
   ```typescript
   // components/QuoteCard.tsx
   interface QuoteCardProps {
     id: number
     text: string
     author: string
     onLike: (id: number) => void
   }

   export const QuoteCard = React.memo<QuoteCardProps>(({ 
     id, 
     text, 
     author, 
     onLike 
   }) => {
     return (
       <div className="quote-card">
         <p>{text}</p>
         <span>{author}</span>
         <button onClick={() => onLike(id)}>Like</button>
       </div>
     )
   })
   ```

2. Use `useMemo` for expensive calculations:
   ```typescript
   import { useMemo } from 'react'

   function QuoteList({ quotes }: { quotes: Quote[] }) {
     const sortedQuotes = useMemo(() => {
       return [...quotes].sort((a, b) => 
         b.popularity - a.popularity
       )
     }, [quotes])

     const statistics = useMemo(() => {
       return {
         total: quotes.length,
         avgLength: quotes.reduce((sum, q) => sum + q.text.length, 0) / quotes.length,
         topAuthors: calculateTopAuthors(quotes),  // Expensive operation
       }
     }, [quotes])

     return <div>{/* Render with sortedQuotes and statistics */}</div>
   }
   ```

3. Use `useCallback` for stable function references:
   ```typescript
   import { useCallback, useState } from 'react'

   function QuoteContainer() {
     const [favorites, setFavorites] = useState<number[]>([])

     // Without useCallback, new function on every render
     const handleLike = useCallback((id: number) => {
       setFavorites(prev => 
         prev.includes(id) 
           ? prev.filter(fid => fid !== id)
           : [...prev, id]
       )
     }, [])  // Empty deps = stable reference

     return <QuoteList quotes={quotes} onLike={handleLike} />
   }
   ```

### Optimize List Rendering
**Purpose**: Handle large lists efficiently.

**Step-by-step:**
1. Install react-window for virtualization:
   ```bash
   npm install react-window @types/react-window
   ```

2. Implement virtualized list:
   ```typescript
   // components/VirtualizedQuoteList.tsx
   import { FixedSizeList as List } from 'react-window'
   import AutoSizer from 'react-virtualized-auto-sizer'

   interface Quote {
     id: number
     text: string
     author: string
   }

   interface RowProps {
     index: number
     style: React.CSSProperties
     data: Quote[]
   }

   const Row = ({ index, style, data }: RowProps) => {
     const quote = data[index]
     return (
       <div style={style} className="quote-row">
         <QuoteCard {...quote} />
       </div>
     )
   }

   export const VirtualizedQuoteList = ({ quotes }: { quotes: Quote[] }) => {
     return (
       <AutoSizer>
         {({ height, width }) => (
           <List
             height={height}
             itemCount={quotes.length}
             itemSize={120}  // Height of each row in pixels
             width={width}
             itemData={quotes}
           >
             {Row}
           </List>
         )}
       </AutoSizer>
     )
   }
   ```

3. Add unique keys for lists:
   ```typescript
   // Always use stable, unique keys
   {quotes.map(quote => (
     <QuoteCard key={quote.id} {...quote} />  // Good: unique ID
   ))}

   // Never use index as key for dynamic lists
   {quotes.map((quote, index) => (
     <QuoteCard key={index} {...quote} />  // Bad: causes issues
   ))}
   ```

### Implement Lazy Loading for Images
**Purpose**: Reduce initial page load and bandwidth.

**Step-by-step:**
1. Create lazy image component:
   ```typescript
   // components/LazyImage.tsx
   import { useState, useEffect, useRef } from 'react'

   interface LazyImageProps {
     src: string
     alt: string
     placeholder?: string
     className?: string
   }

   export const LazyImage = ({ 
     src, 
     alt, 
     placeholder = '/placeholder.svg',
     className = '' 
   }: LazyImageProps) => {
     const [imageSrc, setImageSrc] = useState(placeholder)
     const [isLoaded, setIsLoaded] = useState(false)
     const imgRef = useRef<HTMLImageElement>(null)

     useEffect(() => {
       const observer = new IntersectionObserver(
         (entries) => {
           entries.forEach(entry => {
             if (entry.isIntersecting) {
               setImageSrc(src)
               observer.disconnect()
             }
           })
         },
         { threshold: 0.1 }
       )

       if (imgRef.current) {
         observer.observe(imgRef.current)
       }

       return () => observer.disconnect()
     }, [src])

     return (
       <img
         ref={imgRef}
         src={imageSrc}
         alt={alt}
         className={`${className} ${isLoaded ? 'opacity-100' : 'opacity-50'} transition-opacity`}
         onLoad={() => setIsLoaded(true)}
       />
     )
   }
   ```

2. Or use native lazy loading:
   ```typescript
   <img 
     src={imageUrl} 
     alt={alt}
     loading="lazy"  // Native browser lazy loading
     decoding="async"
   />
   ```

---

## 3. State Management Optimization

### Implement Efficient Context Usage
**Purpose**: Avoid unnecessary re-renders from context changes.

**Step-by-step:**
1. Split contexts by concern:
   ```typescript
   // contexts/QuoteContext.tsx
   import { createContext, useContext, useState, ReactNode } from 'react'

   interface QuoteContextValue {
     quotes: Quote[]
     setQuotes: (quotes: Quote[]) => void
   }

   const QuoteContext = createContext<QuoteContextValue | undefined>(undefined)

   export const QuoteProvider = ({ children }: { children: ReactNode }) => {
     const [quotes, setQuotes] = useState<Quote[]>([])
     
     return (
       <QuoteContext.Provider value={{ quotes, setQuotes }}>
         {children}
       </QuoteContext.Provider>
     )
   }

   export const useQuotes = () => {
     const context = useContext(QuoteContext)
     if (!context) throw new Error('useQuotes must be used within QuoteProvider')
     return context
   }
   ```

2. Separate frequently-changing state:
   ```typescript
   // contexts/UIContext.tsx - separate from data context
   interface UIContextValue {
     isLoading: boolean
     setIsLoading: (loading: boolean) => void
     theme: 'light' | 'dark'
     toggleTheme: () => void
   }

   const UIContext = createContext<UIContextValue | undefined>(undefined)
   ```

3. Use context selectors to prevent unnecessary renders:
   ```typescript
   // Custom hook with selector
   import { useMemo } from 'react'

   export const useQuoteById = (id: number) => {
     const { quotes } = useQuotes()
     
     return useMemo(
       () => quotes.find(q => q.id === id),
       [quotes, id]
     )
   }
   ```

### Use Zustand for Performant State Management
**Purpose**: Simpler, more performant alternative to Context API.

**Step-by-step:**
1. Install Zustand:
   ```bash
   npm install zustand
   ```

2. Create store:
   ```typescript
   // stores/quoteStore.ts
   import { create } from 'zustand'
   import { devtools, persist } from 'zustand/middleware'

   interface Quote {
     id: number
     text: string
     author: string
     topics: string[]
   }

   interface QuoteState {
     quotes: Quote[]
     favorites: number[]
     filters: {
       author?: string
       topic?: string
     }
     
     // Actions
     setQuotes: (quotes: Quote[]) => void
     addFavorite: (id: number) => void
     removeFavorite: (id: number) => void
     setFilter: (key: keyof QuoteState['filters'], value: string) => void
     clearFilters: () => void
     
     // Computed values
     filteredQuotes: () => Quote[]
   }

   export const useQuoteStore = create<QuoteState>()(
     devtools(
       persist(
         (set, get) => ({
           quotes: [],
           favorites: [],
           filters: {},

           setQuotes: (quotes) => set({ quotes }),
           
           addFavorite: (id) => 
             set((state) => ({ 
               favorites: [...state.favorites, id] 
             })),
           
           removeFavorite: (id) =>
             set((state) => ({ 
               favorites: state.favorites.filter(fid => fid !== id) 
             })),
           
           setFilter: (key, value) =>
             set((state) => ({
               filters: { ...state.filters, [key]: value }
             })),
           
           clearFilters: () => set({ filters: {} }),
           
           filteredQuotes: () => {
             const { quotes, filters } = get()
             return quotes.filter(quote => {
               if (filters.author && quote.author !== filters.author) return false
               if (filters.topic && !quote.topics.includes(filters.topic)) return false
               return true
             })
           },
         }),
         { name: 'quote-storage' }  // LocalStorage key
       )
     )
   )
   ```

3. Use in components (only subscribes to used values):
   ```typescript
   // Component only re-renders when favorites change
   function FavoriteButton({ quoteId }: { quoteId: number }) {
     const favorites = useQuoteStore(state => state.favorites)
     const addFavorite = useQuoteStore(state => state.addFavorite)
     const removeFavorite = useQuoteStore(state => state.removeFavorite)
     
     const isFavorite = favorites.includes(quoteId)
     
     return (
       <button onClick={() => 
         isFavorite ? removeFavorite(quoteId) : addFavorite(quoteId)
       }>
         {isFavorite ? '★' : '☆'}
       </button>
     )
   }
   ```

---

## 4. API Communication Optimization

### Implement Request Caching with React Query
**Purpose**: Reduce redundant API calls and manage server state.

**Step-by-step:**
1. Install React Query:
   ```bash
   npm install @tanstack/react-query @tanstack/react-query-devtools
   ```

2. Setup QueryClient:
   ```typescript
   // main.tsx
   import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
   import { ReactQueryDevtools } from '@tanstack/react-query-devtools'

   const queryClient = new QueryClient({
     defaultOptions: {
       queries: {
         staleTime: 5 * 60 * 1000,  // 5 minutes
         cacheTime: 10 * 60 * 1000, // 10 minutes
         retry: 3,
         refetchOnWindowFocus: false,
       },
     },
   })

   ReactDOM.createRoot(document.getElementById('root')!).render(
     <React.StrictMode>
       <QueryClientProvider client={queryClient}>
         <App />
         <ReactQueryDevtools initialIsOpen={false} />
       </QueryClientProvider>
     </React.StrictMode>
   )
   ```

3. Create API client:
   ```typescript
   // api/client.ts
   const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

   export class ApiError extends Error {
     constructor(public status: number, message: string) {
       super(message)
       this.name = 'ApiError'
     }
   }

   async function fetchApi<T>(endpoint: string, options?: RequestInit): Promise<T> {
     const response = await fetch(`${API_BASE}${endpoint}`, {
       headers: {
         'Content-Type': 'application/json',
         ...options?.headers,
       },
       ...options,
     })

     if (!response.ok) {
       throw new ApiError(response.status, `API Error: ${response.statusText}`)
     }

     return response.json()
   }

   export const api = {
     quotes: {
       getAll: () => fetchApi<Quote[]>('/quotes/'),
       getById: (id: number) => fetchApi<Quote>(`/quotes/${id}/`),
       search: (query: string) => fetchApi<Quote[]>(`/quotes/search/?q=${query}`),
     },
     topics: {
       getAll: () => fetchApi<Topic[]>('/topics/'),
       getById: (id: number) => fetchApi<Topic>(`/topics/${id}/`),
     },
   }
   ```

4. Create query hooks:
   ```typescript
   // hooks/useQuotes.ts
   import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
   import { api } from '../api/client'

   export const useQuotes = () => {
     return useQuery({
       queryKey: ['quotes'],
       queryFn: api.quotes.getAll,
     })
   }

   export const useQuote = (id: number) => {
     return useQuery({
       queryKey: ['quote', id],
       queryFn: () => api.quotes.getById(id),
       enabled: !!id,  // Only run if id exists
     })
   }

   export const useQuoteSearch = (query: string) => {
     return useQuery({
       queryKey: ['quotes', 'search', query],
       queryFn: () => api.quotes.search(query),
       enabled: query.length > 2,  // Only search if query is long enough
       staleTime: 30000,  // 30 seconds for search results
     })
   }
   ```

5. Use in components:
   ```typescript
   function QuoteList() {
     const { data: quotes, isLoading, error } = useQuotes()

     if (isLoading) return <LoadingSpinner />
     if (error) return <ErrorMessage error={error} />
     if (!quotes) return null

     return (
       <div>
         {quotes.map(quote => (
           <QuoteCard key={quote.id} {...quote} />
         ))}
       </div>
     )
   }
   ```

### Implement Request Debouncing
**Purpose**: Reduce API calls for search/autocomplete.

**Step-by-step:**
1. Create debounce hook:
   ```typescript
   // hooks/useDebounce.ts
   import { useState, useEffect } from 'react'

   export function useDebounce<T>(value: T, delay: number = 300): T {
     const [debouncedValue, setDebouncedValue] = useState<T>(value)

     useEffect(() => {
       const handler = setTimeout(() => {
         setDebouncedValue(value)
       }, delay)

       return () => {
         clearTimeout(handler)
       }
     }, [value, delay])

     return debouncedValue
   }
   ```

2. Use in search component:
   ```typescript
   // components/QuoteSearch.tsx
   import { useState } from 'react'
   import { useDebounce } from '../hooks/useDebounce'
   import { useQuoteSearch } from '../hooks/useQuotes'

   export function QuoteSearch() {
     const [searchTerm, setSearchTerm] = useState('')
     const debouncedSearch = useDebounce(searchTerm, 500)
     
     const { data: results, isLoading } = useQuoteSearch(debouncedSearch)

     return (
       <div>
         <input
           type="text"
           value={searchTerm}
           onChange={(e) => setSearchTerm(e.target.value)}
           placeholder="Search quotes..."
           className="search-input"
         />
         {isLoading && <span>Searching...</span>}
         {results && <SearchResults results={results} />}
       </div>
     )
   }
   ```

### Implement Request Batching
**Purpose**: Combine multiple API requests into one.

**Step-by-step:**
1. Create batching utility:
   ```typescript
   // utils/batchRequests.ts
   interface BatchRequest {
     endpoint: string
     resolve: (data: any) => void
     reject: (error: any) => void
   }

   class RequestBatcher {
     private queue: BatchRequest[] = []
     private timer: NodeJS.Timeout | null = null
     private readonly delay: number = 50

     add(endpoint: string): Promise<any> {
       return new Promise((resolve, reject) => {
         this.queue.push({ endpoint, resolve, reject })
         
         if (!this.timer) {
           this.timer = setTimeout(() => this.flush(), this.delay)
         }
       })
     }

     private async flush() {
       const requests = [...this.queue]
       this.queue = []
       this.timer = null

       try {
         const response = await fetch('/api/batch/', {
           method: 'POST',
           headers: { 'Content-Type': 'application/json' },
           body: JSON.stringify({
             requests: requests.map(r => r.endpoint),
           }),
         })

         const results = await response.json()
         
         requests.forEach((req, index) => {
           req.resolve(results[index])
         })
       } catch (error) {
         requests.forEach(req => req.reject(error))
       }
     }
   }

   export const batcher = new RequestBatcher()
   ```

---

## 5. TypeScript Type Optimization

### Use Type Inference Wisely
**Purpose**: Reduce bundle size and compilation time.

**Step-by-step:**
1. Let TypeScript infer when obvious:
   ```typescript
   // Bad: Redundant type annotation
   const quotes: Quote[] = useState<Quote[]>([])

   // Good: Type is inferred
   const [quotes, setQuotes] = useState<Quote[]>([])

   // Bad: Obvious type
   const count: number = quotes.length

   // Good: Inferred
   const count = quotes.length
   ```

2. Explicitly type complex return values:
   ```typescript
   // Good: Makes intent clear
   function processQuotes(quotes: Quote[]): ProcessedQuote[] {
     return quotes.map(q => ({
       id: q.id,
       summary: q.text.slice(0, 100),
       wordCount: q.text.split(' ').length,
     }))
   }
   ```

### Use Const Assertions for Better Performance
**Purpose**: More specific types, better tree-shaking.

**Step-by-step:**
1. Use `as const` for literal values:
   ```typescript
   // Bad: Type is string
   const API_ENDPOINTS = {
     quotes: '/api/quotes/',
     topics: '/api/topics/',
   }

   // Good: Literal types
   const API_ENDPOINTS = {
     quotes: '/api/quotes/',
     topics: '/api/topics/',
   } as const

   type Endpoint = typeof API_ENDPOINTS[keyof typeof API_ENDPOINTS]
   ```

2. Use for configuration objects:
   ```typescript
   const PAGINATION_CONFIG = {
     defaultPageSize: 25,
     pageSizes: [10, 25, 50, 100],
     maxPages: 1000,
   } as const

   type PageSize = typeof PAGINATION_CONFIG['pageSizes'][number]  // 10 | 25 | 50 | 100
   ```

### Optimize Type Guards
**Purpose**: Efficient runtime type checking.

**Step-by-step:**
1. Create type guards for API responses:
   ```typescript
   // types/guards.ts
   export function isQuote(value: unknown): value is Quote {
     return (
       typeof value === 'object' &&
       value !== null &&
       'id' in value &&
       'text' in value &&
       'author' in value
     )
   }

   export function isQuoteArray(value: unknown): value is Quote[] {
     return Array.isArray(value) && value.every(isQuote)
   }
   ```

2. Use in API error handling:
   ```typescript
   async function fetchQuotes(): Promise<Quote[]> {
     const response = await fetch('/api/quotes/')
     const data = await response.json()
     
     if (!isQuoteArray(data)) {
       throw new Error('Invalid API response')
     }
     
     return data
   }
   ```

---

## 6. Tailwind CSS Optimization

### Purge Unused CSS
**Purpose**: Minimize CSS bundle size.

**Step-by-step:**
1. Configure in `tailwind.config.js`:
   ```javascript
   /** @type {import('tailwindcss').Config} */
   export default {
     content: [
       "./index.html",
       "./src/**/*.{js,ts,jsx,tsx}",
     ],
     theme: {
       extend: {},
     },
     plugins: [],
   }
   ```

2. Verify purging in production build:
   ```bash
   npm run build
   # Check build output size
   ```

### Use JIT Mode Effectively
**Purpose**: Generate only used utilities on-demand.

**Step-by-step:**
1. Use arbitrary values sparingly:
   ```typescript
   // Good: Use predefined values when possible
   <div className="w-64 h-48" />

   // Use arbitrary values only when necessary
   <div className="w-[347px] h-[234px]" />
   ```

2. Extract common patterns:
   ```typescript
   // Bad: Repeated utility classes
   <div className="px-4 py-2 bg-blue-500 text-white rounded-lg shadow-md">
   <div className="px-4 py-2 bg-blue-500 text-white rounded-lg shadow-md">

   // Good: Create reusable component
   const Button = ({ children, ...props }: ButtonProps) => (
     <button 
       className="px-4 py-2 bg-blue-500 text-white rounded-lg shadow-md hover:bg-blue-600 transition"
       {...props}
     >
       {children}
     </button>
   )
   ```

### Implement CSS Modules for Component Styles
**Purpose**: Scope styles and enable code splitting.

**Step-by-step:**
1. Create module CSS file:
   ```css
   /* QuoteCard.module.css */
   .card {
     @apply rounded-lg shadow-md p-6 bg-white;
     transition: transform 0.2s ease;
   }

   .card:hover {
     @apply shadow-lg;
     transform: translateY(-2px);
   }

   .text {
     @apply text-gray-800 text-lg leading-relaxed;
   }

   .author {
     @apply text-gray-600 text-sm font-medium mt-4;
   }
   ```

2. Use in component:
   ```typescript
   // QuoteCard.tsx
   import styles from './QuoteCard.module.css'

   export const QuoteCard = ({ text, author }: QuoteCardProps) => (
     <div className={styles.card}>
       <p className={styles.text}>{text}</p>
       <span className={styles.author}>— {author}</span>
     </div>
   )
   ```

---

## 7. Web Performance APIs

### Implement Intersection Observer for Lazy Loading
**Purpose**: Load content when visible in viewport.

**Step-by-step:**
1. Create custom hook:
   ```typescript
   // hooks/useInView.ts
   import { useState, useEffect, useRef, RefObject } from 'react'

   interface UseInViewOptions {
     threshold?: number
     rootMargin?: string
     triggerOnce?: boolean
   }

   export function useInView<T extends HTMLElement>(
     options: UseInViewOptions = {}
   ): [RefObject<T>, boolean] {
     const { threshold = 0, rootMargin = '0px', triggerOnce = false } = options
     const ref = useRef<T>(null)
     const [inView, setInView] = useState(false)

     useEffect(() => {
       const element = ref.current
       if (!element) return

       const observer = new IntersectionObserver(
         ([entry]) => {
           const isInView = entry.isIntersecting
           setInView(isInView)
           
           if (isInView && triggerOnce) {
             observer.disconnect()
           }
         },
         { threshold, rootMargin }
       )

       observer.observe(element)

       return () => observer.disconnect()
     }, [threshold, rootMargin, triggerOnce])

     return [ref, inView]
   }
   ```

2. Use for lazy loading:
   ```typescript
   // components/LazyQuoteSection.tsx
   import { useInView } from '../hooks/useInView'

   export const LazyQuoteSection = ({ topicId }: { topicId: number }) => {
     const [ref, inView] = useInView<HTMLDivElement>({
       threshold: 0.1,
       triggerOnce: true,
     })

     const { data: quotes } = useQuery({
       queryKey: ['quotes', topicId],
       queryFn: () => api.quotes.getByTopic(topicId),
       enabled: inView,  // Only fetch when visible
     })

     return (
       <div ref={ref}>
         {inView ? (
           quotes ? <QuoteList quotes={quotes} /> : <LoadingSpinner />
         ) : (
           <div className="h-96" /> // Placeholder
         )}
       </div>
     )
   }
   ```

### Implement Resource Hints
**Purpose**: Optimize resource loading priority.

**Step-by-step:**
1. Add to `index.html`:
   ```html
   <!DOCTYPE html>
   <html lang="en">
     <head>
       <meta charset="UTF-8" />
       <meta name="viewport" content="width=device-width, initial-scale=1.0" />
       
       <!-- Preconnect to API -->
       <link rel="preconnect" href="https://api.wisdombook.com" />
       <link rel="dns-prefetch" href="https://api.wisdombook.com" />
       
       <!-- Preload critical fonts -->
       <link 
         rel="preload" 
         href="/fonts/inter-var.woff2" 
         as="font" 
         type="font/woff2" 
         crossorigin 
       />
       
       <title>Wisdom Book</title>
     </head>
     <body>
       <div id="root"></div>
       <script type="module" src="/src/main.tsx"></script>
     </body>
   </html>
   ```

2. Dynamically add preload hints:
   ```typescript
   // utils/resourceHints.ts
   export function preloadImage(url: string): void {
     const link = document.createElement('link')
     link.rel = 'preload'
     link.as = 'image'
     link.href = url
     document.head.appendChild(link)
   }

   export function prefetchRoute(path: string): void {
     const link = document.createElement('link')
     link.rel = 'prefetch'
     link.href = path
     document.head.appendChild(link)
   }
   ```

### Implement Performance Monitoring
**Purpose**: Track and optimize real-world performance.

**Step-by-step:**
1. Create performance utility:
   ```typescript
   // utils/performance.ts
   export class PerformanceMonitor {
     private static marks = new Map<string, number>()

     static mark(name: string): void {
       this.marks.set(name, performance.now())
     }

     static measure(name: string, startMark: string): number {
       const start = this.marks.get(startMark)
       if (!start) {
         console.warn(`Start mark "${startMark}" not found`)
         return 0
       }

       const duration = performance.now() - start
       
       if (import.meta.env.DEV) {
         console.log(`${name}: ${duration.toFixed(2)}ms`)
       }

       // Send to analytics in production
       if (import.meta.env.PROD) {
         this.sendToAnalytics(name, duration)
       }

       return duration
     }

     private static sendToAnalytics(name: string, duration: number): void {
       // Send to your analytics service
       navigator.sendBeacon('/api/analytics/performance', JSON.stringify({
         metric: name,
         duration,
         timestamp: Date.now(),
       }))
     }

     static observeLCP(): void {
       if (!('PerformanceObserver' in window)) return

       const observer = new PerformanceObserver((list) => {
         const entries = list.getEntries()
         const lastEntry = entries[entries.length - 1]
         
         console.log('LCP:', lastEntry.startTime)
         this.sendToAnalytics('lcp', lastEntry.startTime)
       })

       observer.observe({ entryTypes: ['largest-contentful-paint'] })
     }

     static observeFID(): void {
       if (!('PerformanceObserver' in window)) return

       const observer = new PerformanceObserver((list) => {
         const entries = list.getEntries()
         entries.forEach((entry: any) => {
           console.log('FID:', entry.processingStart - entry.startTime)
           this.sendToAnalytics('fid', entry.processingStart - entry.startTime)
         })
       })

       observer.observe({ entryTypes: ['first-input'] })
     }
   }
   ```

2. Use in app:
   ```typescript
   // App.tsx
   import { useEffect } from 'react'
   import { PerformanceMonitor } from './utils/performance'

   function App() {
     useEffect(() => {
       PerformanceMonitor.observeLCP()
       PerformanceMonitor.observeFID()
     }, [])

     return <div>...</div>
   }
   ```

3. Track component render times:
   ```typescript
   function ExpensiveComponent() {
     useEffect(() => {
       PerformanceMonitor.mark('expensive-component-start')
       
       return () => {
         PerformanceMonitor.measure(
           'ExpensiveComponent render',
           'expensive-component-start'
         )
       }
     })

     return <div>...</div>
   }
   ```

---

## 8. Error Boundaries and Error Handling

### Implement Error Boundaries
**Purpose**: Gracefully handle component errors without crashing app.

**Step-by-step:**
1. Create error boundary component:
   ```typescript
   // components/ErrorBoundary.tsx
   import { Component, ErrorInfo, ReactNode } from 'react'

   interface Props {
     children: ReactNode
     fallback?: ReactNode
     onError?: (error: Error, errorInfo: ErrorInfo) => void
   }

   interface State {
     hasError: boolean
     error?: Error
   }

   export class ErrorBoundary extends Component<Props, State> {
     constructor(props: Props) {
       super(props)
       this.state = { hasError: false }
     }

     static getDerivedStateFromError(error: Error): State {
       return { hasError: true, error }
     }

     componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
       console.error('Error caught by boundary:', error, errorInfo)
       this.props.onError?.(error, errorInfo)
       
       // Log to error tracking service
       if (import.meta.env.PROD) {
         // logErrorToService(error, errorInfo)
       }
     }

     render() {
       if (this.state.hasError) {
         return this.props.fallback || (
           <div className="error-container">
             <h2>Something went wrong</h2>
             <details>
               <summary>Error details</summary>
               <pre>{this.state.error?.message}</pre>
             </details>
             <button onClick={() => this.setState({ hasError: false })}>
               Try again
             </button>
           </div>
         )
       }

       return this.props.children
     }
   }
   ```

2. Use in app structure:
   ```typescript
   // App.tsx
   function App() {
     return (
       <ErrorBoundary>
         <Suspense fallback={<LoadingSpinner />}>
           <Routes>
             <Route path="/" element={
               <ErrorBoundary fallback={<RouteError />}>
                 <QuoteList />
               </ErrorBoundary>
             } />
           </Routes>
         </Suspense>
       </ErrorBoundary>
     )
   }
   ```

---

## 9. Web Workers for Heavy Processing

### Offload Processing to Web Workers
**Purpose**: Keep UI responsive during heavy computations.

**Step-by-step:**
1. Create worker file:
   ```typescript
   // workers/quote-processor.worker.ts
   interface Quote {
     id: number
     text: string
     author: string
   }

   interface ProcessMessage {
     type: 'process'
     quotes: Quote[]
   }

   self.onmessage = (e: MessageEvent<ProcessMessage>) => {
     const { type, quotes } = e.data

     if (type === 'process') {
       // Heavy processing
       const processed = quotes.map(quote => ({
         ...quote,
         wordCount: quote.text.split(' ').length,
         sentiment: analyzeSentiment(quote.text),
         keywords: extractKeywords(quote.text),
       }))

       self.postMessage({ type: 'result', data: processed })
     }
   }

   function analyzeSentiment(text: string): number {
     // Complex sentiment analysis
     return 0.5
   }

   function extractKeywords(text: string): string[] {
     // Complex keyword extraction
     return []
   }
   ```

2. Create worker hook:
   ```typescript
   // hooks/useWorker.ts
   import { useEffect, useRef, useState } from 'react'

   export function useWorker<T, R>(
     workerPath: string
   ): [(data: T) => void, R | null, boolean, Error | null] {
     const workerRef = useRef<Worker>()
     const [result, setResult] = useState<R | null>(null)
     const [isProcessing, setIsProcessing] = useState(false)
     const [error, setError] = useState<Error | null>(null)

     useEffect(() => {
       workerRef.current = new Worker(
         new URL(workerPath, import.meta.url),
         { type: 'module' }
       )

       workerRef.current.onmessage = (e: MessageEvent) => {
         setResult(e.data.data)
         setIsProcessing(false)
       }

       workerRef.current.onerror = (e: ErrorEvent) => {
         setError(new Error(e.message))
         setIsProcessing(false)
       }

       return () => workerRef.current?.terminate()
     }, [workerPath])

     const postMessage = (data: T) => {
       setIsProcessing(true)
       setError(null)
       workerRef.current?.postMessage({ type: 'process', ...data })
     }

     return [postMessage, result, isProcessing, error]
   }
   ```

3. Use in component:
   ```typescript
   // components/QuoteProcessor.tsx
   import { useWorker } from '../hooks/useWorker'

   export function QuoteProcessor({ quotes }: { quotes: Quote[] }) {
     const [processQuotes, processed, isProcessing] = useWorker
       { quotes: Quote[] },
       ProcessedQuote[]
     >('../workers/quote-processor.worker.ts')

     useEffect(() => {
       if (quotes.length > 0) {
         processQuotes({ quotes })
       }
     }, [quotes, processQuotes])

     if (isProcessing) return <LoadingSpinner />
     if (!processed) return null

     return <ProcessedQuoteList quotes={processed} />
   }
   ```

---

## 10. Environment Configuration

### Optimize Environment Variables
**Purpose**: Proper configuration for different environments.

**Step-by-step:**
1. Create `.env` files:
   ```bash
   # .env.development
   VITE_API_URL=http://localhost:8000/api
   VITE_ENABLE_DEVTOOLS=true
   VITE_LOG_LEVEL=debug

   # .env.production
   VITE_API_URL=https://api.wisdombook.com
   VITE_ENABLE_DEVTOOLS=false
   VITE_LOG_LEVEL=error
   ```

2. Create type-safe env config:
   ```typescript
   // config/env.ts
   interface Config {
     apiUrl: string
     enableDevtools: boolean
     logLevel: 'debug' | 'info' | 'warn' | 'error'
     isDevelopment: boolean
     isProduction: boolean
   }

   function getEnvVar(key: string, defaultValue?: string): string {
     const value = import.meta.env[key] ?? defaultValue
     if (value === undefined) {
       throw new Error(`Environment variable ${key} is required`)
     }
     return value
   }

   export const config: Config = {
     apiUrl: getEnvVar('VITE_API_URL'),
     enableDevtools: getEnvVar('VITE_ENABLE_DEVTOOLS') === 'true',
     logLevel: getEnvVar('VITE_LOG_LEVEL', 'info') as Config['logLevel'],
     isDevelopment: import.meta.env.DEV,
     isProduction: import.meta.env.PROD,
   }
   ```

3. Use throughout app:
   ```typescript
   // api/client.ts
   import { config } from '../config/env'

   const API_BASE = config.apiUrl

   export const api = {
     // ... implementation
   }
   ```

---

These TypeScript optimization practices should significantly improve your Django + React frontend performance. Focus first on React Query for API optimization, proper memoization for preventing re-renders, and code splitting for reducing initial bundle size. Use the bundle analyzer to identify specific bottlenecks in your application.
