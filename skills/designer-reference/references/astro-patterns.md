# EmDash Content Patterns

Reference for astro-specific patterns the designer needs when recommending page layouts. These are the patterns the site-builder implements — the designer recommends which to use.

## Content Query Pattern

```astro
---
import { getEmDashCollection, type EmDashEntry } from "emdash";
import { Image, PortableText, EmDashHead } from "emdash/ui";
import type { CacheHint } from "astro";

const cacheHint: CacheHint = { maxAge: 60 };

// List query — for blog index, archives, home pages
const posts = await Astro.cache.set(
	"posts:list",
	() => getEmDashCollection("posts", {
		limit: 10,
		status: "published",
		locale: Astro.locals.emdash.locale,
	}),
	cacheHint
);

// Single entry query — for blog post pages
export async function getEmDashEntry(collection: string, slug: string) {
	const entry = await Astro.cache.set(
		`${collection}:${slug}`,
		() => getEmDashCollection(collection, {
			slug,
			limit: 1,
			locale: Astro.locals.emdash.locale,
		}),
		cacheHint
	);
	return entry.items[0];
}
---
```

## Image Fields

Image fields are objects, not strings:

```astro
<!-- CORRECT -->
<Image image={post.data.featured_image} />

<!-- WRONG — renders [object Object] -->
<img src={post.data.featured_image} />
```

Image object shape: `{ id: string, src: string, alt: string }`

## ID vs Slug

| Property        | Value       | Use for                                          |
| --------------- | ----------- | ------------------------------------------------ |
| `entry.id`      | Slug string | URLs: `href={`/blog/${entry.id}`}`               |
| `entry.data.id` | ULID string | API calls, comments: `contentId={entry.data.id}` |

## Taxonomy Pattern

```astro
---
const categories = await getEmDashCollection("categories", {
	locale: Astro.locals.emdash.locale,
	limit: 50,
});
---

<!-- Category list / filter -->
<ul>
	{categories.items.map(cat => (
		<li>
			<a href={`/categories/${cat.id}`}>
				{cat.data.name} ({cat.data.count ?? 0})
			</a>
		</li>
	))}
</ul>
```

Taxonomy names match the seed exactly. `categories` ≠ `category`.

## Menu Pattern

```astro
---
import { getMenu } from "emdash";
---
<nav>
	{getMenu("main").map(item => (
		<a href={item.href}>{item.label}</a>
	))}
</nav>
```

## Widget Areas

```astro
---
import { WidgetArea } from "emdash/ui";
---
<aside>
	<WidgetArea name="sidebar" />
</aside>
```

## Comments

```astro
---
import { CommentForm, Comments } from "emdash/ui";
---
<Comments contentId={post.data.id} />
<CommentForm contentId={post.data.id} />
```

## Search

```astro
---
import { LiveSearch } from "emdash/ui/search";
---
<LiveSearch collection="posts" />
```

## SEO

```astro
<EmDashHead entry={post} />
```

## Caching

Every content query on a server-rendered page must use `Astro.cache.set(cacheHint)`. Without it, pages re-query on every request.

## RTL Note

All layout must use logical Tailwind classes. Kumo components handle this internally. For custom layout:

```
padding-left → ps-*
padding-right → pe-*
margin-left → ms-*
margin-right → me-*
text-left → text-start
text-right → text-end
border-left → border-s
border-right → border-e
```
