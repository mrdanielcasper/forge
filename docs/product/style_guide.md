# Visual Style Guide

## Global Accessibility (WCAG) Constraint
- **Contrast Ratios:** All text and interactive background colors defined in this document MUST pass a minimum WCAG AA contrast ratio (4.5:1 for normal text, 3:1 for large text/UI components). 
- If an AI agent detects a contrast violation in these foundational tokens, it must FLAG the issue to the founder immediately and halt UI generation.

## Brand Identity & Vibe
- **Vibe:** Clean, dense, utility-focused, enterprise-grade. No playful elements.
- **Border Radius:** `rounded-md` (medium). Do not use `rounded-full` or large pill shapes.

## Color Palette (Tailwind Tokens)
- **Primary:** Deep slate blue. Use `bg-primary` for main actions.
- **Secondary:** Muted gray. Use `bg-secondary` for secondary actions.
- **Destructive:** Standard red. Use `bg-destructive` for delete actions.
- **Background:** White for main canvas, light gray (`bg-muted`) for secondary panels.

## Typography
- **Font Family:** Inter (Sans-serif).
- **Headings:** Bold, tight tracking. Do not use extremely large fonts (max `text-3xl`).
- **Body:** `text-sm` for dense data tables, `text-base` for standard reading.

## Component Rules
- **Buttons:** Always use standard variants (`default`, `outline`, `ghost`, `destructive`).
- **Forms:** Labels must be `text-sm font-medium`. Inputs must have `border-input` and focus rings.
- **Icons:** Use `lucide-react`. Size must match text size (usually `w-4 h-4`).