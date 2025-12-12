I'll provide comprehensive best practices for optimizing Python code in Django web applications, with detailed implementation steps for each.

## 1. Database Query Optimization

### Use `select_related()` and `prefetch_related()`
**Purpose**: Reduce N+1 query problems by fetching related objects in fewer queries.

**Step-by-step:**
1. Identify relationships in your models (ForeignKey, OneToOne, ManyToMany)
2. For ForeignKey/OneToOne, use `select_related()`:
   ```python
   # Bad: Creates N+1 queries
   quotes = Quote.objects.all()
   for quote in quotes:
       print(quote.author.name)  # Each iteration hits DB
   
   # Good: Single JOIN query
   quotes = Quote.objects.select_related('author').all()
   ```
3. For ManyToMany/reverse ForeignKey, use `prefetch_related()`:
   ```python
   # Good: Two queries total
   topics = Topic.objects.prefetch_related('quotes').all()
   ```
4. Chain them for complex relationships:
   ```python
   Quote.objects.select_related('author').prefetch_related('topics')
   ```

### Use `only()` and `defer()`
**Purpose**: Fetch only needed fields to reduce memory and transfer overhead.

**Step-by-step:**
1. Analyze which fields your view actually uses
2. Use `only()` to fetch specific fields:
   ```python
   # Only fetch id and text fields
   quotes = Quote.objects.only('id', 'text')
   ```
3. Use `defer()` to exclude heavy fields:
   ```python
   # Skip large fields you don't need
   quotes = Quote.objects.defer('metadata', 'full_context')
   ```
4. Be cautious: accessing deferred fields triggers additional queries

### Implement Database Indexing
**Purpose**: Speed up query lookups on frequently searched fields.

**Step-by-step:**
1. Identify frequently queried fields (filters, lookups, ordering)
2. Add indexes in your models:
   ```python
   class Quote(models.Model):
       text = models.TextField()
       author = models.CharField(max_length=200, db_index=True)
       created_at = models.DateTimeField(db_index=True)
       
       class Meta:
           indexes = [
               models.Index(fields=['author', 'created_at']),
               models.Index(fields=['-created_at']),  # Descending
           ]
   ```
3. Create migration: `python manage.py makemigrations`
4. Apply migration: `python manage.py migrate`
5. Monitor index usage with `EXPLAIN` queries

### Use `values()` and `values_list()` for Data Extraction
**Purpose**: Fetch dictionaries/tuples instead of model instances when you don't need the full ORM overhead.

**Step-by-step:**
1. For dictionary results, use `values()`:
   ```python
   # Returns [{'id': 1, 'text': '...'}, ...]
   quotes = Quote.objects.values('id', 'text', 'author__name')
   ```
2. For tuple results, use `values_list()`:
   ```python
   # Returns [(1, 'text1'), (2, 'text2'), ...]
   quote_ids = Quote.objects.values_list('id', 'text')
   
   # For single column, use flat=True
   ids = Quote.objects.values_list('id', flat=True)
   ```
3. Use when passing data directly to serializers or templates

### Implement Query Result Caching
**Purpose**: Avoid re-executing identical queries.

**Step-by-step:**
1. Install caching backend (Redis recommended):
   ```bash
   pip install django-redis
   ```
2. Configure in `settings.py`:
   ```python
   CACHES = {
       'default': {
           'BACKEND': 'django_redis.cache.RedisCache',
           'LOCATION': 'redis://127.0.0.1:6379/1',
           'OPTIONS': {
               'CLIENT_CLASS': 'django_redis.client.DefaultClient',
           }
       }
   }
   ```
3. Cache querysets in views:
   ```python
   from django.core.cache import cache
   
   def get_quotes():
       cache_key = 'all_quotes'
       quotes = cache.get(cache_key)
       
       if quotes is None:
           quotes = list(Quote.objects.select_related('author').all())
           cache.set(cache_key, quotes, 3600)  # Cache for 1 hour
       
       return quotes
   ```
4. Invalidate cache when data changes:
   ```python
   from django.db.models.signals import post_save
   from django.dispatch import receiver
   
   @receiver(post_save, sender=Quote)
   def invalidate_quote_cache(sender, **kwargs):
       cache.delete('all_quotes')
   ```

---

## 2. Middleware and Request Processing

