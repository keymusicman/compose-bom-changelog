export function htmlToMarkdown(html: string): string {
  return html
    .replace(/<a\s+href="([^"]*)"[^>]*>([^<]*)<\/a>/g, '[$2]($1)')
    .replace(/<code>([^<]*)<\/code>/g, '`$1`')
    .replace(/<strong>([^<]*)<\/strong>/g, '**$1**')
    .replace(/<[^>]+>/g, '')
}
