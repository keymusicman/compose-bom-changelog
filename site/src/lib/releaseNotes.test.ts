import { describe, it, expect } from 'vitest'
import { mergeReleaseSections, mergedSectionsToMarkdown, versionTag } from './releaseNotes'
import type { LibraryRelease } from './types'

function release(version: string, html: string): LibraryRelease {
  return {
    version,
    release_date: '',
    release_notes_url: '',
    commits_url: '',
    release_notes_html: html,
  }
}

describe('versionTag', () => {
  it('returns "stable" for plain semver', () => {
    expect(versionTag('1.10.0')).toBe('stable')
  })

  it('returns suffix for pre-releases', () => {
    expect(versionTag('1.10.0-alpha02')).toBe('alpha02')
    expect(versionTag('1.10.0-beta01')).toBe('beta01')
    expect(versionTag('1.10.0-rc01')).toBe('rc01')
  })
})

describe('mergeReleaseSections', () => {
  it('recognizes <p><strong>Heading</strong></p> as section heading (AndroidX style)', () => {
    const merged = mergeReleaseSections([
      release(
        '1.10.0-alpha02',
        '<p><strong>Bug Fixes</strong></p><ul><li>Fixed X</li><li>Fixed Y</li></ul>'
      ),
    ])
    expect(merged).toHaveLength(1)
    expect(merged[0].heading).toBe('Bug Fixes')
    expect(merged[0].items).toHaveLength(2)
    expect(merged[0].items[0].html).toBe('Fixed X')
    expect(merged[0].items[0].fromVersion).toBe('alpha02')
  })

  it('recognizes <h4> as section heading too', () => {
    const merged = mergeReleaseSections([
      release('1.10.0', '<h4>API Changes</h4><ul><li>Added foo()</li></ul>'),
    ])
    expect(merged[0].heading).toBe('API Changes')
    expect(merged[0].items[0].fromVersion).toBe('stable')
  })

  it('merges same-named sections across pre-releases', () => {
    const merged = mergeReleaseSections([
      release(
        '1.10.0-alpha01',
        '<p><strong>Bug Fixes</strong></p><ul><li>Fixed A</li></ul>'
      ),
      release(
        '1.10.0-beta01',
        '<p><strong>Bug Fixes</strong></p><ul><li>Fixed B</li></ul>'
      ),
      release(
        '1.10.0',
        '<p><strong>Bug Fixes</strong></p><ul><li>Fixed C</li></ul>'
      ),
    ])
    expect(merged).toHaveLength(1)
    expect(merged[0].heading).toBe('Bug Fixes')
    expect(merged[0].items.map(i => i.fromVersion)).toEqual(['alpha01', 'beta01', 'stable'])
    expect(merged[0].items.map(i => i.html)).toEqual(['Fixed A', 'Fixed B', 'Fixed C'])
  })

  it('keeps distinct sections distinct, in encounter order', () => {
    const merged = mergeReleaseSections([
      release(
        '1.10.0-alpha01',
        '<p><strong>API Changes</strong></p><ul><li>Added X</li></ul>' +
          '<p><strong>Bug Fixes</strong></p><ul><li>Fixed Y</li></ul>'
      ),
    ])
    expect(merged.map(s => s.heading)).toEqual(['API Changes', 'Bug Fixes'])
  })

  it('puts content before any heading into an intro section with empty heading', () => {
    const merged = mergeReleaseSections([
      release(
        '1.0.0-beta01',
        '<p>Beta is a major milestone.</p><p><strong>Bug Fixes</strong></p><ul><li>X</li></ul>'
      ),
    ])
    expect(merged).toHaveLength(2)
    expect(merged[0].heading).toBe('')
    expect(merged[0].items[0].kind).toBe('p')
    expect(merged[0].items[0].html).toBe('Beta is a major milestone.')
    expect(merged[1].heading).toBe('Bug Fixes')
  })

  it('does not treat <p><strong>X</strong> Y</p> as a heading', () => {
    const merged = mergeReleaseSections([
      release(
        '1.10.0',
        '<p><strong>Note:</strong> this is just emphasis, not a heading.</p>'
      ),
    ])
    expect(merged).toHaveLength(1)
    expect(merged[0].heading).toBe('')
    expect(merged[0].items[0].kind).toBe('p')
  })

  it('skips releases with empty html', () => {
    const merged = mergeReleaseSections([
      release('1.10.0-beta02', ''),
      release(
        '1.10.0',
        '<p><strong>Bug Fixes</strong></p><ul><li>X</li></ul>'
      ),
    ])
    expect(merged).toHaveLength(1)
    expect(merged[0].items[0].fromVersion).toBe('stable')
  })
})

describe('mergedSectionsToMarkdown', () => {
  it('renders sections with bold headings and tagged items', () => {
    const merged = mergeReleaseSections([
      release(
        '1.10.0-alpha01',
        '<p><strong>Bug Fixes</strong></p><ul><li>Fixed A</li></ul>'
      ),
      release(
        '1.10.0',
        '<p><strong>Bug Fixes</strong></p><ul><li>Fixed B</li></ul>'
      ),
    ])
    const md = mergedSectionsToMarkdown(merged)
    expect(md).toContain('**Bug Fixes**')
    expect(md).toContain('- Fixed A _(alpha01)_')
    expect(md).toContain('- Fixed B')
    expect(md).not.toContain('_(stable)_')
  })
})