### Use Conditional Middleware
**Purpose**: Avoid unnecessary middleware processing.

**Step-by-step:**
1. Review `MIDDLEWARE` in `settings.py`
2. Remove unused middleware
3. Order middleware efficiently (lightweight first):
   ```python
   MIDDLEWARE = [
       'django.middleware.security.SecurityMiddleware',
       'django.middleware.gzip.GZipMiddleware',  # Compress early
       'django.middleware.http.ConditionalGetMiddleware',
       # ... other middleware
   ]
   ```
4. Create custom middleware that short-circuits when possible:
   ```python
   class EarlyReturnMiddleware:
       def __init__(self, get_response):
           self.get_response = get_response
       
       def __call__(self, request):
           if request.path.startswith('/health/'):
               return HttpResponse('OK')
           return self.get_response(request)
   ```

### Enable GZip Compression
**Purpose**: Reduce response size for faster transfers.

**Step-by-step:**
1. Add to `MIDDLEWARE` (near the top):
   ```python
   MIDDLEWARE = [
       'django.middleware.gzip.GZipMiddleware',
       # ... other middleware
   ]
   ```
2. Configure minimum size to compress:
   ```python
   # In settings.py
   GZIP_COMPRESSOR_MIN_SIZE = 1024  # Only compress responses > 1KB
   ```

---

## 3. Template Optimization

### Cache Template Fragments
**Purpose**: Avoid re-rendering expensive template sections.

**Step-by-step:**
1. Identify slow-rendering template sections
2. Wrap them with cache tags:
   ```django
   {% load cache %}
   
   {% cache 3600 quote_list %}
       {% for quote in quotes %}
           <div class="quote">{{ quote.text }}</div>
       {% endfor %}
   {% endcache %}
   ```
3. Use dynamic cache keys:
   ```django
   {% cache 3600 quote_detail quote.id %}
       {{ quote.text }}
   {% endcache %}
   ```
4. Vary cache by user or language:
   ```django
   {% cache 3600 quotes user.id request.LANGUAGE_CODE %}
   ```

### Use Template Fragment Caching with Conditions
**Purpose**: Cache only when beneficial.

**Step-by-step:**
1. Check if data changes frequently
2. Skip caching for personalized content
3. Implement smart invalidation:
   ```python
   # In views.py
   def quote_detail(request, quote_id):
       cache_version = cache.get(f'quote_{quote_id}_version', 1)
       context = {
           'quote': get_object_or_404(Quote, pk=quote_id),
           'cache_version': cache_version,
       }
       return render(request, 'quote.html', context)
   ```
   ```django
   {% cache 3600 quote_detail quote.id cache_version %}
   ```

---

## 4. Python Code Optimization

### Use List Comprehensions Instead of Loops
**Purpose**: Faster execution through C-optimized operations.

**Step-by-step:**
1. Identify simple for-loops that build lists
2. Convert to list comprehension:
   ```python
   # Slow
   result = []
   for quote in quotes:
       result.append(quote.text.upper())
   
   # Fast
   result = [quote.text.upper() for quote in quotes]
   ```
3. Use generator expressions for large datasets:
   ```python
   # Memory efficient
   result = (quote.text.upper() for quote in quotes)
   ```

### Leverage `bulk_create()` and `bulk_update()`
**Purpose**: Reduce database round trips for multiple inserts/updates.

**Step-by-step:**
1. Collect objects to create:
   ```python
   quotes_to_create = [
       Quote(text=text, author=author)
       for text, author in data_list
   ]
   ```
2. Use `bulk_create()`:
   ```python
   Quote.objects.bulk_create(quotes_to_create, batch_size=1000)
   ```
3. For updates, use `bulk_update()`:
   ```python
   quotes = Quote.objects.all()
   for quote in quotes:
       quote.view_count += 1
   
   Quote.objects.bulk_update(quotes, ['view_count'], batch_size=1000)
   ```

### Use `F()` Expressions for Atomic Updates
**Purpose**: Perform calculations at database level, avoid race conditions.

**Step-by-step:**
1. Import F expression:
   ```python
   from django.db.models import F
   ```
2. Use for atomic increments:
   ```python
   # Bad: Race condition possible
   quote = Quote.objects.get(pk=1)
   quote.view_count += 1
   quote.save()
   
   # Good: Atomic database operation
   Quote.objects.filter(pk=1).update(view_count=F('view_count') + 1)
   ```
