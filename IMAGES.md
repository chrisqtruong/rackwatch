# Image policy

Posts may carry one optional image, shown under the headline in the feed and the archive with a caption (credit, license, and a link to the source). Images are included only where they fit: a plain, relevant, documentary picture. Otherwise a post has no image.

## Data shape

Add an `img` object to a feed post in `docs/data.json`:

```json
"img": {
  "u": "https://…",        // direct https URL of the image file (about 1200px wide)
  "alt": "What the image shows, for screen readers",
  "credit": "Photographer or agency, as the license asks",
  "lic": "Public domain | CC BY 4.0 | CC BY-SA 3.0 | …",
  "page": "https://…"      // the page where the image and its license are listed
}
```

## What is allowed

- Public-domain U.S. government works (court buildings, agency seals and headquarters, official portraits).
- Wikimedia Commons files under a free license (public domain, CC0, CC BY, CC BY-SA), with the license verified on the file page and the credit the license requires.
- Images we make ourselves.

## What is not

- Photos taken from news articles, wire services, or social media, even when credited. A credit is not a license.
- Company logos and press photos, unless the company's own terms clearly allow reuse.
- Images of private individuals, or any image that implies endorsement or guilt (defendants are "charged" until convicted).
- Anything that does not match the site's plain, documentary look: stock art, memes, heavily edited or decorative images.

## Process

1. Find the image and open its file page. Confirm the license, author and credit line.
2. Use the direct image URL you actually saw on that page. Never guess a URL.
3. Write a short factual alt text; never put claims about the story in it.
4. When unsure about rights or fit, leave the image out.
