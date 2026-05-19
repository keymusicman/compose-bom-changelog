export function htmlToMarkdown(html: string): string {
  if (!html) return ''
  return html
    // headings → bold (avoids collision with section levels added by callers)
    .replace(/<h4[^>]*>/gi, '\n\n**')
    .replace(/<\/h4>/gi, '**\n\n')
    .replace(/<h5[^>]*>/gi, '\n\n**')
    .replace(/<\/h5>/gi, '**\n\n')
    // paragraphs and line breaks
    .replace(/<p[^>]*>/gi, '')
    .replace(/<\/p>/gi, '\n\n')
    .replace(/<br\s*\/?>/gi, '\n')
    // list items
    .replace(/<li[^>]*>/gi, '- ')
    .replace(/<\/li>/gi, '\n')
    .replace(/<\/?(ul|ol)[^>]*>/gi, '')
    // inline
    .replace(/<a\s+href="([^"]*)"[^>]*>([\s\S]*?)<\/a>/gi, '[$2]($1)')
    .replace(/<code[^>]*>([\s\S]*?)<\/code>/gi, '`$1`')
    .replace(/<strong[^>]*>([\s\S]*?)<\/strong>/gi, '**$1**')
    .replace(/<b[^>]*>([\s\S]*?)<\/b>/gi, '**$1**')
    .replace(/<em[^>]*>([\s\S]*?)<\/em>/gi, '*$1*')
    // strip any remaining tags
    .replace(/<[^>]+>/g, '')
    // collapse 3+ newlines into 2
    .replace(/\n{3,}/g, '\n\n')
    .trim()
}
