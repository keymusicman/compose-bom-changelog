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

  it('treats a markdown "### Heading" paragraph as a section heading', () => {
    const merged = mergeReleaseSections([
      release(
        '1.12.0',
        '<p>### Hardware-Accelerated Mesh Gradients (ui) </p><p>Painter API is new.</p>'
      ),
    ])
    expect(merged).toHaveLength(1)
    expect(merged[0].heading).toBe('Hardware-Accelerated Mesh Gradients (ui)')
    expect(merged[0].items.map(i => i.html)).toEqual(['Painter API is new.'])
  })

  it('keeps text that follows a "### Heading" in the same paragraph as an item', () => {
    const merged = mergeReleaseSections([
      release(
        '1.12.0',
        '<p>### 6. Espresso Integration for Hybrid UIs (ui-test)<br/>\nScope Compose interactions to the View hierarchy.</p>'
      ),
    ])
    expect(merged).toHaveLength(1)
    expect(merged[0].heading).toBe('6. Espresso Integration for Hybrid UIs (ui-test)')
    expect(merged[0].items.map(i => i.html)).toEqual([
      'Scope Compose interactions to the View hierarchy.',
    ])
  })

  it('drops code blocks that hold nothing but a ────── separator', () => {
    const merged = mergeReleaseSections([
      release(
        '1.12.0',
        '<p>Intro.</p><pre><code>────── \n</code></pre><p>Outro.</p>'
      ),
    ])
    expect(merged[0].items.map(i => i.html)).toEqual(['Intro.', 'Outro.'])
  })

  it('strips a trailing ────── separator line from a real code block', () => {
    const merged = mergeReleaseSections([
      release('1.12.0', '<pre><code>val a = 1\n──────\n</code></pre>'),
    ])
    expect(merged[0].items).toHaveLength(1)
    expect(merged[0].items[0].html).not.toContain('─')
    expect(merged[0].items[0].html).toContain('val a = 1')
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

describe('mergeReleaseSections — dedup', () => {
  it('drops an earlier item that shares a change-id with a later one (stable wins)', () => {
    const merged = mergeReleaseSections([
      release(
        '1.11.0-alpha03',
        '<p><strong>API Changes</strong></p><ul>' +
          '<li>Added a new api LookaheadAnimationVisualDebugging. (<a href="https://x/Id5575389fd198a82de8f3187c4ab2e16036e64d4">Id5575</a>, <a href="https://x/b/390011686">b/390011686</a>)</li>' +
          '</ul>'
      ),
      release(
        '1.11.0',
        '<p><strong>API Changes</strong></p><ul>' +
          '<li>Added new APIs LookaheadAnimationVisualDebugging, etc. (<a href="https://x/Id5575">Id5575</a>, <a href="https://x/b/390011686">b/390011686</a>)</li>' +
          '</ul>'
      ),
    ])
    expect(merged).toHaveLength(1)
    expect(merged[0].items).toHaveLength(1)
    expect(merged[0].items[0].fromVersion).toBe('stable')
    expect(merged[0].items[0].html).toContain('Added new APIs')
  })

  it('drops an earlier item whose text is contained in a later one (no tracker IDs)', () => {
    const merged = mergeReleaseSections([
      release(
        '1.11.0-alpha01',
        '<p><strong>New Features</strong></p><ul>' +
          '<li>Introduced visual debugging capabilities to allow visualizations of shared elements and animated bounds, including target bounds and trajectory.</li>' +
          '</ul>'
      ),
      release(
        '1.11.0',
        '<p><strong>New Features</strong></p><ul>' +
          '<li><strong>Visual Debugging:</strong> Introduced visual debugging capabilities to allow visualizations of shared elements and animated bounds, including target bounds and trajectory.</li>' +
          '</ul>'
      ),
    ])
    expect(merged).toHaveLength(1)
    expect(merged[0].items).toHaveLength(1)
    expect(merged[0].items[0].fromVersion).toBe('stable')
    expect(merged[0].items[0].html).toContain('<strong>Visual Debugging:</strong>')
  })

  it('dedupes items linked to the same Gerrit change-id with no I prefix (bare hex like 0aba38)', () => {
    const merged = mergeReleaseSections([
      release(
        '1.11.0-beta02',
        '<p><strong>Bug Fixes</strong></p><ul>' +
          '<li><code>SeekableTransitionState</code> now properly handles off-thread state changes. (<a href="https://android-review.googlesource.com/#/q/0aba38">0aba38</a>)</li>' +
          '</ul>'
      ),
      release(
        '1.11.0',
        '<p><strong>Bug Fixes</strong></p><ul>' +
          '<li><strong>Thread Safety:</strong> <code>SeekableTransitionState</code> now properly handles off-thread state changes. (<a href="https://android-review.googlesource.com/#/q/0aba38">0aba38</a>)</li>' +
          '</ul>'
      ),
    ])
    expect(merged).toHaveLength(1)
    expect(merged[0].items).toHaveLength(1)
    expect(merged[0].items[0].fromVersion).toBe('stable')
    expect(merged[0].items[0].html).toContain('Thread Safety')
  })

  it('substring dedupe tolerates tiny whitespace/punctuation differences between releases', () => {
    const merged = mergeReleaseSections([
      release(
        '1.0.0-alpha01',
        '<p><strong>Bug Fixes</strong></p><ul>' +
          '<li>Some long description of the fix with details that go on for a while.( extra )</li>' +
          '</ul>'
      ),
      release(
        '1.0.0',
        '<p><strong>Bug Fixes</strong></p><ul>' +
          '<li><strong>Prefix:</strong> Some long description of the fix with details that go on for a while. ( extra )</li>' +
          '</ul>'
      ),
    ])
    expect(merged[0].items).toHaveLength(1)
    expect(merged[0].items[0].fromVersion).toBe('stable')
  })

  it('keeps distinct items that happen to share a section heading', () => {
    const merged = mergeReleaseSections([
      release(
        '1.11.0-alpha01',
        '<p><strong>Bug Fixes</strong></p><ul>' +
          '<li>Fixed thread safety in SeekableTransitionState. (<a href="https://x/Ia">Ia11111</a>)</li>' +
          '</ul>'
      ),
      release(
        '1.11.0',
        '<p><strong>Bug Fixes</strong></p><ul>' +
          '<li>Performance: Improved sharedElements map access. (<a href="https://x/Ib">Ib22222</a>)</li>' +
          '</ul>'
      ),
    ])
    expect(merged).toHaveLength(1)
    expect(merged[0].items).toHaveLength(2)
    expect(merged[0].items.map(i => i.fromVersion)).toEqual(['alpha01', 'stable'])
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
