# Start Here Page - Text Styles

This document outlines the text styles used in the **Start Here!** page of the Wisdom Book application, based on `StartHere.tsx`, `index.css`, and `tailwind.config.js`.

## Global Font Family
- **Sans**: `Google Sans`, `Roboto`, `sans-serif`

## Headings
### `<h1>` (Main Title)
- **Size**: `text-4xl` (36px)
- **Weight**: `font-normal` (400)
- **Line Height**: `leading-tight` (1.25)
- **Spacing**: `mb-4` (16px bottom margin)
- **Color**: Inherits `text-text-primary` (#e8eaed) from body

### `<h2>` (Section Headers)
- **Size**: `text-2xl` (24px)
- **Weight**: `font-normal` (400)
- **Color**: `text-text-primary` (#e8eaed)
- **Spacing**: `mt-8` (32px top margin), `mb-4` (16px bottom margin)

## Body Text
### `<p>` (Paragraphs)
- **Size**: `text-base` (16px)
- **Color**: `text-text-secondary` (#9aa0a6)
- **Opacity**: `75%`
- **Line Height**: `leading-relaxed` (1.625)
- **Spacing**: `mb-6` (24px bottom margin)

## Lists
### `<ul>` (Unordered Lists)
- **Style**: `list-disc`
- **Color**: `text-text-secondary` (#9aa0a6)
- **Spacing**: `pl-5` (20px left padding), `mb-6` (24px bottom margin)

## Links
### `<a>`
- **Color**: `text-accent` (#8ab4f8)
- **Decoration**: `no-underline` (default), `underline` (on hover)

## Color Reference
- **Primary Text**: `#e8eaed`
- **Secondary Text**: `#9aa0a6`
- **Accent Blue**: `#8ab4f8`
