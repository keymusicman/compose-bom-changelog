import type { BomData, LibraryVersion, LibraryRelease, Article } from './types'

export interface LibraryDiff {
  group: string
  fromVersion: string | undefined
  toVersion: string | undefined
  releases: LibraryRelease[]
}

export interface ReleaseGroup {
  stableVersion: string
  releaseDate: string
  releaseNotesUrl: string
  commitsUrl: string
  releases: LibraryRelease[]
}

export function groupReleasesByStable(releases: LibraryRelease[]): ReleaseGroup[] {
  const map = new Map<string, LibraryRelease[]>()
  for (const r of releases) {
    const stableKey = r.version.split('-')[0]
    const list = map.get(stableKey) ?? []
    list.push(r)
    map.set(stableKey, list)
  }
  const groups: ReleaseGroup[] = []
  for (const [stableVersion, items] of map) {
    const sorted = [...items].sort((a, b) => compareSemver(a.version, b.version))
    const stable = sorted.find(r => !r.version.includes('-'))
    const last = sorted[sorted.length - 1]
    groups.push({
      stableVersion,
      releaseDate: stable?.release_date ?? last.release_date,
      releaseNotesUrl: stable?.release_notes_url ?? last.release_notes_url,
      commitsUrl: stable?.commits_url ?? last.commits_url,
      releases: sorted,
    })
  }
  return groups.sort((a, b) => compareSemver(a.stableVersion, b.stableVersion))
}

export type WhatsNewItem = Article & { bomVersion: string }

export interface DiffResult {
  changed: LibraryDiff[]
  unchanged: string[]
  whatsNew: WhatsNewItem[]
}

function parseSemver(v: string): [number, number, number, string] {
  const [main = '', pre = ''] = v.split('-')
  const [major = 0, minor = 0, patch = 0] = main.split('.').map(Number)
  return [major, minor, patch, pre]
}

export function compareSemver(a: string, b: string): number {
  const [aMaj, aMin, aPatch, aPre] = parseSemver(a)
  const [bMaj, bMin, bPatch, bPre] = parseSemver(b)
  if (aMaj !== bMaj) return aMaj - bMaj
  if (aMin !== bMin) return aMin - bMin
  if (aPatch !== bPatch) return aPatch - bPatch
  // stable > pre-release
  if (!aPre && bPre) return 1
  if (aPre && !bPre) return -1
  return aPre.localeCompare(bPre)
}

function sortedBomVersions(data: BomData): string[] {
  // BOM versions are YYYY.MM.PP — lexicographic sort works due to zero-padding
  return Object.keys(data.bom_versions).sort()
}

function releasesInRange(
  groupReleases: Record<string, LibraryVersion>,
  fromVersion: string,
  toVersion: string
): LibraryRelease[] {
  return Object.entries(groupReleases)
    .filter(([v]) => compareSemver(v, fromVersion) > 0 && compareSemver(v, toVersion) <= 0)
    .sort(([a], [b]) => compareSemver(a, b))
    .map(([version, release]) => ({ version, ...release }))
}

export function computeDiff(
  fromBom: string,
  toBom: string,
  data: BomData
): DiffResult {
  const sorted = sortedBomVersions(data)
  const fromIdx = sorted.indexOf(fromBom)
  const toIdx = sorted.indexOf(toBom)

  // Ensure from < to by swapping if reversed
  const [actualFrom, actualTo, actualFromIdx, actualToIdx] =
    fromIdx <= toIdx
      ? [fromBom, toBom, fromIdx, toIdx]
      : [toBom, fromBom, toIdx, fromIdx]

  const fromLibraries = data.bom_versions[actualFrom]?.libraries ?? {}
  const toLibraries = data.bom_versions[actualTo]?.libraries ?? {}
  const allGroups = new Set([...Object.keys(fromLibraries), ...Object.keys(toLibraries)])

  const changed: LibraryDiff[] = []
  const unchanged: string[] = []

  for (const group of [...allGroups].sort()) {
    const fromVersion = fromLibraries[group]
    const toVersion = toLibraries[group]

    if (fromVersion === toVersion) {
      unchanged.push(group)
    } else {
      const groupReleases = data.library_releases[group] ?? {}
      const releases =
        fromVersion && toVersion
          ? releasesInRange(groupReleases, fromVersion, toVersion)
          : []
      changed.push({ group, fromVersion, toVersion, releases })
    }
  }

  // whatsNew: BOM versions strictly after actualFrom, up to and including actualTo, newest first
  const inRange = sorted.slice(actualFromIdx + 1, actualToIdx + 1).reverse()
  const whatsNew: WhatsNewItem[] = inRange.flatMap(v =>
    (data.whats_new[v] ?? []).map(a => ({ ...a, bomVersion: v }))
  )

  return { changed, unchanged, whatsNew }
}
