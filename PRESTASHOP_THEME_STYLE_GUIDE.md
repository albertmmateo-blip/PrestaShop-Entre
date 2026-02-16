# Entretelas PrestaShop Theme Style Guide

**Document Purpose:** This guide provides a comprehensive overview of the Entretelas website's CSS framework to serve as inspiration for creating a new custom PrestaShop theme based on the Hummingbird theme.

**Implementation Strategy:** This guide is structured to enable conservative, incremental theme development. Start with core brand elements (colors, fonts) and progressively layer additional styling. This approach ensures nothing breaks and the theme can be sequentially built upon.

---

## 📋 Table of Contents

1. [Brand Identity](#brand-identity)
2. [Color Palette](#color-palette)
3. [Typography](#typography)
4. [Spacing & Layout](#spacing--layout)
5. [UI Components](#ui-components)
6. [Navigation](#navigation)
7. [Product Components](#product-components)
8. [Forms & Inputs](#forms--inputs)
9. [Buttons](#buttons)
10. [Cards & Containers](#cards--containers)
11. [Responsive Design](#responsive-design)
12. [Implementation Roadmap](#implementation-roadmap)

---

## 🎨 Brand Identity

### Core Brand Values
- **Traditional Craftsmanship:** Warm, earthy tones that evoke traditional haberdashery
- **Modern Functionality:** Clean, accessible design with modern web standards
- **Trust & Reliability:** Professional presentation with clear information hierarchy

### Visual Identity
- **Logo Colors:** Brown (#542e26), Orange (#e87722), Red (#cb2c30)
- **Background:** Soft tan (#f1e5d6) - creates warm, welcoming atmosphere
- **Overall Aesthetic:** Clean, professional, warm, and accessible

---

## 🎨 Color Palette

### Primary Brand Colors

```css
/* Core Logo Colors - Use for primary branding */
--logo-brown: #542e26;        /* Primary brand color, text, headers */
--logo-orange: #e87722;       /* Accent color, CTAs, highlights */
--logo-red: #cb2c30;          /* Secondary accent, emphasis */
--dark-brown: #3e221c;        /* Darker variant for borders, depth */
```

**Usage Guidelines:**
- **Brown (#542e26):** Primary text, headings, navigation links, main brand elements
- **Orange (#e87722):** Call-to-action buttons, links, hover states, highlights
- **Red (#cb2c30):** Secondary CTAs, pricing highlights, discount badges
- **Dark Brown (#3e221c):** Strong borders, category cards, footer

### Background Colors

```css
/* Background Colors */
--soft-tan: #f1e5d6;          /* Main page background */
--white: #ffffff;             /* Card backgrounds, containers */
--bg-light-cream: #f9f4ee;    /* Alternative light background */
```

**Usage Guidelines:**
- Use soft tan as the main body background to create warmth
- Use white for content cards, product cards, form containers
- Light cream for subtle section differentiation

### UI & Semantic Colors

```css
/* Borders & Dividers */
--border-light: #ddd;         /* Light borders, dividers */
--border-medium: #ccc;        /* Medium contrast borders */
--border-dark: #999;          /* Strong borders */

/* Text Colors */
--text-main: #542e26;         /* Primary text (uses logo-brown) */
--text-secondary: #555;       /* Secondary text, descriptions */
--text-muted: #777;           /* Tertiary text, metadata */
--text-light: #999;           /* Placeholder text, disabled states */

/* State Colors */
--color-success: #28a745;     /* Success messages, confirmations */
--color-error: #dc3545;       /* Error messages, validation */
--color-warning: #f59e0b;     /* Warning messages */
--color-info: #3b82f6;        /* Informational messages */
```

### Color Application Examples

**Navigation Bar:**
```css
/* Three-stripe gradient navigation */
background: linear-gradient(
  to bottom,
  #542e26 0%,    /* Brown stripe (top 33%) */
  #542e26 33.33%,
  #e87722 33.33%, /* Orange stripe (middle 33%) */
  #e87722 66.66%,
  #cb2c30 66.66%, /* Red stripe (bottom 33%) */
  #cb2c30 100%
);
```

**Links:**
```css
/* Standard link styling */
color: #e87722;              /* Orange for links */
text-decoration: none;

/* Hover state */
color: #cb2c30;              /* Red on hover */
text-decoration: underline;
```

---

## 📝 Typography

### Font Families

```css
/* Custom Brand Fonts */
--font-display: 'Pump Trid', sans-serif;    /* Display/decorative headings */
--font-heading: 'Quagmire', sans-serif;     /* Section headings, labels */
--font-body: sans-serif;                     /* Body text, descriptions */
```

**Font Files:**
- `Pump Trid Regular.ttf` - Display font for large, decorative headings
- `Quagmire Extended Bold.otf` - Bold heading font for section titles

**Font Loading:**
```css
@font-face {
  font-family: 'Pump Trid';
  src: url('../assets/fonts/PumpTriD Regular.ttf') format('truetype');
  font-display: swap;
}

@font-face {
  font-family: 'Quagmire';
  src: url('../assets/fonts/Quagmire Extended Bold.otf') format('opentype');
  font-display: swap;
}
```

### Font Sizes

```css
/* Font Size Scale */
--text-xs: 0.75rem;      /* 12px - Small labels, metadata */
--text-sm: 0.875rem;     /* 14px - Secondary text */
--text-base: 1rem;       /* 16px - Body text (default) */
--text-lg: 1.125rem;     /* 18px - Emphasized body text */
--text-xl: 1.25rem;      /* 20px - Small headings */
--text-2xl: 1.5rem;      /* 24px - Section headings */
--text-3xl: 1.875rem;    /* 30px - Page headings */
--text-4xl: 2.25rem;     /* 36px - Hero headings */
```

### Font Weights

```css
--font-normal: 400;      /* Body text */
--font-medium: 500;      /* Emphasized text */
--font-semibold: 600;    /* Strong emphasis */
--font-bold: 700;        /* Headings, CTAs */
```

### Line Heights

```css
--leading-tight: 1.25;    /* Tight spacing for headings */
--leading-normal: 1.5;    /* Standard body text */
--leading-relaxed: 1.625; /* Comfortable reading */
--leading-loose: 2;       /* Extra spacious */
```

### Typography Usage Examples

**Body Text:**
```css
body {
  font-family: var(--font-body);
  font-size: var(--text-base);
  line-height: var(--leading-normal);
  color: var(--text-main);
}
```

**Section Headings:**
```css
.section-title {
  font-family: 'Quagmire', sans-serif;
  color: var(--logo-brown);
  font-size: 1.8rem;
  margin: 2rem 0 1rem;
  border-bottom: 2px solid var(--logo-orange);
}
```

**Product Names:**
```css
.product-info h4 {
  font-family: 'Quagmire', sans-serif;
  color: var(--logo-orange);
  font-weight: var(--font-bold);
}
```

**Hero/Display Text:**
```css
.welcome-section h1 {
  font-family: 'Pump Trid', sans-serif;
  color: var(--logo-orange);
  font-size: 3rem;
}
```

**Navigation Links:**
```css
.nav-links a {
  font-family: var(--font-heading);
  text-transform: uppercase;
  font-size: 1.2rem;
  white-space: nowrap;
  line-height: 1;
}
```

---

## 📐 Spacing & Layout

### Spacing Scale

```css
/* Spacing System */
--space-1: 0.25rem;      /* 4px - Minimal spacing */
--space-2: 0.5rem;       /* 8px - Tight spacing */
--space-3: 0.75rem;      /* 12px - Small spacing */
--space-4: 1rem;         /* 16px - Default spacing */
--space-5: 1.25rem;      /* 20px - Medium spacing */
--space-6: 1.5rem;       /* 24px - Large spacing */
--space-8: 2rem;         /* 32px - XL spacing */
--space-10: 2.5rem;      /* 40px - XXL spacing */
--space-12: 3rem;        /* 48px - Section spacing */
--space-16: 4rem;        /* 64px - Major sections */
--space-20: 5rem;        /* 80px - Hero sections */
```

### Layout Dimensions

```css
/* Container Widths */
--max-width: 87.5rem;        /* 1400px - Maximum content width */
--mid-width: 43.75rem;       /* 700px - Medium content width */
--container-sm-width: 31.25rem; /* 500px - Small forms/modals */

/* Navigation */
--nav-height: 5rem;          /* 80px - Navigation bar height */
--logo-width: 15.625rem;     /* 250px - Logo width */

/* Sidebar (Backend) */
--sidebar-width: 16rem;             /* 256px - Full sidebar */
--sidebar-collapsed-width: 4.5rem;  /* 72px - Collapsed sidebar */
```

### Border Radius

```css
/* Border Radius Scale */
--border-radius-sm: 4px;     /* Small elements (inputs, tags) */
--border-radius-md: 8px;     /* Medium elements (cards) */
--border-radius-lg: 12px;    /* Large elements (featured cards) */
--border-radius-xl: 16px;    /* Extra large elements */
--border-radius-pill: 30px;  /* Pill-shaped buttons */
--radius-circle: 50%;        /* Circular elements */
```

### Box Shadows

```css
/* Shadow System (with brand brown tint) */
--shadow-xs: 0 1px 2px 0 rgba(84, 46, 38, 0.05);
--shadow-sm: 0 1px 3px 0 rgba(84, 46, 38, 0.1), 0 1px 2px -1px rgba(84, 46, 38, 0.1);
--shadow-md: 0 4px 6px -1px rgba(84, 46, 38, 0.1), 0 2px 4px -2px rgba(84, 46, 38, 0.1);
--shadow-lg: 0 10px 15px -3px rgba(84, 46, 38, 0.1), 0 4px 6px -4px rgba(84, 46, 38, 0.1);
--shadow-xl: 0 20px 25px -5px rgba(84, 46, 38, 0.1), 0 8px 10px -6px rgba(84, 46, 38, 0.1);
--shadow-2xl: 0 25px 50px -12px rgba(84, 46, 38, 0.25);
```

### Container Patterns

```css
/* Standard content container */
.catalog-container,
.portal-container {
  max-width: var(--max-width);
  margin: 0 auto;
  padding: 2rem 1rem;
}

/* Narrow content container */
.page-content-wrapper {
  max-width: var(--mid-width);
  margin: 0 auto;
  padding: 2rem 1rem;
}
```

---

## 🧩 UI Components

### Product Cards

**Text-based Product Card:**
```css
.product-list-item {
  background: white;
  border: 1px solid var(--border-light);
  border-radius: var(--border-radius-lg);
  padding: 1rem;
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  overflow: hidden;
  transition: box-shadow 0.3s ease;
}

.product-card-link:hover .product-list-item {
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
}

.product-card-link:hover {
  transform: translateY(-3px);
}
```

**Product Thumbnail:**
```css
.product-thumb img {
  width: 80px;
  height: 80px;
  object-fit: cover;
  border-radius: var(--border-radius-sm);
  transition: transform 0.3s ease;
}

.product-card-link:hover .product-thumb img {
  transform: scale(1.05);
}
```

**Product Title:**
```css
.product-info h4 {
  font-family: 'Quagmire', sans-serif;
  color: var(--logo-orange);
  margin-bottom: 0.5rem;
}
```

**Price Display:**
```css
.price {
  font-weight: bold;
  display: block;
  margin-top: 0.5rem;
}

.price.discount-price {
  color: var(--logo-red);
}
```

### Category Cards

**Visual Category Cards:**
```css
.category-card {
  position: relative;
  border: 4px solid var(--dark-brown);
  border-radius: var(--border-radius-lg);
  overflow: hidden;
  height: 200px;
  display: block;
}

.category-card img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s;
}

.category-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
}

.category-overlay h3 {
  font-family: 'Pump Trid', sans-serif;
  color: white;
  font-size: 2rem;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.8);
}

.category-card:hover img {
  transform: scale(1.1);
}
```

### Featured Category Cards (Homepage)

```css
.featured-category-card {
  flex: 0 1 450px;
  height: 300px;
  position: relative;
  border-radius: 12px;
  overflow: hidden;
  border: 6px solid var(--logo-brown);
  background-color: var(--logo-brown);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2);
  transition: transform 0.3s ease;
}

.featured-category-card:hover {
  transform: translateY(-5px);
}

.featured-category-card:hover img {
  transform: scale(1.1);
  opacity: 0.4;
}

/* Hover Text Label */
.category-label-overlay {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-family: 'Pump Trid', sans-serif;
  font-size: 3.5rem;
  color: white;
  text-shadow: 2px 2px 10px rgba(0, 0, 0, 0.8);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.featured-category-card:hover .category-label-overlay {
  opacity: 1;
}
```

---

## 🧭 Navigation

### Navigation Bar Structure

**Three-Stripe Gradient Background:**
```css
.navbar {
  height: var(--nav-height);  /* 5rem / 80px */
  width: 100%;
  position: relative;
  z-index: 1000;
  display: grid;
  grid-template-rows: 1fr 1fr 1fr;
  background: linear-gradient(
    to bottom,
    var(--logo-brown) 0%,
    var(--logo-brown) 33.33%,
    var(--logo-orange) 33.33%,
    var(--logo-orange) 66.66%,
    var(--logo-red) 66.66%,
    var(--logo-red) 100%
  );
}
```

**Navigation Links:**
```css
.nav-links {
  grid-row: 2;  /* Center row (orange stripe) */
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1.5rem;
  padding-left: var(--logo-width);
}

.nav-links a {
  font-family: var(--font-heading);
  color: var(--white);
  text-decoration: none;
  font-size: 1.2rem;
  text-transform: uppercase;
  white-space: nowrap;
  line-height: 1;
}

.nav-links a:hover {
  opacity: 0.8;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}
```

**Logo Overlay:**
```css
.nav-logo {
  position: absolute;
  left: 0;
  bottom: 0;
  height: 66.66%;  /* Covers bottom 2 stripes */
  width: var(--logo-width);
  z-index: 1001;
}

.nav-logo img {
  height: 100%;
  width: auto;
  display: block;
}
```

### Contact Footer Bar

```css
.persistent-contact-bar {
  background-color: var(--soft-tan);
  border-bottom: 2px solid var(--logo-brown);
  padding: 0.5rem 0;
  text-align: center;
}

.contact-content {
  display: flex;
  justify-content: center;
  gap: 1rem;
  flex-wrap: wrap;
  font-family: 'Quagmire', sans-serif;
  color: var(--logo-brown);
}

.contact-content a {
  color: var(--logo-brown);
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}
```

### Breadcrumb Navigation

```css
.breadcrumb {
  background-color: transparent;
  padding: clamp(0.75rem, 2vw, 1rem) clamp(1rem, 3vw, 2rem) 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
}

.breadcrumb-item a {
  color: var(--logo-orange);
  text-decoration: none;
  transition: color 0.3s ease;
}

.breadcrumb-item a:hover {
  color: var(--logo-red);
  text-decoration: underline;
}

/* Breadcrumb separator */
.breadcrumb-item:not(:last-child)::after {
  content: '>';
  margin: 0 0.5rem;
  color: var(--text-secondary);
}
```

---

## 📦 Product Components

### Product Grid Layout

```css
/* Product grid with responsive columns */
.text-catalog-section {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}

/* Category grid */
.category-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}
```

### Product Detail Hero Section

```css
.product-hero {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: clamp(1.5rem, 3vw, 2rem);
  margin-bottom: clamp(1.5rem, 3vw, 2rem);
  align-items: start;
}
```

### Product Gallery

```css
.product-gallery {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.product-image-main {
  position: relative;
  background-color: var(--white);
  border-radius: var(--border-radius-lg);
  overflow: hidden;
  aspect-ratio: 1;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  transition: box-shadow 0.3s ease;
}
```

### Wishlist Button

```css
.add-to-wishlist-btn {
  background: transparent;
  border: 2px solid #e0e0e0;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  color: #666;
}

.add-to-wishlist-btn:hover {
  background: #f5f5f5;
  border-color: var(--logo-red);
  color: var(--logo-red);
  transform: scale(1.1);
}

.add-to-wishlist-btn.added {
  background: var(--logo-red);
  border-color: var(--logo-red);
  color: white;
}
```

---

## 📝 Forms & Inputs

### Form Container

```css
.registration-form-container,
.login-form-container {
  max-width: 600px;
  margin: 2rem auto;
  background: white;
  padding: 2.5rem;
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  border: 2px solid var(--border-light);
}
```

### Form Groups

```css
.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-weight: 600;
  color: var(--logo-brown);
  font-size: 0.95rem;
}
```

### Input Fields

```css
.form-group input[type='text'],
.form-group input[type='email'],
.form-group input[type='tel'],
.form-group input[type='password'] {
  padding: 0.75rem;
  border: 2px solid var(--border-light);
  border-radius: var(--border-radius-sm);
  font-size: 1rem;
  font-family: inherit;
  transition: border-color 0.3s ease;
}

.form-group input:focus {
  outline: none;
  border-color: var(--logo-orange);
}

.form-group input:invalid:not(:placeholder-shown) {
  border-color: var(--logo-red);
}
```

### Select Dropdown

```css
.form-group select {
  padding: 0.75rem;
  border: 2px solid var(--border-light);
  border-radius: var(--border-radius-sm);
  font-size: 1rem;
  font-family: inherit;
  background-color: white;
  cursor: pointer;
  transition: border-color 0.3s ease;
}

.form-group select:focus {
  outline: none;
  border-color: var(--logo-orange);
}
```

### Checkbox Styling

```css
.checkbox-group label {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  font-weight: normal;
  cursor: pointer;
}

.checkbox-group input[type='checkbox'] {
  margin-top: 0.25rem;
  width: 18px;
  height: 18px;
  cursor: pointer;
}
```

### Password Input with Toggle

```css
.password-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.password-input-wrapper input {
  flex: 1;
  padding-right: 45px;
}

.toggle-password {
  position: absolute;
  right: 10px;
  background: none;
  border: none;
  cursor: pointer;
  padding: 5px;
  color: var(--text-secondary);
  transition: color 0.3s ease;
}

.toggle-password:hover {
  color: var(--logo-orange);
}
```

### Error & Success States

```css
/* Error message */
.error-message {
  background-color: #fee;
  border: 2px solid var(--logo-red);
  color: #c00;
  padding: 1rem;
  border-radius: var(--border-radius-sm);
  margin-bottom: 1.5rem;
}

/* Success message */
.success-message {
  background-color: #efe;
  border: 2px solid #4caf50;
  color: #2e7d32;
  padding: 1rem;
  border-radius: var(--border-radius-sm);
  margin-bottom: 1.5rem;
}

/* Field-level errors */
.field-error {
  color: var(--logo-red);
  font-size: 0.85rem;
  margin-top: 0.25rem;
}

.input-error {
  border-color: var(--logo-red) !important;
}
```

---

## 🔘 Buttons

### Button Base Styles

```css
.btn {
  padding: 0.875rem 2rem;
  border: none;
  border-radius: var(--border-radius-pill);
  font-size: 1rem;
  font-weight: bold;
  cursor: pointer;
  text-decoration: none;
  text-align: center;
  transition: all 0.3s ease;
  display: inline-block;
}
```

### Primary Button

```css
.btn-primary {
  background-color: var(--logo-orange);
  color: white;
}

.btn-primary:hover {
  background-color: var(--logo-red);
}
```

### Secondary Button

```css
.btn-secondary {
  background-color: white;
  color: var(--logo-brown);
  border: 2px solid var(--logo-brown);
}

.btn-secondary:hover {
  background-color: var(--logo-brown);
  color: white;
}
```

### Breadcrumb Buttons

```css
/* Orange button variant */
.breadcrumb-btn-orange {
  padding: 0.5rem 1rem;
  background-color: var(--logo-orange);
  color: var(--white);
  border: none;
  border-radius: var(--border-radius-sm);
  font-size: 0.875rem;
  font-weight: 600;
  transition: all 0.3s ease;
}

.breadcrumb-btn-orange:hover {
  background-color: var(--logo-red);
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

/* Gradient button variant */
.breadcrumb-btn-red {
  background: linear-gradient(135deg, var(--logo-red) 0%, var(--logo-orange) 100%);
  color: var(--white);
}

.breadcrumb-btn-red:hover {
  background: linear-gradient(135deg, var(--logo-orange) 0%, var(--logo-red) 100%);
}
```

---

## 🎴 Cards & Containers

### Standard White Card

```css
.info-box,
.registration-benefits {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}
```

### Registration Card (Interactive)

```css
.registration-card {
  flex: 0 1 450px;
  min-height: 400px;
  position: relative;
  border-radius: 12px;
  overflow: hidden;
  border: 4px solid var(--logo-brown);
  background: white;
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
}

.registration-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 15px 30px rgba(0, 0, 0, 0.2);
  border-color: var(--logo-orange);
}
```

### Info Box with Border Accent

```css
.info-box {
  background-color: rgba(249, 144, 65, 0.1);
  border-left: 4px solid var(--logo-orange);
  padding: 1rem;
  margin-top: 1.5rem;
  border-radius: 4px;
}
```

### Section with Bordered Title

```css
.info-box h3 {
  font-family: 'Quagmire', sans-serif;
  color: var(--logo-red);
  border-bottom: 0.125rem solid var(--logo-orange);
  padding-bottom: 0.625rem;
  margin-bottom: 0.9375rem;
}
```

---

## 📱 Responsive Design

### Breakpoints

```css
/* Mobile-first approach */
/* Default: Mobile styles */
/* Tablet: 768px and up */
/* Desktop: 1024px and up */
```

### Mobile Navigation

```css
@media (max-width: 768px) {
  .navbar {
    height: auto;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 1rem 0;
  }

  .nav-logo {
    position: static;
    height: auto;
    width: 200px;
    margin-bottom: 1rem;
  }

  .nav-links {
    width: 100%;
    padding-left: 0;
    flex-wrap: wrap;
    justify-content: center;
  }

  .nav-links a {
    font-size: 1rem;
    padding: 0.5rem;
    white-space: normal;
  }
}
```

### Mobile Product Grid

```css
@media (max-width: 768px) {
  .product-hero {
    grid-template-columns: 1fr;  /* Stack vertically */
  }

  .featured-category-card {
    flex: 1 1 100%;
    height: 250px;
  }

  .category-label-overlay {
    font-size: 2.5rem;
  }
}
```

### Mobile Forms

```css
@media (max-width: 768px) {
  .registration-form-container {
    margin: 1rem;
    padding: 1.5rem;
  }

  .form-actions {
    flex-direction: column;
  }

  .btn {
    width: 100%;
  }

  .form-row {
    grid-template-columns: 1fr;  /* Stack form fields */
  }
}
```

### Responsive Utility: clamp()

```css
/* Dynamic font sizes */
font-size: clamp(0.85rem, 1.5vw, 0.95rem);

/* Dynamic padding */
padding: clamp(0.75rem, 2vw, 1rem) clamp(1rem, 3vw, 2rem);

/* Dynamic gaps */
gap: clamp(1.5rem, 3vw, 2rem);
```

---

## 🎯 Implementation Roadmap

This roadmap is designed for **conservative, incremental implementation** to ensure nothing breaks at any stage.

### Phase 1: Foundation (Priority: HIGH)
**Goal:** Establish core brand identity without breaking existing theme

- [ ] **1.1 CSS Variables Setup**
  - Create custom CSS variables file
  - Define all color palette variables
  - Define typography variables
  - Define spacing variables
  - Test: Verify variables are accessible globally

- [ ] **1.2 Brand Colors**
  - Replace primary colors with brand brown (#542e26)
  - Replace accent colors with brand orange (#e87722)
  - Replace secondary accent with brand red (#cb2c30)
  - Update link colors (orange → red on hover)
  - Test: Check all pages for color consistency

- [ ] **1.3 Typography**
  - Upload custom fonts (Pump Trid, Quagmire)
  - Add @font-face declarations
  - Set body font to sans-serif
  - Set headings to Quagmire
  - Set display elements to Pump Trid
  - Test: Verify fonts load correctly, fallbacks work

- [ ] **1.4 Background Colors**
  - Set body background to soft tan (#f1e5d6)
  - Ensure content areas use white backgrounds
  - Test: Verify contrast ratios for accessibility

### Phase 2: Basic Components (Priority: HIGH)
**Goal:** Update common UI components with brand styling

- [ ] **2.1 Buttons**
  - Style primary buttons (orange background)
  - Style secondary buttons (outlined brown)
  - Add hover states (orange → red transition)
  - Update button border-radius to pill shape
  - Test: Check all button types across the site

- [ ] **2.2 Forms**
  - Update input borders to brand colors
  - Set focus states to orange
  - Style error states with red
  - Add proper border-radius
  - Test: Test all form fields, validation states

- [ ] **2.3 Cards & Containers**
  - Add subtle shadows to cards
  - Set border-radius for cards
  - Style card borders with brand colors
  - Add hover effects (lift + shadow)
  - Test: Verify cards display correctly on all pages

### Phase 3: Navigation (Priority: MEDIUM)
**Goal:** Implement distinctive navigation styling

- [ ] **3.1 Header/Navigation**
  - Consider three-stripe gradient or simplified version
  - Style navigation links (white text on colored background)
  - Add hover effects (opacity/shadow)
  - Ensure logo placement works
  - Test: Desktop and mobile navigation, all screen sizes

- [ ] **3.2 Breadcrumbs**
  - Style breadcrumb links (orange)
  - Add hover states (red)
  - Style separators
  - Test: Verify on product and category pages

- [ ] **3.3 Footer**
  - Match footer styling to brand
  - Add contact bar styling
  - Test: Check on all pages

### Phase 4: Product Components (Priority: MEDIUM)
**Goal:** Apply brand styling to product display elements

- [ ] **4.1 Product Cards**
  - Style product list items
  - Add hover effects (lift, shadow, image zoom)
  - Style product titles (Quagmire, orange)
  - Update price display (red for discounts)
  - Test: Product listing pages, search results

- [ ] **4.2 Product Detail Pages**
  - Style image gallery
  - Update product info section
  - Style quantity selectors
  - Add to cart button styling
  - Test: Various product types

- [ ] **4.3 Category Cards**
  - Add thick brown borders
  - Implement image hover zoom
  - Style category overlays
  - Test: Category browsing pages

### Phase 5: Enhanced Features (Priority: LOW)
**Goal:** Add advanced styling features progressively

- [ ] **5.1 Interactive Elements**
  - Wishlist heart button styling
  - Multi-step form progress indicators
  - Password strength meters
  - Test: User flows with these elements

- [ ] **5.2 Notifications**
  - Toast notifications styling
  - Alert messages
  - Success/error states
  - Test: Trigger various notifications

- [ ] **5.3 Advanced Animations**
  - Smooth transitions on hover
  - Fade-in animations
  - Loading states
  - Test: Performance impact

### Phase 6: Polish & Refinement (Priority: LOW)
**Goal:** Fine-tune details and optimize

- [ ] **6.1 Responsive Refinements**
  - Test all breakpoints
  - Adjust mobile-specific styling
  - Optimize touch targets
  - Test: Various devices and screen sizes

- [ ] **6.2 Accessibility**
  - Verify color contrast ratios
  - Add focus indicators
  - Test keyboard navigation
  - Test: Screen reader compatibility

- [ ] **6.3 Performance**
  - Optimize CSS delivery
  - Minimize CSS file size
  - Test: Page load times, Lighthouse scores

---

## 🔧 PrestaShop Hummingbird Integration Notes

### Where to Apply Styles

**Theme Override Files:**
```
themes/your-custom-theme/
├── assets/
│   ├── css/
│   │   ├── custom-variables.css     ← Phase 1: Add custom CSS variables
│   │   ├── custom-theme.css         ← Phase 2-6: Progressive enhancements
│   │   └── custom-overrides.css     ← Specific Hummingbird overrides
│   └── fonts/
│       ├── PumpTriD-Regular.ttf
│       └── QuagmireExtended-Bold.otf
├── templates/
│   ├── catalog/
│   │   ├── listing/
│   │   └── product.tpl              ← Product page customizations
│   └── _partials/
│       ├── header.tpl                ← Navigation customizations
│       └── footer.tpl                ← Footer customizations
└── config/
    └── theme.yml                     ← Theme configuration
```

### Key PrestaShop Classes to Target

**Product Listings:**
```css
/* Hummingbird product card */
.product-miniature { /* Apply .product-list-item styles */ }
.product-title { /* Apply .product-info h4 styles */ }
.product-price { /* Apply .price styles */ }
```

**Navigation:**
```css
/* Hummingbird header */
#header { /* Apply .navbar styles */ }
.top-menu { /* Apply .nav-links styles */ }
```

**Buttons:**
```css
/* Hummingbird buttons */
.btn-primary { /* Already exists, override with brand colors */ }
.btn-secondary { /* Add secondary styling */ }
.add-to-cart { /* Apply .btn-primary styles */ }
```

**Forms:**
```css
/* Hummingbird form elements */
.form-control { /* Apply input styling */ }
.custom-select { /* Apply select styling */ }
```

### Critical CSS Variables Mapping

**From Entretelas to PrestaShop:**
```css
/* Map Entretelas variables to PrestaShop theme.yml or CSS variables */

/* Colors */
$primary-color: #542e26;        /* --logo-brown */
$secondary-color: #e87722;      /* --logo-orange */
$accent-color: #cb2c30;         /* --logo-red */
$background-color: #f1e5d6;     /* --soft-tan */

/* Typography */
$font-family: sans-serif;       /* --font-body */
$heading-font-family: 'Quagmire', sans-serif;
$display-font-family: 'Pump Trid', sans-serif;

/* Layout */
$border-radius: 8px;            /* --border-radius-md */
$border-radius-pill: 30px;      /* --border-radius-pill */
```

### Testing Checklist for Each Phase

After implementing each phase:

1. **Visual Regression Testing:**
   - Compare before/after screenshots
   - Check all page types (home, category, product, cart, checkout)

2. **Cross-Browser Testing:**
   - Chrome, Firefox, Safari, Edge
   - Test desktop and mobile views

3. **Functionality Testing:**
   - Add to cart works
   - Forms submit correctly
   - Search functions properly
   - User account features work

4. **Performance Testing:**
   - Run Lighthouse audit
   - Check for CSS bloat
   - Verify font loading doesn't block rendering

5. **Accessibility Testing:**
   - WCAG contrast ratios
   - Keyboard navigation
   - Screen reader compatibility

---

## 📚 Additional Resources

### Color Palette Reference

**Quick Copy Hex Codes:**
```
Primary Brown:  #542e26
Primary Orange: #e87722
Primary Red:    #cb2c30
Dark Brown:     #3e221c
Soft Tan:       #f1e5d6
White:          #ffffff
Border Light:   #ddd
Text Secondary: #555
```

### Font Files Needed

1. **Pump Trid Regular** (`PumpTriD Regular.ttf`)
   - Used for: Large decorative headings, hero text
   - License: Verify licensing for commercial use

2. **Quagmire Extended Bold** (`Quagmire Extended Bold.otf`)
   - Used for: Section headings, navigation, labels
   - License: Verify licensing for commercial use

### Design Principles

1. **Warm & Welcoming:** Use soft tan background to create warmth
2. **Clear Hierarchy:** Use Quagmire for structure, Pump Trid for emphasis
3. **Brand Consistency:** Always use logo colors (brown, orange, red)
4. **Accessibility First:** Maintain contrast ratios, keyboard navigation
5. **Performance:** Optimize images, lazy load where possible
6. **Mobile-First:** Design for mobile, enhance for desktop

---

## 🎨 Color Psychology & Usage

**Brown (#542e26):** Trust, reliability, tradition
- Use for: Primary text, headers, navigation text when visible

**Orange (#e87722):** Energy, enthusiasm, warmth
- Use for: CTAs, links, highlights, active states

**Red (#cb2c30):** Urgency, emphasis, passion
- Use for: Sale prices, hover states, important actions

**Soft Tan (#f1e5d6):** Warmth, comfort, approachability
- Use for: Body background, creating welcoming atmosphere

---

## ✅ Final Notes for Implementation

1. **Start Small:** Begin with Phase 1 (colors and fonts) before moving to complex components
2. **Test Continuously:** After each change, verify nothing breaks
3. **Document Changes:** Keep track of what PrestaShop files/classes you override
4. **Backup First:** Always backup the theme before making changes
5. **Version Control:** Use Git to track changes and allow rollback
6. **Staging Environment:** Test all changes on staging before production
7. **User Feedback:** Gather feedback after each phase before moving forward
8. **Performance Monitoring:** Watch for any performance degradation

**Success Metrics:**
- ✅ No broken functionality
- ✅ Consistent brand appearance
- ✅ Improved user experience
- ✅ Maintained or improved performance
- ✅ Accessibility standards met
- ✅ Cross-browser compatibility

---

---

## 🚀 Quick Reference Card

### Essential Variables for Initial Setup

```css
/* Paste these into your theme CSS variables file first */
:root {
  /* Brand Colors */
  --logo-brown: #542e26;
  --logo-orange: #e87722;
  --logo-red: #cb2c30;
  --soft-tan: #f1e5d6;
  --white: #ffffff;
  
  /* Typography */
  --font-body: sans-serif;
  --font-heading: 'Quagmire', sans-serif;
  --font-display: 'Pump Trid', sans-serif;
  
  /* Spacing */
  --space-4: 1rem;
  --space-8: 2rem;
  
  /* Border Radius */
  --border-radius-sm: 4px;
  --border-radius-lg: 8px;
  --border-radius-pill: 30px;
  
  /* Layout */
  --max-width: 87.5rem;
  --nav-height: 5rem;
}
```

### Day 1 Checklist

- [ ] Create `custom-variables.css` with brand colors
- [ ] Upload custom fonts to theme
- [ ] Set body background to soft tan
- [ ] Change primary button color to orange
- [ ] Change link color to orange (hover: red)
- [ ] Test on homepage only
- [ ] Backup before proceeding

### Common Patterns Cheat Sheet

**Link with Hover:**
```css
a { color: #e87722; } /* Orange */
a:hover { color: #cb2c30; } /* Red */
```

**Button - Primary:**
```css
.btn-primary {
  background: #e87722;
  color: white;
  border-radius: 30px;
  padding: 0.875rem 2rem;
}
.btn-primary:hover { background: #cb2c30; }
```

**Card with Shadow:**
```css
.card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(84, 46, 38, 0.1);
}
```

**Product Card Hover:**
```css
.product-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
}
```

---

## 📁 Related Assets

**Logo Files:**
- `src/assets/images/logo_horiz.jpg` - Horizontal logo
- `src/assets/images/LOGO/color/logo_v_color.jpg` - Vertical color logo
- `src/assets/images/LOGO/bn/logo_v_bn.jpg` - Vertical B&W logo

**Font Files:**
- `src/assets/fonts/PumpTriD Regular.ttf`
- `src/assets/fonts/Quagmire Extended Bold.otf`

**Main CSS Files (Reference):**
- `src/css/variables.css` - Design tokens
- `src/css/style.css` - Main stylesheet
- `src/css/product-detail.css` - Product page styles
- `src/css/portal.css` - Homepage portal styles

---

## 💡 Tips for Success

1. **Take It Slow:** Complete one phase before starting the next
2. **Test Everything:** Check functionality after every change
3. **Use Staging:** Never test directly on production
4. **Keep Notes:** Document what PrestaShop classes you override
5. **Ask Questions:** If unsure, consult the team before proceeding
6. **Backup Often:** Create restore points before major changes
7. **Check Mobile:** Always test responsive behavior
8. **Mind Performance:** Monitor page load times with each change

**When in Doubt:** Start with colors and fonts only. Everything else can wait.

---

## 🆘 Troubleshooting

**Problem:** Fonts not loading
- **Solution:** Check font file paths, ensure MIME types are correct, verify @font-face syntax

**Problem:** Colors not applying
- **Solution:** Check CSS specificity, use `!important` sparingly as last resort, verify CSS file is loaded

**Problem:** Responsive layout breaking
- **Solution:** Test each breakpoint individually, check for hardcoded pixel values, use flexible units (rem, %)

**Problem:** Performance degradation
- **Solution:** Minimize CSS file, remove unused styles, optimize font loading with `font-display: swap`

**Problem:** Conflicts with Hummingbird theme
- **Solution:** Use more specific selectors, load custom CSS after theme CSS, use CSS custom properties for easy overrides

---

**Document Version:** 1.0  
**Last Updated:** 2026-02-16  
**Maintained By:** Development Team  
**For:** PrestaShop Custom Theme Development (Hummingbird Base)  
**Source Repository:** albertmmateo-blip/Web-Mateo-Fork
