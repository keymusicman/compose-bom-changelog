import type { LibraryRelease } from './types'

export interface MergedItem {
  html: string
  kind: 'li' | 'p' | 'other'
  fromVersion: string
}

export interface MergedSection {
  heading: string
  items: MergedItem[]
}

export function versionTag(version: string): string {
  const dash = version.indexOf('-')
  return dash === -1 ? 'stable' : version.slice(dash + 1)
}

function asSectionHeading(el: Element): string | null {
  const tag = el.tagName.toLowerCase()
  if (tag === 'h4' || tag === 'h5') {
    return (el.textContent ?? '').trim() || null
  }
  if (tag === 'p' && el.children.length === 1) {
    const child = el.children[0]
    const childTag = child.tagName.toLowerCase()
    if (childTag === 'strong' || childTag === 'b') {
      const parentText = (el.textContent ?? '').trim()
      const childText = (child.textContent ?? '').trim()
      if (parentText && parentText === childText) {
        return childText
      }
    }
  }
  return null
}

function extractItems(el: Element, fromVersion: string): MergedItem[] {
  const tag = el.tagName.toLowerCase()
  if (tag === 'ul' || tag === 'ol') {
    return Array.from(el.children)
      .filter(c => c.tagName.toLowerCase() === 'li')
      .map(li => ({ html: li.innerHTML, kind: 'li' as const, fromVersion }))
  }
  if (tag === 'p') {
    const html = el.innerHTML.trim()
    if (!html) return []
    return [{ html, kind: 'p', fromVersion }]
  }
  return [{ html: el.outerHTML, kind: 'other', fromVersion }]
}

export function mergeReleaseSections(releases: LibraryRelease[]): MergedSection[] {
  const sections: MergedSection[] = []
  const byHeading = new Map<string, MergedSection>()

  function getSection(heading: string): MergedSection {
    let section = byHeading.get(heading)
    if (!section) {
      section = { heading, items: [] }
      byHeading.set(heading, section)
      sections.push(section)
    }
    return section
  }

  for (const release of releases) {
    if (!release.release_notes_html.trim()) continue
    const tag = versionTag(release.version)
    const doc = new DOMParser().parseFromString(
      `<!doctype html><body>${release.release_notes_html}</body>`,
      'text/html'
    )
    const root = doc.body
    let currentHeading = ''

    for (const child of Array.from(root.children)) {
      const heading = asSectionHeading(child)
      if (heading !== null) {
        currentHeading = heading
        continue
      }
      const items = extractItems(child, tag)
      if (items.length === 0) continue
      getSection(currentHeading).items.push(...items)
    }
  }

  return sections.filter(s => s.items.length > 0)
}

export function mergedSectionsToMarkdown(sections: MergedSection[]): string {
  const lines: string[] = []
  for (const section of sections) {
    if (section.heading) {
      lines.push('', `**${section.heading}**`, '')
    }
    for (const item of section.items) {
      const text = htmlInlineToMarkdown(item.html)
      const tag = item.fromVersion === 'stable' ? '' : ` _(${item.fromVersion})_`
      if (item.kind === 'li') {
        lines.push(`- ${text}${tag}`)
      } else {
        lines.push('', `${text}${tag}`)
      }
    }
  }
  return lines.join('\n').replace(/\n{3,}/g, '\n\n').trim()
}

function htmlInlineToMarkdown(html: string): string {
  return html
    .replace(/<a\s+href="([^"]*)"[^>]*>([\s\S]*?)<\/a>/gi, '[$2]($1)')
    .replace(/<code[^>]*>([\s\S]*?)<\/code>/gi, '`$1`')
    .replace(/<strong[^>]*>([\s\S]*?)<\/strong>/gi, '**$1**')
    .replace(/<b[^>]*>([\s\S]*?)<\/b>/gi, '**$1**')
    .replace(/<em[^>]*>([\s\S]*?)<\/em>/gi, '*$1*')
    .replace(/<br\s*\/?>/gi, ' ')
    .replace(/<[^>]+>/g, '')
    .replace(/\s+/g, ' ')
    .trim()
}
