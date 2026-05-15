import type { PageLoad } from './$types'
import type { BomData } from '$lib/types'

export const load: PageLoad = async ({ fetch }) => {
  const response = await fetch('/data/bom-data.json')
  if (!response.ok) {
    throw new Error(`Failed to load BOM data: ${response.status}`)
  }
  const data: BomData = await response.json()
  return { data }
}