3. Use in complex calculations:
   ```python
   Quote.objects.filter(popularity__lt=F('view_count') * 2).update(
       popularity=F('view_count') * 2
   )
   ```

### Implement Lazy Evaluation
**Purpose**: Defer expensive operations until absolutely necessary.

**Step-by-step:**
1. Use `@property` with caching:
   ```python
   from functools import cached_property
   
   class Quote(models.Model):
       text = models.TextField()
       
       @cached_property
       def word_count(self):
           return len(self.text.split())
   ```
2. Use Django's `SimpleLazyObject`:
   ```python
   from django.utils.functional import SimpleLazyObject
   
   def expensive_calculation():
       # Heavy processing
       return result
   
   lazy_result = SimpleLazyObject(expensive_calculation)
   ```

---

## 5. Asynchronous Processing

### Implement Celery for Background Tasks
**Purpose**: Offload time-consuming operations from request/response cycle.

**Step-by-step:**
1. Install Celery:
   ```bash
   pip install celery redis
   ```
2. Create `celery.py` in project root:
   ```python
   from celery import Celery
   import os
   
   os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wisdom_book.settings')
   
   app = Celery('wisdom_book')
   app.config_from_object('django.conf:settings', namespace='CELERY')
   app.autodiscover_tasks()
   ```
3. Configure in `settings.py`:
   ```python
   CELERY_BROKER_URL = 'redis://localhost:6379/0'
   CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
   ```
4. Create tasks in `tasks.py`:
   ```python
   from celery import shared_task
   
   @shared_task
   def sync_from_neo4j():
       # Heavy Neo4j to Postgres sync
       pass
   ```
5. Call tasks asynchronously:
   ```python
   sync_from_neo4j.delay()
   ```
6. Run worker: `celery -A wisdom_book worker -l info`

### Use Django Async Views (Django 3.1+)
**Purpose**: Handle concurrent requests efficiently.

**Step-by-step:**
1. Define async view:
   ```python
   import asyncio
   from django.http import JsonResponse
   
   async def async_quote_list(request):
       quotes = await sync_to_async(list)(
           Quote.objects.all()[:10]
       )
       return JsonResponse({'quotes': quotes})
   ```
2. Configure ASGI in `asgi.py`:
   ```python
   import os
   from django.core.asgi import get_asgi_application
   
   os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wisdom_book.settings')
   application = get_asgi_application()
   ```
3. Run with ASGI server:
   ```bash
   pip install uvicorn
   uvicorn wisdom_book.asgi:application
   ```

---

## 6. Static Files and Asset Management

### Use Django Compressor
**Purpose**: Minify and combine CSS/JS files.

**Step-by-step:**
1. Install:
   ```bash
   pip install django-compressor
   ```
2. Add to `INSTALLED_APPS`:
   ```python
   INSTALLED_APPS = [
       # ...
       'compressor',
   ]
   ```
3. Configure:
   ```python
   COMPRESS_ENABLED = True
   COMPRESS_OFFLINE = True
   STATICFILES_FINDERS = [
       'django.contrib.staticfiles.finders.FileSystemFinder',
       'django.contrib.staticfiles.finders.AppDirectoriesFinder',
       'compressor.finders.CompressorFinder',
   ]
   ```
4. Use in templates:
   ```django
   {% load compress %}
   
   {% compress css %}
       <link rel="stylesheet" href="{% static 'css/style.css' %}">
   {% endcompress %}
   ```
5. Collect static: `python manage.py collectstatic`

### Enable Browser Caching
**Purpose**: Reduce server requests for static assets.

**Step-by-step:**
1. Configure `ManifestStaticFilesStorage`:
   ```python
   STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'
   ```
2. Add cache headers in web server (nginx example):
   ```nginx
   location /static/ {
       expires 1y;
       add_header Cache-Control "public, immutable";
   }
   ```

---

## 7. Connection Pooling

### Implement Database Connection Pooling
**Purpose**: Reuse database connections to reduce overhead.

**Step-by-step:**
1. For PostgreSQL, install:
   ```bash
   pip install psycopg2-binary django-db-connection-pool
   ```
