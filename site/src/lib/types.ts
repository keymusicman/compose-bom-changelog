export interface LibraryVersion {
  release_date: string
  release_notes_url: string
  commits_url: string
  release_notes_html: string
}

export interface LibraryRelease extends LibraryVersion {
  version: string
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
