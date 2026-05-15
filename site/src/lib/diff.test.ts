import { describe, it, expect } from 'vitest'
import { computeDiff } from './diff'
import type { BomData } from './types'

const testData: BomData = {
  last_updated: '2026-01-01T00:00:00Z',
  bom_versions: {
    '2026.01.00': {
      release_date: '2026-01-01',
      libraries: {
        'androidx.compose.ui': '1.10.0',
        'androidx.compose.material3': '1.3.0',
        'androidx.compose.runtime': '1.10.0',
      }
    },
    '2026.02.00': {
      release_date: '2026-02-01',
      libraries: {
        'androidx.compose.ui': '1.11.0',
        'androidx.compose.material3': '1.3.0',
        'androidx.compose.runtime': '1.11.0',
      }
    },
    '2026.03.00': {
      release_date: '2026-03-01',
      libraries: {
        'androidx.compose.ui': '1.11.1',
        'androidx.compose.material3': '1.4.0',
        'androidx.compose.runtime': '1.11.1',
      }
    },
  },
  library_releases: {
    'androidx.compose.ui': {
      '1.10.0': {
        release_date: '2026-01-01',
        release_notes_url: 'https://example.com/ui#1.10.0',
        changes: { new_features: [], bug_fixes: ['Fix A'], api_changes: [] }
      },
      '1.11.0': {
        release_date: '2026-02-01',
        release_notes_url: 'https://example.com/ui#1.11.0',
        changes: { new_features: ['Feature X'], bug_fixes: [], api_changes: [] }
      },
      '1.11.1': {
        release_date: '2026-03-01',
        release_notes_url: 'https://example.com/ui#1.11.1',
        changes: { new_features: [], bug_fixes: ['Fix B'], api_changes: [] }
      },
    },
    'androidx.compose.material3': {
      '1.3.0': {
        release_date: '2026-01-01',
        release_notes_url: 'https://example.com/material3#1.3.0',
        changes: { new_features: [], bug_fixes: [], api_changes: [] }
      },
      '1.4.0': {
        release_date: '2026-03-01',
        release_notes_url: 'https://example.com/material3#1.4.0',
        changes: { new_features: ['Material Feature'], bug_fixes: [], api_changes: [] }
      },
    },
    'androidx.compose.runtime': {
      '1.10.0': {
        release_date: '2026-01-01',
        release_notes_url: 'https://example.com/runtime#1.10.0',
        changes: { new_features: [], bug_fixes: [], api_changes: [] }
      },
      '1.11.0': {
        release_date: '2026-02-01',
        release_notes_url: 'https://example.com/runtime#1.11.0',
        changes: { new_features: [], bug_fixes: ['Runtime fix'], api_changes: [] }
      },
      '1.11.1': {
        release_date: '2026-03-01',
        release_notes_url: 'https://example.com/runtime#1.11.1',
        changes: { new_features: [], bug_fixes: [], api_changes: [] }
      },
    },
  },
  whats_new: {
    '2026.02.00': [{ title: 'Feb release', url: 'https://example.com/feb', summary: 'New stuff' }],
    '2026.03.00': [{ title: 'Mar release', url: 'https://example.com/mar', summary: 'More stuff' }],
  }
}

describe('computeDiff', () => {
  it('identifies changed libraries', () => {
    const result = computeDiff('2026.01.00', '2026.02.00', testData)
    expect(result.changed.map(c => c.group).sort()).toEqual([
      'androidx.compose.runtime',
      'androidx.compose.ui',
    ])
  })

  it('identifies unchanged libraries', () => {
    const result = computeDiff('2026.01.00', '2026.02.00', testData)
    expect(result.unchanged).toEqual(['androidx.compose.material3'])
  })

  it('includes correct fromVersion and toVersion', () => {
    const result = computeDiff('2026.01.00', '2026.02.00', testData)
    const ui = result.changed.find(c => c.group === 'androidx.compose.ui')!
    expect(ui.fromVersion).toBe('1.10.0')
    expect(ui.toVersion).toBe('1.11.0')
  })

  it('includes all intermediate release notes in range', () => {
    const result = computeDiff('2026.01.00', '2026.03.00', testData)
    const ui = result.changed.find(c => c.group === 'androidx.compose.ui')!
    expect(ui.releases).toHaveLength(2) // 1.11.0 and 1.11.1, not 1.10.0
    expect(ui.releases[0].changes.new_features).toContain('Feature X')
    expect(ui.releases[1].changes.bug_fixes).toContain('Fix B')
  })

  it('collects whatsNew articles for BOM versions strictly after from, up to and including to, newest first', () => {
    const result = computeDiff('2026.01.00', '2026.03.00', testData)
    expect(result.whatsNew).toHaveLength(2)
    expect(result.whatsNew[0].title).toBe('Mar release')
    expect(result.whatsNew[1].title).toBe('Feb release')
  })

  it('attaches bomVersion to each whatsNew item', () => {
    const result = computeDiff('2026.01.00', '2026.03.00', testData)
    expect(result.whatsNew[0].bomVersion).toBe('2026.03.00')
    expect(result.whatsNew[1].bomVersion).toBe('2026.02.00')
  })

  it('does not include whatsNew for the fromBom itself', () => {
    const result = computeDiff('2026.01.00', '2026.02.00', testData)
    expect(result.whatsNew).toHaveLength(1)
    expect(result.whatsNew[0].title).toBe('Feb release')
  })

  it('handles reversed from/to by swapping them', () => {
    const normal = computeDiff('2026.01.00', '2026.02.00', testData)
    const reversed = computeDiff('2026.02.00', '2026.01.00', testData)
    expect(reversed.changed.map(c => c.group).sort()).toEqual(
      normal.changed.map(c => c.group).sort()
    )
    expect(reversed.unchanged).toEqual(normal.unchanged)
  })
})
