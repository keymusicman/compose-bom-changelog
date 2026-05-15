import type { BomData, LibraryVersion, Article } from './types'

export interface LibraryDiff {
  group: string
  fromVersion: string | undefined
  toVersion: string | undefined
  releases: LibraryVersion[]
}

export interface DiffResult {
  changed: LibraryDiff[]
  unchanged: string[]
  whatsNew: Article[]
}

function parseSemver(v: string): [number, number, number, string] {
  const [main = '', pre = ''] = v.split('-')
  const [major = 0, minor = 0, patch = 0] = main.split('.').map(Number)
  return [major, minor, patch, pre]
}

function compareSemver(a: string, b: string): number {
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
): LibraryVersion[] {
  return Object.entries(groupReleases)
    .filter(([v]) => compareSemver(v, fromVersion) > 0 && compareSemver(v, toVersion) <= 0)
    .sort(([a], [b]) => compareSemver(a, b))
    .map(([, release]) => release)
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

  // whatsNew: BOM versions strictly after actualFrom, up to and including actualTo
  const inRange = sorted.slice(actualFromIdx + 1, actualToIdx + 1)
  const whatsNew = inRange.flatMap(v => data.whats_new[v] ?? [])

  return { changed, unchanged, whatsNew }
}
