export interface Changes {
  new_features: string[]
  bug_fixes: string[]
  api_changes: string[]
}

export interface Commit {
  sha: string
  message: string
  url: string
}

export interface LibraryVersion {
  release_date: string
  release_notes_url: string
  commits_url?: string
  changes: Changes
  commits?: Commit[]
}

export interface BomVersion {
  release_date: string
  libraries: Record<string, string>
}

export interface Article {
  title: string
  url: string
  summary: string
}

export interface BomData {
  last_updated: string
  bom_versions: Record<string, BomVersion>
  library_releases: Record<string, Record<string, LibraryVersion>>
  whats_new: Record<string, Article[]>
}