2. Update `DATABASES` in settings:
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django_db_connection_pool.backends.postgresql',
           'NAME': 'wisdom_book',
           'USER': 'user',
           'PASSWORD': 'password',
           'HOST': 'localhost',
           'PORT': '5432',
           'POOL_OPTIONS': {
               'POOL_SIZE': 10,
               'MAX_OVERFLOW': 5,
           }
       }
   }
   ```
3. Monitor connection usage with Django Debug Toolbar

---

## 8. Profiling and Monitoring

### Use Django Debug Toolbar
**Purpose**: Identify performance bottlenecks.

**Step-by-step:**
1. Install:
   ```bash
   pip install django-debug-toolbar
   ```
2. Add to `INSTALLED_APPS`:
   ```python
   INSTALLED_APPS = [
       # ...
       'debug_toolbar',
   ]
   ```
3. Add middleware:
   ```python
   MIDDLEWARE = [
       'debug_toolbar.middleware.DebugToolbarMiddleware',
       # ...
   ]
   ```
4. Configure URLs:
   ```python
   if settings.DEBUG:
       import debug_toolbar
       urlpatterns += [path('__debug__/', include(debug_toolbar.urls))]
   ```
5. Set internal IPs:
   ```python
   INTERNAL_IPS = ['127.0.0.1']
   ```
6. Run server and check SQL panel for N+1 queries

### Implement Application Performance Monitoring
**Purpose**: Track production performance issues.

**Step-by-step:**
1. Install Sentry or similar:
   ```bash
   pip install sentry-sdk
   ```
2. Configure in `settings.py`:
   ```python
   import sentry_sdk
   from sentry_sdk.integrations.django import DjangoIntegration
   
   sentry_sdk.init(
       dsn="your-dsn-here",
       integrations=[DjangoIntegration()],
       traces_sample_rate=0.1,
       send_default_pii=True
   )
   ```

---

## 9. Memory Management

### Use Queryset Iteration Efficiently
**Purpose**: Avoid loading entire result sets into memory.

**Step-by-step:**
1. Use `iterator()` for large querysets:
   ```python
   # Bad: Loads all quotes into memory
   for quote in Quote.objects.all():
       process(quote)
   
   # Good: Fetches in chunks
   for quote in Quote.objects.all().iterator(chunk_size=1000):
       process(quote)
   ```
2. Disable result caching when not needed:
   ```python
   quotes = Quote.objects.all().iterator()
   ```

### Implement Pagination
**Purpose**: Limit memory usage per request.

**Step-by-step:**
1. Use Django's Paginator:
   ```python
   from django.core.paginator import Paginator
   
   def quote_list(request):
       quote_list = Quote.objects.all()
       paginator = Paginator(quote_list, 25)  # 25 per page
       
       page_number = request.GET.get('page')
       quotes = paginator.get_page(page_number)
       
       return render(request, 'quotes.html', {'quotes': quotes})
   ```
2. For APIs, use Django REST Framework pagination:
   ```python
   REST_FRAMEWORK = {
       'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
       'PAGE_SIZE': 100
   }
   ```

---

## 10. Code-Level Optimizations

### Use Appropriate Data Structures
**Purpose**: Choose the right tool for the operation.

**Step-by-step:**
1. Use sets for membership testing:
   ```python
   # Slow: O(n)
   if quote_id in quote_list:
       pass
   
   # Fast: O(1)
   quote_ids = set(quote_list)
   if quote_id in quote_ids:
       pass
   ```
2. Use dictionaries for lookups:
   ```python
   # Create lookup dict
   quotes_by_id = {q.id: q for q in quotes}
   quote = quotes_by_id.get(quote_id)
   ```

### Minimize Database Queries in Loops
**Purpose**: Avoid the N+1 problem.

**Step-by-step:**
1. Identify queries inside loops
2. Fetch all data upfront:
   ```python
   # Bad
   for topic in topics:
       quotes = Quote.objects.filter(topic=topic)
   
   # Good
   from django.db.models import Prefetch
   
   topics = Topic.objects.prefetch_related(
       Prefetch('quotes', queryset=Quote.objects.select_related('author'))
   )
   ```

---

These practices should significantly improve your Django application's performance. Start with database query optimization and caching, as those typically provide the biggest wins. Use profiling tools to identify your specific bottlenecks before optimizing.
